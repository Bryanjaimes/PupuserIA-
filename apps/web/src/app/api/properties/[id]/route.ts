import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

/* ═══════════════════════════════════════════════════════
   GET /api/properties/:id
   Returns a single property by its ID.
   ═══════════════════════════════════════════════════════ */

let cached: Record<string, unknown>[] | null = null;
function load() {
  if (cached) return cached;
  const p = path.join(process.cwd(), "public", "data", "properties.json");
  cached = JSON.parse(fs.readFileSync(p, "utf-8"));
  return cached!;
}

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const props = load();
  const property = props.find((p) => p.id === id);

  if (!property) {
    return NextResponse.json({ error: "Property not found" }, { status: 404 });
  }

  return NextResponse.json(property);
}
