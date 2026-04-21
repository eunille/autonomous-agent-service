"use client"

import { CheckCircle2, MessageCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Contact() {
  return (
    <section id="contact" className="bg-zinc-900/30 px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="grid items-center gap-16 lg:grid-cols-2">
          {/* Left — pitch */}
          <div>
            <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">Get started</p>
            <h2 className="mb-5 text-3xl font-bold leading-tight text-zinc-50 sm:text-4xl">
              Tell us about your
              <br />
              <span className="text-emerald-400">sales challenge.</span>
            </h2>
            <p className="mb-8 leading-relaxed text-zinc-400">
              Fill out the short form. Our AI agent will research your business and prepare a
              personalized automation proposal — all before we even have our first call.
            </p>

            <div className="space-y-4 mb-8">
              {[
                "Free audit of your current lead qualification process",
                "Custom automation plan built for your stack",
                "Working demo delivered within 48 hours",
                "No lock-in — pay per result or monthly",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-500" />
                  <span className="text-sm text-zinc-300">{item}</span>
                </div>
              ))}
            </div>

            <Button
              size="lg"
              className="bg-emerald-500 text-zinc-950 font-semibold hover:bg-emerald-400"
              onClick={() => {
                // Trigger Typebot bubble open
                const btn = document.querySelector<HTMLButtonElement>("typebot-bubble")
                if (btn) btn.click()
                // Fallback: open typebot directly
                else window.open("https://typebot.co/lead-scoring-a0cl32c", "_blank")
              }}
            >
              <MessageCircle className="mr-2 h-4 w-4" />
              Start the conversation
            </Button>
          </div>

          {/* Right — what happens */}
          <div className="space-y-4">
            <p className="text-sm font-medium text-zinc-500 uppercase tracking-widest mb-6">
              What happens after you chat
            </p>
            {[
              {
                num: "01",
                title: "Agent qualifies your business",
                body: "Within 30 seconds of submitting, our AI researches your company and generates a fit score.",
              },
              {
                num: "02",
                title: "We review your score",
                body: "We get a Telegram alert with your score, key talking points, and a drafted proposal.",
              },
              {
                num: "03",
                title: "You get a personalized response",
                body: "Within 24 hours we'll reach out with a custom automation plan tailored to your stack.",
              },
            ].map((step) => (
              <div
                key={step.num}
                className="flex gap-5 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5"
              >
                <span className="font-mono text-sm font-bold text-emerald-600 flex-shrink-0 mt-0.5">
                  {step.num}
                </span>
                <div>
                  <p className="mb-1 text-sm font-semibold text-zinc-200">{step.title}</p>
                  <p className="text-xs leading-relaxed text-zinc-500">{step.body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}


