import { ChevronDown } from "lucide-react";
import { useLanguage } from "@/context/language-context";
import { WB_INDICATORS } from "@/lib/world-bank";
import { SECTIONS } from "@/data/static-metrics";
import type { WBDataPoint } from "@/lib/world-bank";
import type { StaticMetric } from "@/data/static-metrics";
import { LiveMetricCard, StaticMetricCard } from "./metric-cards";

interface CategoryAccordionProps {
  sectionData: Record<string, { live: WBDataPoint[]; static: StaticMetric[] }>;
  searchLower: string;
  expandedSections: Set<string>;
  toggleSection: (id: string) => void;
  wbLoading: boolean;
  filteredSections: readonly (typeof SECTIONS)[number][];
}

export function CategoryAccordion({
  sectionData, searchLower, expandedSections, toggleSection, wbLoading, filteredSections,
}: CategoryAccordionProps) {
  const { t } = useLanguage();

  let currentParent = "";
  return (
    <>
      {filteredSections.map((section) => {
        const sd = sectionData[section.id];
        if (!sd) return null;

        const filteredLive = searchLower ? sd.live.filter((dp) => dp.label.toLowerCase().includes(searchLower)) : sd.live;
        const filteredStatic = searchLower ? sd.static.filter((m) => m.label.toLowerCase().includes(searchLower) || m.value.toLowerCase().includes(searchLower)) : sd.static;
        const totalInSection = filteredLive.length + filteredStatic.length;
        if (searchLower && totalInSection === 0) return null;

        const showParent = section.parent !== currentParent;
        if (showParent) currentParent = section.parent;
        const isExpanded = expandedSections.has(section.id);

        return (
          <section key={section.id} id={`section-${section.id}`} className="border-b border-gray-200">
            <div className="mx-auto max-w-7xl px-6">
              {showParent && (
                <div className="pb-2 pt-12 lg:pt-16">
                  <h2 className="font-serif text-lg font-extrabold uppercase tracking-wider text-gold-500/70">{section.parent}</h2>
                </div>
              )}
              <button onClick={() => toggleSection(section.id)}
                className="flex w-full items-center justify-between py-5 text-left transition-colors hover:text-sv-600">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{section.icon}</span>
                  <div>
                    <h3 className="text-lg font-bold text-sv-950">{section.title}</h3>
                    <div className="flex items-center gap-2 text-[10px] text-gray-400">
                      {filteredLive.length > 0 && <span className="flex items-center gap-1 rounded bg-emerald-50 px-1.5 py-0.5 font-mono text-emerald-600"><span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />{filteredLive.length} {t("dash.live")}</span>}
                      {filteredStatic.length > 0 && <span className="rounded bg-amber-50 px-1.5 py-0.5 font-mono text-amber-600">{filteredStatic.length} {t("dash.hardcoded").toLowerCase()}</span>}
                      <span>{totalInSection} {t("dash.total")}</span>
                    </div>
                  </div>
                </div>
                <ChevronDown className={`h-5 w-5 text-gray-300 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
              </button>
              {isExpanded && (
                <div className="grid gap-3 pb-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {filteredLive.map((dp) => <LiveMetricCard key={dp.indicator} dp={dp} loading={false} />)}
                  {wbLoading && Object.values(WB_INDICATORS).filter((i) => i.section === section.id).map((ind) => (
                    <LiveMetricCard key={ind.code} dp={undefined} loading={true} />
                  ))}
                  {filteredStatic.map((m) => <StaticMetricCard key={m.label} m={m} />)}
                </div>
              )}
            </div>
          </section>
        );
      })}
    </>
  );
}
