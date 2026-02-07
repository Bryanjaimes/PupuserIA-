import Link from "next/link";
import {
  Map,
  TrendingUp,
  GraduationCap,
  Bitcoin,
  ArrowRight,
  Star,
  CheckCircle,
} from "lucide-react";
import { HeroSlideshow } from "@/components/hero-slideshow";

const pillars = [
  {
    icon: Map,
    title: "Explore",
    desc: "AI-powered maps, trip planning, and safety dashboards across all 14 departments.",
    href: "/explore",
    gradient: "from-sv-400 to-sv-600",
    color: "text-sv-500",
  },
  {
    icon: TrendingUp,
    title: "Invest",
    desc: "AI property valuations, curated experiences, and diaspora investment from $150/mo.",
    href: "/invest",
    gradient: "from-gold-400 to-gold-600",
    color: "text-gold-600",
  },
  {
    icon: GraduationCap,
    title: "Impact",
    desc: "Every transaction funds AI tutoring, meals, and devices for Salvadoran children.",
    href: "/foundation",
    gradient: "from-impact-400 to-impact-600",
    color: "text-impact-600",
  },
];

export default function HomePage() {
  return (
    <main>
      {/* ── Hero ──────────────────────────────────── */}
      <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-sv-950">
        <HeroSlideshow />

        <div className="relative z-10 mx-auto max-w-4xl px-6 text-center">
          <h1 className="mb-5 text-5xl leading-[1.05] font-extrabold tracking-tight text-white md:text-7xl lg:text-8xl">
            El Salvador,
            <br />
            <span className="bg-gradient-to-r from-gold-400 via-gold-300 to-gold-400 bg-clip-text text-transparent animate-shimmer">
              reimagined.
            </span>
          </h1>

          <p className="mx-auto mb-10 max-w-lg text-base text-white/50 md:text-lg">
            Explore. Invest. Fund education.
            <br className="hidden sm:block" />
            The AI-powered gateway to Central America&apos;s fastest-growing economy.
          </p>

          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href="/explore"
              className="group flex items-center gap-2 rounded-2xl bg-white px-8 py-4 font-semibold text-sv-900 shadow-2xl shadow-black/20 transition-all duration-300 hover:bg-white/95"
            >
              Get Started
              <ArrowRight size={16} className="transition-transform duration-300 group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/invest"
              className="flex items-center gap-2 rounded-2xl border border-white/15 bg-white/5 px-8 py-4 font-semibold text-white backdrop-blur-sm transition-all duration-300 hover:bg-white/10"
            >
              <Bitcoin size={16} className="text-gold-400" />
              Invest Now
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats ─────────────────────────────────── */}
      <section className="bg-gradient-to-r from-sv-900 via-sv-800 to-sv-900">
        <div className="mx-auto grid max-w-5xl grid-cols-2 md:grid-cols-4">
          {[
            { v: "$4.2B", l: "Tourism GDP" },
            { v: "4M+", l: "Annual Visitors" },
            { v: "$10B", l: "Remittances" },
            { v: "0%", l: "AI Tax" },
          ].map((s) => (
            <div key={s.l} className="px-4 py-7 text-center">
              <div className="text-2xl font-extrabold text-white md:text-3xl">{s.v}</div>
              <div className="mt-0.5 text-xs font-medium text-white/40">{s.l}</div>
            </div>
          ))}
        </div>
        <div className="h-px bg-gradient-to-r from-transparent via-gold-500/40 to-transparent" />
      </section>

      {/* ── Pillars ───────────────────────────────── */}
      <section className="bg-gradient-to-b from-white to-sv-50 py-20 lg:py-28">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="mb-4 text-center text-3xl font-extrabold text-sv-950 md:text-4xl">
            One platform. Three missions.
          </h2>
          <p className="mx-auto mb-14 max-w-lg text-center text-sv-700/45">
            Tourism, investment, and education — unified for the first time.
          </p>

          <div className="grid gap-5 md:grid-cols-3">
            {pillars.map((p) => (
              <Link
                key={p.title}
                href={p.href}
                className="glass-card group rounded-2xl p-7 transition-all duration-500 hover:shadow-xl hover:-translate-y-1"
              >
                <div className={`mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${p.gradient} text-white shadow-lg`}>
                  <p.icon size={22} />
                </div>
                <h3 className="mb-2 text-lg font-bold text-sv-900">{p.title}</h3>
                <p className="mb-4 text-sm leading-relaxed text-sv-700/50">{p.desc}</p>
                <span className={`inline-flex items-center gap-1.5 text-sm font-semibold ${p.color} transition-all duration-300 group-hover:gap-2.5`}>
                  Learn more <ArrowRight size={14} />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Cycle ─────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-br from-sv-950 via-sv-900 to-sv-950 py-20 text-white lg:py-28">
        <div className="pointer-events-none absolute top-16 left-1/4 h-[250px] w-[250px] rounded-full bg-sv-500/8 blur-[80px]" />
        <div className="pointer-events-none absolute bottom-16 right-1/4 h-[200px] w-[200px] rounded-full bg-gold-500/6 blur-[80px]" />

        <div className="relative z-10 mx-auto max-w-3xl px-6 text-center">
          <h2 className="mb-4 text-3xl font-extrabold md:text-4xl">
            Every dollar builds the future.
          </h2>
          <p className="mx-auto mb-12 max-w-md text-sm text-white/35">
            Revenue flows directly into education, nutrition, and technology for Salvadoran children.
          </p>

          <div className="mx-auto flex max-w-sm flex-col items-center gap-2">
            {[
              { icon: "🌍", label: "Tourism & Investment" },
              { icon: "⚡", label: "Gateway Platform" },
              { icon: "🏛️", label: "Foundation Fund" },
              { icon: "🧒", label: "Children Empowered" },
            ].map((step, i) => (
              <div key={step.label} className="w-full">
                <div className="glass-dark rounded-xl px-5 py-3.5 transition-all duration-300 hover:bg-white/8">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{step.icon}</span>
                    <span className="text-sm font-semibold">{step.label}</span>
                  </div>
                </div>
                {i < 3 && (
                  <div className="flex justify-center py-1 text-white/15">
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 2v12M4 10l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                  </div>
                )}
              </div>
            ))}
            <div className="mt-3 rounded-full border border-gold-400/15 bg-gold-400/5 px-4 py-1.5 text-xs font-medium text-gold-400">
              ♻️ Virtuous Cycle
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────── */}
      <section id="waitlist" className="bg-gradient-to-b from-sv-50 to-white py-20 lg:py-28">
        <div className="mx-auto max-w-md px-6 text-center">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full glass-gold px-4 py-2 text-xs font-medium text-gold-700">
            <Star size={12} className="text-gold-500" />
            Early Access
          </div>
          <h2 className="mb-3 text-3xl font-extrabold text-sv-950 md:text-4xl">
            Join the waitlist.
          </h2>
          <p className="mb-8 text-sm text-sv-700/45">
            Be first to explore, invest, and make an impact.
          </p>

          <form className="flex flex-col gap-2.5 sm:flex-row">
            <input
              type="email"
              placeholder="you@email.com"
              className="flex-1 rounded-xl glass px-5 py-3.5 text-sm text-sv-900 outline-none transition-all duration-300 placeholder:text-sv-400/40 focus:shadow-lg focus:shadow-sv-500/10"
              required
            />
            <button
              type="submit"
              className="rounded-xl bg-gradient-to-r from-sv-500 to-sv-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-sv-500/20 transition-all duration-300 hover:shadow-xl hover:brightness-110"
            >
              Get Access
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
