"use client";

import { useState, useMemo } from "react";
import { useWorldBankData, useBtcPrice } from "@/hooks/use-indicators";
import { WB_INDICATORS } from "@/lib/world-bank";
import {
  STATIC_METRICS, BTC_RESERVE, SECTIONS,
  type StaticMetric,
} from "@/data/static-metrics";
import type { WBDataPoint } from "@/lib/world-bank";

/* ── Composable sections ── */
import { DashboardHero } from "./_components/dashboard-hero";
import { StickyNav } from "./_components/sticky-nav";
import { BtcReserveSection } from "./_components/btc-reserve-section";
import { SecuritySection } from "./_components/security-section";
import { CategoryAccordion } from "./_components/category-accordion";
import { VolcanoEnergySection } from "./_components/volcano-energy-section";
import { InvestmentsSection } from "./_components/investments-section";
import { TimelineSection } from "./_components/timeline-section";
import { RealtimeFeedsSection } from "./_components/realtime-feeds-section";
import { CoverageGapBanner } from "./_components/coverage-gap-banner";
import { BottomCta } from "./_components/bottom-cta";

/* ═══════════════════════════════════════════════════════
   MAIN PAGE — thin orchestrator
   ═══════════════════════════════════════════════════════ */

export default function DashboardPage() {
  const wb = useWorldBankData();
  const btc = useBtcPrice();
  const [search, setSearch] = useState("");
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  /* ── Derived data ── */
  const sectionData = useMemo(() => {
    const map: Record<string, { live: WBDataPoint[]; static: StaticMetric[] }> = {};
    SECTIONS.forEach((s) => { map[s.id] = { live: [], static: [] }; });

    for (const [key, dp] of wb.data.entries()) {
      const ind = WB_INDICATORS[key];
      if (ind && map[ind.section]) map[ind.section].live.push(dp);
    }
    for (const m of STATIC_METRICS) {
      if (map[m.section]) map[m.section].static.push(m);
    }
    return map;
  }, [wb.data]);

  const searchLower = search.toLowerCase();
  const filteredSections = useMemo(() => {
    if (!searchLower) return SECTIONS;
    return SECTIONS.filter((s) => {
      const sd = sectionData[s.id];
      if (!sd) return false;
      const liveMatch = sd.live.some((dp) => dp.label.toLowerCase().includes(searchLower));
      const staticMatch = sd.static.some((m) => m.label.toLowerCase().includes(searchLower) || m.value.toLowerCase().includes(searchLower));
      return liveMatch || staticMatch || s.title.toLowerCase().includes(searchLower);
    });
  }, [searchLower, sectionData]);

  const toggleSection = (id: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const reserveValue = btc.price ? BTC_RESERVE.totalBtc * btc.price : 0;
  const unrealizedPnl = btc.price ? (btc.price - BTC_RESERVE.avgBuyPrice) * BTC_RESERVE.totalBtc : 0;
  const pnlPercent = btc.price ? ((btc.price - BTC_RESERVE.avgBuyPrice) / BTC_RESERVE.avgBuyPrice) * 100 : 0;

  const totalLive = wb.data.size;
  const totalStatic = STATIC_METRICS.length;
  const totalMetrics = totalLive + totalStatic;

  return (
    <main className="min-h-screen bg-white pt-28">
      <DashboardHero
        totalMetrics={totalMetrics}
        totalLive={totalLive}
        totalStatic={totalStatic}
        wbLoading={wb.loading}
        wbRefetch={wb.refetch}
        wbLastUpdated={wb.lastUpdated}
        wbError={wb.error}
      />

      <StickyNav
        search={search}
        setSearch={setSearch}
        totalMetrics={totalMetrics}
        expandedSections={expandedSections}
        setExpandedSections={setExpandedSections}
      />

      <BtcReserveSection
        btcLoading={btc.loading}
        btcPrice={btc.price}
        btcChange24h={btc.change24h}
        reserveValue={reserveValue}
        unrealizedPnl={unrealizedPnl}
        pnlPercent={pnlPercent}
      />

      <RealtimeFeedsSection />

      <SecuritySection />

      <CategoryAccordion
        sectionData={sectionData}
        searchLower={searchLower}
        expandedSections={expandedSections}
        toggleSection={toggleSection}
        wbLoading={wb.loading}
        filteredSections={filteredSections}
      />

      <VolcanoEnergySection />

      <InvestmentsSection />

      <TimelineSection />

      <CoverageGapBanner />

      <BottomCta
        totalMetrics={totalMetrics}
        totalLive={totalLive}
        totalStatic={totalStatic}
      />
    </main>
  );
}
