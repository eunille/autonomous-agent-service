import { Clock, Users, TrendingUp, Zap } from "lucide-react"

const stats = [
  { icon: Clock, value: "< 30s", label: "Per lead qualified", sub: "Research · Score · Email" },
  { icon: Users, value: "0", label: "Human hours required", sub: "Fully autonomous" },
  { icon: TrendingUp, value: "100pt", label: "Scoring scale", sub: "HOT · WARM · COLD · DISQUALIFY" },
  { icon: Zap, value: "6", label: "AI tools in the pipeline", sub: "All free tier APIs" },
]

export default function Stats() {
  return (
    <section id="results" className="px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6"
            >
              <stat.icon className="mb-4 h-5 w-5 text-emerald-400" />
              <div className="mb-1 font-mono text-3xl font-bold text-zinc-50">{stat.value}</div>
              <div className="mb-1 text-sm font-medium text-zinc-300">{stat.label}</div>
              <div className="text-xs text-zinc-500">{stat.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
