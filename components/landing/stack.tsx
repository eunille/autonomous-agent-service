const tools = [
  {
    name: "Groq",
    description: "LLM inference — reasoning, scoring, and email drafting. Free tier.",
    detail: "llama-3.3-70b-versatile",
    url: "console.groq.com",
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
  },
  {
    name: "Serper",
    description: "Google Search API wrapper. 2,500 free searches/month — 1,250 leads.",
    detail: "serper.dev",
    url: "serper.dev",
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
  },
  {
    name: "Supabase",
    description: "PostgreSQL database for lead profiles, scores, and email drafts.",
    detail: "Free tier — 500MB",
    url: "supabase.com",
    color: "text-green-400",
    bg: "bg-green-500/10",
    border: "border-green-500/20",
  },
  {
    name: "Telegram Bot API",
    description: "Instant lead alerts to your phone. Free, no rate limits.",
    detail: "@BotFather → /newbot",
    url: "core.telegram.org",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  },
]

export default function Stack() {
  return (
    <section className="bg-zinc-900/30 px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">Tech stack</p>
          <h2 className="text-3xl font-bold text-zinc-50 sm:text-4xl">Fully free to run</h2>
          <p className="mx-auto mt-4 max-w-xl text-zinc-400">
            No OpenAI. No paid APIs required. This agent runs on the free tier of every service — no
            credit card needed to build and demo.
          </p>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          {tools.map((tool) => (
            <div
              key={tool.name}
              className={`rounded-xl border p-6 ${tool.bg} ${tool.border}`}
            >
              <div className="mb-3 flex items-start justify-between">
                <h3 className={`text-lg font-bold ${tool.color}`}>{tool.name}</h3>
                <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] font-medium text-zinc-400">
                  FREE
                </span>
              </div>
              <p className="mb-3 text-sm text-zinc-400">{tool.description}</p>
              <div className="rounded-md bg-zinc-950/50 px-3 py-1.5 font-mono text-xs text-zinc-500">
                {tool.detail}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
