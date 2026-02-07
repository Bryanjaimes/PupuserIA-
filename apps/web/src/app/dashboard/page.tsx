"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import {
  Bitcoin, TrendingUp, Shield, Zap, ExternalLink,
  ArrowUpRight, ArrowDownRight, ChevronRight,
  Wallet, Lock, Pickaxe, BarChart3, Clock,
  Ship, Landmark, Leaf, Building2, Plane, Heart, School,
  RefreshCw, ChevronDown, Search, AlertTriangle, ChevronUp,
} from "lucide-react";
import { useWorldBankData, useBtcPrice } from "@/hooks/use-indicators";
import { formatValue, WB_INDICATORS } from "@/lib/world-bank";
import {
  STATIC_METRICS, BTC_RESERVE, INVESTMENTS, TIMELINE, SECTIONS,
  type StaticMetric,
} from "@/data/static-metrics";
import type { WBDataPoint } from "@/lib/world-bank";

/* ═══════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════ */

const ICON_MAP: Record<string, React.ReactNode> = {
  Ship: <Ship className="h-5 w-5" />,
  Landmark: <Landmark className="h-5 w-5" />,
  Leaf: <Leaf className="h-5 w-5" />,
  Building2: <Building2 className="h-5 w-5" />,
  Plane: <Plane className="h-5 w-5" />,
  Bitcoin: <Bitcoin className="h-5 w-5" />,
  Heart: <Heart className="h-5 w-5" />,
  School: <School className="h-5 w-5" />,
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  approved: "bg-sv-400/15 text-sv-400 border-sv-400/20",
  construction: "bg-orange-400/15 text-orange-400 border-orange-400/20",
  executed: "bg-gold-400/15 text-gold-400 border-gold-400/20",
  planned: "bg-white/10 text-white/50 border-white/10",
};

const TIMELINE_CAT_COLORS: Record<string, string> = {
  bitcoin: "text-[#f7931a] bg-[#f7931a]/10 border-[#f7931a]/20",
  security: "text-red-400 bg-red-400/10 border-red-400/20",
  infrastructure: "text-sv-400 bg-sv-400/10 border-sv-400/20",
  finance: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
  governance: "text-gold-400 bg-gold-400/10 border-gold-400/20",
  social: "text-purple-400 bg-purple-400/10 border-purple-400/20",
};

function fmtUsd(n: number) {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  return `$${n.toLocaleString()}`;
}

/* Regional comparison benchmarks for key World Bank indicators */
const REGIONAL_BENCH: Record<string, { label: string; value: string }> = {
  "NY.GDP.PCAP.CD": { label: "Central America avg", value: "$5,800" },
  "NY.GDP.MKTP.KD.ZG": { label: "Central America avg", value: "3.2%" },
  "FP.CPI.TOTL.ZG": { label: "Central America avg", value: "4.8%" },
  "SL.UEM.TOTL.ZS": { label: "Central America avg", value: "5.6%" },
  "SP.DYN.LE00.IN": { label: "Central America avg", value: "73.5 yrs" },
  "SE.XPD.TOTL.GD.ZS": { label: "Central America avg", value: "4.2%" },
  "SH.XPD.CHEX.GD.ZS": { label: "Central America avg", value: "6.8%" },
  "EN.ATM.CO2E.KT": { label: "Central America avg", value: "12,000 kt" },
  "IT.NET.USER.ZS": { label: "Central America avg", value: "55%" },
};

/* ═══════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════ */

function Skeleton({ w = "w-20", h = "h-6" }: { w?: string; h?: string }) {
  return <span className={`inline-block ${w} ${h} animate-pulse rounded bg-white/10`} />;
}

function LiveMetricCard({ dp, loading }: { dp: WBDataPoint | undefined; loading: boolean }) {
  if (loading) return (
    <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
      <Skeleton w="w-32" h="h-3" /><div className="mt-2"><Skeleton w="w-16" h="h-7" /></div>
    </div>
  );
  if (!dp) return null;
  const dataYear = parseInt(dp.date, 10);
  const currentYear = new Date().getFullYear();
  const isStale = !isNaN(dataYear) && currentYear - dataYear >= 2;
  const bench = REGIONAL_BENCH[dp.indicator];
  return (
    <div className={`group rounded-xl border bg-white/[0.02] p-4 transition-all hover:bg-white/[0.04] ${isStale ? "border-amber-500/15" : "border-white/5"}`}>
      <div className="mb-1 text-[11px] font-medium leading-tight text-white/45">{dp.label}</div>
      <div className="text-xl font-extrabold text-white">{formatValue(dp.value, dp.unit)}</div>
      {bench && (
        <div className="mt-1 text-[10px] text-white/30">
          <span className="text-white/20">vs</span> {bench.label}: {bench.value}
        </div>
      )}
      <div className="mt-1 flex flex-wrap items-center gap-2 text-[10px] text-white/25">
        <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 font-mono text-emerald-400">LIVE</span>
        <span>{dp.date}</span>
        <span>· World Bank</span>
        {isStale && (
          <span className="flex items-center gap-1 rounded bg-amber-500/10 px-1.5 py-0.5 font-mono text-amber-400">
            <AlertTriangle className="h-2.5 w-2.5" />{currentYear - dataYear}yr old
          </span>
        )}
      </div>
    </div>
  );
}

function StaticMetricCard({ m }: { m: StaticMetric }) {
  return (
    <div className="group rounded-xl border border-white/5 bg-white/[0.02] p-4 transition-all hover:bg-white/[0.04]">
      <div className="mb-1 flex items-start justify-between gap-2">
        <span className="text-[11px] font-medium leading-tight text-white/35">{m.label}</span>
        {m.trend && (
          <span className={`flex-shrink-0 ${m.trendGood ? "text-emerald-400" : "text-red-400"}`}>
            {m.trend === "up" ? <ArrowUpRight className="h-3 w-3" /> : m.trend === "down" ? <ArrowDownRight className="h-3 w-3" /> : <span className="text-white/20">—</span>}
          </span>
        )}
      </div>
      <div className="text-xl font-extrabold text-white">{m.value}</div>
      <div className="mt-1 flex items-center gap-2 text-[10px] text-white/20">
        <span className="rounded bg-white/5 px-1.5 py-0.5 font-mono text-white/30">STATIC</span>
        <span>{m.year}</span>
        {m.sourceUrl ? (
          <a href={m.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline decoration-dotted hover:text-gold-400 transition-colors">
            {m.source}
          </a>
        ) : (
          <span>· {m.source}</span>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════
   MAIN PAGE
   ═══════════════════════════════════════════════════════ */

export default function DashboardPage() {
  const wb = useWorldBankData();
  const btc = useBtcPrice();
  const [search, setSearch] = useState("");
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [timelineFilter, setTimelineFilter] = useState<string | null>(null);

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
  const filteredTimeline = timelineFilter ? TIMELINE.filter((t) => t.category === timelineFilter) : TIMELINE;

  const totalLive = wb.data.size;
  const totalStatic = STATIC_METRICS.length;
  const totalMetrics = totalLive + totalStatic;

  /* NAV index mapping for jump links */
  const parentStartIdx: Record<string, number> = {};
  SECTIONS.forEach((s, i) => { if (!(s.parent in parentStartIdx)) parentStartIdx[s.parent] = i; });

  return (
    <main className="min-h-screen bg-sv-950 pt-20">

      {/* ═══════════ HERO HEADER ═══════════ */}
      <div className="relative overflow-hidden border-b border-white/5">
        <div className="pointer-events-none absolute -top-40 left-1/4 h-[500px] w-[500px] rounded-full bg-[#f7931a]/5 blur-[150px]" />
        <div className="pointer-events-none absolute -bottom-20 right-1/3 h-[400px] w-[400px] rounded-full bg-sv-500/5 blur-[120px]" />

        <div className="relative mx-auto max-w-7xl px-6 py-16 lg:py-20">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-2xl">
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[#f7931a]/20 bg-[#f7931a]/10 px-4 py-1.5 text-xs font-semibold text-[#f7931a]">
                <Zap className="h-3 w-3" />
                Live Data · {totalMetrics} Metrics
              </div>
              <h1 className="mb-3 text-4xl font-extrabold text-white md:text-5xl lg:text-6xl">
                El Salvador<br />
                <span className="bg-gradient-to-r from-gold-400 via-[#f7931a] to-gold-400 bg-clip-text text-transparent">
                  National Dashboard
                </span>
              </h1>
              <p className="max-w-xl text-base text-white/50 lg:text-lg">
                {totalMetrics} indicators across economy, health, education, environment, security,
                governance, and citizen well-being. Live APIs + verified public sources.
              </p>
            </div>

            <div className="flex gap-4 lg:gap-6">
              <div className="rounded-2xl border border-emerald-500/10 bg-emerald-500/5 px-5 py-4 text-center">
                <div className="text-2xl font-extrabold text-emerald-400">{wb.loading ? "..." : totalLive}</div>
                <div className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400/50">Live APIs</div>
              </div>
              <div className="rounded-2xl border border-white/5 bg-white/[0.03] px-5 py-4 text-center">
                <div className="text-2xl font-extrabold text-white">{totalStatic}</div>
                <div className="text-[10px] font-semibold uppercase tracking-wider text-white/30">Verified</div>
              </div>
              <div className="rounded-2xl border border-gold-400/10 bg-gold-400/5 px-5 py-4 text-center">
                <div className="text-2xl font-extrabold text-gold-400">7</div>
                <div className="text-[10px] font-semibold uppercase tracking-wider text-gold-400/50">Categories</div>
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
                className="inline-flex items-center gap-1.5 rounded-full border border-white/8 bg-white/[0.03] px-3.5 py-1.5 text-[11px] font-medium text-white/30 transition-all hover:border-gold-400/30 hover:text-gold-400">
                {src.label}<ExternalLink className="h-2.5 w-2.5" />
              </a>
            ))}
            <button onClick={wb.refetch}
              className="ml-auto inline-flex items-center gap-1.5 rounded-full border border-sv-400/20 bg-sv-400/10 px-3.5 py-1.5 text-[11px] font-semibold text-sv-400 transition-all hover:bg-sv-400/20">
              <RefreshCw className={`h-3 w-3 ${wb.loading ? "animate-spin" : ""}`} /> Refresh
            </button>
          </div>
          {wb.lastUpdated && (
            <div className="mt-2 text-[10px] text-white/40">
              Last fetched: {wb.lastUpdated.toLocaleTimeString()} · BTC updates every 60s · World Bank cached 1hr
            </div>
          )}
        </div>
      </div>

      {/* ═══════════ ERROR BANNER ═══════════ */}
      {wb.error && (
        <div className="border-b border-amber-500/20 bg-amber-500/10">
          <div className="mx-auto flex max-w-7xl items-center gap-3 px-6 py-3">
            <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
            <p className="flex-1 text-xs font-medium text-amber-300">
              World Bank API is unavailable — showing cached data. <span className="text-amber-400/60">{wb.error}</span>
            </p>
            <button onClick={wb.refetch} className="rounded-lg border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-400 transition-all hover:bg-amber-400/20">
              Retry
            </button>
          </div>
        </div>
      )}

      {/* ═══════════ STICKY SEARCH + NAV ═══════════ */}
      <div className="sticky top-16 z-30 border-b border-white/5 bg-sv-950/90 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-6 py-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/20" />
              <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                placeholder={`Search ${totalMetrics} metrics...`}
                className="w-full rounded-xl border border-white/8 bg-white/[0.03] py-2 pl-10 pr-4 text-sm text-white placeholder-white/20 outline-none transition-all focus:border-gold-400/30 focus:bg-white/[0.05]" />
            </div>
            <nav className="flex flex-wrap items-center gap-1 text-[10px]">
              {[
                { num: "I",   label: "Economy",     sid: SECTIONS[0].id },
                { num: "II",  label: "Health",       sid: SECTIONS[3].id },
                { num: "III", label: "Education",    sid: SECTIONS[6].id },
                { num: "IV",  label: "Environment",  sid: SECTIONS[8].id },
                { num: "V",   label: "Stability",    sid: SECTIONS[10].id },
                { num: "VI",  label: "Happiness",    sid: SECTIONS[13].id },
                { num: "VII", label: "Misc",          sid: SECTIONS[14].id },
              ].map((n) => (
                <a key={n.num} href={`#section-${n.sid}`}
                  className="rounded-lg border border-white/5 bg-white/[0.03] px-2.5 py-1.5 font-semibold text-white/40 transition-all hover:bg-white/[0.08] hover:text-white/70">
                  {n.num}. {n.label}
                </a>
              ))}
              <a href="#btc-reserve" className="rounded-lg border border-[#f7931a]/15 bg-[#f7931a]/5 px-2.5 py-1.5 font-semibold text-[#f7931a]/60 transition-all hover:bg-[#f7931a]/10 hover:text-[#f7931a]">₿ BTC</a>
              <a href="#investments" className="rounded-lg border border-gold-400/15 bg-gold-400/5 px-2.5 py-1.5 font-semibold text-gold-400/60 transition-all hover:bg-gold-400/10 hover:text-gold-400">Investments</a>
              <a href="#timeline" className="rounded-lg border border-sv-400/15 bg-sv-400/5 px-2.5 py-1.5 font-semibold text-sv-400/60 transition-all hover:bg-sv-400/10 hover:text-sv-400">Timeline</a>
              <button
                onClick={() => {
                  if (expandedSections.size === SECTIONS.length) {
                    setExpandedSections(new Set());
                  } else {
                    setExpandedSections(new Set(SECTIONS.map((s) => s.id)));
                  }
                }}
                className="ml-1 flex items-center gap-1 rounded-lg border border-white/10 bg-white/[0.05] px-2.5 py-1.5 font-semibold text-white/40 transition-all hover:bg-white/[0.1] hover:text-white/60"
              >
                {expandedSections.size === SECTIONS.length ? (
                  <><ChevronUp className="h-3 w-3" /> Collapse</>
                ) : (
                  <><ChevronDown className="h-3 w-3" /> Expand All</>
                )}
              </button>
            </nav>
          </div>
        </div>
      </div>

      {/* ═══════════ BTC RESERVE ═══════════ */}
      <section className="border-b border-white/5 py-12 lg:py-16" id="btc-reserve">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#f7931a]/15 text-[#f7931a]"><Bitcoin className="h-5 w-5" /></div>
            <div>
              <h2 className="text-2xl font-extrabold text-white">Strategic Bitcoin Reserve</h2>
              <p className="text-xs text-white/30">First nation-state BTC reserve · Buying since {BTC_RESERVE.firstBuy}</p>
            </div>
          </div>

          <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 transition-all hover:bg-white/[0.04]">
              <div className="mb-2 flex items-center justify-between"><span className="text-xs font-medium text-white/35">Total Holdings</span><Wallet className="h-4 w-4 text-[#f7931a]" /></div>
              <div className="text-3xl font-extrabold text-white">{BTC_RESERVE.totalBtc.toLocaleString()}</div>
              <div className="mt-1 text-sm font-semibold text-[#f7931a]">BTC</div>
              <div className="mt-2 text-[11px] text-white/25">+1 BTC/day since {BTC_RESERVE.dailyBuySince}</div>
            </div>

            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 transition-all hover:bg-white/[0.04]">
              <div className="mb-2 flex items-center justify-between"><span className="text-xs font-medium text-white/35">Reserve Value</span><TrendingUp className="h-4 w-4 text-emerald-400" /></div>
              <div className="text-3xl font-extrabold text-white">{btc.loading ? <Skeleton w="w-32" h="h-9" /> : fmtUsd(reserveValue)}</div>
              <div className="mt-1 flex items-center gap-1 text-sm">
                {pnlPercent >= 0
                  ? <span className="flex items-center gap-1 font-semibold text-emerald-400"><ArrowUpRight className="h-3.5 w-3.5" />+{pnlPercent.toFixed(1)}%</span>
                  : <span className="flex items-center gap-1 font-semibold text-red-400"><ArrowDownRight className="h-3.5 w-3.5" />{pnlPercent.toFixed(1)}%</span>}
                <span className="text-white/25">unrealized</span>
              </div>
            </div>

            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 transition-all hover:bg-white/[0.04]">
              <div className="mb-2 flex items-center justify-between"><span className="text-xs font-medium text-white/35">BTC Price (Live)</span><Zap className="h-4 w-4 text-gold-400" /></div>
              <div className="text-3xl font-extrabold text-white">{btc.loading ? <Skeleton w="w-28" h="h-9" /> : `$${btc.price?.toLocaleString()}`}</div>
              <div className="mt-1 flex items-center gap-1 text-sm">
                {btc.change24h >= 0
                  ? <span className="flex items-center gap-1 font-semibold text-emerald-400"><ArrowUpRight className="h-3.5 w-3.5" />+{btc.change24h.toFixed(2)}%</span>
                  : <span className="flex items-center gap-1 font-semibold text-red-400"><ArrowDownRight className="h-3.5 w-3.5" />{btc.change24h.toFixed(2)}%</span>}
                <span className="text-white/25">24h</span>
              </div>
            </div>

            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 transition-all hover:bg-white/[0.04]">
              <div className="mb-2 flex items-center justify-between"><span className="text-xs font-medium text-white/35">Avg Buy Price</span><Shield className="h-4 w-4 text-sv-400" /></div>
              <div className="text-3xl font-extrabold text-white">${BTC_RESERVE.avgBuyPrice.toLocaleString()}</div>
              <div className="mt-1 text-sm">
                <span className="text-white/25">P&L: </span>
                <span className={`font-semibold ${unrealizedPnl >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {unrealizedPnl >= 0 ? "+" : ""}{fmtUsd(Math.abs(unrealizedPnl))}
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-[#f7931a]/10 bg-[#f7931a]/[0.03] p-5">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div><div className="mb-1 text-xs font-medium text-white/30">First Purchase</div><div className="text-sm font-bold text-white">{BTC_RESERVE.firstBuy}</div><div className="text-[11px] text-white/20">200 BTC @ ~$46,000</div></div>
              <div><div className="mb-1 text-xs font-medium text-white/30">Managed By</div><div className="text-sm font-bold text-white">{BTC_RESERVE.managedBy}</div><div className="text-[11px] text-white/20">{BTC_RESERVE.directors}</div></div>
              <div><div className="mb-1 text-xs font-medium text-white/30">IMF Status</div><div className="text-sm font-bold text-white">{BTC_RESERVE.imfStatus}</div><div className="text-[11px] text-white/20">{BTC_RESERVE.imfLoan}</div></div>
              <div><div className="mb-1 text-xs font-medium text-white/30">Daily Purchase</div><div className="text-sm font-bold text-white">1 BTC / day</div><div className="text-[11px] text-white/20">Since {BTC_RESERVE.dailyBuySince}</div></div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ SECURITY HIGHLIGHT ═══════════ */}
      <section className="border-b border-white/5 py-12 lg:py-16" id="security-highlight">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500/15 text-red-400"><Lock className="h-5 w-5" /></div>
            <div>
              <h2 className="text-2xl font-extrabold text-white">Security Transformation</h2>
              <p className="text-xs text-white/30">Plan Control Territorial · State of Exception · CECOT</p>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="row-span-2 flex flex-col justify-between rounded-2xl border border-white/5 bg-white/[0.02] p-6">
              <div>
                <div className="mb-1 text-xs font-medium text-white/35">Homicide Rate (per 100k)</div>
                <div className="mt-3"><div className="text-[11px] text-white/20 line-through">103/100k (2015)</div><div className="text-5xl font-extrabold text-emerald-400">1.7</div><div className="text-sm text-white/30">per 100k (2024)</div></div>
              </div>
              <div className="mt-6">
                <div className="mb-2 flex justify-between text-[10px] text-white/25"><span>2015</span><span>2024</span></div>
                <div className="relative h-3 w-full overflow-hidden rounded-full bg-white/5"><div className="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-red-500 via-orange-400 to-emerald-400 transition-all duration-1000" style={{ width: "98.3%" }} /></div>
                <div className="mt-1 text-center text-xs font-bold text-emerald-400">98.3% reduction</div>
              </div>
            </div>
            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6"><div className="mb-1 text-xs font-medium text-white/35">Gang Arrests</div><div className="text-3xl font-extrabold text-white">94,844+</div><div className="mt-1 text-[11px] text-white/20">State of Exception · 47+ extensions</div></div>
            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6"><div className="mb-1 text-xs font-medium text-white/35">CECOT Prison</div><div className="text-3xl font-extrabold text-white">40,000</div><div className="mt-1 text-[11px] text-white/20">World&apos;s largest · Tecoluca, San Vicente</div></div>
            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6"><div className="mb-1 text-xs font-medium text-white/35">Re-election</div><div className="text-3xl font-extrabold text-gold-400">84.65%</div><div className="mt-1 text-[11px] text-white/20">Feb 2024 — largest in ES history</div></div>
            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6"><div className="mb-1 text-xs font-medium text-white/35">Citizen Safety Perception</div><div className="text-3xl font-extrabold text-sv-400">91%</div><div className="mt-1 text-[11px] text-white/20">Feel safe · CID Gallup 2024</div></div>
          </div>
        </div>
      </section>

      {/* ═══════════ ALL 7 CATEGORIES ═══════════ */}
      {(() => {
        let currentParent = "";
        return filteredSections.map((section) => {
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
            <section key={section.id} id={`section-${section.id}`} className="border-b border-white/5">
              <div className="mx-auto max-w-7xl px-6">
                {showParent && (
                  <div className="pb-2 pt-12 lg:pt-16">
                    <h2 className="text-lg font-extrabold uppercase tracking-wider text-gold-400/40">{section.parent}</h2>
                  </div>
                )}
                <button onClick={() => toggleSection(section.id)}
                  className="flex w-full items-center justify-between py-5 text-left transition-colors hover:text-white">
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{section.icon}</span>
                    <div>
                      <h3 className="text-lg font-bold text-white">{section.title}</h3>
                      <div className="flex items-center gap-2 text-[10px] text-white/25">
                        {filteredLive.length > 0 && <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 font-mono text-emerald-400">{filteredLive.length} LIVE</span>}
                        {filteredStatic.length > 0 && <span className="rounded bg-white/5 px-1.5 py-0.5 font-mono text-white/30">{filteredStatic.length} verified</span>}
                        <span>{totalInSection} metrics</span>
                      </div>
                    </div>
                  </div>
                  <ChevronDown className={`h-5 w-5 text-white/20 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                </button>
                {isExpanded && (
                  <div className="grid gap-3 pb-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {filteredLive.map((dp) => <LiveMetricCard key={dp.indicator} dp={dp} loading={false} />)}
                    {wb.loading && Object.values(WB_INDICATORS).filter((i) => i.section === section.id).map((ind) => (
                      <LiveMetricCard key={ind.code} dp={undefined} loading={true} />
                    ))}
                    {filteredStatic.map((m) => <StaticMetricCard key={m.label} m={m} />)}
                  </div>
                )}
              </div>
            </section>
          );
        });
      })()}

      {/* ═══════════ VOLCANO ENERGY ═══════════ */}
      <section className="border-b border-white/5 py-12 lg:py-16" id="volcano-energy">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-500/15 text-orange-400"><Pickaxe className="h-5 w-5" /></div>
            <div><h2 className="text-2xl font-extrabold text-white">Volcano Energy & BTC Mining</h2><p className="text-xs text-white/30">Geothermal power · Clean energy BTC mining</p></div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6"><div className="text-3xl font-extrabold text-orange-400">204.4 MW</div><div className="mt-1 text-xs text-white/40">Installed geothermal capacity</div><div className="mt-1 text-[11px] text-white/20">Largest in Central America</div></div>
            <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6"><div className="text-3xl font-extrabold text-emerald-400">24%</div><div className="mt-1 text-xs text-white/40">Of national electricity grid</div><div className="mt-1 text-[11px] text-white/20">100% renewable source</div></div>
            <div className="col-span-1 sm:col-span-2 rounded-2xl border border-white/5 bg-white/[0.02] p-6">
              <div className="mb-2 text-xs font-medium text-white/35">Geothermal Plants</div>
              <div className="space-y-2">
                {["Ahuachapán (95 MW)", "Berlín (109.4 MW)"].map((p) => <div key={p} className="flex items-center gap-2"><div className="h-2 w-2 rounded-full bg-orange-400" /><span className="text-sm font-medium text-white/70">{p}</span></div>)}
              </div>
              <div className="mt-3 rounded-xl border border-[#f7931a]/10 bg-[#f7931a]/5 px-4 py-2">
                <div className="flex items-center gap-2"><Bitcoin className="h-4 w-4 text-[#f7931a]" /><span className="text-xs font-semibold text-[#f7931a]">Volcano-powered BTC mining: Active</span></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ MAJOR INVESTMENTS ═══════════ */}
      <section className="border-b border-white/5 py-12 lg:py-16" id="investments">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gold-400/15 text-gold-400"><BarChart3 className="h-5 w-5" /></div>
            <div><h2 className="text-2xl font-extrabold text-white">Major Investments & Deals</h2><p className="text-xs text-white/30">Billions in infrastructure, finance, and conservation</p></div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {INVESTMENTS.map((inv) => (
              <div key={inv.title} className="group rounded-2xl border border-white/5 bg-white/[0.02] p-6 transition-all hover:bg-white/[0.04]">
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/5 text-white/60">{ICON_MAP[inv.iconName] ?? <Building2 className="h-5 w-5" />}</div>
                    <div><h3 className="text-base font-bold text-white">{inv.title}</h3><div className="text-[11px] text-white/25">{inv.partner}</div></div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-extrabold text-gold-400">{inv.amount}</div>
                    <span className={`mt-1 inline-block rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${STATUS_COLORS[inv.status]}`}>{inv.status}</span>
                  </div>
                </div>
                <p className="text-sm leading-relaxed text-white/35">{inv.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ TIMELINE ═══════════ */}
      <section className="py-12 lg:py-16" id="timeline">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sv-400/15 text-sv-400"><Clock className="h-5 w-5" /></div>
            <div><h2 className="text-2xl font-extrabold text-white">Bukele Administration Timeline</h2><p className="text-xs text-white/30">Key policies, milestones, and outcomes since June 2019</p></div>
          </div>

          <div className="mb-6 flex flex-wrap gap-2">
            <button onClick={() => setTimelineFilter(null)}
              className={`rounded-full px-4 py-1.5 text-xs font-semibold transition-all ${!timelineFilter ? "bg-white text-sv-900" : "bg-white/5 text-white/40 hover:bg-white/10"}`}>
              All ({TIMELINE.length})
            </button>
            {Object.entries(TIMELINE_CAT_COLORS).map(([cat, cls]) => {
              const count = TIMELINE.filter((t) => t.category === cat).length;
              return (
                <button key={cat} onClick={() => setTimelineFilter(timelineFilter === cat ? null : cat)}
                  className={`rounded-full border px-4 py-1.5 text-xs font-semibold capitalize transition-all ${timelineFilter === cat ? cls : "border-white/5 bg-white/5 text-white/30 hover:bg-white/10"}`}>
                  {cat} ({count})
                </button>
              );
            })}
          </div>

          <div className="relative">
            <div className="absolute bottom-0 left-5 top-0 w-px bg-white/5" />
            <div className="space-y-1">
              {filteredTimeline.map((item, i) => (
                <div key={i} className="group relative flex gap-4 py-3 pl-1">
                  <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-sv-950 text-base transition-all group-hover:border-gold-400/30 group-hover:bg-white/5">{item.icon}</div>
                  <div className="min-w-0 flex-1 pt-0.5">
                    <div className="mb-0.5 flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-gold-400/60">{item.date}</span>
                      <span className={`rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${TIMELINE_CAT_COLORS[item.category]}`}>{item.category}</span>
                    </div>
                    <h4 className="text-sm font-bold text-white/80 transition-colors group-hover:text-white">{item.title}</h4>
                    <p className="mt-0.5 text-xs leading-relaxed text-white/30">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ BOTTOM CTA ═══════════ */}
      <section className="border-t border-white/5 bg-gradient-to-b from-sv-950 to-[#0a1628] py-16">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="mb-3 text-2xl font-extrabold text-white md:text-3xl">Explore everything on the map</h2>
          <p className="mb-8 text-sm text-white/30">See every government project, Bitcoin landmark, and investment site on our interactive satellite map.</p>
          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link href="/explore" className="group flex items-center gap-2 rounded-2xl bg-white px-8 py-4 font-semibold text-sv-900 shadow-2xl shadow-black/20 transition-all hover:bg-white/95">
              Open Interactive Map<ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link href="/invest" className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-8 py-4 font-semibold text-white backdrop-blur-sm transition-all hover:bg-white/10">
              <Bitcoin className="h-4 w-4 text-[#f7931a]" /> Invest
            </Link>
          </div>
        </div>
      </section>

      {/* ── Source Footer ── */}
      <div className="border-t border-white/5 py-6">
        <div className="mx-auto max-w-7xl px-6 text-center text-[10px] text-white/40">
          {totalMetrics} metrics · {totalLive} live (World Bank API + CoinGecko) · {totalStatic} verified (WHO, UNDP, IMF, IDB, EIU, WEF, Gallup, TI, public records).
          <br />BTC price: 60s refresh. World Bank: 1hr cache. Last verified: Jan 2025.
        </div>
      </div>
    </main>
  );
}
