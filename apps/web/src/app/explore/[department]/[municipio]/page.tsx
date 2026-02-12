"use client";

import { useState, useMemo } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import {
  Search,
  MapPin,
  BedDouble,
  Bath,
  Maximize,
  TrendingUp,
  Star,
  ChevronLeft,
  ChevronRight,
  Home,
  Building2,
  TreePine,
  Store,
  ArrowLeft,
} from "lucide-react";
import { departmentFromSlug, toSlug } from "@/lib/property-slugs";
import { useProperties, usePropertyStats, type PropertyListing } from "@/hooks/use-properties";

/* ═══════════════════════════════════════════════════════
   Municipality Listings — /explore/[dept]/[muni]
   Property card grid with filters, sorting, pagination.
   ═══════════════════════════════════════════════════════ */

// ── Helpers ──────────────────────────────────────────

function formatPrice(price: number | null): string {
  if (!price) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(price);
}

function formatArea(m2: number | null): string {
  if (!m2) return "";
  if (m2 >= 10000) return `${(m2 / 10000).toFixed(1)} ha`;
  return `${m2.toLocaleString()} m²`;
}

function featureLabel(f: string): string {
  return f
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function resolveTitle(slug: string, results: PropertyListing[]): string {
  for (const p of results) {
    if (toSlug(p.municipio) === slug) return p.municipio;
  }
  return slug
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// ── Constants ────────────────────────────────────────

const PROPERTY_TYPES = [
  { value: "", label: "All", icon: Search },
  { value: "house", label: "House", icon: Home },
  { value: "apartment", label: "Apt", icon: Building2 },
  { value: "land", label: "Land", icon: TreePine },
  { value: "commercial", label: "Commercial", icon: Store },
];

const SORT_OPTIONS = [
  { value: "newest", label: "Newest" },
  { value: "price_asc", label: "Price ↑" },
  { value: "price_desc", label: "Price ↓" },
  { value: "score", label: "Best" },
] as const;

const PAGE_SIZE = 12;

// ── Property Card ────────────────────────────────────

function PropertyCard({
  property,
  deptSlug,
  muniSlug,
}: {
  property: PropertyListing;
  deptSlug: string;
  muniSlug: string;
}) {
  const [imgIdx, setImgIdx] = useState(0);
  const images =
    property.images.length > 0
      ? property.images
      : [
          "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800",
        ];

  return (
    <Link
      href={`/explore/${deptSlug}/${muniSlug}/${property.id}`}
      className="group glass-card overflow-hidden rounded-2xl transition-all duration-500 hover:-translate-y-1 hover:shadow-xl"
    >
      {/* Image */}
      <div className="relative h-52 overflow-hidden bg-sv-100">
        <Image
          src={images[imgIdx]}
          alt={property.title}
          fill
          className="object-cover transition-transform duration-700 group-hover:scale-105"
          sizes="(max-width:640px) 100vw,(max-width:1024px) 50vw,33vw"
          unoptimized
        />
        {images.length > 1 && (
          <>
            <div className="absolute bottom-2 right-2 rounded-full bg-black/60 px-2 py-0.5 text-xs text-white">
              {imgIdx + 1}/{images.length}
            </div>
            <button
              onClick={(e) => {
                e.preventDefault();
                setImgIdx((i) => (i === 0 ? images.length - 1 : i - 1));
              }}
              className="absolute left-1.5 top-1/2 -translate-y-1/2 rounded-full bg-white/80 p-1 opacity-0 transition group-hover:opacity-100 hover:bg-white"
              aria-label="Previous"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                setImgIdx((i) => (i === images.length - 1 ? 0 : i + 1));
              }}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full bg-white/80 p-1 opacity-0 transition group-hover:opacity-100 hover:bg-white"
              aria-label="Next"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </>
        )}
        {/* Badges */}
        <div className="absolute left-2 top-2 flex gap-1.5">
          {property.is_featured && (
            <span className="flex items-center gap-1 rounded-full bg-gold-500 px-2 py-0.5 text-xs font-semibold text-white shadow">
              <Star className="h-3 w-3" /> Featured
            </span>
          )}
          <span className="rounded-full bg-white/90 px-2 py-0.5 text-xs font-medium capitalize text-sv-800">
            {property.property_type}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        <div className="mb-1 flex items-center gap-1.5 text-xs text-sv-500">
          <MapPin className="h-3 w-3" />
          {property.municipio}, {property.department}
        </div>
        <h3 className="mb-2 line-clamp-2 text-base font-bold leading-tight text-sv-900">
          {property.title}
        </h3>

        {/* Price */}
        <div className="mb-3 flex items-baseline gap-2">
          <span className="text-xl font-extrabold text-sv-950">
            {formatPrice(property.price_usd)}
          </span>
          {property.ai_valuation_usd &&
            property.price_usd &&
            property.ai_valuation_usd > property.price_usd && (
              <span className="flex items-center gap-0.5 text-xs font-medium text-emerald-600">
                <TrendingUp className="h-3 w-3" />
                AI: {formatPrice(property.ai_valuation_usd)}
              </span>
            )}
        </div>

        {/* Stats */}
        <div className="flex flex-wrap gap-3 text-xs text-sv-600">
          {property.bedrooms != null && (
            <span className="flex items-center gap-1">
              <BedDouble className="h-3.5 w-3.5" /> {property.bedrooms} bd
            </span>
          )}
          {property.bathrooms != null && (
            <span className="flex items-center gap-1">
              <Bath className="h-3.5 w-3.5" /> {property.bathrooms} ba
            </span>
          )}
          {property.area_m2 != null && (
            <span className="flex items-center gap-1">
              <Maximize className="h-3.5 w-3.5" /> {formatArea(property.area_m2)}
            </span>
          )}
        </div>

        {/* Features */}
        {property.features.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {property.features.slice(0, 3).map((f) => (
              <span
                key={f}
                className="rounded-full bg-sv-50 px-2 py-0.5 text-[10px] font-medium text-sv-600"
              >
                {featureLabel(f)}
              </span>
            ))}
            {property.features.length > 3 && (
              <span className="rounded-full bg-sv-50 px-2 py-0.5 text-[10px] font-medium text-sv-500">
                +{property.features.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Score bar */}
        {property.neighborhood_score != null && (
          <div className="mt-3 flex items-center gap-2">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-sv-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-gold-400 to-gold-500 transition-all"
                style={{
                  width: `${(property.neighborhood_score / 10) * 100}%`,
                }}
              />
            </div>
            <span className="text-[10px] font-semibold text-gold-700">
              {property.neighborhood_score}/10
            </span>
          </div>
        )}
      </div>
    </Link>
  );
}

// ── Main Page ────────────────────────────────────────

export default function MunicipalityListingsPage() {
  const params = useParams<{ department: string; municipio: string }>();
  const deptSlug = params.department;
  const muniSlug = params.municipio;
  const deptName = departmentFromSlug(deptSlug);

  const [propertyType, setPropertyType] = useState("");
  const [sortBy, setSortBy] = useState<"newest" | "price_asc" | "price_desc" | "score">("newest");
  const [page, setPage] = useState(1);

  const searchParams = useMemo(
    () => ({
      department: deptName || undefined,
      municipio: muniSlug.replace(/-/g, " "),
      property_type: propertyType || undefined,
      sort_by: sortBy,
      page,
      page_size: PAGE_SIZE,
    }),
    [deptName, muniSlug, propertyType, sortBy, page],
  );

  const { properties, total, loading, error } = useProperties(searchParams);
  const totalPages = Math.ceil(total / PAGE_SIZE);

  const muniName = resolveTitle(muniSlug, properties);

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

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20 animate-[fadeIn_0.4s_ease-out]">
      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* ── Breadcrumb ──────────────────────────── */}
        <nav className="mb-6 flex flex-wrap items-center gap-2 text-sm text-sv-500">
          <Link href="/explore" className="hover:text-sv-800 transition">
            <ArrowLeft className="mr-1 inline h-3.5 w-3.5" />
            Departments
          </Link>
          <ChevronRight className="h-3 w-3 text-sv-300" />
          <Link
            href={`/explore/${deptSlug}`}
            className="hover:text-sv-800 transition"
          >
            {deptName}
          </Link>
          <ChevronRight className="h-3 w-3 text-sv-300" />
          <span className="font-semibold text-sv-800">{muniName}</span>
        </nav>

        {/* ── Header ──────────────────────────────── */}
        <h1 className="text-3xl font-extrabold text-sv-950 md:text-4xl">
          Properties in {muniName}
        </h1>
        <p className="mt-1 text-base text-sv-500">
          {deptName} Department
          {!loading && ` — ${total} listing${total !== 1 ? "s" : ""}`}
        </p>

        {/* ── Filters ─────────────────────────────── */}
        <div className="mt-6 mb-6 flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1 rounded-xl border border-sv-200 bg-white p-1">
            {PROPERTY_TYPES.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                onClick={() => {
                  setPropertyType(value);
                  setPage(1);
                }}
                className={`flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                  propertyType === value
                    ? "bg-sv-900 text-white"
                    : "text-sv-600 hover:bg-sv-50"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {label}
              </button>
            ))}
          </div>

          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value as typeof sortBy);
              setPage(1);
            }}
            className="rounded-xl border border-sv-200 bg-white px-3 py-2 text-sm text-sv-800 focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* ── Results count ────────────────────────── */}
        <div className="mb-4 text-sm text-sv-500">
          {loading ? "Loading…" : `${total} properties found`}
        </div>

        {/* ── Error ────────────────────────────────── */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Error: {error}
          </div>
        )}

        {/* ── Grid ─────────────────────────────────── */}
        {loading ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="glass-card animate-pulse rounded-2xl">
                <div className="h-52 rounded-t-2xl bg-sv-200" />
                <div className="space-y-3 p-5">
                  <div className="h-3 w-24 rounded bg-sv-200" />
                  <div className="h-4 w-3/4 rounded bg-sv-200" />
                  <div className="h-6 w-1/2 rounded bg-sv-200" />
                </div>
              </div>
            ))}
          </div>
        ) : properties.length === 0 ? (
          <div className="rounded-2xl border border-sv-200 bg-white p-12 text-center">
            <Search className="mx-auto mb-3 h-10 w-10 text-sv-300" />
            <h3 className="mb-1 text-lg font-bold text-sv-800">
              No properties found
            </h3>
            <p className="text-sm text-sv-500">
              Try changing the filters or check back later.
            </p>
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {properties.map((p) => (
              <PropertyCard
                key={p.id}
                property={p}
                deptSlug={deptSlug}
                muniSlug={muniSlug}
              />
            ))}
          </div>
        )}

        {/* ── Pagination ───────────────────────────── */}
        {totalPages > 1 && (
          <div className="mt-8 flex items-center justify-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="rounded-lg border border-sv-200 bg-white px-3 py-1.5 text-sm transition disabled:opacity-40 hover:bg-sv-50"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(
                (p) =>
                  p === 1 || p === totalPages || Math.abs(p - page) <= 2,
              )
              .map((p, idx, arr) => (
                <span key={p} className="contents">
                  {idx > 0 && arr[idx - 1] !== p - 1 && (
                    <span className="px-1 text-sv-400">…</span>
                  )}
                  <button
                    onClick={() => setPage(p)}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                      p === page
                        ? "bg-sv-900 text-white"
                        : "border border-sv-200 bg-white text-sv-600 hover:bg-sv-50"
                    }`}
                  >
                    {p}
                  </button>
                </span>
              ))}
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="rounded-lg border border-sv-200 bg-white px-3 py-1.5 text-sm transition disabled:opacity-40 hover:bg-sv-50"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
