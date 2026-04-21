"use client"

import Link from "next/link"
import { Zap } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Nav() {
  return (
    <nav className="fixed top-0 z-50 w-full border-b border-zinc-800/60 bg-zinc-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-500">
            <Zap className="h-4 w-4 text-zinc-950" />
          </div>
          <span className="font-semibold tracking-tight text-zinc-100">AutoSystems</span>
        </div>
        <div className="flex items-center gap-6">
          <a href="#services" className="hidden text-sm text-zinc-400 transition hover:text-zinc-100 sm:block">
            Services
          </a>
          <a href="#how-it-works" className="hidden text-sm text-zinc-400 transition hover:text-zinc-100 sm:block">
            How it works
          </a>
          <a href="#results" className="hidden text-sm text-zinc-400 transition hover:text-zinc-100 sm:block">
            Results
          </a>
          <Button asChild size="sm" className="bg-emerald-500 text-zinc-950 hover:bg-emerald-400">
            <a href="#contact">Book a call</a>
          </Button>
        </div>
      </div>
    </nav>
  )
}
