"use client";

import { ShoppingBag, Home, Plane } from "lucide-react";
import { useLanguage } from "@/context/language-context";

export default function MarketplacePage() {
  const { t } = useLanguage();

  const cards = [
    { icon: Plane, titleKey: "market.tours.title", descKey: "market.tours.desc", emoji: "✈️" },
    { icon: Home, titleKey: "market.properties.title", descKey: "market.properties.desc", emoji: "🏡" },
    { icon: ShoppingBag, titleKey: "market.diaspora.title", descKey: "market.diaspora.desc", emoji: "💼" },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20">
      <div className="mx-auto max-w-7xl px-6 py-24">
        <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-wider text-gold-600 uppercase">
          <span className="h-px w-8 bg-gold-500/30" />
          {t("market.commerce")}
          <span className="h-px w-8 bg-gold-500/30" />
        </div>
        <h1 className="mb-4 text-4xl font-extrabold text-sv-950 md:text-5xl">
          {t("market.title")}
        </h1>
        <p className="mb-12 max-w-2xl text-lg text-sv-700/50">
          {t("market.desc")}
        </p>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {cards.map((card) => (
            <div key={card.titleKey} className="glass-card rounded-2xl p-8 transition-all duration-500 hover:shadow-xl hover:-translate-y-1">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-gold-100 to-gold-50 text-xl">
                {card.emoji}
              </div>
              <h3 className="mb-2 text-lg font-bold text-sv-900">{t(card.titleKey)}</h3>
              <p className="text-sm leading-relaxed text-sv-700/50">{t(card.descKey)}</p>
              <div className="mt-4 inline-flex items-center rounded-full bg-gold-500/10 px-3 py-1 text-xs font-medium text-gold-700">
                {t("market.comingSoon")}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
