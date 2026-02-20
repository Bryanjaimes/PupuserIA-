"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
  MapPin,
  BedDouble,
  Bath,
  Maximize,
  TreePine,
  TrendingUp,
  Star,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Loader2,
  ArrowLeft,
  Home,
  Tag,
  Ruler,
  Globe,
} from "lucide-react";
import { departmentFromSlug, toSlug } from "@/lib/property-slugs";

/* ═══════════════════════════════════════════════════════
   Property Detail — /explore/[dept]/[muni]/[id]
   Full image gallery, all details, map, and source link.
   ═══════════════════════════════════════════════════════ */

const PropertyExplorerMap = dynamic(
  () => import("@/components/property-explorer-map"),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full w-full items-center justify-center bg-white/10 rounded-2xl">
        <Loader2 className="h-6 w-6 animate-spin text-sv-300" />
      </div>
    ),
  },
);

// ── Helpers ──────────────────────────────────────────

function fmt(n: number | null | undefined): string {
  if (!n) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

function fmtArea(m2: number | null | undefined): string {
  if (!m2) return "—";
  if (m2 >= 10000) return `${(m2 / 10000).toFixed(1)} ha`;
  return `${m2.toLocaleString()} m²`;
}

function featureLabel(f: string): string {
  return f.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// ── Types ────────────────────────────────────────────

interface PropertyDetail {
  id: string;
  title: string;
  title_es: string;
  department: string;
  municipio: string;
  price_usd: number | null;
  ai_valuation_usd: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  area_m2: number | null;
  lot_size_m2: number | null;
  property_type: string;
  latitude: number;
  longitude: number;
  thumbnail_url: string | null;
  images: string[];
  is_featured: boolean;
  neighborhood_score: number | null;
  features: string[];
  description: string | null;
  description_es: string | null;
  source: string | null;
  source_url: string | null;
}

// ── Page ─────────────────────────────────────────────

export default function PropertyDetailPage() {
  const params = useParams<{
    department: string;
    municipio: string;
    id: string;
  }>();
  const deptSlug = params.department;
  const muniSlug = params.municipio;
  const propertyId = params.id;
  const deptName = departmentFromSlug(deptSlug);

  const [property, setProperty] = useState<PropertyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [mainImg, setMainImg] = useState(0);

  useEffect(() => {
    fetch(`/api/properties/${propertyId}`)
      .then((r) => {
        if (!r.ok) throw new Error("not found");
        return r.json();
      })
      .then((data) => {
        setProperty(data);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [propertyId]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#0a0a0a] pt-20">
        <Loader2 className="h-10 w-10 animate-spin text-sv-400" />
      </main>
    );
  }

  if (error || !property) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#0a0a0a] pt-20">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white/90">Property not found</h1>
          <Link
            href={`/explore/${deptSlug}`}
            className="mt-4 inline-block text-sm text-gold-400 hover:underline"
          >
            ← Back to {deptName || "department"}
          </Link>
        </div>
      </main>
    );
  }

  const images =
    property.images.length > 0
      ? property.images
      : property.thumbnail_url
        ? [property.thumbnail_url]
        : ["https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"];

  const muniName = property.municipio || muniSlug.replace(/-/g, " ");

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20 animate-[fadeIn_0.4s_ease-out]">
      <div className="mx-auto max-w-6xl px-6 py-8">
        {/* ── Breadcrumb ─────────────────────────── */}
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
          <Link
            href={`/explore/${deptSlug}/${muniSlug}`}
            className="hover:text-sv-800 transition"
          >
            {muniName}
          </Link>
          <ChevronRight className="h-3 w-3 text-sv-300" />
          <span className="font-medium text-white/60 truncate max-w-[200px]">
            Property
          </span>
        </nav>

        {/* ═══════════════════════════════════════════
            IMAGE GALLERY
            ═══════════════════════════════════════════ */}
        <div className="mb-8">
          {/* Main Image */}
          <div className="relative overflow-hidden rounded-2xl bg-white/10" style={{ height: 420 }}>
            <Image
              src={images[mainImg]}
              alt={property.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 900px"
              priority
              unoptimized
            />
            {/* Nav arrows */}
            {images.length > 1 && (
              <>
                <button
                  onClick={() =>
                    setMainImg((i) =>
                      i === 0 ? images.length - 1 : i - 1,
                    )
                  }
                  className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-black/90 p-2 shadow-lg transition hover:bg-[#0a0a0a]"
                  aria-label="Previous"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <button
                  onClick={() =>
                    setMainImg((i) =>
                      i === images.length - 1 ? 0 : i + 1,
                    )
                  }
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-black/90 p-2 shadow-lg transition hover:bg-[#0a0a0a]"
                  aria-label="Next"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
                <div className="absolute bottom-3 right-3 rounded-full bg-black/60 px-3 py-1 text-sm text-white">
                  {mainImg + 1} / {images.length}
                </div>
              </>
            )}
            {/* Badges */}
            <div className="absolute left-3 top-3 flex gap-2">
              {property.is_featured && (
                <span className="flex items-center gap-1 rounded-full bg-gold-500/100 px-3 py-1 text-xs font-semibold text-white shadow-lg">
                  <Star className="h-3 w-3" /> Featured
                </span>
              )}
              <span className="rounded-full bg-black/90 px-3 py-1 text-xs font-medium capitalize text-sv-800">
                {property.property_type}
              </span>
            </div>
          </div>

          {/* Thumbnail Strip */}
          {images.length > 1 && (
            <div className="mt-3 flex gap-2 overflow-x-auto pb-2">
              {images.map((img, i) => (
                <button
                  key={i}
                  onClick={() => setMainImg(i)}
                  className={`relative h-16 w-24 flex-shrink-0 overflow-hidden rounded-lg transition ${
                    i === mainImg
                      ? "ring-2 ring-gold-500 ring-offset-2"
                      : "opacity-60 hover:opacity-100"
                  }`}
                >
                  <Image
                    src={img}
                    alt={`Photo ${i + 1}`}
                    fill
                    className="object-cover"
                    sizes="96px"
                    unoptimized
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* ═══════════════════════════════════════════
            DETAILS GRID
            ═══════════════════════════════════════════ */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* ── Left: Title, Description ────────── */}
          <div className="lg:col-span-2">
            {/* Location */}
            <div className="mb-2 flex items-center gap-1.5 text-sm text-sv-500">
              <MapPin className="h-4 w-4" />
              {muniName}, {property.department}
            </div>

            {/* Title */}
            <h1 className="mb-4 text-2xl font-extrabold text-white md:text-3xl leading-tight">
              {property.title}
            </h1>

            {/* Price */}
            <div className="mb-6 flex flex-wrap items-baseline gap-3">
              <span className="text-3xl font-extrabold text-white">
                {fmt(property.price_usd)}
              </span>
              {property.ai_valuation_usd != null && (
                <span className="flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700">
                  <TrendingUp className="h-3.5 w-3.5" />
                  AI Valuation: {fmt(property.ai_valuation_usd)}
                </span>
              )}
            </div>

            {/* Stats pills */}
            <div className="mb-6 flex flex-wrap gap-3">
              {property.bedrooms != null && (
                <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-[#0a0a0a] px-4 py-2">
                  <BedDouble className="h-4 w-4 text-sv-500" />
                  <div>
                    <div className="text-sm font-bold text-white/90">{property.bedrooms}</div>
                    <div className="text-[10px] text-sv-500">Bedrooms</div>
                  </div>
                </div>
              )}
              {property.bathrooms != null && (
                <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-[#0a0a0a] px-4 py-2">
                  <Bath className="h-4 w-4 text-sv-500" />
                  <div>
                    <div className="text-sm font-bold text-white/90">{property.bathrooms}</div>
                    <div className="text-[10px] text-sv-500">Bathrooms</div>
                  </div>
                </div>
              )}
              {property.area_m2 != null && (
                <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-[#0a0a0a] px-4 py-2">
                  <Maximize className="h-4 w-4 text-sv-500" />
                  <div>
                    <div className="text-sm font-bold text-white/90">{fmtArea(property.area_m2)}</div>
                    <div className="text-[10px] text-sv-500">Living Area</div>
                  </div>
                </div>
              )}
              {property.lot_size_m2 != null && property.lot_size_m2 > 0 && (
                <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-[#0a0a0a] px-4 py-2">
                  <Ruler className="h-4 w-4 text-sv-500" />
                  <div>
                    <div className="text-sm font-bold text-white/90">{fmtArea(property.lot_size_m2)}</div>
                    <div className="text-[10px] text-sv-500">Lot Size</div>
                  </div>
                </div>
              )}
            </div>

            {/* Description */}
            {property.description && (
              <div className="mb-8">
                <h2 className="mb-3 text-lg font-bold text-white/90">Description</h2>
                <div className="prose prose-sm max-w-none text-white/60 leading-relaxed whitespace-pre-line">
                  {property.description}
                </div>
              </div>
            )}
            {property.description_es && property.description_es !== property.description && (
              <div className="mb-8">
                <h2 className="mb-3 text-lg font-bold text-white/90">
                  Descripción
                </h2>
                <div className="prose prose-sm max-w-none text-white/60 leading-relaxed whitespace-pre-line">
                  {property.description_es}
                </div>
              </div>
            )}

            {/* Features */}
            {property.features.length > 0 && (
              <div className="mb-8">
                <h2 className="mb-3 text-lg font-bold text-white/90">Features</h2>
                <div className="flex flex-wrap gap-2">
                  {property.features.map((f) => (
                    <span
                      key={f}
                      className="flex items-center gap-1.5 rounded-full border border-white/10 bg-[#0a0a0a] px-3 py-1.5 text-xs font-medium text-white/60"
                    >
                      <Tag className="h-3 w-3 text-sv-400" />
                      {featureLabel(f)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ── Right Sidebar ────────────────────── */}
          <div className="space-y-5">
            {/* Quick Info Card */}
            <div className="glass-card rounded-2xl p-5">
              <h3 className="mb-4 text-sm font-bold uppercase tracking-wider text-sv-500">
                Property Details
              </h3>
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="flex items-center gap-1.5 text-sv-500">
                    <Home className="h-3.5 w-3.5" /> Type
                  </dt>
                  <dd className="font-semibold capitalize text-white/90">
                    {property.property_type}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="flex items-center gap-1.5 text-sv-500">
                    <MapPin className="h-3.5 w-3.5" /> Department
                  </dt>
                  <dd className="font-semibold text-white/90">
                    {property.department}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="flex items-center gap-1.5 text-sv-500">
                    <MapPin className="h-3.5 w-3.5" /> Municipality
                  </dt>
                  <dd className="font-semibold text-white/90">{muniName}</dd>
                </div>
                {/* source kept in DB for internal tracking — not shown to users */}
              </dl>

              {/* Neighborhood score */}
              {property.neighborhood_score != null && (
                <div className="mt-5 border-t border-white/10 pt-4">
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className="text-sv-500">Neighborhood Score</span>
                    <span className="font-bold text-gold-700">
                      {property.neighborhood_score}/10
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-gold-400 to-gold-500"
                      style={{
                        width: `${(property.neighborhood_score / 10) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Map */}
            {property.latitude !== 0 && property.longitude !== 0 && (
              <div className="overflow-hidden rounded-2xl border border-white/10 shadow" style={{ height: 240 }}>
                <PropertyExplorerMap
                  center={[property.latitude, property.longitude]}
                  zoom={14}
                  markers={[
                    {
                      lat: property.latitude,
                      lng: property.longitude,
                      label: muniName,
                      color: "#0047ab",
                      size: "md",
                    },
                  ]}
                  showBorder={false}
                  className="h-full w-full"
                />
              </div>
            )}

            {/* View Original */}
            {property.source_url && (
              <a
                href={property.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-sv-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sv-800"
              >
                <ExternalLink className="h-4 w-4" />
                View Original Listing
              </a>
            )}

            {/* Back link */}
            <Link
              href={`/explore/${deptSlug}/${muniSlug}`}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-[#0a0a0a] px-5 py-3 text-sm font-semibold text-white/60 transition hover:bg-white/5"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to {muniName} listings
            </Link>
          </div>
        </div>

        {/* ── All Images Section ───────────────── */}
        {images.length > 3 && (
          <section className="mt-12 border-t border-white/10 pt-8">
            <h2 className="mb-4 text-lg font-bold text-white/90">
              All Photos ({images.length})
            </h2>
            <div className="columns-2 gap-3 sm:columns-3 lg:columns-4">
              {images.map((img, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setMainImg(i);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                  className="mb-3 block w-full break-inside-avoid overflow-hidden rounded-xl transition hover:opacity-90"
                >
                  <Image
                    src={img}
                    alt={`${property.title} — Photo ${i + 1}`}
                    width={400}
                    height={300}
                    className="w-full rounded-xl object-cover"
                    unoptimized
                  />
                </button>
              ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
