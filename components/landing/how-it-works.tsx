import { UserPlus, Bot, BellRing } from "lucide-react"

const steps = [
  {
    num: "01",
    icon: UserPlus,
    title: "Lead submits",
    body: "A prospect fills out your Typebot chat — name, company, and email. Takes 60 seconds. No complex forms.",
    aside: "Typebot chat widget on your site",
    color: "text-emerald-400",
    iconBg: "bg-emerald-500/15",
  },
  {
    num: "02",
    icon: Bot,
    title: "Agent qualifies",
    body: "Our AI agent automatically researches the company, scores the lead 0–100, and drafts a personalized outreach email. All in under 30 seconds.",
    aside: "Groq · Serper · Supabase",
    color: "text-blue-400",
    iconBg: "bg-blue-500/15",
  },
  {
    num: "03",
    icon: BellRing,
    title: "You close",
    body: "You get a Telegram alert with the score, key talking points, and a ready-to-send email. Just review and hit send.",
    aside: "Telegram alert in seconds",
    color: "text-violet-400",
    iconBg: "bg-violet-500/15",
  },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-zinc-900/30 px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">How it works</p>
          <h2 className="text-3xl font-bold text-zinc-50 sm:text-4xl">
            Three steps. Zero manual work.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-zinc-400">
            Your prospect submits. The agent runs. You get a qualified lead with a drafted email — all
            before you finish your coffee.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {steps.map((step) => (
            <div key={step.num} className="relative rounded-2xl border border-zinc-800 bg-zinc-900/60 p-8">
              <div className="mb-6 flex items-center justify-between">
                <div className={`rounded-xl p-3 ${step.iconBg}`}>
                  <step.icon className={`h-6 w-6 ${step.color}`} />
                </div>
                <span className={`font-mono text-4xl font-bold opacity-20 ${step.color}`}>{step.num}</span>
              </div>

              <h3 className="mb-3 text-xl font-semibold text-zinc-50">{step.title}</h3>
              <p className="mb-5 text-sm leading-relaxed text-zinc-400">{step.body}</p>

              <div className={`rounded-lg px-3 py-2 text-xs ${step.iconBg}`}>
                <span className={step.color}>{step.aside}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 hidden items-center justify-center lg:flex">
          <div className="h-px flex-1 bg-zinc-800" />
          <div className="mx-4 rounded-full border border-zinc-700 px-4 py-1.5 text-xs text-zinc-500">
            Total time: under 2 minutes
          </div>
          <div className="h-px flex-1 bg-zinc-800" />
        </div>
      </div>
    </section>
  )
}
