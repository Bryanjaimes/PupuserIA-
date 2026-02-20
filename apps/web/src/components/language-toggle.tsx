"use client";

import { useLocaleContext } from "@/context/language-provider";

export function LanguageToggle() {
  const { locale, setLocale } = useLocaleContext();

  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-0.5 rounded-full border border-white/10 bg-[#0a0a0a] p-1 shadow-lg">
      <button
        onClick={() => setLocale("en")}
        className={`rounded-full px-3 py-1.5 text-xs font-bold tracking-wide transition-all ${
          locale === "en"
            ? "bg-sv-500 text-white shadow-sm"
            : "text-gray-400 hover:text-sv-400"
        }`}
        aria-label="Switch to English"
      >
        EN
      </button>
      <button
        onClick={() => setLocale("es")}
        className={`rounded-full px-3 py-1.5 text-xs font-bold tracking-wide transition-all ${
          locale === "es"
            ? "bg-sv-500 text-white shadow-sm"
            : "text-gray-400 hover:text-sv-400"
        }`}
        aria-label="Cambiar a Español"
      >
        ES
      </button>
    </div>
  );
}
