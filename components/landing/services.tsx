import { Search, Mail, Database, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

const services = [
  {
    icon: Search,
    label: "Service 01",
    title: "AI Lead Qualification",
    description:
      "Our agent researches every prospect automatically — company size, growth signals, recent news, funding — and assigns a score 0 to 100. HOT leads get flagged instantly.",
    features: ["Company research via web", "0–100 lead scoring", "Tier: HOT / WARM / COLD", "Instant Telegram alert"],
    accent: "emerald",
    mockup: <LeadQualMockup />,
  },
  {
    icon: Mail,
    label: "Service 02",
    title: "Personalized Outreach Drafts",
    description:
      "For every qualified lead, the agent drafts a personalized cold email based on what it found — company expansion, recent hires, funding rounds. No generic templates.",
    features: ["Context-aware subject lines", "Personalized body copy", "Talking points included", "Ready to send in seconds"],
    accent: "blue",
    mockup: <EmailMockup />,
  },
  {
    icon: Database,
    label: "Service 03",
    title: "CRM Auto-Logging",
    description:
      "Every lead — score, reasoning, email draft, research summary — gets logged automatically to your Supabase CRM. Full audit trail, no manual entry ever.",
    features: ["Full lead profile saved", "Score + reasoning logged", "Email draft stored", "Search & filter ready"],
    accent: "violet",
    mockup: <CrmMockup />,
  },
]

export default function Services() {
  return (
    <section id="services" className="px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">What we build</p>
          <h2 className="text-3xl font-bold text-zinc-50 sm:text-4xl">
            Three systems. One automated pipeline.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-zinc-400">
            Each AutoSystems package is a focused automation that eliminates a specific manual
            bottleneck in your sales workflow.
          </p>
        </div>

        <div className="space-y-8">
          {services.map((service, i) => (
            <div
              key={service.title}
              className={`overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50 ${i % 2 === 1 ? "lg:flex-row-reverse" : ""}`}
            >
              <div className="grid lg:grid-cols-2">
                {/* Content */}
                <div className={`p-8 lg:p-10 ${i % 2 === 1 ? "lg:order-2" : ""}`}>
                  <div className="mb-4 flex items-center gap-3">
                    <div className={`rounded-lg p-2
                      ${service.accent === "emerald" ? "bg-emerald-500/15" : ""}
                      ${service.accent === "blue" ? "bg-blue-500/15" : ""}
                      ${service.accent === "violet" ? "bg-violet-500/15" : ""}
                    `}>
                      <service.icon className={`h-5 w-5
                        ${service.accent === "emerald" ? "text-emerald-400" : ""}
                        ${service.accent === "blue" ? "text-blue-400" : ""}
                        ${service.accent === "violet" ? "text-violet-400" : ""}
                      `} />
                    </div>
                    <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">{service.label}</span>
                  </div>

                  <h3 className="mb-4 text-2xl font-bold text-zinc-50">{service.title}</h3>
                  <p className="mb-6 leading-relaxed text-zinc-400">{service.description}</p>

                  <ul className="mb-8 space-y-2">
                    {service.features.map((f) => (
                      <li key={f} className="flex items-center gap-2.5 text-sm text-zinc-300">
                        <div className={`h-1.5 w-1.5 rounded-full flex-shrink-0
                          ${service.accent === "emerald" ? "bg-emerald-500" : ""}
                          ${service.accent === "blue" ? "bg-blue-500" : ""}
                          ${service.accent === "violet" ? "bg-violet-500" : ""}
                        `} />
                        {f}
                      </li>
                    ))}
                  </ul>

                  <Button asChild size="sm" className="bg-emerald-500 text-zinc-950 hover:bg-emerald-400">
                    <a href="#contact">
                      Get started <ArrowRight className="h-4 w-4" />
                    </a>
                  </Button>
                </div>

                {/* Mockup */}
                <div className={`flex items-center justify-center border-zinc-800 bg-zinc-950/40 p-6 lg:p-8 ${i % 2 === 1 ? "lg:order-1 lg:border-r" : "lg:border-l"}`}>
                  {service.mockup}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ── CSS Mockups ── */

function LeadQualMockup() {
  const leads = [
    { name: "Maria Santos", company: "TechCorp PH", score: 78, tier: "WARM", color: "text-emerald-400", dot: "bg-emerald-500" },
    { name: "James Reyes", company: "ScaleUp Inc", score: 91, tier: "HOT", color: "text-red-400", dot: "bg-red-500" },
    { name: "Ana Cruz", company: "StartupXYZ", score: 34, tier: "COLD", color: "text-blue-400", dot: "bg-blue-500" },
  ]
  return (
    <div className="w-full max-w-sm rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
      <div className="border-b border-zinc-800 px-4 py-3">
        <p className="text-xs font-medium text-zinc-400">Lead Queue — Today</p>
      </div>
      <div className="divide-y divide-zinc-800/60">
        {leads.map((l) => (
          <div key={l.name} className="flex items-center justify-between px-4 py-3">
            <div>
              <p className="text-sm font-medium text-zinc-200">{l.name}</p>
              <p className="text-xs text-zinc-500">{l.company}</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className={`text-sm font-bold font-mono ${l.color}`}>{l.score}</p>
                <p className={`text-[10px] ${l.color}`}>{l.tier}</p>
              </div>
              <div className={`h-2 w-2 rounded-full ${l.dot}`} />
            </div>
          </div>
        ))}
      </div>
      <div className="px-4 py-3 bg-emerald-500/5 border-t border-emerald-500/10">
        <p className="text-xs text-emerald-400">Agent processed 3 leads in 1m 24s</p>
      </div>
    </div>
  )
}

function EmailMockup() {
  return (
    <div className="w-full max-w-sm rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
      <div className="border-b border-zinc-800 px-4 py-3 flex items-center justify-between">
        <p className="text-xs font-medium text-zinc-400">Draft Email</p>
        <span className="rounded-full bg-blue-500/15 px-2 py-0.5 text-[10px] text-blue-400">Auto-generated</span>
      </div>
      <div className="p-4 space-y-3">
        <div className="rounded-lg bg-zinc-800/60 px-3 py-2">
          <p className="text-[10px] text-zinc-500 mb-0.5">To</p>
          <p className="text-xs text-zinc-300">maria@techcorph.com</p>
        </div>
        <div className="rounded-lg bg-zinc-800/60 px-3 py-2">
          <p className="text-[10px] text-zinc-500 mb-0.5">Subject</p>
          <p className="text-xs text-zinc-300">Congrats on the Singapore expansion, Maria</p>
        </div>
        <div className="rounded-lg bg-zinc-800/60 px-3 py-2">
          <p className="text-[10px] text-zinc-500 mb-1">Body</p>
          <p className="text-xs leading-relaxed text-zinc-400">
            Hi Maria, I came across TechCorp PH while researching growing HR tech companies in Southeast Asia — the Singapore expansion caught my attention...
          </p>
        </div>
        <div className="flex gap-2">
          <div className="rounded-md bg-blue-500/15 px-2 py-1 text-[10px] text-blue-400">Singapore expansion</div>
          <div className="rounded-md bg-blue-500/15 px-2 py-1 text-[10px] text-blue-400">3 open roles</div>
        </div>
      </div>
    </div>
  )
}

function CrmMockup() {
  return (
    <div className="w-full max-w-sm rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
      <div className="border-b border-zinc-800 px-4 py-3 flex items-center justify-between">
        <p className="text-xs font-medium text-zinc-400">Supabase — leads</p>
        <span className="rounded-full bg-violet-500/15 px-2 py-0.5 text-[10px] text-violet-400">Auto-logged</span>
      </div>
      <div className="p-4">
        <div className="space-y-2">
          {[
            { col: "lead_name", val: "Maria Santos" },
            { col: "company", val: "TechCorp PH" },
            { col: "score", val: "78" },
            { col: "tier", val: "WARM" },
            { col: "email_subject", val: "Congrats on the Singapore..." },
            { col: "logged_at", val: "2025-04-21 11:31:22" },
          ].map((row) => (
            <div key={row.col} className="flex items-center gap-3 rounded-md bg-zinc-800/50 px-3 py-1.5">
              <span className="w-28 flex-shrink-0 text-[10px] font-mono text-zinc-500">{row.col}</span>
              <span className="truncate text-[10px] text-zinc-300">{row.val}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="px-4 py-3 bg-violet-500/5 border-t border-violet-500/10">
        <p className="text-xs text-violet-400">1 row inserted — ID: 2db06169</p>
      </div>
    </div>
  )
}
