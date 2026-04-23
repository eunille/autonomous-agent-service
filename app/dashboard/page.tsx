"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Loader2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  RefreshCw,
  Play,
  Upload,
  Lock,
  LayoutDashboard,
  Inbox,
  ChevronLeft,
  FlaskConical,
  Plus,
  X,
  LogOut,
} from "lucide-react"

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type StepLabel = "researching" | "scoring" | "drafting_email" | "logging" | "done" | "error"

interface BatchInputRow {
  id: string
  company: string
  email: string
  leadName: string
}

interface BatchRow {
  index: number
  leadName: string
  company: string
  step: StepLabel | null
  score: number | null
  tier: string | null
  reasoning: string
  recommendedAction: string
  emailSubject: string
  emailBody: string
  leadId: string | null
  agentSteps: number | null
  error: string | null
}

interface HistoryLead {
  id: string
  lead_name: string
  company: string
  email: string
  score: number | null
  tier: string | null
  email_status: string | null
  region: string | null
  recommended_action: string | null
  email_subject: string | null
  email_draft: string | null
  created_at: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const STEP_LABELS: Record<StepLabel, string> = {
  researching: "Researching",
  scoring: "Scoring",
  drafting_email: "Drafting email",
  logging: "Logging",
  done: "Done",
  error: "Error",
}

const TIER_COLORS: Record<string, string> = {
  HOT: "bg-red-500/20 text-red-400 border-red-500/30",
  WARM: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  COLD: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  DISQUALIFY: "bg-zinc-700/50 text-zinc-400 border-zinc-600",
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://autonomous-agent-service.onrender.com"
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? ""
const DASHBOARD_PASSWORD = process.env.NEXT_PUBLIC_DASHBOARD_PASSWORD ?? ""

const AUTH_STORAGE_KEY = "dashboard_authed"
const PAGE_SIZE = 10

const SAMPLE_BATCH = `Sprout Solutions, hr@sproutsolutions.com.ph, Maria Santos
PayMongo, operations@paymongo.com, Juan Reyes
GrowSari, partners@growsari.com, Ana Cruz
Konduit, info@konduit.me, Mark Lim
Ortega Group, hr@ortegagroup.com.ph, Rosa Ortega`

const SAMPLE_ROWS: Omit<BatchInputRow, "id">[] = [
  { company: "Sprout Solutions", email: "hr@sproutsolutions.com.ph", leadName: "Maria Santos" },
  { company: "PayMongo", email: "operations@paymongo.com", leadName: "Juan Reyes" },
  { company: "GrowSari", email: "partners@growsari.com", leadName: "Ana Cruz" },
  { company: "Konduit", email: "info@konduit.me", leadName: "Mark Lim" },
  { company: "Ortega Group", email: "hr@ortegagroup.com.ph", leadName: "Rosa Ortega" },
]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseBatchInput(raw: string): Array<{ lead_name: string; company: string; email: string }> {
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const parts = line.split(",").map((p) => p.trim())
      const company = parts[0] ?? ""
      const email = parts[1] ?? `contact@${company.toLowerCase().replace(/\s+/g, "")}.com`
      const lead_name = parts[2] ?? "Contact"
      return { company, email, lead_name }
    })
    .filter((row) => row.company.length > 0)
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("en-PH", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function TierBadge({ tier }: { tier: string | null }) {
  if (!tier) return null
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${TIER_COLORS[tier] ?? "bg-zinc-700 text-zinc-300"}`}
    >
      {tier}
    </span>
  )
}

function StepIndicator({ step }: { step: StepLabel | null }) {
  if (!step) return <span className="text-zinc-500 text-sm">Waiting</span>
  if (step === "done")
    return (
      <span className="flex items-center gap-1.5 text-emerald-400 text-sm">
        <CheckCircle2 size={14} />
        Done
      </span>
    )
  if (step === "error")
    return (
      <span className="flex items-center gap-1.5 text-red-400 text-sm">
        <XCircle size={14} />
        Error
      </span>
    )
  return (
    <span className="flex items-center gap-1.5 text-zinc-300 text-sm">
      <Loader2 size={14} className="animate-spin text-emerald-400" />
      {STEP_LABELS[step]}
    </span>
  )
}

function EmailPreview({
  subject,
  body,
  leadName,
  company,
}: {
  subject: string
  body: string
  leadName: string
  company: string
}) {
  if (!body) return <p className="text-zinc-500 text-sm">No email draft — score below threshold.</p>
  return (
    <div className="space-y-3">
      <div>
        <span className="text-xs text-zinc-500 uppercase tracking-wide">Subject</span>
        <p className="text-zinc-200 text-sm mt-0.5">{subject || "(no subject)"}</p>
      </div>
      <div>
        <span className="text-xs text-zinc-500 uppercase tracking-wide">Body</span>
        <pre className="mt-1 text-zinc-300 text-sm whitespace-pre-wrap font-sans leading-relaxed border border-zinc-800 rounded-lg p-3 bg-zinc-950/50">
          {body}
        </pre>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main dashboard
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  // Auth
  const [authed, setAuthed] = useState(false)
  const [passwordInput, setPasswordInput] = useState("")
  const [authError, setAuthError] = useState("")

  // Batch form
  const [batchInput, setBatchInput] = useState(
    "Sprout Solutions, careers@sproutsolutions.ph, Maria Santos\nPayMongo, hr@paymongo.com, Juan Reyes"
  )
  const [batchInputRows, setBatchInputRows] = useState<BatchInputRow[]>([
    { id: crypto.randomUUID(), company: "", email: "", leadName: "" },
    { id: crypto.randomUUID(), company: "", email: "", leadName: "" },
    { id: crypto.randomUUID(), company: "", email: "", leadName: "" },
  ])
  const [defaultRegion, setDefaultRegion] = useState("Philippines")
  const [isRunning, setIsRunning] = useState(false)
  const [batchRows, setBatchRows] = useState<BatchRow[]>([])
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())

  // Run history
  const [history, setHistory] = useState<HistoryLead[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState("")
  const [expandedHistory, setExpandedHistory] = useState<Set<string>>(new Set())
  const [historyPage, setHistoryPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)

  const abortRef = useRef<AbortController | null>(null)

  // ── Auth ────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = sessionStorage.getItem(AUTH_STORAGE_KEY)
      if (stored === "1") setAuthed(true)
    }
  }, [])

  function handleAuth() {
    const correct = DASHBOARD_PASSWORD || API_KEY
    if (!correct || passwordInput === correct) {
      sessionStorage.setItem(AUTH_STORAGE_KEY, "1")
      setAuthed(true)
    } else {
      setAuthError("Incorrect password.")
    }
  }

  function handleLogout() {
    sessionStorage.removeItem(AUTH_STORAGE_KEY)
    setAuthed(false)
    setPasswordInput("")
    setAuthError("")
  }

  // ── Run history ─────────────────────────────────────────────────────────
  const fetchHistory = useCallback(async (page = 1) => {
    setHistoryLoading(true)
    setHistoryError("")
    try {
      const offset = (page - 1) * PAGE_SIZE
      const res = await fetch(`${API_BASE}/leads?limit=${PAGE_SIZE + 1}&offset=${offset}`, {
        headers: { "X-API-Key": API_KEY },
      })
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
      const data = await res.json()
      const leads: HistoryLead[] = data.leads ?? []
      setHasMore(leads.length > PAGE_SIZE)
      setHistory(leads.slice(0, PAGE_SIZE))
    } catch (err) {
      setHistoryError(err instanceof Error ? err.message : "Failed to load history.")
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
    if (authed) fetchHistory(1)
  }, [authed, fetchHistory])

  // ── Batch run ───────────────────────────────────────────────────────────
  function addInputRow() {
    setBatchInputRows((prev) => [
      ...prev,
      { id: crypto.randomUUID(), company: "", email: "", leadName: "" },
    ])
  }

  function removeInputRow(id: string) {
    setBatchInputRows((prev) => prev.filter((row) => row.id !== id))
  }

  function updateInputRow(id: string, field: keyof Omit<BatchInputRow, "id">, value: string) {
    setBatchInputRows((prev) =>
      prev.map((row) => (row.id === id ? { ...row, [field]: value } : row))
    )
  }

  function loadSampleRows() {
    setBatchInputRows(SAMPLE_ROWS.map((row) => ({ ...row, id: crypto.randomUUID() })))
  }

  async function runBatch() {
    const leads = batchInputRows
      .filter((row) => row.company.trim().length > 0)
      .map((row) => ({
        company: row.company.trim(),
        email: row.email.trim() || `contact@${row.company.toLowerCase().replace(/\s+/g, "")}.com`,
        lead_name: row.leadName.trim() || "Contact",
      }))
    if (leads.length === 0) return

    abortRef.current = new AbortController()
    setIsRunning(true)
    setExpandedRows(new Set())

    const initial: BatchRow[] = leads.map((l, i) => ({
      index: i,
      leadName: l.lead_name,
      company: l.company,
      step: null,
      score: null,
      tier: null,
      reasoning: "",
      recommendedAction: "",
      emailSubject: "",
      emailBody: "",
      leadId: null,
      agentSteps: null,
      error: null,
    }))
    setBatchRows(initial)

    try {
      const res = await fetch(`${API_BASE}/qualify-batch`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
        },
        body: JSON.stringify({
          leads: leads.map((l) => ({
            lead_name: l.lead_name,
            company: l.company,
            email: l.email,
            source: "dashboard",
            region: defaultRegion,
          })),
        }),
        signal: abortRef.current.signal,
      })

      if (!res.ok || !res.body) {
        throw new Error(`Server returned ${res.status}`)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split("\n")
        buffer = lines.pop() ?? ""

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          try {
            const event = JSON.parse(line.slice(6))
            handleSSEEvent(event)
          } catch {
            // Ignore malformed events
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        console.error("Batch stream error:", err)
      }
    } finally {
      setIsRunning(false)
      fetchHistory()
    }
  }

  function handleSSEEvent(event: Record<string, unknown>) {
    const type = event.type as string
    const index = event.index as number

    if (type === "step") {
      setBatchRows((prev) =>
        prev.map((row) =>
          row.index === index ? { ...row, step: event.step as StepLabel } : row
        )
      )
    } else if (type === "lead_done") {
      setBatchRows((prev) =>
        prev.map((row) =>
          row.index === index
            ? {
                ...row,
                step: "done",
                score: event.score as number | null,
                tier: event.tier as string | null,
                reasoning: (event.reasoning as string) || "",
                recommendedAction: (event.recommended_action as string) || "",
                emailSubject: (event.email_subject as string) || "",
                emailBody: (event.email_body as string) || "",
                leadId: (event.lead_id as string) || null,
                agentSteps: (event.agent_steps as number) || null,
                error: null,
              }
            : row
        )
      )
    } else if (type === "lead_error") {
      setBatchRows((prev) =>
        prev.map((row) =>
          row.index === index
            ? { ...row, step: "error", error: (event.error as string) || "Unknown error" }
            : row
        )
      )
    }
  }

  function toggleRow(index: number) {
    setExpandedRows((prev) => {
      const next = new Set(prev)
      if (next.has(index)) {
        next.delete(index)
      } else {
        next.add(index)
      }
      return next
    })
  }

  function toggleHistory(id: string) {
    setExpandedHistory((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  // ── CSV upload ──────────────────────────────────────────────────────────
  function handleCSV(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      const text = (ev.target?.result as string) ?? ""
      const lines = text.split("\n").filter((l) => l.trim())
      const firstLine = lines[0]?.toLowerCase() ?? ""
      const dataLines = firstLine.includes("company") ? lines.slice(1) : lines
      
      const rows: BatchInputRow[] = dataLines.map((line) => {
        const parts = line.split(",").map((p) => p.trim())
        return {
          id: crypto.randomUUID(),
          company: parts[0] ?? "",
          email: parts[1] ?? "",
          leadName: parts[2] ?? "",
        }
      })
      
      setBatchInputRows(rows)
    }
    reader.readAsText(file)
    e.target.value = ""
  }

  // ── Password gate ────────────────────────────────────────────────────────
  if (!authed) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-4">
        <div className="w-full max-w-sm space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-emerald-500 rounded-lg flex items-center justify-center">
              <Lock size={16} className="text-zinc-950" />
            </div>
            <div>
              <p className="text-zinc-100 font-semibold">Dashboard</p>
              <p className="text-zinc-500 text-xs">AutoSystems · Lead Intelligence</p>
            </div>
          </div>

          <div className="space-y-3">
            <Label htmlFor="pw" className="text-zinc-400 text-sm">
              Access password
            </Label>
            <Input
              id="pw"
              type="password"
              placeholder="Enter password"
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAuth()}
              className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 h-10"
            />
            {authError && <p className="text-red-400 text-sm">{authError}</p>}
            <Button onClick={handleAuth} className="w-full bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-semibold">
              Unlock
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // ── Dashboard ────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
            <LayoutDashboard size={14} className="text-zinc-950" />
          </div>
          <div>
            <span className="text-zinc-100 font-semibold text-sm">AutoSystems</span>
            <span className="text-zinc-500 text-xs ml-2">Lead Intelligence Dashboard</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => { setHistoryPage(1); fetchHistory(1) }}
            className="text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 gap-2"
          >
            <RefreshCw size={14} />
            Refresh
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-zinc-400 hover:text-red-400 hover:bg-zinc-800 gap-2"
          >
            <LogOut size={14} />
            Logout
          </Button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-10">

        {/* ── Batch input ── */}
        <section className="space-y-4">
          <div>
            <h2 className="text-zinc-100 font-semibold text-base">Batch Qualification</h2>
            <p className="text-zinc-500 text-sm mt-0.5">
              Enter company details below — one company per row
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-[1fr_240px] gap-6">
            {/* Input rows */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-zinc-400 text-sm">Companies</Label>
                <button
                  type="button"
                  onClick={loadSampleRows}
                  className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-emerald-400 transition-colors"
                >
                  <FlaskConical size={11} />
                  Load samples
                </button>
              </div>

              <div className="space-y-2">
                {/* Header row */}
                <div className="grid grid-cols-[2fr_2fr_1.5fr_36px] gap-2 text-xs text-zinc-500 uppercase tracking-wide px-1">
                  <span>Company</span>
                  <span>Email</span>
                  <span>Lead Name</span>
                  <span></span>
                </div>

                {/* Input rows */}
                {batchInputRows.map((row, idx) => (
                  <div key={row.id} className="grid grid-cols-[2fr_2fr_1.5fr_36px] gap-2 items-center">
                    <Input
                      value={row.company}
                      onChange={(e) => updateInputRow(row.id, "company", e.target.value)}
                      placeholder="Sprout Solutions"
                      className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 h-9 text-sm"
                    />
                    <Input
                      value={row.email}
                      onChange={(e) => updateInputRow(row.id, "email", e.target.value)}
                      placeholder="hr@company.com"
                      type="email"
                      className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 h-9 text-sm"
                    />
                    <Input
                      value={row.leadName}
                      onChange={(e) => updateInputRow(row.id, "leadName", e.target.value)}
                      placeholder="Maria Santos"
                      className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 h-9 text-sm"
                    />
                    <button
                      type="button"
                      onClick={() => removeInputRow(row.id)}
                      disabled={batchInputRows.length <= 1}
                      className="w-9 h-9 flex items-center justify-center rounded-lg border border-zinc-700 text-zinc-500 hover:text-red-400 hover:border-red-500/30 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Remove row"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}

                {/* Add row button */}
                <button
                  type="button"
                  onClick={addInputRow}
                  disabled={batchInputRows.length >= 10}
                  className="w-full flex items-center justify-center gap-2 py-2 rounded-lg border border-dashed border-zinc-700 text-zinc-500 hover:text-emerald-400 hover:border-emerald-500/30 transition-colors text-sm disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <Plus size={14} />
                  Add row {batchInputRows.length >= 10 && "(max 10)"}
                </button>
              </div>
            </div>

            {/* Region + CSV + Run */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-zinc-400 text-sm">Region</Label>
                <Input
                  value={defaultRegion}
                  onChange={(e) => setDefaultRegion(e.target.value)}
                  placeholder="Philippines"
                  className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-zinc-400 text-sm">CSV upload</Label>
                <label className="flex items-center gap-2 cursor-pointer border border-zinc-700 border-dashed rounded-lg px-3 py-2 text-zinc-500 text-sm hover:border-zinc-600 hover:text-zinc-400 transition-colors">
                  <Upload size={13} />
                  Choose CSV
                  <input type="file" accept=".csv" onChange={handleCSV} className="hidden" />
                </label>
              </div>

              <Button
                onClick={runBatch}
                disabled={
                  isRunning || batchInputRows.filter((r) => r.company.trim()).length === 0
                }
                className="w-full bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-semibold gap-2 disabled:opacity-50"
              >
                {isRunning ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    Running
                  </>
                ) : (
                  <>
                    <Play size={14} />
                    Run Batch
                  </>
                )}
              </Button>
            </div>
          </div>
        </section>

        {/* ── Live results ── */}
        {batchRows.length > 0 && (
          <section className="space-y-3">
            <h2 className="text-zinc-100 font-semibold text-base">Live Results</h2>
            <div className="border border-zinc-800 rounded-xl overflow-hidden">
              {batchRows.map((row) => (
                <div key={row.index} className="border-b border-zinc-800 last:border-b-0">
                  {/* Row header */}
                  <button
                    onClick={() => toggleRow(row.index)}
                    className="w-full flex items-center gap-4 px-4 py-3 hover:bg-zinc-900/50 transition-colors text-left"
                  >
                    <span className="w-4 h-4 text-zinc-600 flex-shrink-0">
                      {expandedRows.has(row.index) ? (
                        <ChevronDown size={14} />
                      ) : (
                        <ChevronRight size={14} />
                      )}
                    </span>
                    <span className="text-zinc-100 text-sm font-medium min-w-[160px]">
                      {row.company}
                    </span>
                    <span className="text-zinc-500 text-xs min-w-[80px]">{row.leadName}</span>
                    <div className="flex-1">
                      <StepIndicator step={row.step} />
                    </div>
                    {row.score !== null && (
                      <span className="text-zinc-300 text-sm font-mono">{row.score}/100</span>
                    )}
                    <TierBadge tier={row.tier} />
                  </button>

                  {/* Expanded content */}
                  {expandedRows.has(row.index) && (
                    <div className="px-8 pb-4 space-y-4 bg-zinc-900/30">
                      {row.error && (
                        <div className="flex items-start gap-2 text-red-400 text-sm">
                          <AlertCircle size={14} className="mt-0.5 flex-shrink-0" />
                          {row.error}
                        </div>
                      )}
                      {row.reasoning && (
                        <div>
                          <span className="text-xs text-zinc-500 uppercase tracking-wide">
                            Reasoning
                          </span>
                          <p className="text-zinc-300 text-sm mt-1">{row.reasoning}</p>
                        </div>
                      )}
                      {row.recommendedAction && (
                        <div>
                          <span className="text-xs text-zinc-500 uppercase tracking-wide">
                            Action
                          </span>
                          <p className="text-emerald-400 text-sm mt-1 font-medium capitalize">
                            {row.recommendedAction}
                          </p>
                        </div>
                      )}
                      <div>
                        <span className="text-xs text-zinc-500 uppercase tracking-wide block mb-2">
                          Email Draft
                        </span>
                        <EmailPreview
                          subject={row.emailSubject}
                          body={row.emailBody}
                          leadName={row.leadName}
                          company={row.company}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Run history ── */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Inbox size={15} className="text-zinc-400" />
              <h2 className="text-zinc-100 font-semibold text-base">Run History</h2>
            </div>
            {historyLoading && <Loader2 size={14} className="animate-spin text-zinc-500" />}
          </div>

          {historyError && (
            <div className="flex items-center gap-2 text-red-400 text-sm border border-red-900/50 rounded-lg px-3 py-2 bg-red-950/20">
              <AlertCircle size={14} />
              {historyError}
            </div>
          )}

          {history.length === 0 && !historyLoading && !historyError && (
            <div className="text-center py-10 text-zinc-600 text-sm border border-zinc-800/50 rounded-xl">
              No runs yet. Submit a batch above to get started.
            </div>
          )}

          {history.length > 0 && (
            <div className="space-y-3">
            <div className="border border-zinc-800 rounded-xl overflow-hidden">
              {/* Table header */}
              <div className="grid grid-cols-[1fr_100px_80px_120px_140px] gap-4 px-4 py-2.5 bg-zinc-900 border-b border-zinc-800 text-xs text-zinc-500 uppercase tracking-wide font-medium">
                <span>Company</span>
                <span>Score</span>
                <span>Tier</span>
                <span>Action</span>
                <span>Date</span>
              </div>

              {history.map((lead) => (
                <div key={lead.id} className="border-b border-zinc-800 last:border-b-0">
                  <button
                    onClick={() => toggleHistory(lead.id)}
                    className="w-full grid grid-cols-[1fr_100px_80px_120px_140px] gap-4 items-center px-4 py-3 hover:bg-zinc-900/40 transition-colors text-left"
                  >
                    <div>
                      <p className="text-zinc-100 text-sm font-medium">{lead.company}</p>
                      <p className="text-zinc-500 text-xs">{lead.lead_name}</p>
                    </div>
                    <span className="text-zinc-300 text-sm font-mono">
                      {lead.score !== null ? `${lead.score}/100` : "—"}
                    </span>
                    <TierBadge tier={lead.tier} />
                    <span className="text-zinc-400 text-xs truncate">
                      {lead.recommended_action ?? "—"}
                    </span>
                    <span className="text-zinc-500 text-xs">
                      {lead.created_at ? formatDate(lead.created_at) : "—"}
                    </span>
                  </button>

                  {expandedHistory.has(lead.id) && (
                    <div className="px-8 pb-4 space-y-4 bg-zinc-900/30">
                      {lead.email_subject || lead.email_draft ? (
                        <div>
                          <span className="text-xs text-zinc-500 uppercase tracking-wide block mb-2">
                            Email Draft
                          </span>
                          <EmailPreview
                            subject={lead.email_subject ?? ""}
                            body={lead.email_draft ?? ""}
                            leadName={lead.lead_name}
                            company={lead.company}
                          />
                        </div>
                      ) : (
                        <p className="text-zinc-500 text-sm">No email draft stored for this lead.</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Pagination controls */}
            <div className="flex items-center justify-between px-1">
              <Button
                variant="ghost"
                size="sm"
                disabled={historyPage <= 1 || historyLoading}
                onClick={() => {
                  const prev = historyPage - 1
                  setHistoryPage(prev)
                  fetchHistory(prev)
                }}
                className="text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 gap-1.5 disabled:opacity-30"
              >
                <ChevronLeft size={14} />
                Previous
              </Button>
              <span className="text-zinc-500 text-xs">
                Page {historyPage}
              </span>
              <Button
                variant="ghost"
                size="sm"
                disabled={!hasMore || historyLoading}
                onClick={() => {
                  const next = historyPage + 1
                  setHistoryPage(next)
                  fetchHistory(next)
                }}
                className="text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 gap-1.5 disabled:opacity-30"
              >
                Next
                <ChevronRight size={14} />
              </Button>
            </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
