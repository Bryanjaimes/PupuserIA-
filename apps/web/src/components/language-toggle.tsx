"use client";

import { useLanguage } from "@/context/language-context";

export function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-0.5 rounded-full border border-gray-200 bg-white p-1 shadow-lg">
      <button
        onClick={() => setLang("en")}
        className={`rounded-full px-3 py-1.5 text-xs font-bold tracking-wide transition-all ${
          lang === "en"
            ? "bg-sv-500 text-white shadow-sm"
            : "text-gray-400 hover:text-sv-600"
        }`}
        aria-label="Switch to English"
      >
        EN
      </button>
      <button
        onClick={() => setLang("es")}
        className={`rounded-full px-3 py-1.5 text-xs font-bold tracking-wide transition-all ${
          lang === "es"
            ? "bg-sv-500 text-white shadow-sm"
            : "text-gray-400 hover:text-sv-600"
        }`}
        aria-label="Cambiar a Español"
      >
        ES
      </button>
    </div>
  );
}
