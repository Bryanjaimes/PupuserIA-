"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { NextIntlClientProvider } from "next-intl";

import enMessages from "../../messages/en.json";
import esMessages from "../../messages/es.json";

export type Locale = "en" | "es";

const messages: Record<Locale, typeof enMessages> = {
  en: enMessages,
  es: esMessages,
};

interface LanguageContextType {
  locale: Locale;
  setLocale: (l: Locale) => void;
}

const LanguageContext = createContext<LanguageContextType>({
  locale: "en",
  setLocale: () => {},
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  /* Restore persisted language */
  useEffect(() => {
    const saved = localStorage.getItem("pupuseria-lang") as Locale | null;
    if (saved === "en" || saved === "es") setLocaleState(saved);
  }, []);

  /* Update <html lang> whenever language changes */
  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("pupuseria-lang", l);
  }, []);

  return (
    <LanguageContext.Provider value={{ locale, setLocale }}>
      <NextIntlClientProvider locale={locale} messages={messages[locale]}>
        {children}
      </NextIntlClientProvider>
    </LanguageContext.Provider>
  );
}

/** Access the current locale and toggle function (for the language toggle button). */
export const useLocaleContext = () => useContext(LanguageContext);
