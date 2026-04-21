import { Geist, Geist_Mono, Inter } from "next/font/google"
import Script from "next/script"

import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { cn } from "@/lib/utils";

const inter = Inter({subsets:['latin'],variable:'--font-sans'})

const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn("antialiased", fontMono.variable, "font-sans", inter.variable)}
    >
      <body>
        <ThemeProvider>{children}</ThemeProvider>
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
      </body>
    </html>
  )
}
