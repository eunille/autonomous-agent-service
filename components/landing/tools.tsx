import { Globe, Activity, BarChart3, Mail, Database, Bell } from "lucide-react"

const tools = [
  {
    icon: Globe,
    name: "search_company()",
    description: "Searches the web for company overview: size, industry, website, founding year, and description.",
    api: "Serper API",
    color: "emerald",
  },
  {
    icon: Activity,
    name: "search_recent_activity()",
    description: "Scans for hiring signals, funding rounds, product launches, and press coverage in the past 12 months.",
    api: "Serper API",
    color: "emerald",
  },
  {
    icon: BarChart3,
    name: "score_lead()",
    description: "LLM analyzes all research and scores the lead 0–100 with tier, reasoning, and risk flags.",
    api: "Groq LLaMA-3",
    color: "amber",
  },
  {
    icon: Mail,
    name: "draft_outreach_email()",
    description: "Generates a personalized email referencing specific research findings — not a generic template.",
    api: "Groq LLaMA-3",
    color: "amber",
  },
  {
    icon: Database,
    name: "log_to_supabase()",
    description: "Saves the full lead profile — research, score, email draft, and agent step count — to the CRM.",
    api: "Supabase",
    color: "blue",
  },
  {
    icon: Bell,
    name: "send_telegram_alert()",
    description: "Sends an instant formatted notification to the sales analyst with score, findings, and action.",
    api: "Telegram Bot API",
    color: "violet",
  },
]

export default function Tools() {
  return (
    <section id="tools" className="bg-zinc-900/30 px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">Agent tools</p>
          <h2 className="text-3xl font-bold text-zinc-50 sm:text-4xl">6 tools. One autonomous loop.</h2>
          <p className="mx-auto mt-4 max-w-xl text-zinc-400">
            The LLM decides which tools to call and in what order. The agent adapts — it doesn&apos;t
            follow a hardcoded script.
          </p>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {tools.map((tool) => {
            const Icon = tool.icon
            return (
              <div
                key={tool.name}
                className="group rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 transition hover:border-zinc-600"
              >
                <div
                  className={`mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg
                    ${tool.color === "emerald" ? "bg-emerald-500/10 text-emerald-400" : ""}
                    ${tool.color === "amber" ? "bg-amber-500/10 text-amber-400" : ""}
                    ${tool.color === "blue" ? "bg-blue-500/10 text-blue-400" : ""}
                    ${tool.color === "violet" ? "bg-violet-500/10 text-violet-400" : ""}
                  `}
                >
                  <Icon className="h-5 w-5" />
                </div>
                <div className="mb-1 font-mono text-sm font-semibold text-zinc-100">{tool.name}</div>
                <p className="mb-4 text-sm leading-relaxed text-zinc-400">{tool.description}</p>
                <div className="inline-flex items-center rounded-md border border-zinc-700 px-2 py-1 text-xs text-zinc-500">
                  {tool.api}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
