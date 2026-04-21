import { ArrowRight, Bot, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Hero() {
  return (
    <section className="relative overflow-hidden px-6 pt-32 pb-20">
      {/* Ambient glow */}
      <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-emerald-500/[0.06] blur-3xl" />

      <div className="relative z-10 mx-auto max-w-7xl">
        <div className="grid items-center gap-16 lg:grid-cols-2">
          {/* Left — headline + CTA */}
          <div>
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/8 px-4 py-1.5">
              <Bot className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-xs font-medium text-emerald-400">AI-Powered Sales Automation</span>
            </div>

            <h1 className="mb-5 text-4xl font-bold leading-[1.1] tracking-tight text-zinc-50 sm:text-5xl lg:text-6xl">
              Stop chasing cold leads.
              <br />
              <span className="text-emerald-400">Let AI qualify them for you.</span>
            </h1>

            <p className="mb-8 max-w-lg text-lg leading-relaxed text-zinc-400">
              AutoSystems builds autonomous agents that research prospects, score them 0–100, draft
              outreach emails, and ping your team — in under 30 seconds. No manual work.
            </p>

            <div className="flex flex-wrap items-center gap-4">
              <Button asChild size="lg" className="bg-emerald-500 text-zinc-950 hover:bg-emerald-400 font-semibold">
                <a href="#contact">
                  Get a free audit
                  <ArrowRight className="h-4 w-4" />
                </a>
              </Button>
              <Button asChild variant="ghost" size="lg" className="text-zinc-400 hover:text-zinc-100">
                <a href="#how-it-works">See how it works</a>
              </Button>
            </div>

            <div className="mt-8 flex flex-wrap gap-5">
              {[
                "No CRM setup required",
                "Works in 30 seconds per lead",
                "Free to start",
              ].map((item) => (
                <div key={item} className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-emerald-500" />
                  <span className="text-sm text-zinc-400">{item}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right — terminal mockup showing live agent */}
          <div className="lg:pl-8">
            <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900 shadow-2xl shadow-black/40">
              {/* Window chrome */}
              <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-3">
                <div className="flex gap-2">
                  <div className="h-3 w-3 rounded-full bg-zinc-700" />
                  <div className="h-3 w-3 rounded-full bg-zinc-700" />
                  <div className="h-3 w-3 rounded-full bg-zinc-700" />
                </div>
                <div className="rounded-md bg-zinc-800 px-3 py-0.5 font-mono text-[11px] text-zinc-500">
                  autosystems — agent
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="h-2 w-2 rounded-full bg-emerald-500" />
                  <span className="text-[11px] text-zinc-500">live</span>
                </div>
              </div>

              {/* Agent output */}
              <div className="space-y-1 p-5 font-mono text-sm">
                <p className="text-zinc-600">$ qualify --lead &quot;Maria Santos&quot; --company &quot;TechCorp PH&quot;</p>
                <div className="pt-2" />
                <div className="flex items-center gap-2 text-zinc-400">
                  <span className="text-zinc-600">[1]</span> Searching company profile...
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                </div>
                <div className="flex items-center gap-2 text-zinc-400">
                  <span className="text-zinc-600">[2]</span> Analyzing recent activity...
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                </div>
                <div className="flex items-center gap-2 text-zinc-400">
                  <span className="text-zinc-600">[3]</span> Scoring lead quality...
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                </div>
                <div className="flex items-center gap-2 text-zinc-400">
                  <span className="text-zinc-600">[4]</span> Drafting outreach email...
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                </div>
                <div className="flex items-center gap-2 text-zinc-400">
                  <span className="text-zinc-600">[5]</span> Logging to CRM...
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                </div>
                <div className="flex items-center gap-2 text-zinc-400">
                  <span className="text-zinc-600">[6]</span> Sending alert...
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                </div>
                <div className="pt-2" />
                <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-400">Lead Score</span>
                    <span className="font-bold text-emerald-400">78 / 100</span>
                  </div>
                  <div className="mt-1.5 h-1.5 w-full rounded-full bg-zinc-800">
                    <div className="h-full w-4/5 rounded-full bg-emerald-500" />
                  </div>
                  <p className="mt-2 text-xs text-zinc-500">WARM — Personalized email drafted. Follow up in 3 days.</p>
                </div>
              </div>
            </div>

            {/* Social proof under terminal */}
            <p className="mt-4 text-center text-xs text-zinc-600">
              Runs on Groq · Serper · Supabase · Telegram — all free tiers
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
