import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

/* ═══════════════════════════════════════════════════════
   GET /api/properties/departments
   Returns per-department aggregations: count, avg price,
   center coordinates, and municipality breakdown.
   ═══════════════════════════════════════════════════════ */

interface Property {
  department: string;
  municipio: string;
  price_usd: number | null;
  thumbnail_url: string | null;
  images: string[];
  is_featured: boolean;
}

/** Department center coordinates [lng, lat] — from DEPARTMENT_LABELS */
const CENTERS: Record<string, [number, number]> = {
  Ahuachapán: [-89.84, 13.92],
  "Santa Ana": [-89.56, 14.03],
  Sonsonate: [-89.72, 13.72],
  Chalatenango: [-88.94, 14.17],
  "La Libertad": [-89.32, 13.6],
  "San Salvador": [-89.19, 13.7],
  Cuscatlán: [-88.93, 13.73],
  "La Paz": [-88.93, 13.44],
  Cabañas: [-88.74, 13.96],
  "San Vicente": [-88.72, 13.63],
  Usulután: [-88.46, 13.44],
  "San Miguel": [-88.2, 13.58],
  Morazán: [-88.1, 13.82],
  "La Unión": [-87.84, 13.55],
};

function toSlug(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "");
}

let cached: Property[] | null = null;
function load(): Property[] {
  if (cached) return cached;
  const p = path.join(process.cwd(), "public", "data", "properties.json");
  cached = JSON.parse(fs.readFileSync(p, "utf-8"));
  return cached!;
}

export async function GET() {
  const props = load();

  const map = new Map<
    string,
    {
      count: number;
      prices: number[];
      municipios: Map<string, number>;
      sampleImg: string | null;
    }
  >();

  for (const p of props) {
    const dept = p.department || "Unknown";
    if (!map.has(dept))
      map.set(dept, { count: 0, prices: [], municipios: new Map(), sampleImg: null });
    const d = map.get(dept)!;
    d.count++;
    if (p.price_usd && p.price_usd > 0) d.prices.push(p.price_usd);
    const muni = p.municipio || "Other";
    d.municipios.set(muni, (d.municipios.get(muni) || 0) + 1);
    if (!d.sampleImg && (p.thumbnail_url || p.images?.[0]))
      d.sampleImg = p.thumbnail_url || p.images[0];
  }

  const departments = Array.from(map.entries())
    .map(([name, d]) => {
      const center = CENTERS[name];
      return {
        name,
        slug: toSlug(name),
        count: d.count,
        avg_price: d.prices.length
          ? Math.round(d.prices.reduce((a, b) => a + b, 0) / d.prices.length)
          : null,
        center: center ? [center[1], center[0]] : null, // swap to [lat, lng]
        sample_image: d.sampleImg,
        municipalities: Array.from(d.municipios.entries())
          .map(([mn, mc]) => ({ name: mn, slug: toSlug(mn), count: mc }))
          .sort((a, b) => b.count - a.count),
      };
    })
    .sort((a, b) => b.count - a.count);

  return NextResponse.json({ departments, total: props.length });
}
