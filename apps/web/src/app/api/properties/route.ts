import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

/* ═══════════════════════════════════════════════════════
   GET /api/properties
   Serves scraped properties from public/data/properties.json
   with filtering, sorting, and pagination.
   ═══════════════════════════════════════════════════════ */

interface Property {
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
  description: string;
  description_es: string;
  source: string;
  source_url: string;
}

let cachedProperties: Property[] | null = null;

function loadProperties(): Property[] {
  if (cachedProperties) return cachedProperties;
  const filePath = path.join(process.cwd(), "public", "data", "properties.json");
  const raw = fs.readFileSync(filePath, "utf-8");
  cachedProperties = JSON.parse(raw) as Property[];
  return cachedProperties;
}

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;

  const department = searchParams.get("department");
  const municipio = searchParams.get("municipio");
  const minPrice = searchParams.get("min_price");
  const maxPrice = searchParams.get("max_price");
  const propertyType = searchParams.get("property_type");
  const bedrooms = searchParams.get("bedrooms");
  const featuredOnly = searchParams.get("featured_only");
  const sortBy = searchParams.get("sort_by") || "newest";
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "20", 10);
  const search = searchParams.get("q");

  let properties = loadProperties();

  // ── Filter ──
  if (department) {
    properties = properties.filter(
      (p) => p.department.toLowerCase() === department.toLowerCase()
    );
  }
  if (municipio) {
    properties = properties.filter(
      (p) => p.municipio.toLowerCase().includes(municipio.toLowerCase())
    );
  }
  if (minPrice) {
    const min = parseFloat(minPrice);
    properties = properties.filter((p) => (p.price_usd ?? 0) >= min);
  }
  if (maxPrice) {
    const max = parseFloat(maxPrice);
    properties = properties.filter((p) => (p.price_usd ?? Infinity) <= max);
  }
  if (propertyType) {
    properties = properties.filter(
      (p) => p.property_type.toLowerCase() === propertyType.toLowerCase()
    );
  }
  if (bedrooms) {
    const beds = parseInt(bedrooms, 10);
    properties = properties.filter((p) => (p.bedrooms ?? 0) >= beds);
  }
  if (featuredOnly === "true") {
    properties = properties.filter((p) => p.is_featured);
  }
  if (search) {
    const q = search.toLowerCase();
    properties = properties.filter(
      (p) =>
        p.title.toLowerCase().includes(q) ||
        p.department.toLowerCase().includes(q) ||
        p.municipio.toLowerCase().includes(q) ||
        (p.description || "").toLowerCase().includes(q)
    );
  }

  // ── Sort ──
  switch (sortBy) {
    case "price_asc":
      properties.sort((a, b) => (a.price_usd ?? 0) - (b.price_usd ?? 0));
      break;
    case "price_desc":
      properties.sort((a, b) => (b.price_usd ?? 0) - (a.price_usd ?? 0));
      break;
    case "score":
      properties.sort((a, b) => {
        const sa = (a.is_featured ? 100 : 0) + (a.images.length * 5) + (a.description ? 20 : 0);
        const sb = (b.is_featured ? 100 : 0) + (b.images.length * 5) + (b.description ? 20 : 0);
        return sb - sa;
      });
      break;
    case "newest":
    default:
      // Already in order from the JSONL
      break;
  }

  // ── Paginate ──
  const total = properties.length;
  const start = (page - 1) * pageSize;
  const results = properties.slice(start, start + pageSize);

  return NextResponse.json({ total, page, page_size: pageSize, results });
}
