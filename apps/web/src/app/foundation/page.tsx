"use client";

import { GraduationCap, Utensils, Laptop, Zap } from "lucide-react";
import { useLanguage } from "@/context/language-context";

export default function FoundationPage() {
  const { t } = useLanguage();

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

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20">
      <div className="mx-auto max-w-7xl px-6 py-24">
        <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-wider text-impact-600 uppercase">
          <span className="h-px w-8 bg-impact-500/30" />
          {t("foundation.impact")}
          <span className="h-px w-8 bg-impact-500/30" />
        </div>
        <h1 className="mb-4 text-4xl font-extrabold text-sv-950 md:text-5xl">
          {t("foundation.title")}
        </h1>
        <p className="mb-12 max-w-2xl text-lg text-sv-700/50">
          {t("foundation.desc")}
        </p>

        {/* Impact counters */}
        <div className="mb-12 grid grid-cols-2 gap-4 md:grid-cols-4">
          {counters.map((stat) => (
            <div key={stat.labelKey} className="glass-card rounded-2xl p-6 text-center transition-all duration-500 hover:shadow-lg">
              <div className="mb-2 text-2xl">{stat.emoji}</div>
              <div className="text-3xl font-extrabold text-sv-900">{stat.value}</div>
              <div className="mt-1 text-xs font-medium text-sv-700/50">{t(stat.labelKey)}</div>
            </div>
          ))}
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {cards.map((card) => (
            <div key={card.titleKey} className="glass-card rounded-2xl p-7 transition-all duration-500 hover:shadow-xl hover:-translate-y-1">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-impact-400/20 to-impact-500/10 text-xl">
                {card.emoji}
              </div>
              <h3 className="mb-2 text-base font-bold text-sv-900">{t(card.titleKey)}</h3>
              <p className="text-sm leading-relaxed text-sv-700/50">{t(card.descKey)}</p>
              <div className="mt-4 inline-flex items-center rounded-full bg-impact-500/10 px-3 py-1 text-xs font-medium text-impact-600">
                {t("foundation.launchingSoon")}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
