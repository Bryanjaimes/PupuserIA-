"use client";

import Link from "next/link";
import { TrendingUp, BarChart3, Calendar, Bitcoin, ArrowRight } from "lucide-react";
import { useLanguage } from "@/context/language-context";

export default function InvestPage() {
  const { t } = useLanguage();

  const cards = [
    { icon: TrendingUp, titleKey: "investPage.search.title", descKey: "investPage.search.desc", emoji: "📍" },
    { icon: BarChart3, titleKey: "investPage.ai.title", descKey: "investPage.ai.desc", emoji: "🤖" },
    { icon: Bitcoin, titleKey: "investPage.btc.title", descKey: "investPage.btc.desc", emoji: "₿" },
    { icon: Calendar, titleKey: "investPage.consulting.title", descKey: "investPage.consulting.desc", emoji: "📅" },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20">
      <div className="mx-auto max-w-7xl px-6 py-24">
        <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-wider text-gold-600 uppercase">
          <span className="h-px w-8 bg-gold-500/30" />
          {t("investPage.investment")}
          <span className="h-px w-8 bg-gold-500/30" />
        </div>
        <h1 className="mb-4 text-4xl font-extrabold text-sv-950 md:text-5xl">
          {t("investPage.title")}
        </h1>
        <p className="mb-12 max-w-2xl text-lg text-sv-700/50">
          {t("investPage.desc")}
        </p>

        {/* Browse Properties CTA */}
        <Link
          href="/invest/properties"
          className="mb-10 flex items-center justify-between rounded-2xl bg-gradient-to-r from-sv-900 to-sv-800 p-8 text-white shadow-lg transition-all hover:shadow-xl hover:-translate-y-0.5"
        >
          <div>
            <h2 className="mb-1 text-2xl font-extrabold">🏠 {t("investPage.search.title")}</h2>
            <p className="text-sm text-white/70">{t("investPage.search.desc")}</p>
          </div>
          <div className="flex items-center gap-2 rounded-xl bg-white/10 px-4 py-2 text-sm font-semibold backdrop-blur">
            {t("investPage.viewProperties")} <ArrowRight className="h-4 w-4" />
          </div>
        </Link>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {cards.map((card) => (
            <div key={card.titleKey} className="glass-card rounded-2xl p-7 transition-all duration-500 hover:shadow-xl hover:-translate-y-1">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-gold-100 to-gold-50 text-xl">
                {card.emoji}
              </div>
              <h3 className="mb-2 text-base font-bold text-sv-900">{t(card.titleKey)}</h3>
              <p className="text-sm leading-relaxed text-sv-700/50">{t(card.descKey)}</p>
              <div className="mt-4 inline-flex items-center rounded-full bg-gold-500/10 px-3 py-1 text-xs font-medium text-gold-700">
                {t("investPage.comingSoon")}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
