"use client";

import { Zap, ExternalLink, RefreshCw, AlertTriangle } from "lucide-react";
import { useLanguage } from "@/context/language-context";

interface DashboardHeroProps {
  totalMetrics: number;
  totalLive: number;
  totalStatic: number;
  wbLoading: boolean;
  wbRefetch: () => void;
  wbLastUpdated: Date | null;
  wbError: string | null;
}

export function DashboardHero({
  totalMetrics,
  totalLive,
  totalStatic,
  wbLoading,
  wbRefetch,
  wbLastUpdated,
  wbError,
}: DashboardHeroProps) {
  const { t } = useLanguage();

  return (
    <>
      {/* ═══════════ HERO HEADER ═══════════ */}
      <div className="border-b border-gray-200 bg-[#f8f9fc]">
        <div className="mx-auto max-w-7xl px-6 py-16 lg:py-20">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-2xl">
              <div className="mb-3 inline-flex items-center gap-2 rounded-md border border-orange-200 bg-orange-50 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-orange-700">
                <Zap className="h-3 w-3" />
                {t("dash.liveData")} · {totalMetrics} {t("dash.metrics")}
              </div>
              <h1 className="mb-3 font-serif text-4xl font-extrabold text-sv-950 md:text-5xl lg:text-6xl">
                {t("dash.title1")}<br />
                <span className="text-gold-500">{t("dash.title2")}</span>
              </h1>
              <p className="max-w-xl text-base text-gray-500 lg:text-lg">
                {totalMetrics} {t("dash.desc")}
              </p>
            </div>

            <div className="flex gap-4 lg:gap-6">
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-5 py-4 text-center">
                <div className="flex items-center justify-center gap-2 text-2xl font-extrabold text-emerald-700">
                  <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
                  {wbLoading ? "..." : totalLive}
                </div>
                <div className="text-[10px] font-semibold uppercase tracking-wider text-emerald-600/60">{t("dash.liveApi")}</div>
              </div>
              <div className="rounded-lg border border-amber-200 bg-amber-50 px-5 py-4 text-center">
                <div className="text-2xl font-extrabold text-amber-700">{totalStatic}</div>
                <div className="text-[10px] font-semibold uppercase tracking-wider text-amber-600/60">{t("dash.hardcoded")}</div>
              </div>
              <div className="rounded-lg border border-gray-200 bg-white px-5 py-4 text-center">
                <div className="text-2xl font-extrabold text-sv-600">7</div>
                <div className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">{t("dash.categories")}</div>
              </div>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap items-center gap-2">
            {[
              { label: "World Bank", url: "https://data.worldbank.org/country/el-salvador" },
              { label: "bitcoin.gob.sv", url: "https://bitcoin.gob.sv" },
              { label: "CoinGecko", url: "https://www.coingecko.com" },
              { label: "WHO", url: "https://www.who.int/data/gho" },
              { label: "UNDP", url: "https://hdr.undp.org" },
              { label: "IMF", url: "https://www.imf.org/en/Countries/SLV" },
            ].map((src) => (
              <a key={src.label} href={src.url} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3.5 py-1.5 text-[11px] font-medium text-gray-400 transition-all hover:border-sv-300 hover:text-sv-600">
                {src.label}<ExternalLink className="h-2.5 w-2.5" />
              </a>
            ))}
            <button onClick={wbRefetch}
              className="ml-auto inline-flex items-center gap-1.5 rounded-md border border-sv-200 bg-sv-50 px-3.5 py-1.5 text-[11px] font-semibold text-sv-600 transition-all hover:bg-sv-100">
              <RefreshCw className={`h-3 w-3 ${wbLoading ? "animate-spin" : ""}`} /> {t("dash.refresh")}
            </button>
          </div>
          {wbLastUpdated && (
            <div className="mt-2 text-[10px] text-gray-400">
              {t("dash.lastFetched")} {wbLastUpdated.toLocaleTimeString()} · {t("dash.btcCache")}
            </div>
          )}
        </div>
      </div>

      {/* ═══════════ ERROR BANNER ═══════════ */}
      {wbError && (
        <div className="border-b border-amber-200 bg-amber-50">
          <div className="mx-auto flex max-w-7xl items-center gap-3 px-6 py-3">
            <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600" />
            <p className="flex-1 text-xs font-medium text-amber-700">
              {t("dash.wbUnavailable")} <span className="text-amber-500">{wbError}</span>
            </p>
            <button onClick={wbRefetch} className="rounded-md border border-amber-300 bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700 transition-all hover:bg-amber-200">
              {t("dash.retry")}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
