import { AlertTriangle, ArrowDownRight, ArrowUpRight } from "lucide-react";
import { formatValue } from "@/lib/world-bank";
import type { WBDataPoint } from "@/lib/world-bank";
import type { StaticMetric } from "@/data/static-metrics";
import { REGIONAL_BENCH } from "./helpers";

/* ── Skeleton ── */

export function Skeleton({ w = "w-20", h = "h-6" }: { w?: string; h?: string }) {
  return <span className={`inline-block ${w} ${h} animate-pulse rounded bg-gray-200`} />;
}

/* ── Live Metric Card ── */

export function LiveMetricCard({ dp, loading }: { dp: WBDataPoint | undefined; loading: boolean }) {
  if (loading) return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <Skeleton w="w-32" h="h-3" /><div className="mt-2"><Skeleton w="w-16" h="h-7" /></div>
    </div>
  );
  if (!dp) return null;
  const dataYear = parseInt(dp.date, 10);
  const currentYear = new Date().getFullYear();
  const isStale = !isNaN(dataYear) && currentYear - dataYear >= 4;
  const bench = REGIONAL_BENCH[dp.indicator];
  return (
    <div className={`group relative overflow-hidden rounded-lg border bg-white p-4 pl-5 transition-all hover:shadow-md ${isStale ? "border-amber-200" : "border-gray-200"}`}>
      <div className="absolute inset-y-0 left-0 w-1 bg-emerald-500" />
      <div className="mb-1 text-[11px] font-medium leading-tight text-gray-500">{dp.label}</div>
      <div className="text-xl font-extrabold text-sv-950">{formatValue(dp.value, dp.unit)}</div>
      {bench && (
        <div className="mt-1 text-[10px] text-gray-400">
          <span className="text-gray-300">vs</span> {bench.label}: {bench.value}
        </div>
      )}
      <div className="mt-1 flex flex-wrap items-center gap-2 text-[10px] text-gray-400">
        <span className="flex items-center gap-1 rounded bg-emerald-50 px-1.5 py-0.5 font-mono text-emerald-600">
          <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />LIVE
        </span>
        <span>{dp.date}</span>
        <span>· World Bank API</span>
        {isStale && (
          <span className="flex items-center gap-1 rounded bg-amber-50 px-1.5 py-0.5 font-mono text-amber-600">
            <AlertTriangle className="h-2.5 w-2.5" />{currentYear - dataYear}yr old
          </span>
        )}
      </div>
    </div>
  );
}

/* ── Static Metric Card ── */

export function StaticMetricCard({ m }: { m: StaticMetric }) {
  const dataYear = parseInt(m.year, 10);
  const currentYear = new Date().getFullYear();
  const isStale = !isNaN(dataYear) && currentYear - dataYear >= 4;
  return (
    <div className={`group relative overflow-hidden rounded-lg border bg-white p-4 pl-5 transition-all hover:shadow-md ${isStale ? "border-amber-200" : "border-gray-200"}`}>
      <div className="absolute inset-y-0 left-0 w-1 bg-amber-400" />
      <div className="mb-1 flex items-start justify-between gap-2">
        <span className="text-[11px] font-medium leading-tight text-gray-500">{m.label}</span>
        {m.trend && (
          <span className={`flex-shrink-0 ${m.trendGood ? "text-emerald-600" : "text-red-500"}`}>
            {m.trend === "up" ? <ArrowUpRight className="h-3 w-3" /> : m.trend === "down" ? <ArrowDownRight className="h-3 w-3" /> : <span className="text-gray-300">—</span>}
          </span>
        )}
      </div>
      <div className="text-xl font-extrabold text-sv-950">{m.value}</div>
      <div className="mt-1 flex flex-wrap items-center gap-2 text-[10px] text-gray-400">
        <span className="rounded bg-amber-50 px-1.5 py-0.5 font-mono text-amber-600">HARDCODED</span>
        <span>{m.year}</span>
        {m.sourceUrl ? (
          <a href={m.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline decoration-dotted hover:text-sv-500 transition-colors">
            {m.source}
          </a>
        ) : (
          <span>· {m.source}</span>
        )}
        {isStale && (
          <span className="flex items-center gap-1 rounded bg-amber-50 px-1.5 py-0.5 font-mono text-amber-600">
            <AlertTriangle className="h-2.5 w-2.5" />{currentYear - dataYear}yr old
          </span>
        )}
      </div>
    </div>
  );
}
