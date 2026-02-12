"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import dynamic from "next/dynamic";
import {
  MapPin,
  Building2,
  ChevronRight,
  ArrowLeft,
  Loader2,
  Star,
  TrendingUp,
  BookOpen,
  Mountain,
  Users,
  Landmark,
} from "lucide-react";
import { departmentFromSlug, toSlug } from "@/lib/property-slugs";
import { DEPARTMENT_LABELS } from "@/data/el-salvador-border";
import { getDepartmentInfo, type DepartmentInfo } from "@/data/department-info";

/* ═══════════════════════════════════════════════════════
   Department Detail — /explore/[department]
   History, highlights, zoomed map with property dots,
   and a grid of municipality cards.
   ═══════════════════════════════════════════════════════ */

const PropertyExplorerMap = dynamic(
  () => import("@/components/property-explorer-map"),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full w-full items-center justify-center bg-sv-100">
        <Loader2 className="h-8 w-8 animate-spin text-sv-400" />
      </div>
    ),
  },
);

// ── Helpers ──────────────────────────────────────────

function fmt(n: number | null) {
  if (!n) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

interface Property {
  id: string;
  title: string;
  municipio: string;
  price_usd: number | null;
  latitude: number;
  longitude: number;
  thumbnail_url: string | null;
  images: string[];
  is_featured: boolean;
  property_type: string;
  bedrooms: number | null;
  bathrooms: number | null;
  area_m2: number | null;
}

interface MuniAgg {
  name: string;
  slug: string;
  count: number;
  avg_price: number | null;
  featured: number;
  lat: number;
  lng: number;
  sample: string | null;
}

// ── Page ─────────────────────────────────────────────

export default function DepartmentPage() {
  const params = useParams<{ department: string }>();
  const router = useRouter();
  const deptSlug = params.department;
  const deptName = departmentFromSlug(deptSlug);
  const deptInfo = deptName ? getDepartmentInfo(deptName) : undefined;

  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!deptName) return;
    fetch(
      `/api/properties?department=${encodeURIComponent(deptName)}&page_size=600`,
    )
      .then((r) => r.json())
      .then((data) => {
        setProperties(data.results);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [deptName]);

  /* Aggregate municipalities */
  const municipalities = useMemo<MuniAgg[]>(() => {
    const map = new Map<
      string,
      { count: number; prices: number[]; featured: number; lat: number; lng: number; sample: string | null }
    >();
    for (const p of properties) {
      const name = p.municipio || "Other";
      if (!map.has(name))
        map.set(name, { count: 0, prices: [], featured: 0, lat: 0, lng: 0, sample: null });
      const m = map.get(name)!;
      m.count++;
      if (p.price_usd && p.price_usd > 0) m.prices.push(p.price_usd);
      if (p.is_featured) m.featured++;
      if (p.latitude && p.longitude) {
        m.lat = p.latitude;
        m.lng = p.longitude;
      }
      if (!m.sample && (p.thumbnail_url || p.images?.[0]))
        m.sample = p.thumbnail_url || p.images[0];
    }
    return Array.from(map.entries())
      .map(([name, m]) => ({
        name,
        slug: toSlug(name),
        count: m.count,
        avg_price: m.prices.length
          ? Math.round(m.prices.reduce((a, b) => a + b, 0) / m.prices.length)
          : null,
        featured: m.featured,
        lat: m.lat,
        lng: m.lng,
        sample: m.sample,
      }))
      .sort((a, b) => b.count - a.count);
  }, [properties]);

  /* Department center for the map */
  const deptLabel = DEPARTMENT_LABELS.find((l) => l.name === deptName);
  const mapCenter: [number, number] = deptLabel
    ? [deptLabel.center[1], deptLabel.center[0]]
    : [13.7, -88.9];

  /* Map markers – one per municipality */
  const markers = municipalities
    .filter((m) => m.lat && m.lng)
    .map((m) => ({
      lat: m.lat,
      lng: m.lng,
      label: m.name,
      sub: `${m.count}`,
      color: "#0047ab",
      size: "md" as const,
    }));

  /* Navigate to municipality */
  const handleMarkerClick = (idx: number) => {
    const muni = municipalities.filter((m) => m.lat && m.lng)[idx];
    if (muni) router.push(`/explore/${deptSlug}/${muni.slug}`);
  };

  if (!deptName) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white pt-20">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-sv-900">Department not found</h1>
          <Link href="/explore" className="mt-4 inline-block text-sm text-gold-600 hover:underline">
            ← Back to all departments
          </Link>
        </div>
      </main>
    );
  }

  const totalPrice = properties.filter((p) => p.price_usd).length;
  const avgPrice = totalPrice
    ? Math.round(
        properties.reduce((s, p) => s + (p.price_usd || 0), 0) / totalPrice,
      )
    : null;

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20 animate-[fadeIn_0.45s_ease-out]">
      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* ── Breadcrumb ────────────────────────────── */}
        <nav className="mb-6 flex items-center gap-2 text-sm text-sv-500">
          <Link href="/explore" className="hover:text-sv-800 transition">
            <ArrowLeft className="mr-1 inline h-3.5 w-3.5" />
            All Departments
          </Link>
          <ChevronRight className="h-3 w-3 text-sv-300" />
          <span className="font-semibold text-sv-800">{deptName}</span>
        </nav>

        {/* ── Header ────────────────────────────────── */}
        <h1 className="text-3xl font-extrabold text-sv-950 md:text-4xl">
          {deptInfo?.emoji || "📍"} {deptName}
        </h1>
        <p className="mt-1 text-base text-sv-500">
          {loading
            ? "Loading properties…"
            : `${properties.length} properties across ${municipalities.length} municipalities`}
        </p>

        {/* ── Stats row ─────────────────────────────── */}
        {!loading && (
          <div className="mt-4 flex flex-wrap gap-3">
            <div className="rounded-xl border border-sv-200 bg-white px-4 py-2.5 text-center">
              <div className="text-xl font-extrabold text-sv-950">{properties.length}</div>
              <div className="text-[11px] text-sv-500">Listings</div>
            </div>
            <div className="rounded-xl border border-sv-200 bg-white px-4 py-2.5 text-center">
              <div className="text-xl font-extrabold text-sv-950">{fmt(avgPrice)}</div>
              <div className="text-[11px] text-sv-500">Avg Price</div>
            </div>
            <div className="rounded-xl border border-sv-200 bg-white px-4 py-2.5 text-center">
              <div className="text-xl font-extrabold text-sv-950">{municipalities.length}</div>
              <div className="text-[11px] text-sv-500">Municipios</div>
            </div>
            <div className="rounded-xl border border-sv-200 bg-white px-4 py-2.5 text-center">
              <div className="text-xl font-extrabold text-gold-600">
                {properties.filter((p) => p.is_featured).length}
              </div>
              <div className="text-[11px] text-sv-500">Featured</div>
            </div>
            {deptInfo && (
              <>
                <div className="rounded-xl border border-sv-200 bg-white px-4 py-2.5 text-center">
                  <div className="text-xl font-extrabold text-sv-950">{deptInfo.population}</div>
                  <div className="text-[11px] text-sv-500">Population</div>
                </div>
                <div className="rounded-xl border border-sv-200 bg-white px-4 py-2.5 text-center">
                  <div className="text-xl font-extrabold text-sv-950">{deptInfo.area_km2.toLocaleString()} km²</div>
                  <div className="text-[11px] text-sv-500">Area</div>
                </div>
              </>
            )}
          </div>
        )}

        {/* ═══════════════════════════════════════════
            DEPARTMENT HISTORY & INFO
            ═══════════════════════════════════════════ */}
        {deptInfo && (
          <section className="mt-8 rounded-2xl border border-sv-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <BookOpen className="h-5 w-5 text-gold-600" />
              <h2 className="text-lg font-bold text-sv-900">
                About {deptName}
              </h2>
            </div>

            {/* Summary */}
            <p className="text-sm leading-relaxed text-sv-700 mb-4">
              {deptInfo.summary}
            </p>

            {/* History */}
            <div className="mb-5">
              <h3 className="text-sm font-bold text-sv-800 mb-2 flex items-center gap-1.5">
                <Landmark className="h-4 w-4 text-sv-500" />
                Brief History
              </h3>
              <p className="text-sm leading-relaxed text-sv-600">
                {deptInfo.history}
              </p>
            </div>

            {/* Quick facts row */}
            <div className="flex flex-wrap gap-4 mb-5 text-sm">
              <div className="flex items-center gap-1.5 text-sv-600">
                <Landmark className="h-3.5 w-3.5 text-sv-400" />
                Capital: <span className="font-semibold text-sv-800">{deptInfo.capital}</span>
              </div>
              <div className="flex items-center gap-1.5 text-sv-600">
                <Mountain className="h-3.5 w-3.5 text-sv-400" />
                Elevation: <span className="font-semibold text-sv-800">{deptInfo.elevation}</span>
              </div>
              <div className="flex items-center gap-1.5 text-sv-600">
                <Users className="h-3.5 w-3.5 text-sv-400" />
                Pop: <span className="font-semibold text-sv-800">{deptInfo.population}</span>
              </div>
            </div>

            {/* Highlights */}
            <h3 className="text-sm font-bold text-sv-800 mb-2 flex items-center gap-1.5">
              <Star className="h-4 w-4 text-gold-500" />
              Highlights
            </h3>
            <ul className="grid gap-1.5 sm:grid-cols-2 lg:grid-cols-3">
              {deptInfo.highlights.map((h) => (
                <li
                  key={h}
                  className="flex items-center gap-2 rounded-lg bg-sv-50 px-3 py-2 text-xs font-medium text-sv-700"
                >
                  <span className="h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gold-500" />
                  {h}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* ── Map ───────────────────────────────────── */}
        <div className="mt-8 overflow-hidden rounded-2xl border border-sv-200 shadow-lg" style={{ height: 380 }}>
          {!loading && markers.length > 0 ? (
            <PropertyExplorerMap
              center={mapCenter}
              zoom={10}
              markers={markers}
              onMarkerClick={handleMarkerClick}
              className="h-full w-full"
            />
          ) : (
            <div className="flex h-full items-center justify-center bg-sv-100">
              <Loader2 className="h-8 w-8 animate-spin text-sv-300" />
            </div>
          )}
        </div>

        {/* ── Municipality Grid ─────────────────────── */}
        <h2 className="mt-10 mb-5 text-xl font-bold text-sv-900">
          Municipalities in {deptName}
        </h2>

        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-32 animate-pulse rounded-2xl bg-sv-100" />
            ))}
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {municipalities.map((muni) => (
              <Link
                key={muni.slug}
                href={`/explore/${deptSlug}/${muni.slug}`}
                className="group glass-card flex items-center gap-4 overflow-hidden rounded-2xl p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg"
              >
                {/* Thumbnail */}
                {muni.sample ? (
                  <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-xl bg-sv-100">
                    <Image
                      src={muni.sample}
                      alt={muni.name}
                      fill
                      className="object-cover transition-transform duration-500 group-hover:scale-110"
                      sizes="80px"
                      unoptimized
                    />
                  </div>
                ) : (
                  <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-xl bg-sv-100">
                    <MapPin className="h-6 w-6 text-sv-300" />
                  </div>
                )}

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-sv-900 group-hover:text-gold-700 transition-colors truncate">
                    {muni.name}
                  </h3>
                  <div className="mt-0.5 flex items-center gap-3 text-xs text-sv-500">
                    <span className="flex items-center gap-1">
                      <Building2 className="h-3 w-3" /> {muni.count}
                    </span>
                    <span className="flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" /> {fmt(muni.avg_price)}
                    </span>
                    {muni.featured > 0 && (
                      <span className="flex items-center gap-1 text-gold-600">
                        <Star className="h-3 w-3" /> {muni.featured}
                      </span>
                    )}
                  </div>
                </div>

                <ChevronRight className="h-4 w-4 flex-shrink-0 text-sv-300 transition-all group-hover:translate-x-1 group-hover:text-sv-500" />
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
