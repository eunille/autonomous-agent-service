import Nav from "@/components/landing/nav"
import Hero from "@/components/landing/hero"
import Problem from "@/components/landing/problem"
import Services from "@/components/landing/services"
import HowItWorks from "@/components/landing/how-it-works"
import Stats from "@/components/landing/stats"
import Contact from "@/components/landing/contact"
import Footer from "@/components/landing/footer"

export default function Page() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <Nav />
      <main>
        <Hero />
        <Problem />
        <Services />
        <HowItWorks />
        <Stats />
        <Contact />
      </main>
      <Footer />
    </div>
  )
}
