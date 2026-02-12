import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

let cached: any[] | null = null;

function load() {
  if (cached) return cached;
  const p = path.join(process.cwd(), "public", "data", "properties.json");
  cached = JSON.parse(fs.readFileSync(p, "utf-8"));
  return cached!;
}

export async function GET(request: NextRequest) {
  const limit = parseInt(request.nextUrl.searchParams.get("limit") || "8", 10);
  const props = load();
  const featured = props
    .filter((p: any) => p.is_featured)
    .sort((a: any, b: any) => {
      const sa = (a.images?.length || 0) * 5 + (a.description ? 20 : 0) + (a.price_usd || 0) / 100000;
      const sb = (b.images?.length || 0) * 5 + (b.description ? 20 : 0) + (b.price_usd || 0) / 100000;
      return sb - sa;
    })
    .slice(0, limit);

  return NextResponse.json(featured);
}
