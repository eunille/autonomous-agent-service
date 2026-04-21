import { Flame, CheckCircle2, Snowflake, Ban } from "lucide-react"

const tiers = [
  {
    tier: "HOT",
    range: "80 – 100",
    icon: Flame,
    description: "Immediate outreach. Personal call. High fit, strong growth signals, no red flags.",
    action: "Call today",
    bg: "from-red-500/10 to-orange-500/5",
    border: "border-red-500/30",
    badge: "bg-red-500/15 text-red-400",
    iconColor: "text-red-400",
    bar: "bg-gradient-to-r from-red-500 to-orange-400",
    barWidth: "w-full",
  },
  {
    tier: "WARM",
    range: "60 – 79",
    icon: CheckCircle2,
    description: "Personalized email. Follow up within 3 days. Good fit, some growth signals.",
    action: "Email this week",
    bg: "from-emerald-500/10 to-teal-500/5",
    border: "border-emerald-500/30",
    badge: "bg-emerald-500/15 text-emerald-400",
    iconColor: "text-emerald-400",
    bar: "bg-gradient-to-r from-emerald-500 to-teal-400",
    barWidth: "w-4/5",
  },
  {
    tier: "COLD",
    range: "40 – 59",
    icon: Snowflake,
    description: "Add to nurture sequence. Potential fit but missing key signals right now.",
    action: "Nurture sequence",
    bg: "from-blue-500/10 to-cyan-500/5",
    border: "border-blue-500/30",
    badge: "bg-blue-500/15 text-blue-400",
    iconColor: "text-blue-400",
    bar: "bg-gradient-to-r from-blue-500 to-cyan-400",
    barWidth: "w-3/5",
  },
  {
    tier: "DISQUALIFY",
    range: "0 – 39",
    icon: Ban,
    description: "Not a fit. Logged to CRM with reasoning. No email drafted. Move on.",
    action: "Log and skip",
    bg: "from-zinc-700/20 to-zinc-800/10",
    border: "border-zinc-700/50",
    badge: "bg-zinc-700/30 text-zinc-400",
    iconColor: "text-zinc-500",
    bar: "bg-zinc-700",
    barWidth: "w-2/5",
  },
]

export default function Scoring() {
  return (
    <section className="px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">Lead scoring</p>
          <h2 className="text-3xl font-bold text-zinc-50 sm:text-4xl">AI-powered lead tiers</h2>
          <p className="mx-auto mt-4 max-w-xl text-zinc-400">
            No hardcoded rules. The LLM reasons over company size, growth signals, industry fit, and
            decision-maker seniority to assign a score with full explanation.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {tiers.map((tier) => (
            <div
              key={tier.tier}
              className={`rounded-xl border bg-gradient-to-br p-6 ${tier.bg} ${tier.border}`}
            >
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <tier.icon className={`h-5 w-5 ${tier.iconColor}`} />
                    <span className={`rounded-full px-3 py-1 text-xs font-bold tracking-wider ${tier.badge}`}>
                      {tier.tier}
                    </span>
                  </div>
                  <div className="mt-2 font-mono text-2xl font-bold text-zinc-200">{tier.range}</div>
                </div>
                <div className="rounded-lg border border-zinc-700 px-3 py-1.5 text-xs text-zinc-400">
                  {tier.action}
                </div>
              </div>

              {/* Score bar */}
              <div className="mb-4 h-1.5 rounded-full bg-zinc-800">
                <div className={`h-full rounded-full ${tier.bar} ${tier.barWidth}`} />
              </div>

              <p className="text-sm text-zinc-400">{tier.description}</p>
            </div>
          ))}
        </div>

        {/* Scoring criteria */}
        <div className="mt-10 rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
          <h3 className="mb-4 text-sm font-semibold text-zinc-300">Scoring criteria</h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { label: "Company size fit (10–500 employees)", points: "+20 pts" },
              { label: "Industry relevance to B2B SaaS", points: "+20 pts" },
              { label: "Growth signals (hiring, funding, expansion)", points: "+20 pts" },
              { label: "Recent activity (news, social presence)", points: "+15 pts" },
              { label: "Decision-maker seniority", points: "+15 pts" },
              { label: "No red flags (layoffs, bad press)", points: "+10 pts" },
            ].map((c) => (
              <div key={c.label} className="flex items-center justify-between gap-4 rounded-lg bg-zinc-950/50 px-4 py-3">
                <span className="text-xs text-zinc-400">{c.label}</span>
                <span className="flex-shrink-0 font-mono text-xs font-semibold text-emerald-400">{c.points}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
