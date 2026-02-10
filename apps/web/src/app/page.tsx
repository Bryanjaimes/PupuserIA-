"use client";

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
import { useLanguage } from "@/context/language-context";

const pillarKeys = [
  {
    icon: Map,
    titleKey: "home.explore.title",
    descKey: "home.explore.desc",
    href: "/explore",
    accent: "bg-sv-500",
    color: "text-sv-500",
  },
  {
    icon: TrendingUp,
    titleKey: "home.invest.title",
    descKey: "home.invest.desc",
    href: "/invest",
    accent: "bg-gold-500",
    color: "text-gold-600",
  },
  {
    icon: GraduationCap,
    titleKey: "home.impact.title",
    descKey: "home.impact.desc",
    href: "/foundation",
    accent: "bg-impact-500",
    color: "text-impact-600",
  },
];

export default function HomePage() {
  const { t } = useLanguage();

  return (
    <main>
      {/* ── Hero ──────────────────────────────────── */}
      <section className="relative flex min-h-[85vh] flex-col items-center justify-center overflow-hidden bg-[#f8f9fc] pt-28">

        <div className="relative z-10 mx-auto max-w-4xl px-6 text-center">
          {/* Gov badge */}
          <div className="mb-8 inline-flex items-center gap-2 rounded border border-sv-200 bg-sv-50 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-sv-600">
            <span className="text-sm">🇸🇻</span>
            {t("home.badge")}
          </div>

          <h1 className="mb-6 font-serif text-5xl leading-[1.08] font-black tracking-tight text-sv-950 md:text-7xl lg:text-8xl">
            {t("home.title1")}
            <br />
            <span className="text-gold-500">{t("home.title2")}</span>
          </h1>

          <p className="mx-auto mb-10 max-w-lg text-lg leading-relaxed text-gray-500">
            {t("home.subtitle")}
            <br className="hidden sm:block" />
            {t("home.desc")}
          </p>

          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href="/explore"
              className="group flex items-center gap-2 rounded-md bg-sv-500 px-8 py-4 text-sm font-semibold text-white transition-all hover:bg-sv-600"
            >
              {t("home.getStarted")}
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/invest"
              className="flex items-center gap-2 rounded-md border border-gray-200 bg-white px-8 py-4 text-sm font-semibold text-sv-900 transition-all hover:border-gray-300 hover:bg-gray-50"
            >
              <Bitcoin size={16} className="text-gold-500" />
              {t("home.investNow")}
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats ─────────────────────────────────── */}
      <section className="border-y border-gray-200 bg-sv-950">
        <div className="mx-auto grid max-w-5xl grid-cols-2 divide-x divide-white/10 md:grid-cols-4">
          {[
            { v: "$4.2B", lKey: "home.tourismGdp" },
            { v: "4M+", lKey: "home.annualVisitors" },
            { v: "$10B", lKey: "home.remittances" },
            { v: "0%", lKey: "home.aiTax" },
          ].map((s) => (
            <div key={s.lKey} className="px-4 py-8 text-center">
              <div className="font-serif text-3xl font-bold text-white md:text-4xl">{s.v}</div>
              <div className="mt-1 text-xs font-medium uppercase tracking-wider text-white/40">{t(s.lKey)}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Pillars ───────────────────────────────── */}
      <section className="bg-white py-24 lg:py-32">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="mb-3 text-center font-serif text-4xl font-bold text-sv-950 md:text-5xl">
            {t("home.pillarsTitle1")}<br />{t("home.pillarsTitle2")}
          </h2>
          <p className="mx-auto mb-16 max-w-lg text-center text-gray-400">
            {t("home.pillarsSubtitle")}
          </p>

          <div className="grid gap-6 md:grid-cols-3">
            {pillarKeys.map((p) => (
              <Link
                key={p.titleKey}
                href={p.href}
                className="gov-card group rounded-lg p-8 transition-all hover:-translate-y-0.5"
              >
                <div className={`mb-5 flex h-11 w-11 items-center justify-center rounded-lg ${p.accent} text-white`}>
                  <p.icon size={20} />
                </div>
                <h3 className="mb-2 text-lg font-bold text-sv-900">{t(p.titleKey)}</h3>
                <p className="mb-5 text-sm leading-relaxed text-gray-400">{t(p.descKey)}</p>
                <span className={`inline-flex items-center gap-1.5 text-sm font-semibold ${p.color} transition-all group-hover:gap-2.5`}>
                  {t("home.learnMore")} <ArrowRight size={14} />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Cycle ─────────────────────────────────── */}
      <section className="border-y border-gray-200 bg-[#f8f9fc] py-24 lg:py-32">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="mb-3 font-serif text-4xl font-bold text-sv-950 md:text-5xl">
            {t("home.cycleTitle1")}<br />{t("home.cycleTitle2")}
          </h2>
          <p className="mx-auto mb-14 max-w-md text-gray-400">
            {t("home.cycleSubtitle")}
          </p>

          <div className="mx-auto flex max-w-sm flex-col items-center gap-2">
            {[
              { icon: "🌍", labelKey: "home.cycle.tourism" },
              { icon: "⚡", labelKey: "home.cycle.platform" },
              { icon: "🏛️", labelKey: "home.cycle.fund" },
              { icon: "🧒", labelKey: "home.cycle.children" },
            ].map((step, i) => (
              <div key={step.labelKey} className="w-full">
                <div className="gov-card rounded-lg px-6 py-4">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{step.icon}</span>
                    <span className="text-sm font-semibold text-sv-900">{t(step.labelKey)}</span>
                  </div>
                </div>
                {i < 3 && (
                  <div className="flex justify-center py-1.5 text-gray-300">
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 2v12M4 10l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                  </div>
                )}
              </div>
            ))}
            <div className="mt-4 rounded border border-gold-400/30 bg-gold-50 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-gold-600">
              {t("home.virtuousCycle")}
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────── */}
      <section id="waitlist" className="bg-white py-24 lg:py-32">
        <div className="mx-auto max-w-md px-6 text-center">
          <div className="mb-5 inline-flex items-center gap-2 rounded border border-gold-400/30 bg-gold-50 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-gold-600">
            <Star size={12} />
            {t("home.earlyAccess")}
          </div>
          <h2 className="mb-3 font-serif text-4xl font-bold text-sv-950 md:text-5xl">
            {t("home.joinWaitlist")}
          </h2>
          <p className="mb-8 text-gray-400">
            {t("home.waitlistDesc")}
          </p>

          <form className="flex flex-col gap-2.5 sm:flex-row">
            <input
              type="email"
              placeholder={t("home.emailPlaceholder")}
              className="flex-1 rounded-md border border-gray-200 bg-white px-5 py-3.5 text-sm text-sv-900 outline-none transition-all placeholder:text-gray-300 focus:border-sv-500 focus:ring-2 focus:ring-sv-500/20"
              required
            />
            <button
              type="submit"
              className="rounded-md bg-sv-500 px-6 py-3.5 text-sm font-semibold text-white transition-all hover:bg-sv-600"
            >
              {t("home.getAccess")}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
