"use client"

import { usePathname } from "next/navigation"
import Script from "next/script"

export function TypebotWidget() {
  const pathname = usePathname()

  // Don't show the Typebot bubble on the dashboard
  if (pathname.startsWith("/dashboard")) return null

  return (
    <Script
      type="module"
      strategy="lazyOnload"
      dangerouslySetInnerHTML={{
        __html: `
          import Typebot from 'https://cdn.jsdelivr.net/npm/@typebot.io/js@0.3/dist/web.js'
          Typebot.initBubble({
            typebot: 'lead-scoring-a0cl32c',
            theme: {
              button: { backgroundColor: '#10b981', color: '#fff' },
              chatWindow: { backgroundColor: '#18181b' },
            },
          })
        `,
      }}
    />
  )
}
