"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
  MapPin,
  Building2,
  ChevronRight,
  Loader2,
  Globe,
  Compass,
  BookOpen,
} from "lucide-react";
import { DEPARTMENT_INFO } from "@/data/department-info";

/* ═══════════════════════════════════════════════════════
   Explore Page — /explore
   Interactive satellite map of El Salvador with department
   markers, info cards & history, and property counts.
   ═══════════════════════════════════════════════════════ */

const PropertyExplorerMap = dynamic(
  () => import("@/components/property-explorer-map"),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full w-full items-center justify-center bg-sv-950">
        <Loader2 className="h-8 w-8 animate-spin text-white/40" />
      </div>
    ),
  },
);

// ── Per-department accent colour ─────────────────────

const COLORS: Record<string, string> = {
  "San Salvador": "#0047ab",
  "La Libertad": "#059669",
  "Santa Ana": "#7c3aed",
  "San Miguel": "#dc2626",
  Sonsonate: "#0891b2",
  "La Paz": "#ca8a04",
  Usulután: "#16a34a",
  Ahuachapán: "#ea580c",
  Chalatenango: "#2563eb",
  "San Vicente": "#9333ea",
  Cuscatlán: "#0d9488",
  "La Unión": "#e11d48",
  Morazán: "#4f46e5",
  Cabañas: "#65a30d",
};

function fmt(n: number | null) {
  if (!n) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

// ── Types ────────────────────────────────────────────

interface DepartmentData {
  name: string;
  slug: string;
  count: number;
  avg_price: number | null;
  center: [number, number] | null;
  municipalities: { name: string; slug: string; count: number }[];
}

// ── Page ─────────────────────────────────────────────

export default function ExplorePage() {
  const router = useRouter();
  const [departments, setDepartments] = useState<DepartmentData[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/properties/departments")
      .then((r) => r.json())
      .then((data) => {
        setDepartments(data.departments);
        setTotal(data.total);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  /* Map markers – one per department */
  const markers = departments
    .filter((d) => d.center)
    .map((d) => ({
      lat: d.center![0],
      lng: d.center![1],
      label: d.name,
      sub: `${d.count} listings`,
      color: COLORS[d.name] || "#0047ab",
      size: "lg" as const,
    }));

  const handleMarkerClick = (idx: number) => {
    const dept = departments.filter((d) => d.center)[idx];
    if (dept) router.push(`/explore/${dept.slug}`);
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-sv-950 via-sv-900 to-sv-950 pt-20 animate-[fadeIn_0.5s_ease-out]">
      {/* ── Header ─────────────────────────────────── */}
      <div className="px-6 pt-10 pb-6">
        <div className="mx-auto max-w-7xl">
          <div className="flex items-center gap-2 text-sm text-white/50">
            <Compass className="h-4 w-4" />
            Explore El Salvador
          </div>
          <h1 className="mt-3 text-4xl font-extrabold text-white md:text-5xl">
            Discover Every Department
          </h1>
          <p className="mt-2 flex items-center gap-2 text-base text-white/50">
            <Globe className="h-4 w-4" />
            {total.toLocaleString()} properties across all 14 departments — click a marker or card to explore.
          </p>
        </div>
      </div>

      {/* ── Map (contained card) ───────────────────── */}
      <div className="mx-auto max-w-7xl px-6 pb-10">
        <div className="relative overflow-hidden rounded-2xl border border-white/10 shadow-2xl" style={{ height: 400 }}>
          {!loading && markers.length > 0 && (
            <PropertyExplorerMap
              center={[13.72, -88.9]}
              zoom={8}
              markers={markers}
              onMarkerClick={handleMarkerClick}
              className="h-full w-full"
            />
          )}
          {loading && (
            <div className="flex h-full w-full items-center justify-center bg-sv-900">
              <Loader2 className="h-10 w-10 animate-spin text-white/30" />
            </div>
          )}
        </div>
      </div>

      {/* ── Department Grid ────────────────────────── */}
      <section className="mx-auto max-w-7xl px-6 pb-24">
        <h2 className="mb-6 text-lg font-bold text-white/80 tracking-wide flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-gold-400" />
          Choose a Department
        </h2>

        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 14 }).map((_, i) => (
              <div key={i} className="h-56 animate-pulse rounded-2xl bg-white/5" />
            ))}
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {departments.map((dept) => {
              const info = DEPARTMENT_INFO[dept.name];
              return (
                <Link
                  key={dept.slug}
                  href={`/explore/${dept.slug}`}
                  className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:border-white/20 hover:bg-white/10 hover:shadow-2xl"
                >
                  {/* Accent bar */}
                  <div
                    className="absolute left-0 top-0 h-1 w-full transition-all duration-300 group-hover:h-1.5"
                    style={{ background: COLORS[dept.name] || "#0047ab" }}
                  />

                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-white transition-colors group-hover:text-gold-300">
                        {info?.emoji || "📍"} {dept.name}
                      </h3>
                      <div className="mt-1 flex items-center gap-1.5 text-sm text-white/50">
                        <Building2 className="h-3.5 w-3.5" />
                        {dept.count} {dept.count === 1 ? "property" : "properties"}
                      </div>
                    </div>
                    <ChevronRight className="h-5 w-5 text-white/20 transition-all group-hover:translate-x-1 group-hover:text-white/60" />
                  </div>

                  {/* Brief summary from department-info */}
                  {info && (
                    <p className="mt-3 text-xs leading-relaxed text-white/40 line-clamp-3 group-hover:text-white/60 transition-colors">
                      {info.summary}
                    </p>
                  )}

                  <div className="mt-4 flex items-end justify-between">
                    <div>
                      <div className="text-[11px] font-medium uppercase tracking-wider text-white/30">
                        Avg. Price
                      </div>
                      <div className="text-sm font-semibold text-white/80">
                        {fmt(dept.avg_price)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-[11px] font-medium uppercase tracking-wider text-white/30">
                        Municipios
                      </div>
                      <div className="flex items-center gap-1 text-sm font-semibold text-white/80">
                        <MapPin className="h-3 w-3" />
                        {dept.municipalities.length}
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}
