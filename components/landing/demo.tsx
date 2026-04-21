"use client"

import { useState } from "react"
import { ArrowRight, Loader2, CheckCircle2, Database, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

const MOCK_RESULT = {
  lead_name: "Maria Santos",
  company: "TechCorp PH",
  score: 78,
  tier: "WARM",
  reasoning:
    "TechCorp PH is a 50-person SaaS startup in HR Tech — ideal size fit. They recently raised a $2M seed round and are actively hiring 3 roles, indicating strong growth momentum. The Singapore expansion is a strong buying intent signal.",
  key_talking_points: [
    "Singapore expansion timing — scaling challenges incoming",
    "3 open roles = growing ops without proportional headcount",
    "HR software adjacent — natural upsell opportunity",
  ],
  email_subject: "Congrats on the Singapore expansion, Maria",
  email_body: `Hi Maria,

I came across TechCorp PH while researching growing HR tech companies in Southeast Asia — the Singapore expansion caught my attention.

Companies in your growth phase (and with 3 open roles to fill) often run into the same challenge: scaling people operations without scaling headcount proportionally.

[Your value proposition here]

Would a 20-minute call this week make sense?

Best,
[Your name]`,
  recommended_action: "Personalized email → follow up in 3 days",
  agent_steps: 6,
  telegram_sent: true,
}

export default function Demo() {
  const [name, setName] = useState("Maria Santos")
  const [company, setCompany] = useState("TechCorp PH")
  const [email, setEmail] = useState("maria@techcorph.com")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<typeof MOCK_RESULT | null>(null)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    // Simulate agent run
    setTimeout(() => {
      setResult({ ...MOCK_RESULT, lead_name: name, company })
      setLoading(false)
    }, 2800)
  }

  return (
    <section id="demo" className="bg-zinc-900/30 px-6 py-24">
      <div className="mx-auto max-w-5xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">Live demo</p>
          <h2 className="text-3xl font-bold text-zinc-50 sm:text-4xl">Try it now</h2>
          <p className="mx-auto mt-4 max-w-xl text-zinc-400">
            Enter a lead and watch the agent run — research, score, email draft, and Telegram alert.
          </p>
          <p className="mt-2 text-xs text-zinc-600">
            (Demo uses cached results. Connect your API keys to run the live agent.)
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Form */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900/80 p-6">
            <h3 className="mb-5 text-sm font-semibold text-zinc-300">Lead input</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="lead-name" className="mb-1.5 text-xs text-zinc-500">Lead name</Label>
                <Input
                  id="lead-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="border-zinc-700 bg-zinc-800/50 text-zinc-100 focus:border-emerald-500/50"
                  placeholder="Maria Santos"
                  required
                />
              </div>
              <div>
                <Label htmlFor="company" className="mb-1.5 text-xs text-zinc-500">Company</Label>
                <Input
                  id="company"
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="border-zinc-700 bg-zinc-800/50 text-zinc-100 focus:border-emerald-500/50"
                  placeholder="TechCorp PH"
                  required
                />
              </div>
              <div>
                <Label htmlFor="email" className="mb-1.5 text-xs text-zinc-500">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="border-zinc-700 bg-zinc-800/50 text-zinc-100 focus:border-emerald-500/50"
                  placeholder="maria@techcorph.com"
                  required
                />
              </div>
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-emerald-500 text-zinc-950 hover:bg-emerald-400 disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Agent running...
                  </>
                ) : (
                  <>
                    Qualify this lead
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            </form>

            {/* Agent steps */}
            {(loading || result) && (
              <div className="mt-6 space-y-2">
                <p className="text-xs text-zinc-500">Agent steps</p>
                {[
                  "search_company()",
                  "search_recent_activity()",
                  "score_lead()",
                  "draft_outreach_email()",
                  "log_to_supabase()",
                  "send_telegram_alert()",
                ].map((step, i) => (
                  <div key={step} className="flex items-center gap-3">
                    <div
                      className={`h-1.5 w-1.5 rounded-full transition-all duration-500 ${
                        result
                          ? "bg-emerald-400"
                          : loading && i === 0
                            ? "bg-emerald-400"
                            : "bg-zinc-700"
                      }`}
                    />
                    <span className="font-mono text-xs text-zinc-500">{step}</span>
                    {result && <CheckCircle2 className="h-3 w-3 text-emerald-400" />}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Result */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900/80 p-6">
            <h3 className="mb-5 text-sm font-semibold text-zinc-300">Agent output</h3>

            {!result && !loading && (
              <div className="flex h-64 items-center justify-center">
                <p className="text-sm text-zinc-600">Submit a lead to see results</p>
              </div>
            )}

            {loading && (
              <div className="flex h-64 flex-col items-center justify-center gap-3">
                <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
                <p className="text-sm text-zinc-500">Agent is researching {company}...</p>
              </div>
            )}

            {result && (
              <div className="space-y-5">
                {/* Score */}
                <div className="flex items-center justify-between rounded-lg bg-emerald-500/10 px-4 py-3">
                  <div>
                    <div className="text-2xl font-bold text-emerald-400">{result.score}/100</div>
                    <div className="text-xs text-zinc-400">Lead score</div>
                  </div>
                  <div className="rounded-full bg-emerald-500/20 px-4 py-1.5 text-sm font-bold text-emerald-400">
                    {result.tier}
                  </div>
                </div>

                {/* Reasoning */}
                <div>
                  <p className="mb-1 text-xs text-zinc-500">Reasoning</p>
                  <p className="text-sm leading-relaxed text-zinc-400">{result.reasoning}</p>
                </div>

                {/* Talking points */}
                <div>
                  <p className="mb-2 text-xs text-zinc-500">Key talking points</p>
                  <ul className="space-y-1.5">
                    {result.key_talking_points.map((pt) => (
                      <li key={pt} className="flex items-start gap-2 text-sm text-zinc-300">
                        <span className="mt-1 text-emerald-400">•</span>
                        {pt}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Email subject */}
                <div className="rounded-lg border border-zinc-700 bg-zinc-950/50 px-4 py-3">
                  <p className="mb-1 text-xs text-zinc-500">Email subject drafted</p>
                  <p className="text-sm font-medium text-zinc-200">{result.email_subject}</p>
                </div>

                {/* Status */}
                <div className="flex gap-3">
                  <span className="flex items-center gap-1.5 rounded-md bg-blue-500/10 px-2 py-1 text-xs text-blue-400">
                    <Database className="h-3 w-3" /> Logged to Supabase
                  </span>
                  <span className="flex items-center gap-1.5 rounded-md bg-violet-500/10 px-2 py-1 text-xs text-violet-400">
                    <Send className="h-3 w-3" /> Telegram alert sent
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
