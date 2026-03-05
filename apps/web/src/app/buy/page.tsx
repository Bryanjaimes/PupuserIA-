"use client";

import { useState, useMemo, useCallback, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
  SlidersHorizontal,
  X,
  Sparkles,
  Bitcoin,
  Heart,
  Users,
  GraduationCap,
  Waves,
  Shield,
  DollarSign,
  LayoutGrid,
  List,
} from "lucide-react";
import { toSlug, DEPARTMENTS } from "@/lib/property-slugs";
import { useProperties, type PropertySearchParams, type PropertyListing } from "@/hooks/use-properties";
import { useViewMode } from "@/context/view-mode";

/* ═══════════════════════════════════════════════════════
   Buy / Search — /buy
   Full search page with sidebar filters, property cards,
   sort, and pagination. Uses all 2,849 real listings.
   ═══════════════════════════════════════════════════════ */

// ── Helpers ──────────────────────────────────────────

function fmt(n: number | null): string {
  if (!n) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

function fmtArea(m2: number | null): string {
  if (!m2) return "";
  if (m2 >= 10000) return `${(m2 / 10000).toFixed(1)} ha`;
  return `${m2.toLocaleString()} m²`;
}

// ── Constants ────────────────────────────────────────

const PROPERTY_TYPES = [
  { value: "", label: "All Types", icon: Search },
  { value: "house", label: "House", icon: Home },
  { value: "apartment", label: "Apartment", icon: Building2 },
  { value: "land", label: "Land / Lot", icon: TreePine },
  { value: "commercial", label: "Commercial", icon: Store },
];

const SORT_OPTIONS = [
  { value: "score", label: "Best Match" },
  { value: "newest", label: "Newest" },
  { value: "price_asc", label: "Price: Low → High" },
  { value: "price_desc", label: "Price: High → Low" },  { value: "family_score", label: "\uD83D\uDC68\u200D\uD83D\uDC69\u200D\uD83D\uDC67 Best for Families" },
  { value: "investment", label: "\uD83D\uDCC8 Investment Potential" },] as const;

const PRICE_PRESETS = [
  { label: "Any", min: undefined, max: undefined },
  { label: "Under $50k", min: undefined, max: 50000 },
  { label: "$50k–$150k", min: 50000, max: 150000 },
  { label: "$150k–$300k", min: 150000, max: 300000 },
  { label: "$300k–$500k", min: 300000, max: 500000 },
  { label: "$500k+", min: 500000, max: undefined },
];

const BED_OPTIONS = [
  { value: 0, label: "Any" },
  { value: 1, label: "1+" },
  { value: 2, label: "2+" },
  { value: 3, label: "3+" },
  { value: 4, label: "4+" },
  { value: 5, label: "5+" },
];

const BATH_OPTIONS = [
  { value: 0, label: "Any" },
  { value: 1, label: "1+" },
  { value: 2, label: "2+" },
  { value: 3, label: "3+" },
];

const PAGE_SIZE = 24;

// ── Trending Searches ────────────────────────────────

const TRENDING_FAMILY = [
  { label: "Zaragoza Family Homes", q: "Zaragoza casa", icon: Heart },
  { label: "Safe Neighborhoods", q: "seguro residencial", icon: Shield },
  { label: "3+ Bedrooms", q: "3 habitaciones familia", icon: Users },
  { label: "Garden Houses", q: "casa jard\u00edn patio", icon: GraduationCap },
  { label: "Single Story", q: "una planta accesible", icon: Home },
];

const TRENDING_INVESTOR = [
  { label: "Surf City Lots", q: "playa terreno", icon: Waves },
  { label: "Airbnb Ready", q: "furnished view Airbnb", icon: DollarSign },
  { label: "Fixer-Uppers", q: "oportunidad remodelar", icon: TrendingUp },
  { label: "Santa Tecla Apartments", q: "Santa Tecla apartamento", icon: Building2 },
  { label: "Commercial", q: "comercial inversi\u00f3n", icon: Store },
];

// ── Property Card ────────────────────────────────────

function PropertyCard({ property }: { property: PropertyListing }) {
  const [imgIdx, setImgIdx] = useState(0);
  const images =
    property.images.length > 0
      ? property.images
      : ["https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"];

  const deptSlug = toSlug(property.department);
  const muniSlug = toSlug(property.municipio);

  return (
    <Link
      href={`/explore/${deptSlug}/${muniSlug}/${property.id}`}
      className="group glass-card overflow-hidden rounded-2xl transition-all duration-500 hover:-translate-y-1 hover:shadow-xl hover:shadow-white/5"
    >
      {/* Image */}
      <div className="relative h-52 overflow-hidden bg-white/5">
        <Image
          src={images[imgIdx]}
          alt={property.title}
          fill
          className="object-cover transition-transform duration-700 group-hover:scale-105"
          sizes="(max-width:640px) 100vw,(max-width:1024px) 50vw,33vw"
        />
        {images.length > 1 && (
          <>
            <div className="absolute bottom-2 right-2 rounded-full bg-black/60 px-2 py-0.5 text-xs text-white/80">
              {imgIdx + 1}/{images.length}
            </div>
            <button
              onClick={(e) => {
                e.preventDefault();
                setImgIdx((i) => (i === 0 ? images.length - 1 : i - 1));
              }}
              className="absolute left-1.5 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-1 text-white opacity-0 transition group-hover:opacity-100 hover:bg-black/80"
              aria-label="Previous"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                setImgIdx((i) => (i === images.length - 1 ? 0 : i + 1));
              }}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-1 text-white opacity-0 transition group-hover:opacity-100 hover:bg-black/80"
              aria-label="Next"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </>
        )}
        {/* Badges */}
        <div className="absolute left-2 top-2 flex gap-1.5">
          {property.is_featured && (
            <span className="flex items-center gap-1 rounded-full bg-gold-500 px-2 py-0.5 text-xs font-semibold text-black shadow">
              <Star className="h-3 w-3" /> Gold
            </span>
          )}
          <span className="rounded-full bg-black/80 px-2 py-0.5 text-xs font-medium capitalize text-white/70">
            {property.property_type}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="mb-1 flex items-center gap-1.5 text-xs text-white/40">
          <MapPin className="h-3 w-3" />
          {property.municipio}, {property.department}
        </div>
        <h3 className="mb-2 line-clamp-2 text-sm font-bold leading-tight text-white/90">
          {property.title}
        </h3>

        {/* Price */}
        <div className="mb-3">
          <span className="text-lg font-extrabold text-white">
            {fmt(property.price_usd)}
          </span>
        </div>

        {/* Stats */}
        <div className="flex flex-wrap gap-3 text-xs text-white/50">
          {property.bedrooms != null && property.bedrooms > 0 && (
            <span className="flex items-center gap-1">
              <BedDouble className="h-3.5 w-3.5" /> {property.bedrooms} bd
            </span>
          )}
          {property.bathrooms != null && property.bathrooms > 0 && (
            <span className="flex items-center gap-1">
              <Bath className="h-3.5 w-3.5" /> {property.bathrooms} ba
            </span>
          )}
          {property.area_m2 != null && (
            <span className="flex items-center gap-1">
              <Maximize className="h-3.5 w-3.5" /> {fmtArea(property.area_m2)}
            </span>
          )}
        </div>

        {/* Quality bar */}
        {property.neighborhood_score != null && property.neighborhood_score > 0 && (
          <div className="mt-3 flex items-center gap-2">
            <div className="h-1 flex-1 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-gold-400 to-gold-600 transition-all"
                style={{ width: `${property.neighborhood_score}%` }}
              />
            </div>
            <span className="text-[10px] font-semibold text-gold-400">
              {property.neighborhood_score}%
            </span>
          </div>
        )}
      </div>
    </Link>
  );
}

// ── Filter Sidebar ───────────────────────────────────

function FilterSidebar({
  filters,
  setFilters,
  departments,
  municipios,
  onClose,
}: {
  filters: Filters;
  setFilters: (f: Filters) => void;
  departments: string[];
  municipios: string[];
  onClose?: () => void;
}) {
  return (
    <div className="space-y-6">
      {/* Header (mobile) */}
      {onClose && (
        <div className="flex items-center justify-between lg:hidden">
          <h3 className="text-lg font-bold text-white">Filters</h3>
          <button onClick={onClose} className="rounded-lg p-1 text-white/60 hover:bg-white/10">
            <X className="h-5 w-5" />
          </button>
        </div>
      )}

      {/* Search */}
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-white/40">
          Search
        </label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/30" />
          <input
            type="text"
            value={filters.q}
            onChange={(e) => setFilters({ ...filters, q: e.target.value, page: 1 })}
            placeholder="Modern house Zaragoza garden..."
            className="w-full rounded-xl border border-white/10 bg-white/5 py-2.5 pr-3 pl-9 text-sm text-white placeholder-white/30 focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400"
          />
        </div>
      </div>

      {/* Location */}
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-white/40">
          Department
        </label>
        <select
          value={filters.department}
          onChange={(e) => setFilters({ ...filters, department: e.target.value, municipio: "", page: 1 })}
          className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400"
        >
          <option value="" className="bg-[#111] text-white">All Departments</option>
          {departments.map((d) => (
            <option key={d} value={d} className="bg-[#111] text-white">{d}</option>
          ))}
        </select>
      </div>

      {municipios.length > 0 && (
        <div>
          <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-white/40">
            Municipio
          </label>
          <select
            value={filters.municipio}
            onChange={(e) => setFilters({ ...filters, municipio: e.target.value, page: 1 })}
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400"
          >
            <option value="" className="bg-[#111] text-white">All Municipios</option>
            {municipios.map((m) => (
              <option key={m} value={m} className="bg-[#111] text-white">{m}</option>
            ))}
          </select>
        </div>
      )}

      {/* Property Type */}
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-white/40">
          Property Type
        </label>
        <div className="grid grid-cols-2 gap-1.5">
          {PROPERTY_TYPES.map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              onClick={() => setFilters({ ...filters, propertyType: value, page: 1 })}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition ${
                filters.propertyType === value
                  ? "bg-gold-500/20 text-gold-400 ring-1 ring-gold-400/30"
                  : "bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/70"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Price */}
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-white/40">
          Price (USD)
        </label>
        <div className="grid grid-cols-2 gap-1.5">
          {PRICE_PRESETS.map((p) => {
            const active =
              filters.minPrice === p.min && filters.maxPrice === p.max;
            return (
              <button
                key={p.label}
                onClick={() =>
                  setFilters({ ...filters, minPrice: p.min, maxPrice: p.max, page: 1 })
                }
                className={`rounded-lg px-3 py-2 text-xs font-medium transition ${
                  active
                    ? "bg-gold-500/20 text-gold-400 ring-1 ring-gold-400/30"
                    : "bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/70"
                }`}
              >
                {p.label}
              </button>
            );
          })}
        </div>
        {/* BTC toggle */}
        <div className="mt-2 flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-white/40">
          <Bitcoin className="h-3.5 w-3.5 text-amber-400" />
          <span>BTC prices coming soon</span>
        </div>
      </div>

      {/* Bedrooms */}
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-white/40">
          Bedrooms
        </label>
        <div className="flex gap-1.5">
          {BED_OPTIONS.map((b) => (
            <button
              key={b.value}
              onClick={() => setFilters({ ...filters, bedrooms: b.value, page: 1 })}
              className={`flex-1 rounded-lg py-2 text-center text-xs font-medium transition ${
                filters.bedrooms === b.value
                  ? "bg-gold-500/20 text-gold-400 ring-1 ring-gold-400/30"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {b.label}
            </button>
          ))}
        </div>
      </div>

      {/* Bathrooms */}
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-white/40">
          Bathrooms
        </label>
        <div className="flex gap-1.5">
          {BATH_OPTIONS.map((b) => (
            <button
              key={b.value}
              onClick={() => setFilters({ ...filters, bathrooms: b.value, page: 1 })}
              className={`flex-1 rounded-lg py-2 text-center text-xs font-medium transition ${
                filters.bathrooms === b.value
                  ? "bg-gold-500/20 text-gold-400 ring-1 ring-gold-400/30"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {b.label}
            </button>
          ))}
        </div>
      </div>

      {/* Featured Only */}
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-white/40">
          Quality
        </label>
        <button
          onClick={() => setFilters({ ...filters, featuredOnly: !filters.featuredOnly, page: 1 })}
          className={`flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-xs font-medium transition ${
            filters.featuredOnly
              ? "bg-gold-500/20 text-gold-400 ring-1 ring-gold-400/30"
              : "bg-white/5 text-white/50 hover:bg-white/10"
          }`}
        >
          <Star className="h-3.5 w-3.5" />
          Gold-tier listings only
        </button>
      </div>

      {/* Clear */}
      <button
        onClick={() =>
          setFilters({
            q: "",
            department: "",
            municipio: "",
            propertyType: "",
            minPrice: undefined,
            maxPrice: undefined,
            bedrooms: 0,
            bathrooms: 0,
            featuredOnly: false,
            sortBy: "score",
            page: 1,
          })
        }
        className="w-full rounded-xl border border-white/10 py-2.5 text-xs font-semibold text-white/40 transition hover:border-white/20 hover:text-white/60"
      >
        Clear All Filters
      </button>
    </div>
  );
}

// ── Types ────────────────────────────────────────────

interface Filters {
  q: string;
  department: string;
  municipio: string;
  propertyType: string;
  minPrice: number | undefined;
  maxPrice: number | undefined;
  bedrooms: number;
  bathrooms: number;
  featuredOnly: boolean;
  sortBy: string;
  page: number;
}

// ── Page ─────────────────────────────────────────────

export default function BuyPage() {
  const [mobileFilters, setMobileFilters] = useState(false);
  const [departments, setDepartments] = useState<string[]>([]);
  const [municipios, setMunicipios] = useState<string[]>([]);
  const { mode, filterPresets, modeLabel, modeIcon } = useViewMode();
  const trending = mode === "family" ? TRENDING_FAMILY : TRENDING_INVESTOR;

  const [filters, setFilters] = useState<Filters>({
    q: "",
    department: "",
    municipio: "",
    propertyType: "",
    minPrice: undefined,
    maxPrice: undefined,
    bedrooms: 0,
    bathrooms: 0,
    featuredOnly: false,
    sortBy: "score",
    page: 1,
  });

  // Load department list
  useEffect(() => {
    fetch("/api/properties/departments")
      .then((r) => r.json())
      .then((data) => {
        const depts = data.departments.map((d: { name: string }) => d.name).sort();
        setDepartments(depts);
      })
      .catch(() => {});
  }, []);

  // Load municipios when department changes
  useEffect(() => {
    if (!filters.department) {
      setMunicipios([]);
      return;
    }
    fetch(`/api/properties/departments`)
      .then((r) => r.json())
      .then((data) => {
        const dept = data.departments.find(
          (d: { name: string }) => d.name === filters.department
        );
        if (dept) {
          setMunicipios(dept.municipalities.map((m: { name: string }) => m.name).sort());
        }
      })
      .catch(() => {});
  }, [filters.department]);

  // Build search params
  const searchParams = useMemo<PropertySearchParams>(
    () => ({
      q: filters.q || undefined,
      department: filters.department || undefined,
      municipio: filters.municipio || undefined,
      property_type: filters.propertyType || undefined,
      min_price: filters.minPrice,
      max_price: filters.maxPrice,
      bedrooms: filters.bedrooms || undefined,
      bathrooms: filters.bathrooms || undefined,
      featured_only: filters.featuredOnly || undefined,
      sort_by: (filters.sortBy as PropertySearchParams["sort_by"]) || "score",
      page: filters.page,
      page_size: PAGE_SIZE,
    }),
    [filters]
  );

  const { properties, total, loading } = useProperties(searchParams);
  const totalPages = Math.ceil(total / PAGE_SIZE);

  // Active filter count
  const activeCount = [
    filters.q,
    filters.department,
    filters.municipio,
    filters.propertyType,
    filters.minPrice,
    filters.maxPrice,
    filters.bedrooms > 0,
    filters.bathrooms > 0,
    filters.featuredOnly,
  ].filter(Boolean).length;

  return (
    <main className="min-h-screen bg-black pt-20">
      {/* ── Hero Search Bar ────────────────────────── */}
      <div className="border-b border-white/5 bg-gradient-to-b from-[#0a0a0a] to-black px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="flex items-center gap-2 text-sm text-white/40">
            <Sparkles className="h-4 w-4 text-gold-400" />
            <span>{modeIcon} {modeLabel}</span>
            <span className="text-white/20">\u00b7</span>
            2,849 listings across all 14 departments
          </div>
          <h1 className="mt-2 text-3xl font-extrabold text-white md:text-4xl">
            {mode === "family" ? "Find Your Family Home" : "Find Your Investment"}
          </h1>
          <p className="mt-1 text-base text-white/40">
            {mode === "family"
              ? "Safe neighborhoods, gardens, schools — properties scored for families."
              : "Cap rates, Airbnb potential, price/m\u00b2 — data-driven investing."}
          </p>

          {/* Trending */}
          <div className="mt-5 flex flex-wrap gap-2">
            {trending.map(({ label, q, icon: Icon }) => (
              <button
                key={label}
                onClick={() => setFilters({ ...filters, q, page: 1 })}
                className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white/60 transition hover:border-gold-400/30 hover:bg-gold-500/10 hover:text-gold-400"
              >
                <Icon className="h-3 w-3" />
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Main Content ───────────────────────────── */}
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex gap-8">
          {/* ── Desktop Sidebar ──────────────────── */}
          <aside className="hidden w-72 shrink-0 lg:block">
            <div className="sticky top-28 rounded-2xl border border-white/10 bg-[#0a0a0a] p-5">
              <FilterSidebar
                filters={filters}
                setFilters={setFilters}
                departments={departments}
                municipios={municipios}
              />
            </div>
          </aside>

          {/* ── Results ──────────────────────────── */}
          <div className="min-w-0 flex-1">
            {/* Toolbar */}
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                {/* Mobile filter toggle */}
                <button
                  onClick={() => setMobileFilters(true)}
                  className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-white/60 transition hover:bg-white/10 lg:hidden"
                >
                  <SlidersHorizontal className="h-4 w-4" />
                  Filters
                  {activeCount > 0 && (
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-gold-500 text-[10px] font-bold text-black">
                      {activeCount}
                    </span>
                  )}
                </button>

                <div className="text-sm text-white/40">
                  {loading ? (
                    "Searching..."
                  ) : (
                    <>
                      <span className="font-semibold text-white">{total.toLocaleString()}</span>{" "}
                      properties found
                    </>
                  )}
                </div>
              </div>

              {/* Sort */}
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters({ ...filters, sortBy: e.target.value, page: 1 })}
                className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/70 focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400"
              >
                {SORT_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value} className="bg-[#111] text-white">
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Active filter pills */}
            {activeCount > 0 && (
              <div className="mb-4 flex flex-wrap gap-2">
                {filters.q && (
                  <span className="flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">
                    &quot;{filters.q}&quot;
                    <button onClick={() => setFilters({ ...filters, q: "", page: 1 })} className="ml-1 hover:text-white">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {filters.department && (
                  <span className="flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">
                    {filters.department}
                    <button onClick={() => setFilters({ ...filters, department: "", municipio: "", page: 1 })} className="ml-1 hover:text-white">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {filters.propertyType && (
                  <span className="flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">
                    {filters.propertyType}
                    <button onClick={() => setFilters({ ...filters, propertyType: "", page: 1 })} className="ml-1 hover:text-white">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {(filters.minPrice || filters.maxPrice) && (
                  <span className="flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">
                    {filters.minPrice ? fmt(filters.minPrice) : "$0"} – {filters.maxPrice ? fmt(filters.maxPrice) : "∞"}
                    <button onClick={() => setFilters({ ...filters, minPrice: undefined, maxPrice: undefined, page: 1 })} className="ml-1 hover:text-white">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {filters.bedrooms > 0 && (
                  <span className="flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">
                    {filters.bedrooms}+ beds
                    <button onClick={() => setFilters({ ...filters, bedrooms: 0, page: 1 })} className="ml-1 hover:text-white">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {filters.bathrooms > 0 && (
                  <span className="flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">
                    {filters.bathrooms}+ baths
                    <button onClick={() => setFilters({ ...filters, bathrooms: 0, page: 1 })} className="ml-1 hover:text-white">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {filters.featuredOnly && (
                  <span className="flex items-center gap-1 rounded-full bg-gold-500/20 px-3 py-1 text-xs text-gold-400">
                    Gold only
                    <button onClick={() => setFilters({ ...filters, featuredOnly: false, page: 1 })} className="ml-1 hover:text-gold-300">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
              </div>
            )}

            {/* Grid */}
            {loading ? (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 12 }).map((_, i) => (
                  <div key={i} className="glass-card animate-pulse rounded-2xl">
                    <div className="h-52 rounded-t-2xl bg-white/5" />
                    <div className="space-y-3 p-4">
                      <div className="h-3 w-24 rounded bg-white/5" />
                      <div className="h-4 w-3/4 rounded bg-white/5" />
                      <div className="h-6 w-1/2 rounded bg-white/5" />
                    </div>
                  </div>
                ))}
              </div>
            ) : properties.length === 0 ? (
              <div className="rounded-2xl border border-white/10 bg-[#0a0a0a] p-16 text-center">
                <Search className="mx-auto mb-4 h-12 w-12 text-white/20" />
                <h3 className="mb-2 text-lg font-bold text-white/80">No properties found</h3>
                <p className="text-sm text-white/40">
                  Try adjusting your filters or search terms.
                </p>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {properties.map((p) => (
                  <PropertyCard key={p.id} property={p} />
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <button
                  disabled={filters.page <= 1}
                  onClick={() => setFilters({ ...filters, page: Math.max(1, filters.page - 1) })}
                  className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white/60 transition disabled:opacity-30 hover:bg-white/10"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <span className="px-3 text-sm text-white/50">
                  Page <span className="font-semibold text-white">{filters.page}</span> of {totalPages}
                </span>
                <button
                  disabled={filters.page >= totalPages}
                  onClick={() => setFilters({ ...filters, page: Math.min(totalPages, filters.page + 1) })}
                  className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white/60 transition disabled:opacity-30 hover:bg-white/10"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Mobile Filter Drawer ───────────────────── */}
      {mobileFilters && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={() => setMobileFilters(false)}
          />
          <div className="absolute inset-y-0 left-0 w-80 overflow-y-auto bg-[#0a0a0a] p-6 shadow-2xl">
            <FilterSidebar
              filters={filters}
              setFilters={setFilters}
              departments={departments}
              municipios={municipios}
              onClose={() => setMobileFilters(false)}
            />
          </div>
        </div>
      )}
    </main>
  );
}
