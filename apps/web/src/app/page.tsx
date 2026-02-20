"use client";

import Link from "next/link";
import Image from "next/image";
import { useState, useEffect } from "react";
import {
  Map,
  TrendingUp,
  GraduationCap,
  Bitcoin,
  ArrowRight,
  Star,
  Heart,
  Zap,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useTranslations } from "next-intl";

/* ── Hero images — stunning El Salvador photography ── */
const heroImages = [
  {
    src: "https://images.unsplash.com/photo-1622653902334-28275c5d7100?w=1920&q=85&auto=format",
    alt: "Santa Ana Volcano at sunset, El Salvador",
    credit: "Unsplash",
  },
  {
    src: "https://images.unsplash.com/photo-1605216663980-a3521b9c7b0e?w=1920&q=85&auto=format",
    alt: "El Tunco beach, golden hour surf waves",
    credit: "Unsplash",
  },
  {
    src: "https://images.unsplash.com/photo-1596395463362-48f3fea0b228?w=1920&q=85&auto=format",
    alt: "Colonial architecture in Suchitoto, El Salvador",
    credit: "Unsplash",
  },
  {
    src: "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=1920&q=85&auto=format",
    alt: "Joya de Cerén archaeological site, El Salvador",
    credit: "Unsplash",
  },
  {
    src: "https://images.unsplash.com/photo-1591112668397-b0e07634a707?w=1920&q=85&auto=format",
    alt: "Lush El Imposible National Park, El Salvador",
    credit: "Unsplash",
  },
];

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
    accent: "bg-gold-500/100",
    color: "text-gold-400",
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

const marketData = [
  { key: "home.market.tourismRev", value: "~$4.2B", source: "MITUR / World Bank" },
  { key: "home.market.tourismGdp", value: "14.5%", source: "BCR" },
  { key: "home.market.tourists", value: "4M+", source: "MITUR" },
  { key: "home.market.remittances", value: "$10B/yr", source: "BCR" },
  { key: "home.market.remInvest", value: "<0.25%", source: "World Bank" },
  { key: "home.market.construction", value: "$2.45B → $2.89B", source: "Mordor Intelligence" },
  { key: "home.market.hotelGap", value: "10,000 rooms", source: "Tourism Ministry" },
  { key: "home.market.mls", value: "None", source: "—" },
  { key: "home.market.license", value: "No", source: "—" },
  { key: "home.market.aiTax", value: "0%", source: "ES AI Law (2025)" },
  { key: "home.market.sixthGrade", value: ">50%", source: "UNICEF" },
  { key: "home.market.ruralSchool", value: "5.6 years", source: "HRW / EHPM" },
  { key: "home.market.malnutrition", value: "10%", source: "UN Joint Programme" },
  { key: "home.market.neet", value: "21.5%", source: "World Bank" },
];

export default function HomePage() {
  const t = useTranslations();
  const [imgIdx, setImgIdx] = useState(0);

  /* Auto-rotate hero images */
  useEffect(() => {
    const timer = setInterval(() => setImgIdx((i) => (i + 1) % heroImages.length), 6000);
    return () => clearInterval(timer);
  }, []);

  const prevImg = () => setImgIdx((i) => (i - 1 + heroImages.length) % heroImages.length);
  const nextImg = () => setImgIdx((i) => (i + 1) % heroImages.length);

  return (
    <main>
      {/* ── Hero — Cinematic Dark ──────────────────── */}
      <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-black">
        {/* Background images with crossfade */}
        {heroImages.map((img, i) => (
          <div
            key={img.src}
            className="absolute inset-0 transition-opacity duration-[1500ms] ease-in-out"
            style={{ opacity: i === imgIdx ? 1 : 0 }}
          >
            <Image
              src={img.src}
              alt={img.alt}
              fill
              className="object-cover"
              priority={i === 0}
              sizes="100vw"
              unoptimized
            />
          </div>
        ))}

        {/* Gradient overlays */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black/80 z-[1]" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/40 via-transparent to-black/40 z-[1]" />

        {/* Image navigation arrows */}
        <button
          onClick={prevImg}
          className="absolute left-4 top-1/2 -translate-y-1/2 z-20 rounded-full bg-white/10 p-2 text-white/60 backdrop-blur-sm transition hover:bg-white/20 hover:text-white"
          aria-label="Previous image"
        >
          <ChevronLeft size={24} />
        </button>
        <button
          onClick={nextImg}
          className="absolute right-4 top-1/2 -translate-y-1/2 z-20 rounded-full bg-white/10 p-2 text-white/60 backdrop-blur-sm transition hover:bg-white/20 hover:text-white"
          aria-label="Next image"
        >
          <ChevronRight size={24} />
        </button>

        {/* Dots */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex gap-2">
          {heroImages.map((_, i) => (
            <button
              key={i}
              onClick={() => setImgIdx(i)}
              className={`h-2 rounded-full transition-all ${
                i === imgIdx ? "w-8 bg-gold-400" : "w-2 bg-white/30 hover:bg-white/50"
              }`}
              aria-label={`Image ${i + 1}`}
            />
          ))}
        </div>

        {/* Content */}
        <div className="relative z-10 mx-auto max-w-5xl px-6 text-center">
          <div className="mb-8 text-8xl md:text-9xl select-none drop-shadow-2xl">🇸🇻</div>
          <h1 className="mb-6 font-serif text-6xl leading-[1.05] font-black tracking-tight text-white md:text-8xl lg:text-9xl drop-shadow-lg">
            {t("home.title1")}
            <br />
            <span className="text-gold-400">{t("home.title2")}</span>
          </h1>

          <p className="mx-auto mb-10 max-w-lg text-lg leading-relaxed text-white/70">
            {t("home.subtitle")}
            <br className="hidden sm:block" />
            {t("home.desc")}
          </p>

          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href="/explore"
              className="group flex items-center gap-2 rounded-md bg-[#0a0a0a] px-8 py-4 text-sm font-semibold text-white shadow-lg transition-all hover:bg-gold-500/10 hover:shadow-xl"
            >
              {t("home.getStarted")}
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/invest"
              className="flex items-center gap-2 rounded-md border border-white/20 bg-white/10 px-8 py-4 text-sm font-semibold text-white backdrop-blur-sm transition-all hover:border-white/40 hover:bg-white/20"
            >
              <Bitcoin size={16} className="text-gold-400" />
              {t("home.investNow")}
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats ─────────────────────────────────── */}
      <section className="border-y border-white/10 bg-sv-950">
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

      {/* ── The Mission ─────────────────────────── */}
      <section className="bg-sv-950 py-24 lg:py-32">
        <div className="mx-auto max-w-4xl px-6">
          <div className="mb-8 text-center">
            <h2 className="font-serif text-5xl font-black tracking-tight text-white md:text-6xl lg:text-7xl">
              {t("home.missionTitle1")}
              <br />
              <span className="text-impact-400">{t("home.missionTitle2")}</span>
            </h2>
          </div>
          <div className="mx-auto max-w-3xl space-y-6 text-center">
            <p className="text-lg leading-relaxed text-white/60">{t("home.missionP1")}</p>
            <p className="text-lg leading-relaxed text-white/60">{t("home.missionP2")}</p>
            <p className="text-2xl font-bold text-white">{t("home.missionP3")}</p>
            <p className="text-lg leading-relaxed text-white/60">{t("home.missionP4")}</p>
            <p className="text-lg font-medium leading-relaxed text-gold-400">{t("home.missionP5")}</p>
          </div>
        </div>
      </section>

      {/* ── Pipeline Equation — THE MATH ──────────── */}
      <section className="relative overflow-hidden border-y border-white/5 bg-[#0d0d0d] py-24 lg:py-32">
        <div className="pointer-events-none absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h40v40H0z' fill='none' stroke='%23ffffff' stroke-width='0.5'/%3E%3C/svg%3E\")" }} />
        <div className="relative z-10 mx-auto max-w-5xl px-6">
          <div className="mb-6 text-center">
            <h2 className="mb-3 font-serif text-5xl font-black tracking-tight text-white md:text-6xl lg:text-7xl">
              {t("eq.title1")}<br /><span className="text-impact-500">{t("eq.title2")}</span>
            </h2>
            <p className="mx-auto max-w-lg text-lg text-white/40">
              {t("eq.subtitle")}
            </p>
          </div>

          {/* The Equation — Large & Prominent */}
          <div className="mx-auto mb-14 max-w-3xl rounded-2xl border-2 border-white/15 bg-white/5 backdrop-blur-sm p-8 text-center shadow-lg md:p-12">
            <div className="mb-3 text-xs font-semibold uppercase tracking-widest text-white/40">
              {t("eq.formulaLabel")}
            </div>
            <div className="equation-hero text-white">
              <span className="text-impact-500">F</span>{" "}
              <span className="text-white/30">=</span>{" "}
              <span className="text-sv-500">O</span>{" "}
              <span className="text-white/30">×</span>{" "}
              <span className="text-sv-500">m</span>{" "}
              <span className="text-white/30">×</span>{" "}
              <span className="text-sv-500">f</span>{" "}
              <span className="text-white/30">×</span>{" "}
              <span className="text-gold-500">α</span>{" "}
              <span className="text-white/30">×</span>{" "}
              <span className="text-gold-500">e</span>
            </div>
            <div className="mt-4 text-sm font-medium text-white/50">
              <span className="font-bold text-impact-600">F</span> = {t("eq.F")}
            </div>
          </div>

          {/* Variable Breakdown Cards */}
          <div className="mb-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {/* O */}
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-white/10 text-sv-400">O</div>
                <div>
                  <div className="text-sm font-bold text-white">${"13.6B"}</div>
                  <div className="text-xs text-white/40">{t("eq.O.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-white/50">{t("eq.O.detail")}</p>
            </div>
            {/* m */}
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-white/10 text-sv-400">m</div>
                <div>
                  <div className="text-sm font-bold text-white">{"0.5% → 3%+"}</div>
                  <div className="text-xs text-white/40">{t("eq.m.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-white/50">{t("eq.m.detail")}</p>
            </div>
            {/* f */}
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-white/10 text-sv-400">f</div>
                <div>
                  <div className="text-sm font-bold text-white">{"12%"}</div>
                  <div className="text-xs text-white/40">{t("eq.f.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-white/50">{t("eq.f.detail")}</p>
            </div>
            {/* α */}
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-gold-100 text-gold-400">α</div>
                <div>
                  <div className="text-sm font-bold text-white">{"17.5%"}</div>
                  <div className="text-xs text-white/40">{t("eq.alpha.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-white/50">{t("eq.alpha.detail")}</p>
            </div>
            {/* e */}
            <div className="equation-card">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-gold-100 text-gold-400">e</div>
                <div>
                  <div className="text-sm font-bold text-white">{"92%"}</div>
                  <div className="text-xs text-white/40">{t("eq.e.label")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-white/50">{t("eq.e.detail")}</p>
            </div>
            {/* Per-child cost */}
            <div className="equation-card border-impact-200 bg-impact-500/[0.03]">
              <div className="mb-3 flex items-center gap-3">
                <div className="equation-variable bg-impact-100 text-impact-600">
                  <Heart size={16} />
                </div>
                <div>
                  <div className="text-sm font-bold text-white">{"$250/yr"}</div>
                  <div className="text-xs text-white/40">{t("eq.perChild")}</div>
                </div>
              </div>
              <p className="text-xs leading-relaxed text-white/50">{t("eq.perChildDetail")}</p>
            </div>
          </div>

          {/* Sensitivity Table */}
          <div className="mx-auto mb-14 max-w-2xl">
            <div className="mb-4 text-center">
              <h3 className="text-lg font-bold text-white">{t("eq.tableTitle")}</h3>
              <p className="text-sm text-white/40">{t("eq.tableSubtitle")}</p>
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
                {[
                  { m: "0.5%", f: "$1.31M", kids: "5,240" },
                  { m: "1.0%", f: "$2.62M", kids: "10,480" },
                  { m: "3.0%", f: "$7.87M", kids: "31,480" },
                  { m: "5.0%", f: "$13.12M", kids: "52,480" },
                ].map((row) => (
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
            <div className="rounded-xl border border-white/10 bg-white/5 p-6">
              <div className="mb-2 flex items-center gap-2">
                <Zap size={16} className="text-sv-500" />
                <h4 className="text-sm font-bold text-white">{t("eq.bridgeTitle")}</h4>
              </div>
              <p className="text-sm leading-relaxed text-white/50">{t("eq.bridgeDesc")}</p>
            </div>
            <div className="rounded-xl border border-impact-500/20 bg-impact-500/10 p-6">
              <div className="mb-2 flex items-center gap-2">
                <Heart size={16} className="text-impact-500" />
                <h4 className="text-sm font-bold text-white">{t("eq.effectsTitle")}</h4>
              </div>
              <p className="text-sm leading-relaxed text-white/50">{t("eq.effectsDesc")}</p>
            </div>
          </div>

          {/* Tagline */}
          <p className="mt-10 text-center text-sm font-semibold uppercase tracking-widest text-white/20">
            {t("eq.tagline")}
          </p>
        </div>
      </section>

      {/* ── Description — Full-Funnel Country Platform ── */}
      <section className="bg-[#0a0a0a] py-24 lg:py-32">
        <div className="mx-auto max-w-4xl px-6">
          <div className="mb-8 text-center">
            <h2 className="font-serif text-5xl font-black tracking-tight text-white md:text-6xl">
              {t("home.descTitle1")}<br /><span className="text-sv-400">{t("home.descTitle2")}</span>
            </h2>
          </div>
          <div className="mx-auto max-w-3xl space-y-6 text-center">
            <p className="text-lg leading-relaxed text-white/60">{t("home.descP1")}</p>
            <p className="text-lg leading-relaxed text-white/60">{t("home.descP2")}</p>
            <p className="text-lg font-medium leading-relaxed text-impact-400">{t("home.descP3")}</p>
          </div>
        </div>
      </section>

      {/* ── Pillars ───────────────────────────────── */}
      <section className="border-y border-white/5 bg-[#111] py-24 lg:py-32">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="mb-3 text-center font-serif text-4xl font-bold text-white md:text-5xl">
            {t("home.pillarsTitle1")}<br />{t("home.pillarsTitle2")}
          </h2>
          <p className="mx-auto mb-16 max-w-lg text-center text-white/40">
            {t("home.pillarsSubtitle")}
          </p>

          <div className="grid gap-6 md:grid-cols-3">
            {pillarKeys.map((p) => (
              <Link
                key={p.titleKey}
                href={p.href}
                className="group rounded-xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-white/20 hover:bg-white/10"
              >
                <div className={`mb-5 flex h-11 w-11 items-center justify-center rounded-lg ${p.accent} text-white`}>
                  <p.icon size={20} />
                </div>
                <h3 className="mb-2 text-lg font-bold text-white">{t(p.titleKey)}</h3>
                <p className="mb-5 text-sm leading-relaxed text-white/40">{t(p.descKey)}</p>
                <span className={`inline-flex items-center gap-1.5 text-sm font-semibold ${p.color} transition-all group-hover:gap-2.5`}>
                  {t("home.learnMore")} <ArrowRight size={14} />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Market Opportunity ─────────────────────── */}
      <section className="bg-[#0a0a0a] py-24 lg:py-32">
        <div className="mx-auto max-w-5xl px-6">
          <div className="mb-10 text-center">
            <h2 className="mb-3 font-serif text-5xl font-black tracking-tight text-white md:text-6xl">
              {t("home.marketTitle1")}<br />
              <span className="text-gold-400">{t("home.marketTitle2")}</span>
            </h2>
            <p className="mx-auto max-w-md text-white/40">{t("home.marketSubtitle")}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {marketData.map((item) => (
              <div key={item.key} className="rounded-lg border border-white/10 bg-white/5 px-5 py-4 transition hover:border-white/20">
                <div className="flex items-start justify-between">
                  <div className="text-sm text-white/50">{t(item.key)}</div>
                  <div className="text-right text-xs text-white/20">{item.source}</div>
                </div>
                <div className="mt-1 font-serif text-xl font-bold text-white">{item.value}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Cycle ─────────────────────────────────── */}
      <section className="border-y border-white/10 bg-[#0d0d0d] py-24 lg:py-32">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="mb-3 font-serif text-4xl font-bold text-white md:text-5xl">
            {t("home.cycleTitle1")}<br />{t("home.cycleTitle2")}
          </h2>
          <p className="mx-auto mb-14 max-w-md text-white/40">
            {t("home.cycleSubtitle")}
          </p>

          <div className="mx-auto flex max-w-sm flex-col items-center gap-2">
            {[
              { icon: "�", labelKey: "home.cycle.tourism" },
              { icon: "🫓", labelKey: "home.cycle.platform" },
              { icon: "🏛️", labelKey: "home.cycle.fund" },
              { icon: "🧒🏽", labelKey: "home.cycle.children" },
            ].map((step, i) => (
              <div key={step.labelKey} className="w-full">
                <div className="rounded-lg border border-white/10 bg-white/5 px-6 py-4">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{step.icon}</span>
                    <span className="text-sm font-semibold text-white">{t(step.labelKey)}</span>
                  </div>
                </div>
                {i < 3 && (
                  <div className="flex justify-center py-1.5 text-white/20">
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 2v12M4 10l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                  </div>
                )}
              </div>
            ))}

          </div>
        </div>
      </section>

      {/* ── Impact Statement ──────────────────────── */}
      <section className="relative bg-sv-950 py-24 lg:py-32">
        <div className="pointer-events-none absolute inset-0 opacity-[0.04]" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3E%3Ctext x='40' y='45' text-anchor='middle' font-size='30' opacity='0.3'%3E🇸🇻%3C/text%3E%3C/svg%3E\")" }} />
        <div className="relative z-10 mx-auto max-w-3xl px-6 text-center">
          <div className="mx-auto mb-6 text-4xl">🫓</div>
          <blockquote className="font-serif text-xl leading-relaxed font-medium text-white/80 italic md:text-2xl lg:text-3xl">
            &ldquo;{t("home.impactStatement")}&rdquo;
          </blockquote>
          <p className="mt-8 text-sm font-semibold uppercase tracking-widest text-white/20">
            PupuserIA · Inteligencia Artificial · Para los niños de El Salvador 🇸🇻
          </p>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────── */}
      <section id="waitlist" className="bg-[#0a0a0a] py-24 lg:py-32">
        <div className="mx-auto max-w-md px-6 text-center">
          <div className="mb-5 inline-flex items-center gap-2 rounded border border-gold-400/30 bg-gold-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-gold-400">
            <Star size={12} />
            {t("home.earlyAccess")}
          </div>
          <h2 className="mb-3 font-serif text-4xl font-bold text-white md:text-5xl">
            {t("home.joinWaitlist")}
          </h2>
          <p className="mb-8 text-white/40">
            {t("home.waitlistDesc")}
          </p>

          <form className="flex flex-col gap-2.5 sm:flex-row">
            <input
              type="email"
              placeholder={t("home.emailPlaceholder")}
              className="flex-1 rounded-md border border-white/15 bg-white/5 px-5 py-3.5 text-sm text-white outline-none transition-all placeholder:text-white/30 focus:border-gold-400 focus:ring-2 focus:ring-gold-400/20"
              required
            />
            <button
              type="submit"
              className="rounded-md bg-gold-500/100 px-6 py-3.5 text-sm font-semibold text-white transition-all hover:bg-gold-400"
            >
              {t("home.getAccess")}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
