import Link from "next/link"
import { GitFork, ArrowRight, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Cta() {
  return (
    <section className="px-6 py-24">
      <div className="mx-auto max-w-3xl text-center">
        <div className="rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 to-zinc-900/80 p-12">
          <h2 className="mb-4 text-3xl font-bold text-zinc-50 sm:text-4xl">
            Ready to qualify leads autonomously?
          </h2>
          <p className="mx-auto mb-8 max-w-lg text-zinc-400">
            Clone the repo, add your free API keys, and run your first lead in under 5 minutes.
            No paid services required.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button asChild size="lg" className="bg-emerald-500 text-zinc-950 hover:bg-emerald-400">
              <Link href="https://github.com" target="_blank">
                <GitFork className="h-4 w-4" />
                View on GitHub
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="border-zinc-700 text-zinc-300 hover:border-zinc-500 hover:text-zinc-100">
              <a href="#demo">
                Try the demo
                <ArrowRight className="h-4 w-4" />
              </a>
            </Button>
          </div>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-zinc-600">
            {["Groq free tier", "Serper 2,500 req/mo free", "Supabase 500MB free", "Telegram free forever"].map((item) => (
              <span key={item} className="flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-700" />
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
