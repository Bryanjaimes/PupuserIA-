"use client";

import { useState, useMemo } from "react";
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
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  Home,
  Building2,
  TreePine,
  Store,
  X,
} from "lucide-react";
import { useLanguage } from "@/context/language-context";
import { useProperties, usePropertyStats, type PropertyListing } from "@/hooks/use-properties";

/* ═══════════════════════════════════════════════════════
   Real Estate Page — /invest/properties
   Browse, filter, and explore property listings
   across all 14 departments of El Salvador.
   ═══════════════════════════════════════════════════════ */

const PROPERTY_TYPES = [
  { value: "", labelKey: "properties.allTypes", icon: Search },
  { value: "house", labelKey: "properties.house", icon: Home },
  { value: "apartment", labelKey: "properties.apartment", icon: Building2 },
  { value: "land", labelKey: "properties.land", icon: TreePine },
  { value: "commercial", labelKey: "properties.commercial", icon: Store },
];

const DEPARTMENTS = [
  "", "Ahuachapán", "Cabañas", "Chalatenango", "Cuscatlán",
  "La Libertad", "La Paz", "La Unión", "Morazán",
  "San Miguel", "San Salvador", "San Vicente", "Santa Ana",
  "Sonsonate", "Usulután",
];

const SORT_OPTIONS = [
  { value: "newest" as const, labelKey: "properties.sortNewest" },
  { value: "price_asc" as const, labelKey: "properties.sortPriceAsc" },
  { value: "price_desc" as const, labelKey: "properties.sortPriceDesc" },
  { value: "score" as const, labelKey: "properties.sortScore" },
];

function formatPrice(price: number | null): string {
  if (!price) return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(price);
}

function formatArea(m2: number | null): string {
  if (!m2) return "";
  if (m2 >= 10000) return `${(m2 / 10000).toFixed(1)} ha`;
  return `${m2.toLocaleString()} m²`;
}

function featureLabel(f: string): string {
  return f.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// ── Property Card ────────────────────────────────────

function PropertyCard({ property, lang }: { property: PropertyListing; lang: "en" | "es" }) {
  const [imgIdx, setImgIdx] = useState(0);
  const images = property.images.length > 0 ? property.images : ["https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"];
  const title = lang === "es" ? property.title_es : property.title;

  return (
    <div className="group glass-card overflow-hidden rounded-2xl transition-all duration-500 hover:shadow-xl hover:-translate-y-1">
      {/* Image Carousel */}
      <div className="relative h-56 overflow-hidden bg-sv-100">
        <Image
          src={images[imgIdx]}
          alt={title}
          fill
          className="object-cover transition-transform duration-700 group-hover:scale-105"
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          unoptimized
        />
        {/* Image counter & nav */}
        {images.length > 1 && (
          <>
            <div className="absolute bottom-2 right-2 rounded-full bg-black/60 px-2 py-0.5 text-xs text-white">
              {imgIdx + 1}/{images.length}
            </div>
            <button
              onClick={(e) => { e.preventDefault(); setImgIdx((i) => (i === 0 ? images.length - 1 : i - 1)); }}
              className="absolute left-1.5 top-1/2 -translate-y-1/2 rounded-full bg-white/80 p-1 opacity-0 transition group-hover:opacity-100 hover:bg-white"
              aria-label="Previous image"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={(e) => { e.preventDefault(); setImgIdx((i) => (i === images.length - 1 ? 0 : i + 1)); }}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full bg-white/80 p-1 opacity-0 transition group-hover:opacity-100 hover:bg-white"
              aria-label="Next image"
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
        <h3 className="mb-2 line-clamp-2 text-base font-bold text-sv-900 leading-tight">
          {title}
        </h3>

        {/* Price */}
        <div className="mb-3 flex items-baseline gap-2">
          <span className="text-xl font-extrabold text-sv-950">{formatPrice(property.price_usd)}</span>
          {property.ai_valuation_usd && property.price_usd && property.ai_valuation_usd > property.price_usd && (
            <span className="flex items-center gap-0.5 text-xs font-medium text-emerald-600">
              <TrendingUp className="h-3 w-3" />
              AI: {formatPrice(property.ai_valuation_usd)}
            </span>
          )}
        </div>

        {/* Stats row */}
        <div className="flex flex-wrap gap-3 text-xs text-sv-600">
          {property.bedrooms != null && (
            <span className="flex items-center gap-1">
              <BedDouble className="h-3.5 w-3.5" /> {property.bedrooms} {lang === "es" ? "hab" : "bd"}
            </span>
          )}
          {property.bathrooms != null && (
            <span className="flex items-center gap-1">
              <Bath className="h-3.5 w-3.5" /> {property.bathrooms} {lang === "es" ? "baños" : "ba"}
            </span>
          )}
          {property.area_m2 && (
            <span className="flex items-center gap-1">
              <Maximize className="h-3.5 w-3.5" /> {formatArea(property.area_m2)}
            </span>
          )}
          {property.lot_size_m2 && property.lot_size_m2 > 0 && (
            <span className="flex items-center gap-1">
              <TreePine className="h-3.5 w-3.5" /> {formatArea(property.lot_size_m2)} lot
            </span>
          )}
        </div>

        {/* Features */}
        {property.features.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {property.features.slice(0, 3).map((f) => (
              <span key={f} className="rounded-full bg-sv-50 px-2 py-0.5 text-[10px] font-medium text-sv-600">
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

        {/* Neighborhood score */}
        {property.neighborhood_score != null && (
          <div className="mt-3 flex items-center gap-2">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-sv-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-gold-400 to-gold-500 transition-all"
                style={{ width: `${(property.neighborhood_score / 10) * 100}%` }}
              />
            </div>
            <span className="text-[10px] font-semibold text-gold-700">{property.neighborhood_score}/10</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Stats Bar ────────────────────────────────────────

function StatsBar({ t }: { t: (k: string) => string }) {
  const { stats, loading } = usePropertyStats();

  if (loading || !stats) return null;

  const items = [
    { label: t("properties.totalListings"), value: stats.total_listings.toString() },
    { label: t("properties.avgPrice"), value: formatPrice(stats.avg_price_usd) },
    { label: t("properties.departments"), value: `${stats.departments_covered}/14` },
    { label: t("properties.featured"), value: stats.featured_count.toString() },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="glass-card rounded-xl p-4 text-center">
          <div className="text-xl font-extrabold text-sv-950">{item.value}</div>
          <div className="text-xs text-sv-500">{item.label}</div>
        </div>
      ))}
    </div>
  );
}

// ── Main Page ────────────────────────────────────────

export default function PropertiesPage() {
  const { t, lang } = useLanguage();

  // Filters
  const [department, setDepartment] = useState("");
  const [propertyType, setPropertyType] = useState("");
  const [sortBy, setSortBy] = useState<"newest" | "price_asc" | "price_desc" | "score">("newest");
  const [minPrice, setMinPrice] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();
  const [showFilters, setShowFilters] = useState(false);
  const [page, setPage] = useState(1);

  const searchParams = useMemo(
    () => ({
      department: department || undefined,
      property_type: propertyType || undefined,
      sort_by: sortBy,
      min_price: minPrice,
      max_price: maxPrice,
      page,
      page_size: 12,
    }),
    [department, propertyType, sortBy, minPrice, maxPrice, page]
  );

  const { properties, total, loading, error } = useProperties(searchParams);
  const totalPages = Math.ceil(total / 12);

  const activeFilters = [department, propertyType, minPrice, maxPrice].filter(Boolean).length;

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20">
      <div className="mx-auto max-w-7xl px-6 py-12">
        {/* Header */}
        <div className="mb-2">
          <Link href="/invest" className="text-sm text-sv-500 hover:text-sv-700 transition">
            ← {t("properties.backToInvest")}
          </Link>
        </div>
        <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-wider text-gold-600 uppercase">
          <span className="h-px w-8 bg-gold-500/30" />
          {t("properties.realEstate")}
          <span className="h-px w-8 bg-gold-500/30" />
        </div>
        <h1 className="mb-2 text-3xl font-extrabold text-sv-950 md:text-4xl">
          {t("properties.title")}
        </h1>
        <p className="mb-8 max-w-2xl text-base text-sv-700/50">
          {t("properties.subtitle")}
        </p>

        {/* Stats */}
        <div className="mb-8">
          <StatsBar t={t} />
        </div>

        {/* Filters Bar */}
        <div className="mb-6 flex flex-wrap items-center gap-3">
          {/* Department Select */}
          <select
            value={department}
            onChange={(e) => { setDepartment(e.target.value); setPage(1); }}
            className="rounded-xl border border-sv-200 bg-white px-3 py-2 text-sm text-sv-800 focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400"
          >
            <option value="">{t("properties.allDepartments")}</option>
            {DEPARTMENTS.filter(Boolean).map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>

          {/* Type Filters */}
          <div className="flex items-center gap-1 rounded-xl border border-sv-200 bg-white p-1">
            {PROPERTY_TYPES.map(({ value, labelKey, icon: Icon }) => (
              <button
                key={value}
                onClick={() => { setPropertyType(value); setPage(1); }}
                className={`flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                  propertyType === value
                    ? "bg-sv-900 text-white"
                    : "text-sv-600 hover:bg-sv-50"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {t(labelKey)}
              </button>
            ))}
          </div>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => { setSortBy(e.target.value as typeof sortBy); setPage(1); }}
            className="rounded-xl border border-sv-200 bg-white px-3 py-2 text-sm text-sv-800 focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{t(opt.labelKey)}</option>
            ))}
          </select>

          {/* Price Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-1.5 rounded-xl border px-3 py-2 text-sm font-medium transition ${
              showFilters || activeFilters > 0
                ? "border-gold-400 bg-gold-50 text-gold-700"
                : "border-sv-200 bg-white text-sv-600 hover:border-sv-300"
            }`}
          >
            <SlidersHorizontal className="h-4 w-4" />
            {t("properties.filters")}
            {activeFilters > 0 && (
              <span className="ml-1 flex h-4 w-4 items-center justify-center rounded-full bg-gold-500 text-[10px] text-white">
                {activeFilters}
              </span>
            )}
          </button>

          {/* Clear Filters */}
          {activeFilters > 0 && (
            <button
              onClick={() => { setDepartment(""); setPropertyType(""); setMinPrice(undefined); setMaxPrice(undefined); setPage(1); }}
              className="flex items-center gap-1 text-xs text-sv-500 hover:text-sv-700"
            >
              <X className="h-3 w-3" /> {t("properties.clearFilters")}
            </button>
          )}
        </div>

        {/* Price Filters Dropdown */}
        {showFilters && (
          <div className="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-sv-200 bg-white p-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-sv-600">{t("properties.minPrice")}</label>
              <input
                type="number"
                value={minPrice ?? ""}
                onChange={(e) => { setMinPrice(e.target.value ? Number(e.target.value) : undefined); setPage(1); }}
                placeholder="$0"
                className="w-32 rounded-lg border border-sv-200 px-3 py-1.5 text-sm focus:border-gold-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-sv-600">{t("properties.maxPrice")}</label>
              <input
                type="number"
                value={maxPrice ?? ""}
                onChange={(e) => { setMaxPrice(e.target.value ? Number(e.target.value) : undefined); setPage(1); }}
                placeholder={t("properties.noLimit")}
                className="w-32 rounded-lg border border-sv-200 px-3 py-1.5 text-sm focus:border-gold-400 focus:outline-none"
              />
            </div>
          </div>
        )}

        {/* Results count */}
        <div className="mb-4 text-sm text-sv-500">
          {loading
            ? t("properties.loading")
            : `${total} ${t("properties.propertiesFound")}`}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {t("properties.errorLoading")}: {error}
          </div>
        )}

        {/* Property Grid */}
        {loading ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="glass-card animate-pulse rounded-2xl">
                <div className="h-56 rounded-t-2xl bg-sv-200" />
                <div className="space-y-3 p-5">
                  <div className="h-3 w-24 rounded bg-sv-200" />
                  <div className="h-4 w-3/4 rounded bg-sv-200" />
                  <div className="h-6 w-1/2 rounded bg-sv-200" />
                  <div className="flex gap-3">
                    <div className="h-3 w-12 rounded bg-sv-200" />
                    <div className="h-3 w-12 rounded bg-sv-200" />
                    <div className="h-3 w-16 rounded bg-sv-200" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : properties.length === 0 ? (
          <div className="rounded-2xl border border-sv-200 bg-white p-12 text-center">
            <Search className="mx-auto mb-3 h-10 w-10 text-sv-300" />
            <h3 className="mb-1 text-lg font-bold text-sv-800">{t("properties.noResults")}</h3>
            <p className="text-sm text-sv-500">{t("properties.noResultsDesc")}</p>
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {properties.map((p) => (
              <PropertyCard key={p.id} property={p} lang={lang} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-8 flex items-center justify-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="rounded-lg border border-sv-200 bg-white px-3 py-1.5 text-sm disabled:opacity-40 hover:bg-sv-50 transition"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => setPage(p)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                  p === page
                    ? "bg-sv-900 text-white"
                    : "border border-sv-200 bg-white text-sv-600 hover:bg-sv-50"
                }`}
              >
                {p}
              </button>
            ))}
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="rounded-lg border border-sv-200 bg-white px-3 py-1.5 text-sm disabled:opacity-40 hover:bg-sv-50 transition"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Image Gallery Section */}
        {!loading && properties.length > 0 && (
          <section className="mt-16">
            <h2 className="mb-2 text-xl font-bold text-sv-900">{t("properties.galleryTitle")}</h2>
            <p className="mb-6 text-sm text-sv-500">{t("properties.galleryDesc")}</p>
            <div className="columns-2 gap-3 sm:columns-3 lg:columns-4">
              {properties
                .flatMap((p) =>
                  p.images.map((img, i) => ({
                    src: img,
                    alt: `${lang === "es" ? p.title_es : p.title} — ${i + 1}`,
                    location: `${p.municipio}, ${p.department}`,
                  }))
                )
                .slice(0, 20)
                .map((img, idx) => (
                  <div key={idx} className="mb-3 break-inside-avoid overflow-hidden rounded-xl">
                    <div className="group relative">
                      <Image
                        src={img.src}
                        alt={img.alt}
                        width={400}
                        height={300}
                        className="w-full rounded-xl object-cover transition-transform duration-500 group-hover:scale-105"
                        unoptimized
                      />
                      <div className="absolute bottom-0 left-0 right-0 rounded-b-xl bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 transition-opacity group-hover:opacity-100">
                        <p className="text-xs font-medium text-white">{img.alt}</p>
                        <p className="flex items-center gap-1 text-[10px] text-white/70">
                          <MapPin className="h-2.5 w-2.5" /> {img.location}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
