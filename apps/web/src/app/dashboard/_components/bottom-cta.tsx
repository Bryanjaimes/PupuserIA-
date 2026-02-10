"use client";

import Link from "next/link";
import { Bitcoin, ChevronRight } from "lucide-react";
import { useLanguage } from "@/context/language-context";

interface BottomCtaProps {
  totalMetrics: number;
  totalLive: number;
  totalStatic: number;
}

export function BottomCta({ totalMetrics, totalLive, totalStatic }: BottomCtaProps) {
  const { t } = useLanguage();

  return (
    <>
      {/* ═══════════ BOTTOM CTA ═══════════ */}
      <section className="border-t border-gray-200 bg-sv-950 py-16">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="mb-3 font-serif text-2xl font-extrabold text-white md:text-3xl">{t("dash.exploreMapCta")}</h2>
          <p className="mb-8 text-sm text-white/50">{t("dash.exploreMapDesc")}</p>
          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link href="/explore" className="group flex items-center gap-2 rounded-md bg-white px-8 py-4 font-semibold text-sv-950 transition-all hover:bg-gray-100">
              {t("dash.openMap")}<ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link href="/invest" className="flex items-center gap-2 rounded-md border border-white/20 px-8 py-4 font-semibold text-white transition-all hover:bg-white/10">
              <Bitcoin className="h-4 w-4 text-[#f7931a]" /> {t("dash.investBtn")}
            </Link>
          </div>
        </div>
      </section>

      {/* ── Source Footer ── */}
      <div className="border-t border-gray-200 bg-[#f8f9fc] py-6">
        <div className="mx-auto max-w-7xl px-6 text-center text-[10px] text-gray-400">
          {totalMetrics} {t("dash.metrics").toLowerCase()} · <span className="text-emerald-600">{totalLive} {t("dash.live")}</span> (World Bank API + CoinGecko) · <span className="text-amber-600">{totalStatic} {t("dash.hardcoded").toLowerCase()}</span> (WHO, UNDP, IMF, IDB, EIU, WEF, Gallup, TI).
          <br />BTC price: 60s refresh. World Bank: 1hr cache. Hardcoded values: update in <span className="font-mono text-gray-500">static-metrics.ts</span>
        </div>
      </div>
    </>
  );
}
