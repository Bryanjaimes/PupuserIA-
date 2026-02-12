import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

interface Property {
  price_usd: number | null;
  department: string;
  property_type: string;
  is_featured: boolean;
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
  const prices = props.map((p) => p.price_usd).filter((p): p is number => p != null && p > 0);
  const byType: Record<string, number> = {};
  const depts = new Set<string>();

  for (const p of props) {
    if (p.property_type) byType[p.property_type] = (byType[p.property_type] || 0) + 1;
    if (p.department) depts.add(p.department);
  }

  return NextResponse.json({
    total_listings: props.length,
    avg_price_usd: prices.length ? Math.round(prices.reduce((a, b) => a + b, 0) / prices.length) : null,
    min_price_usd: prices.length ? Math.min(...prices) : null,
    max_price_usd: prices.length ? Math.max(...prices) : null,
    departments_covered: depts.size,
    featured_count: props.filter((p) => p.is_featured).length,
    by_type: byType,
  });
}
