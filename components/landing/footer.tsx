import { Zap } from "lucide-react"

export default function Footer() {
  return (
    <footer className="border-t border-zinc-800 px-6 py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-center sm:flex-row sm:text-left">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-emerald-500">
            <Zap className="h-3.5 w-3.5 text-zinc-950" />
          </div>
          <span className="text-sm font-semibold text-zinc-400">AutoSystems</span>
        </div>
        <p className="text-xs text-zinc-600">AI sales automation — powered by Groq, Serper, Supabase, Telegram</p>
        <p className="text-xs text-zinc-700">Built as a portfolio project · Project 4</p>
      </div>
    </footer>
  )
}
