"use client";

import { useState } from "react";
import {
  BarChart3, Users, Eye, Search, Map, MessageSquare, Compass,
  Heart, GraduationCap, Utensils, Laptop, Zap, BookOpen,
  Shield, ArrowUpRight, Activity, Globe, TrendingUp, School,
} from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { usePlatformOverview, useImpactDashboard } from "@/hooks/use-dashboard-metrics";

/* ════════════════════════════════════════════════════
   IMPACT & ANALYTICS DASHBOARD
   /dashboard/impact
   ════════════════════════════════════════════════════ */

export default function ImpactDashboardPage() {
  const t = useTranslations("impactDash");
  const [tab, setTab] = useState<"platform" | "impact">("platform");
  const platform = usePlatformOverview(30_000);
  const impact = useImpactDashboard(60_000);

  return (
    <main className="min-h-screen bg-[#0a0a0a] pt-28 pb-20">
      {/* ── Header ── */}
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-2 flex items-center gap-2">
          <Link href="/dashboard" className="text-xs font-medium text-gray-400 hover:text-gold-400 transition">
            ← Dashboard
          </Link>
        </div>
        <div className="mb-1 inline-flex items-center gap-2 rounded border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-sv-500">
          <Activity size={12} />
          {t("liveLabel")}
        </div>
        <h1 className="mt-3 font-serif text-4xl font-black tracking-tight text-white md:text-5xl">
          {t("title")}
        </h1>
        <p className="mt-3 max-w-2xl text-gray-400 leading-relaxed">
          {t("subtitle")}
        </p>

        {/* ── Tab toggle ── */}
        <div className="mt-8 flex gap-1 rounded-lg border border-white/10 bg-[#111] p-1 w-fit">
          <button
            onClick={() => setTab("platform")}
            className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition ${
              tab === "platform"
                ? "bg-[#0a0a0a] text-white/60 shadow-sm"
                : "text-gray-400 hover:text-gray-600"
            }`}
          >
            <BarChart3 size={16} />
            {t("platformTab")}
          </button>
          <button
            onClick={() => setTab("impact")}
            className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition ${
              tab === "impact"
                ? "bg-[#0a0a0a] text-impact-600 shadow-sm"
                : "text-gray-400 hover:text-gray-600"
            }`}
          >
            <Heart size={16} />
            {t("impactTab")}
          </button>
        </div>
      </div>

      {/* ── Content ── */}
      <div className="mx-auto max-w-6xl px-6 mt-10">
        {tab === "platform" ? (
          <PlatformSection t={t} data={platform.data} loading={platform.loading} />
        ) : (
          <ImpactSection t={t} data={impact.data} loading={impact.loading} />
        )}
      </div>
    </main>
  );
}


/* ═══════════════════════════════════════════════════
   PLATFORM ANALYTICS TAB
   ═══════════════════════════════════════════════════ */

function PlatformSection({
  t,
  data,
  loading,
}: {
  t: ReturnType<typeof useTranslations>;
  data: ReturnType<typeof usePlatformOverview>["data"];
  loading: boolean;
}) {
  if (loading) return <LoadingSkeleton />;

  const d = data;

  return (
    <div className="space-y-10">
      {/* ── Realtime row ── */}
      <div>
        <SectionLabel icon={Activity} label={t("platformTitle")} />
        <p className="mb-6 text-sm text-gray-400">{t("platformDesc")}</p>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          <MetricCard
            icon={Users}
            label={t("activeNow")}
            value={d?.activeVisitorsNow ?? 0}
            pulse
          />
          <MetricCard
            icon={Eye}
            label={t("todayViews")}
            value={d?.pageViewsToday ?? 0}
          />
          <MetricCard
            icon={Compass}
            label={t("todaySessions")}
            value={d?.sessionsToday ?? 0}
          />
        </div>
      </div>

      {/* ── Trailing period ── */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricCard
          icon={Users}
          label={t("visitors7d")}
          value={d?.visitors7d ?? 0}
          color="blue"
        />
        <MetricCard
          icon={Users}
          label={t("visitors30d")}
          value={d?.visitors30d ?? 0}
          color="blue"
        />
        <MetricCard
          icon={Eye}
          label={t("pageViews7d")}
          value={d?.pageViews7d ?? 0}
          color="blue"
        />
        <MetricCard
          icon={Activity}
          label={t("avgSession")}
          value={d?.avgSessionDurationSec ? `${Math.round(d.avgSessionDurationSec)}s` : `0 ${t("seconds")}`}
          color="blue"
        />
      </div>

      {/* ── Engagement ── */}
      <div>
        <SectionLabel icon={TrendingUp} label={t("engagementTitle")} />
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          <MetricCard icon={Eye} label={t("propertyViews")} value={d?.propertyViews7d ?? 0} color="indigo" small />
          <MetricCard icon={Search} label={t("searches")} value={d?.propertySearches7d ?? 0} color="indigo" small />
          <MetricCard icon={Compass} label={t("tourViews")} value={d?.tourViews7d ?? 0} color="indigo" small />
          <MetricCard icon={MessageSquare} label={t("conciergeChats")} value={d?.conciergeChats7d ?? 0} color="indigo" small />
          <MetricCard icon={Map} label={t("mapInteractions")} value={d?.mapInteractions7d ?? 0} color="indigo" small />
        </div>
      </div>

      {/* ── Content coverage ── */}
      <div>
        <SectionLabel icon={Globe} label={t("contentTitle")} />
        <div className="grid grid-cols-3 gap-4">
          <MetricCard
            icon={BarChart3}
            label={t("totalListings")}
            value={d?.totalListings?.toLocaleString() ?? "0"}
            color="green"
          />
          <MetricCard
            icon={TrendingUp}
            label={t("aiValuations")}
            value={d?.listingsWithValuation ?? 0}
            color="green"
          />
          <MetricCard
            icon={Map}
            label={t("departments")}
            value={`${d?.departmentsCovered ?? 0}/14`}
            color="green"
          />
        </div>
      </div>

      {/* ── Traffic chart placeholder ── */}
      <div>
        <SectionLabel icon={TrendingUp} label={t("trafficTrend")} />
        {d?.dailyVisitors && d.dailyVisitors.length > 0 ? (
          <MiniBarChart
            data={d.dailyVisitors}
            color="#0047ab"
            label={t("visitors")}
          />
        ) : (
          <EmptyState message={t("noDataYet")} />
        )}
      </div>

      {/* ── Top countries / departments ── */}
      {(d?.topCountries && Object.keys(d.topCountries).length > 0) && (
        <div className="grid gap-6 md:grid-cols-2">
          <RankingList title={t("topCountries")} data={d.topCountries} />
          <RankingList title={t("topDepartments")} data={d?.topDepartments ?? {}} />
        </div>
      )}
    </div>
  );
}


/* ═══════════════════════════════════════════════════
   FOUNDATION IMPACT TAB
   ═══════════════════════════════════════════════════ */

function ImpactSection({
  t,
  data,
  loading,
}: {
  t: ReturnType<typeof useTranslations>;
  data: ReturnType<typeof useImpactDashboard>["data"];
  loading: boolean;
}) {
  if (loading) return <LoadingSkeleton />;

  const d = data;
  const isPreRevenue = !d || d.totalPlatformRevenueUsd === 0;

  return (
    <div className="space-y-10">
      {/* ── Impact hero metrics ── */}
      <div>
        <SectionLabel icon={Heart} label={t("impactTitle")} color="rose" />
        <p className="mb-6 text-sm text-gray-400">{t("impactDesc")}</p>

        {isPreRevenue && (
          <div className="mb-8 rounded-xl border-2 border-dashed border-gold-300 bg-gold-500/10/50 p-6">
            <div className="flex items-start gap-3">
              <div className="mt-0.5 rounded-full bg-gold-100 p-2">
                <Shield size={16} className="text-gold-400" />
              </div>
              <div>
                <h3 className="font-semibold text-gold-800">{t("preRevenue")}</h3>
                <p className="mt-1 text-sm text-gold-400 leading-relaxed">{t("preRevenueDesc")}</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          <MetricCard
            icon={BarChart3}
            label={t("totalRevenue")}
            value={`$${(d?.totalPlatformRevenueUsd ?? 0).toLocaleString()}`}
            color="emerald"
          />
          <MetricCard
            icon={Heart}
            label={t("allocated")}
            value={`$${(d?.foundationAllocationUsd ?? 0).toLocaleString()}`}
            color="rose"
          />
          <MetricCard
            icon={Shield}
            label={t("allocationRate")}
            value={`${d?.allocationRate ?? 17.5}%`}
            color="rose"
          />
        </div>
      </div>

      {/* ── Human impact counters ── */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <ImpactCounter emoji="🎓" label={t("students")} value={d?.studentsReached ?? 0} />
        <ImpactCounter emoji="🍽️" label={t("meals")} value={d?.mealsServed ?? 0} />
        <ImpactCounter emoji="💻" label={t("devices")} value={d?.devicesDeployed ?? 0} />
        <ImpactCounter emoji="🏫" label={t("schools")} value={d?.schoolsActive ?? 0} />
        <ImpactCounter emoji="☀️" label={t("solar")} value={d?.solarInstallations ?? 0} />
        <ImpactCounter emoji="📚" label={t("supplies")} value={d?.supplyKits ?? 0} />
      </div>

      {/* ── Efficiency & transparency ── */}
      <div className="grid grid-cols-3 gap-4">
        <MetricCard
          icon={Shield}
          label={t("efficiency")}
          value={`${d?.fundEfficiencyPct ?? 92}%`}
          color="emerald"
        />
        <MetricCard
          icon={Activity}
          label={t("verified")}
          value={d?.blockchainVerifiedCount ?? 0}
          color="emerald"
        />
        <MetricCard
          icon={GraduationCap}
          label={t("perChild")}
          value="$250"
          color="emerald"
        />
      </div>

      {/* ── Program breakdown ── */}
      {d?.programBreakdown && d.programBreakdown.length > 0 && (
        <div>
          <SectionLabel icon={BookOpen} label={t("programsTitle")} color="rose" />
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
            {d.programBreakdown.map((prog) => (
              <div
                key={prog.program}
                className="rounded-xl border border-white/5 bg-[#0a0a0a] p-4 shadow-sm"
              >
                <div className="mb-2 text-2xl">{prog.emoji}</div>
                <div className="text-sm font-semibold text-white/80">{prog.program}</div>
                <div className="mt-1 text-lg font-bold text-white/60">
                  ${prog.allocatedUsd.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Transparency note ── */}
      <div className="rounded-xl border border-white/5 bg-[#111] p-6">
        <div className="flex items-start gap-3">
          <Shield size={20} className="mt-0.5 text-sv-500" />
          <p className="text-sm leading-relaxed text-gray-500">
            {t("transparencyNote")}
          </p>
        </div>
      </div>
    </div>
  );
}


/* ═══════════════════════════════════════════════════
   REUSABLE COMPONENTS
   ═══════════════════════════════════════════════════ */

function SectionLabel({
  icon: Icon,
  label,
  color = "blue",
}: {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  color?: string;
}) {
  const colors: Record<string, string> = {
    blue: "text-sv-500",
    rose: "text-impact-500",
    green: "text-emerald-500",
  };
  return (
    <div className="mb-4 flex items-center gap-2">
      <Icon size={16} className={colors[color] || colors.blue} />
      <h2 className="text-sm font-bold uppercase tracking-widest text-gray-400">
        {label}
      </h2>
    </div>
  );
}


function MetricCard({
  icon: Icon,
  label,
  value,
  color = "default",
  pulse = false,
  small = false,
}: {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  value: number | string;
  color?: string;
  pulse?: boolean;
  small?: boolean;
}) {
  const colors: Record<string, { bg: string; icon: string; border: string }> = {
    default: { bg: "bg-[#111]", icon: "text-gray-400", border: "border-white/5" },
    blue: { bg: "bg-white/5", icon: "text-sv-500", border: "border-white/10" },
    indigo: { bg: "bg-indigo-50", icon: "text-indigo-500", border: "border-indigo-100" },
    green: { bg: "bg-emerald-50", icon: "text-emerald-500", border: "border-emerald-100" },
    emerald: { bg: "bg-emerald-50", icon: "text-emerald-600", border: "border-emerald-100" },
    rose: { bg: "bg-rose-50", icon: "text-rose-500", border: "border-rose-100" },
  };
  const c = colors[color] || colors.default;

  return (
    <div className={`rounded-xl border ${c.border} ${c.bg} ${small ? "p-3" : "p-5"} transition hover:shadow-sm`}>
      <div className="flex items-center gap-2 mb-1">
        <Icon size={small ? 14 : 16} className={c.icon} />
        {pulse && (
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
            <span className="inline-flex h-2 w-2 rounded-full bg-green-500" />
          </span>
        )}
      </div>
      <div className={`font-bold text-white/90 ${small ? "text-lg" : "text-2xl"} font-serif`}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>
      <div className={`mt-0.5 font-medium text-gray-400 ${small ? "text-[10px]" : "text-xs"} uppercase tracking-wider`}>
        {label}
      </div>
    </div>
  );
}


function ImpactCounter({
  emoji,
  label,
  value,
}: {
  emoji: string;
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-[#0a0a0a] p-4 text-center shadow-sm">
      <div className="mb-1 text-2xl">{emoji}</div>
      <div className="font-serif text-2xl font-bold text-white">
        {value.toLocaleString()}
      </div>
      <div className="mt-1 text-[10px] font-medium uppercase tracking-wider text-gray-400">
        {label}
      </div>
    </div>
  );
}


function MiniBarChart({
  data,
  color,
  label,
}: {
  data: { date: string; value: number }[];
  color: string;
  label: string;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="rounded-xl border border-white/5 bg-[#0a0a0a] p-6">
      <div className="mb-4 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
          {label}
        </span>
        <span className="text-xs text-gray-300">
          {data[0]?.date} → {data[data.length - 1]?.date}
        </span>
      </div>
      <div className="flex items-end gap-[2px] h-24">
        {data.map((d, i) => (
          <div
            key={i}
            className="flex-1 rounded-t-sm transition-all hover:opacity-80"
            style={{
              height: `${(d.value / max) * 100}%`,
              backgroundColor: color,
              opacity: 0.15 + (d.value / max) * 0.85,
              minHeight: "2px",
            }}
            title={`${d.date}: ${d.value}`}
          />
        ))}
      </div>
    </div>
  );
}


function RankingList({
  title,
  data,
}: {
  title: string;
  data: Record<string, number>;
}) {
  const sorted = Object.entries(data).sort(([, a], [, b]) => b - a).slice(0, 10);
  const max = sorted[0]?.[1] || 1;

  return (
    <div className="rounded-xl border border-white/5 bg-[#0a0a0a] p-6">
      <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-gray-400">{title}</h3>
      <div className="space-y-2">
        {sorted.map(([key, val]) => (
          <div key={key} className="flex items-center gap-3">
            <span className="w-16 text-xs font-medium text-gray-600 truncate">{key}</span>
            <div className="flex-1 h-2 rounded-full bg-[#1a1a1a]">
              <div
                className="h-2 rounded-full bg-sv-400 transition-all"
                style={{ width: `${(val / max) * 100}%` }}
              />
            </div>
            <span className="text-xs font-semibold text-gray-500 w-10 text-right">{val}</span>
          </div>
        ))}
      </div>
    </div>
  );
}


function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, j) => (
            <div key={j} className="h-24 rounded-xl bg-[#1a1a1a]" />
          ))}
        </div>
      ))}
    </div>
  );
}


function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-xl border-2 border-dashed border-white/10 bg-[#111] p-12 text-center">
      <BarChart3 size={32} className="mx-auto mb-3 text-gray-300" />
      <p className="text-sm text-gray-400">{message}</p>
    </div>
  );
}
