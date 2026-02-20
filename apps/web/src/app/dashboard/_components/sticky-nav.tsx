"use client";

import { Search, ChevronDown, ChevronUp } from "lucide-react";
import { useTranslations } from "next-intl";
import { SECTIONS } from "@/data/static-metrics";

interface StickyNavProps {
  search: string;
  setSearch: (v: string) => void;
  totalMetrics: number;
  expandedSections: Set<string>;
  setExpandedSections: (v: Set<string>) => void;
}

export function StickyNav({
  search,
  setSearch,
  totalMetrics,
  expandedSections,
  setExpandedSections,
}: StickyNavProps) {
  const t = useTranslations();

  return (
    <div className="sticky top-24 z-30 border-b border-white/10 bg-black/95 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-6 py-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-300" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={`${t("dash.searchPlaceholder")} ${totalMetrics} ${t("dash.metrics").toLowerCase()}...`}
              className="w-full rounded-md border border-white/10 bg-[#0a0a0a] py-2 pl-10 pr-4 text-sm text-white placeholder-gray-400 outline-none transition-all focus:border-sv-400 focus:ring-1 focus:ring-sv-400"
            />
          </div>
          <nav className="flex flex-wrap items-center gap-1 text-[10px]">
            {[
              { num: "I",   label: t("dash.economy"),    sid: SECTIONS[0]?.id },
              { num: "II",  label: t("dash.health"),     sid: SECTIONS[3]?.id },
              { num: "III", label: t("dash.education"),  sid: SECTIONS[6]?.id },
              { num: "IV",  label: t("dash.environment"),sid: SECTIONS[8]?.id },
              { num: "V",   label: t("dash.stability"),  sid: SECTIONS[10]?.id },
              { num: "VI",  label: t("dash.happiness"),  sid: SECTIONS[13]?.id },
              { num: "VII", label: t("dash.misc"),       sid: SECTIONS[14]?.id },
            ].map((n) => (
              <a key={n.num} href={`#section-${n.sid}`}
                className="rounded-md border border-white/10 bg-[#0a0a0a] px-2.5 py-1.5 font-semibold text-gray-500 transition-all hover:border-sv-300 hover:text-sv-400">
                {n.num}. {n.label}
              </a>
            ))}
            <a href="#btc-reserve" className="rounded-md border border-orange-200 bg-orange-50 px-2.5 py-1.5 font-semibold text-orange-600 transition-all hover:bg-orange-100">₿ BTC</a>
            <a href="#investments" className="rounded-md border border-gold-200 bg-gold-500/10 px-2.5 py-1.5 font-semibold text-gold-400 transition-all hover:bg-gold-100">{t("dash.investmentsTitle").split(" ")[0]}</a>
            <a href="#timeline" className="rounded-md border border-white/10 bg-white/5 px-2.5 py-1.5 font-semibold text-sv-400 transition-all hover:bg-white/10">{t("dash.timelineTitle").split(" ").slice(-1)[0]}</a>
            <button
              onClick={() => {
                if (expandedSections.size === SECTIONS.length) {
                  setExpandedSections(new Set());
                } else {
                  setExpandedSections(new Set(SECTIONS.map((s) => s.id)));
                }
              }}
              className="ml-1 flex items-center gap-1 rounded-md border border-white/10 bg-[#111] px-2.5 py-1.5 font-semibold text-gray-500 transition-all hover:bg-white/10 hover:text-white/70"
            >
              {expandedSections.size === SECTIONS.length ? (
                <><ChevronUp className="h-3 w-3" /> {t("dash.collapse")}</>
              ) : (
                <><ChevronDown className="h-3 w-3" /> {t("dash.expandAll")}</>
              )}
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
}
