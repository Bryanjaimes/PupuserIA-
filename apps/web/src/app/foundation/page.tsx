"use client";

import { GraduationCap, Utensils, Laptop, Zap, Heart, Shield, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";

export default function FoundationPage() {
  const t = useTranslations();

  const counters = [
    { value: "0", labelKey: "foundation.studentsTutored", emoji: "🎓" },
    { value: "0", labelKey: "foundation.mealsServed", emoji: "🍽️" },
    { value: "0", labelKey: "foundation.devicesDeployed", emoji: "💻" },
    { value: "0", labelKey: "foundation.schoolsConnected", emoji: "🏫" },
  ];

  const cards = [
    { icon: GraduationCap, titleKey: "foundation.aiTutoring.title", descKey: "foundation.aiTutoring.desc", emoji: "🤖" },
    { icon: Utensils, titleKey: "foundation.meals.title", descKey: "foundation.meals.desc", emoji: "🥘" },
    { icon: Laptop, titleKey: "foundation.devices.title", descKey: "foundation.devices.desc", emoji: "💻" },
    { icon: Zap, titleKey: "foundation.solar.title", descKey: "foundation.solar.desc", emoji: "☀️" },
  ];

  const sensitivityData = [
    { m: "0.5%", f: "$1.31M", kids: "5,240" },
    { m: "1.0%", f: "$2.62M", kids: "10,480" },
    { m: "3.0%", f: "$7.87M", kids: "31,480" },
    { m: "5.0%", f: "$13.12M", kids: "52,480" },
  ];

  return (
    <main className="min-h-screen bg-[#0a0a0a] pt-20">
      {/* ── Hero / Mission ── */}
      <section className="relative overflow-hidden border-b border-white/5 bg-[#0d0d0d] py-24 lg:py-32">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded border border-impact-500/20 bg-impact-500/5 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-impact-600">
            <Heart size={12} />
            {t("foundation.impact")}
          </div>
          <h1 className="mb-6 font-serif text-5xl font-black tracking-tight text-white md:text-6xl lg:text-7xl">
            {t("foundation.title")}
          </h1>
          <p className="mx-auto max-w-2xl text-lg leading-relaxed text-gray-500">
            {t("foundation.desc")}
          </p>
        </div>
      </section>

      {/* ── Impact Counters ── */}
      <section className="border-b border-white/10 bg-sv-950">
        <div className="mx-auto grid max-w-5xl grid-cols-2 divide-x divide-white/10 md:grid-cols-4">
          {counters.map((stat) => (
            <div key={stat.labelKey} className="px-4 py-8 text-center">
              <div className="mb-1 text-2xl">{stat.emoji}</div>
              <div className="font-serif text-3xl font-bold text-white md:text-4xl">{stat.value}</div>
              <div className="mt-1 text-xs font-medium uppercase tracking-wider text-white/40">{t(stat.labelKey)}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Pipeline Equation — Full Breakdown ── */}
      <section className="relative overflow-hidden py-24 lg:py-32">
        <div className="pointer-events-none absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h40v40H0z' fill='none' stroke='%230047ab' stroke-width='0.5'/%3E%3C/svg%3E\")" }} />
        <div className="relative z-10 mx-auto max-w-5xl px-6">
          <div className="mb-6 text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-sv-500">
              <Shield size={12} />
              {t("eq.formulaLabel")}
            </div>
            <h2 className="mb-3 font-serif text-4xl font-bold text-white md:text-5xl">
              {t("eq.title1")}<br /><span className="text-impact-500">{t("eq.title2")}</span>
            </h2>
            <p className="mx-auto max-w-lg text-gray-400">
              {t("eq.subtitle")}
            </p>
          </div>

          {/* Large Equation */}
          <div className="mx-auto mb-14 max-w-3xl rounded-2xl border-2 border-white/10 bg-gradient-to-br from-sv-50/80 to-white p-8 text-center shadow-lg md:p-12">
            <div className="equation-hero text-white">
              <span className="text-impact-500">F</span>{" "}
              <span className="text-gray-300">=</span>{" "}
              <span className="text-sv-500">O</span>{" "}
              <span className="text-gray-300">×</span>{" "}
              <span className="text-sv-500">m</span>{" "}
              <span className="text-gray-300">×</span>{" "}
              <span className="text-sv-500">f</span>{" "}
              <span className="text-gray-300">×</span>{" "}
              <span className="text-gold-500">α</span>{" "}
              <span className="text-gray-300">×</span>{" "}
              <span className="text-gold-500">e</span>
            </div>
            <div className="mt-4 text-base font-medium text-gray-400">
              <span className="font-bold text-impact-600">F</span> = {t("eq.F")} &nbsp;·&nbsp; <span className="font-bold text-white/60">{t("eq.perChild")}</span>: $250/yr
            </div>
          </div>

          {/* Variable Breakdown */}
          <div className="mb-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-white/10 text-sv-400">O</div>
                <div>
                  <div className="text-sm font-bold text-white/90">$13.6B</div>
                  <div className="text-xs text-gray-400">{t("eq.O.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-gray-500">{t("eq.O.detail")}</p>
            </div>
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-white/10 text-sv-400">m</div>
                <div>
                  <div className="text-sm font-bold text-white/90">0.5% → 3%+</div>
                  <div className="text-xs text-gray-400">{t("eq.m.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-gray-500">{t("eq.m.detail")}</p>
            </div>
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-white/10 text-sv-400">f</div>
                <div>
                  <div className="text-sm font-bold text-white/90">12%</div>
                  <div className="text-xs text-gray-400">{t("eq.f.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-gray-500">{t("eq.f.detail")}</p>
            </div>
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-gold-100 text-gold-400">α</div>
                <div>
                  <div className="text-sm font-bold text-white/90">17.5%</div>
                  <div className="text-xs text-gray-400">{t("eq.alpha.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-gray-500">{t("eq.alpha.detail")}</p>
            </div>
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-gold-100 text-gold-400">e</div>
                <div>
                  <div className="text-sm font-bold text-white/90">92%</div>
                  <div className="text-xs text-gray-400">{t("eq.e.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-gray-500">{t("eq.e.detail")}</p>
            </div>
            <div className="equation-card border-impact-200 bg-impact-500/[0.03]">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-impact-100 text-impact-600">
                  <Heart size={16} />
                </div>
                <div>
                  <div className="text-sm font-bold text-white/90">$250/yr</div>
                  <div className="text-xs text-gray-400">{t("eq.perChild")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-gray-500">{t("eq.perChildDetail")}</p>
            </div>
          </div>

          {/* Sensitivity Table */}
          <div className="mx-auto mb-14 max-w-2xl">
            <div className="mb-4 text-center">
              <h3 className="text-lg font-bold text-white">{t("eq.tableTitle")}</h3>
              <p className="text-sm text-gray-400">{t("eq.tableSubtitle")}</p>
            </div>
            <table className="sensitivity-table">
              <thead>
                <tr>
                  <th>{t("eq.captureRate")} (m)</th>
                  <th>{t("eq.fundsMM")} (F)</th>
                  <th>{t("eq.kidsYear")}</th>
                </tr>
              </thead>
              <tbody>
                {sensitivityData.map((row) => (
                  <tr key={row.m}>
                    <td>{row.m}</td>
                    <td className="font-semibold">{row.f}</td>
                    <td>
                      <span className="inline-flex items-center gap-1.5">
                        <span className="inline-block h-2 w-2 rounded-full bg-impact-500" />
                        {row.kids}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Bridge + Effects */}
          <div className="mx-auto grid max-w-3xl gap-5 md:grid-cols-2">
            <div className="rounded-xl border border-white/10 bg-white/5/50 p-6">
              <div className="mb-2 flex items-center gap-2">
                <Zap size={16} className="text-sv-500" />
                <h4 className="text-sm font-bold text-white/90">{t("eq.bridgeTitle")}</h4>
              </div>
              <p className="text-sm leading-relaxed text-gray-500">{t("eq.bridgeDesc")}</p>
            </div>
            <div className="rounded-xl border border-impact-200 bg-impact-500/[0.03] p-6">
              <div className="mb-2 flex items-center gap-2">
                <Heart size={16} className="text-impact-500" />
                <h4 className="text-sm font-bold text-white/90">{t("eq.effectsTitle")}</h4>
              </div>
              <p className="text-sm leading-relaxed text-gray-500">{t("eq.effectsDesc")}</p>
            </div>
          </div>

          <p className="mt-10 text-center text-sm font-semibold uppercase tracking-widest text-gray-300">
            {t("eq.tagline")}
          </p>
        </div>
      </section>

      {/* ── Our Belief ── */}
      <section className="border-b border-white/5 bg-[#0a0a0a] py-24 lg:py-32">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="mb-6 font-serif text-4xl font-bold text-white md:text-5xl">
            {t("foundation.missionTitle")}
          </h2>
          <div className="space-y-6">
            <p className="text-lg leading-relaxed text-gray-500">{t("foundation.missionP1")}</p>
            <p className="text-lg leading-relaxed text-gray-500">{t("foundation.missionP2")}</p>
          </div>
        </div>
      </section>

      {/* ── Programs ── */}
      <section className="border-t border-white/5 bg-[#0d0d0d] py-24 lg:py-32">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="mb-3 text-center font-serif text-4xl font-bold text-white md:text-5xl">
            {t("foundation.programsTitle")}
          </h2>
          <p className="mx-auto mb-14 max-w-md text-center text-gray-400">
            {t("foundation.programsDesc")}
          </p>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {cards.map((card) => (
              <div key={card.titleKey} className="equation-card rounded-xl p-7 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-impact-400/20 to-impact-500/10 text-xl">
                  {card.emoji}
                </div>
                <h3 className="mb-2 text-base font-bold text-white/90">{t(card.titleKey)}</h3>
                <p className="text-sm leading-relaxed text-gray-400">{t(card.descKey)}</p>
                <div className="mt-4 inline-flex items-center rounded-full bg-impact-500/10 px-3 py-1 text-xs font-medium text-impact-600">
                  {t("foundation.launchingSoon")}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="bg-[#0a0a0a] py-24 lg:py-32">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="mb-4 font-serif text-4xl font-bold text-white md:text-5xl">
            {t("foundation.ctaTitle")}
          </h2>
          <p className="mx-auto mb-8 max-w-md text-gray-400">
            {t("foundation.ctaDesc")}
          </p>
          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link href="/explore" className="group flex items-center gap-2 rounded-md bg-sv-500 px-8 py-4 text-sm font-semibold text-white transition-all hover:bg-sv-600">
              {t("foundation.startExploring")} <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link href="/invest" className="flex items-center gap-2 rounded-md border border-white/10 bg-[#0a0a0a] px-8 py-4 text-sm font-semibold text-white/90 transition-all hover:border-gray-300 hover:bg-white/5">
              {t("foundation.investNow")}
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
