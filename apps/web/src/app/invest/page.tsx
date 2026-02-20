"use client";

import Link from "next/link";
import { TrendingUp, BarChart3, Calendar, Bitcoin } from "lucide-react";
import { useTranslations } from "next-intl";

export default function InvestPage() {
  const t = useTranslations();

  const cards = [
    { icon: TrendingUp, titleKey: "investPage.search.title", descKey: "investPage.search.desc", emoji: "📍" },
    { icon: BarChart3, titleKey: "investPage.ai.title", descKey: "investPage.ai.desc", emoji: "🤖" },
    { icon: Bitcoin, titleKey: "investPage.btc.title", descKey: "investPage.btc.desc", emoji: "₿" },
    { icon: Calendar, titleKey: "investPage.consulting.title", descKey: "investPage.consulting.desc", emoji: "📅" },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20">
      <div className="mx-auto max-w-7xl px-6 py-24">
        <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-wider text-gold-400 uppercase">
          <span className="h-px w-8 bg-gold-500/100/30" />
          {t("investPage.investment")}
          <span className="h-px w-8 bg-gold-500/100/30" />
        </div>
        <h1 className="mb-4 text-4xl font-extrabold text-white md:text-5xl">
          {t("investPage.title")}
        </h1>
        <p className="mb-12 max-w-2xl text-lg text-white/40">
          {t("investPage.desc")}
        </p>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {cards.map((card) => (
            <div key={card.titleKey} className="glass-card rounded-2xl p-7 transition-all duration-500 hover:shadow-xl hover:-translate-y-1">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-gold-100 to-gold-50 text-xl">
                {card.emoji}
              </div>
              <h3 className="mb-2 text-base font-bold text-white/90">{t(card.titleKey)}</h3>
              <p className="text-sm leading-relaxed text-white/40">{t(card.descKey)}</p>
              <div className="mt-4 inline-flex items-center rounded-full bg-gold-500/100/10 px-3 py-1 text-xs font-medium text-gold-700">
                {t("investPage.comingSoon")}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
