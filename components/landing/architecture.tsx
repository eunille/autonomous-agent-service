import { ImageIcon } from "lucide-react"

const nodes = [
  { id: "lead", label: "Lead arrives", sub: "name · company · email", col: 1, row: 1, color: "zinc" },
  { id: "agent", label: "Agent Core", sub: "Groq LLM + tool calling", col: 2, row: 1, color: "emerald", highlight: true },
  { id: "serper", label: "Serper", sub: "Web search API", col: 3, row: 0, color: "emerald" },
  { id: "groq", label: "Groq LLM", sub: "Scoring + email", col: 3, row: 2, color: "amber" },
  { id: "supabase", label: "Supabase", sub: "CRM logging", col: 4, row: 0, color: "blue" },
  { id: "telegram", label: "Telegram", sub: "Instant alert", col: 4, row: 2, color: "violet" },
]

const colorMap: Record<string, { border: string; bg: string; text: string; badge: string }> = {
  zinc: { border: "border-zinc-600", bg: "bg-zinc-800", text: "text-zinc-200", badge: "bg-zinc-700 text-zinc-400" },
  emerald: {
    border: "border-emerald-500/50",
    bg: "bg-emerald-500/10",
    text: "text-emerald-300",
    badge: "bg-emerald-500/20 text-emerald-400",
  },
  amber: {
    border: "border-amber-500/50",
    bg: "bg-amber-500/10",
    text: "text-amber-300",
    badge: "bg-amber-500/20 text-amber-400",
  },
  blue: {
    border: "border-blue-500/50",
    bg: "bg-blue-500/10",
    text: "text-blue-300",
    badge: "bg-blue-500/20 text-blue-400",
  },
  violet: {
    border: "border-violet-500/50",
    bg: "bg-violet-500/10",
    text: "text-violet-300",
    badge: "bg-violet-500/20 text-violet-400",
  },
}

export default function Architecture() {
  return (
    <section className="px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">Architecture</p>
          <h2 className="text-3xl font-bold text-zinc-50 sm:text-4xl">How the agent is wired</h2>
          <p className="mx-auto mt-4 max-w-xl text-zinc-400">
            The Groq LLM orchestrates every tool call. It observes results and decides what to do next —
            no hardcoded pipeline.
          </p>
        </div>

        {/* Illustration placeholder */}
        <div className="mb-8 flex h-56 items-center justify-center rounded-xl border border-dashed border-zinc-700 bg-zinc-900/30">
          <div className="flex flex-col items-center gap-2 text-center">
            <ImageIcon className="h-8 w-8 text-zinc-700" />
            <p className="text-xs text-zinc-600">Architecture diagram / screenshot</p>
            <p className="text-[10px] text-zinc-700">Drop your own image here — full agent flow, system diagram, etc.</p>
          </div>
        </div>

        {/* Visual flow */}
        <div className="overflow-x-auto rounded-xl border border-zinc-800 bg-zinc-900/50 p-8">
          <div className="flex min-w-[640px] flex-col gap-4">
            {/* Row 1: input → agent → serper → supabase */}
            <div className="flex items-center gap-4">
              <ArchNode label="Lead Input" sub="name · company · email" color="zinc" />
              <Arrow />
              <ArchNode label="Agent Core" sub="Groq LLM · tool calling" color="emerald" highlight />
              <Arrow />
              <ArchNode label="Serper API" sub="Web research" color="emerald" />
              <Arrow />
              <ArchNode label="Supabase" sub="CRM logging" color="blue" />
            </div>

            {/* Row 2: LLM reasoning branch */}
            <div className="flex items-center gap-4">
              <div className="w-40 flex-shrink-0" />
              <div className="w-4" />
              <div className="flex flex-col items-center">
                <div className="h-6 w-px bg-emerald-500/30" />
                <ArchNode label="Groq LLM" sub="Scoring · Email drafting" color="amber" />
                <div className="h-6 w-px bg-violet-500/30" />
              </div>
              <Arrow />
              <ArchNode label="Telegram" sub="Instant alert" color="violet" />
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          {[
            { label: "Research", color: "emerald" },
            { label: "LLM reasoning", color: "amber" },
            { label: "Storage", color: "blue" },
            { label: "Notification", color: "violet" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              <div
                className={`h-3 w-3 rounded-full
                  ${item.color === "emerald" ? "bg-emerald-500" : ""}
                  ${item.color === "amber" ? "bg-amber-500" : ""}
                  ${item.color === "blue" ? "bg-blue-500" : ""}
                  ${item.color === "violet" ? "bg-violet-500" : ""}
                `}
              />
              <span className="text-xs text-zinc-500">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function ArchNode({
  label,
  sub,
  color,
  highlight,
}: {
  label: string
  sub: string
  color: string
  highlight?: boolean
}) {
  const c = colorMap[color] ?? colorMap.zinc
  return (
    <div
      className={`flex w-40 flex-shrink-0 flex-col items-center rounded-xl border p-4 text-center ${c.border} ${c.bg} ${highlight ? "ring-1 ring-emerald-500/30" : ""}`}
    >
      <div className={`text-sm font-semibold ${c.text}`}>{label}</div>
      <div className={`mt-1 rounded-md px-2 py-0.5 text-[10px] ${c.badge}`}>{sub}</div>
    </div>
  )
}

function Arrow() {
  return (
    <div className="flex flex-shrink-0 items-center gap-0.5 text-zinc-600">
      <div className="h-px w-6 bg-zinc-700" />
      <div className="border-y-4 border-l-4 border-r-0 border-y-transparent border-l-zinc-600" />
    </div>
  )
}
