import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Dashboard — AutoSystems",
  description: "Lead Intelligence Dashboard",
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Intentionally does NOT include the Typebot bubble widget
  return <>{children}</>
}
