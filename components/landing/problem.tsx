import { Clock, Users, TrendingDown, AlertTriangle } from "lucide-react"

const pains = [
  {
    icon: Clock,
    title: "Hours wasted on research",
    body: "Your team manually looks up every company, checks LinkedIn, reads news — before even knowing if the lead is worth contacting.",
    color: "text-red-400",
    bg: "bg-red-500/8",
    border: "border-red-500/15",
  },
  {
    icon: Users,
    title: "Reps working cold leads",
    body: "60–70% of leads in most pipelines will never convert. Without qualification, reps chase everyone — burning time and morale.",
    color: "text-orange-400",
    bg: "bg-orange-500/8",
    border: "border-orange-500/15",
  },
  {
    icon: TrendingDown,
    title: "Slow follow-up kills deals",
    body: "Studies show leads go cold in under 5 minutes. Manual qualification means your best prospects are already talking to competitors.",
    color: "text-amber-400",
    bg: "bg-amber-500/8",
    border: "border-amber-500/15",
  },
  {
    icon: AlertTriangle,
    title: "No consistent scoring",
    body: "Every rep qualifies differently. No shared criteria means inconsistent pipeline quality and unpredictable revenue.",
    color: "text-yellow-400",
    bg: "bg-yellow-500/8",
    border: "border-yellow-500/15",
  },
]

export default function Problem() {
  return (
    <section className="bg-zinc-900/30 px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="grid items-start gap-16 lg:grid-cols-2">
          {/* Left — problem statement */}
          <div>
            <p className="mb-3 text-sm font-medium uppercase tracking-widest text-red-400">The problem</p>
            <h2 className="mb-6 text-3xl font-bold leading-tight text-zinc-50 sm:text-4xl">
              Manual lead qualification
              <br />
              <span className="text-zinc-400">is costing you deals.</span>
            </h2>
            <p className="mb-6 text-zinc-400 leading-relaxed">
              The average sales rep spends 21% of their day on manual data entry and lead research —
              time that should go toward actually selling. The result is a leaky pipeline and missed
              revenue.
            </p>
            <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-6">
              <div className="mb-2 font-mono text-4xl font-bold text-red-400">21%</div>
              <p className="text-sm text-zinc-500">of sales rep time lost to manual research and data entry</p>
              <div className="mt-4 mb-2 font-mono text-4xl font-bold text-orange-400">5 min</div>
              <p className="text-sm text-zinc-500">average time before a lead goes cold after first contact</p>
            </div>
          </div>

          {/* Right — pain points */}
          <div className="grid gap-4 sm:grid-cols-2">
            {pains.map((pain) => (
              <div
                key={pain.title}
                className={`rounded-xl border p-5 ${pain.bg} ${pain.border}`}
              >
                <pain.icon className={`mb-3 h-5 w-5 ${pain.color}`} />
                <h3 className="mb-2 text-sm font-semibold text-zinc-200">{pain.title}</h3>
                <p className="text-xs leading-relaxed text-zinc-500">{pain.body}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
