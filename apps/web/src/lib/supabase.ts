import { createClient } from "@supabase/supabase-js";

/* ═══════════════════════════════════════════════════════
   Supabase Client — PupuserIA

   Browser client (anon key) for public reads.
   Server client (service key) for writes/admin.

   Connect by setting .env.local:
     NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
     NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
   ═══════════════════════════════════════════════════════ */

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

/**
 * Public (browser) Supabase client.
 * Uses anon key — respects RLS policies.
 * Returns null if env vars not configured yet.
 */
export function getSupabaseClient() {
  if (!supabaseUrl || !supabaseAnonKey) return null;
  return createClient(supabaseUrl, supabaseAnonKey);
}

/**
 * Server-side Supabase client with service role key.
 * Bypasses RLS — use only in API routes / server actions.
 */
export function getSupabaseAdmin() {
  const serviceKey = process.env.SUPABASE_SERVICE_KEY || "";
  if (!supabaseUrl || !serviceKey) return null;
  return createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false },
  });
}

/**
 * Check if Supabase is configured.
 */
export function isSupabaseConfigured(): boolean {
  return Boolean(supabaseUrl && supabaseAnonKey);
}

/**
 * Property image URL helper.
 * Returns Supabase Storage URL if available, otherwise original CDN URL.
 */
export function getImageUrl(
  originalUrl: string,
  storagePath?: string
): string {
  if (storagePath && supabaseUrl) {
    return `${supabaseUrl}/storage/v1/object/public/${storagePath}`;
  }
  return originalUrl;
}

/* ── Types matching the Supabase schema ────────────── */

export interface PropertyRow {
  id: string;
  title: string;
  title_es: string;
  description: string;
  description_es: string;
  english_summary: string | null;
  department: string;
  municipio: string;
  address: string;
  latitude: number;
  longitude: number;
  price_usd: number | null;
  ai_valuation_usd: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  area_m2: number | null;
  lot_size_m2: number | null;
  property_type: string;
  thumbnail_url: string | null;
  images: string[];
  images_storage: string[];
  is_featured: boolean;
  neighborhood_score: number;
  completeness_score: number;
  quality_tier: string;
  missing_fields: string[];
  ad_ready: boolean;
  impact_score: number | null;
  is_single_story: boolean | null;
  needs_remodel: boolean | null;
  ideal_for: string[];
  family_friendly_score: number | null;
  investment_potential: number | null;
  surf_proximity: string;
  walkability_estimate: string;
  embedding: number[] | null;
  source: string | null;
  source_url: string | null;
  seller: string | null;
  is_active: boolean;
  listing_date: string | null;
  last_checked_at: string | null;
  freshness_status: string;
  created_at: string;
  updated_at: string;
}

/* ── Vector search helper ──────────────────────────── */

export async function semanticSearch(
  queryText: string,
  options?: {
    department?: string;
    maxPrice?: number;
    bedrooms?: number;
    limit?: number;
  }
) {
  const client = getSupabaseClient();
  if (!client) return [];

  // In production: call your own API route that generates the embedding server-side
  // For now this is a placeholder showing the Supabase RPC call structure
  const { data, error } = await client.rpc("match_properties", {
    query_embedding: [], // TODO: generate via /api/embed endpoint
    match_threshold: 0.7,
    match_count: options?.limit || 10,
    filter_department: options?.department || null,
    filter_max_price: options?.maxPrice || null,
    filter_bedrooms: options?.bedrooms || null,
  });

  if (error) {
    console.error("Semantic search error:", error);
    return [];
  }

  return data || [];
}
