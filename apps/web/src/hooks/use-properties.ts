"use client";

import { useEffect, useState, useCallback } from "react";

/* ═══════════════════════════════════════════════════════
   Properties Hook — fetches real estate listings
   from the FastAPI backend with filtering support.
   ═══════════════════════════════════════════════════════ */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ────────────────────────────────────────────

export interface PropertyListing {
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
}

export interface PropertyDetail extends PropertyListing {
  description: string | null;
  description_es: string | null;
  ai_confidence: number | null;
  rental_yield_estimate: number | null;
  appreciation_5yr_estimate: number | null;
  listing_url: string | null;
  source: string | null;
}

export interface PropertyStats {
  total_listings: number;
  avg_price_usd: number | null;
  min_price_usd: number | null;
  max_price_usd: number | null;
  departments_covered: number;
  featured_count: number;
  by_type: Record<string, number>;
}

export interface PropertySearchParams {
  department?: string;
  municipio?: string;
  min_price?: number;
  max_price?: number;
  property_type?: string;
  bedrooms?: number;
  featured_only?: boolean;
  sort_by?: "newest" | "price_asc" | "price_desc" | "score";
  page?: number;
  page_size?: number;
}

// ── Hook: useProperties ──────────────────────────────

export function useProperties(params: PropertySearchParams = {}) {
  const [properties, setProperties] = useState<PropertyListing[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProperties = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const searchParams = new URLSearchParams();
      if (params.department) searchParams.set("department", params.department);
      if (params.municipio) searchParams.set("municipio", params.municipio);
      if (params.min_price !== undefined) searchParams.set("min_price", params.min_price.toString());
      if (params.max_price !== undefined) searchParams.set("max_price", params.max_price.toString());
      if (params.property_type) searchParams.set("property_type", params.property_type);
      if (params.bedrooms !== undefined) searchParams.set("bedrooms", params.bedrooms.toString());
      if (params.featured_only) searchParams.set("featured_only", "true");
      if (params.sort_by) searchParams.set("sort_by", params.sort_by);
      searchParams.set("page", (params.page || 1).toString());
      searchParams.set("page_size", (params.page_size || 20).toString());

      const res = await fetch(`${API_BASE}/api/v1/properties/?${searchParams}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setProperties(data.results);
      setTotal(data.total);
    } catch (err) {
      console.error("Failed to fetch properties:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
      setProperties([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [
    params.department,
    params.municipio,
    params.min_price,
    params.max_price,
    params.property_type,
    params.bedrooms,
    params.featured_only,
    params.sort_by,
    params.page,
    params.page_size,
  ]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  return { properties, total, loading, error, refetch: fetchProperties };
}

// ── Hook: usePropertyStats ──────────────────────────

export function usePropertyStats() {
  const [stats, setStats] = useState<PropertyStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/properties/stats`);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        setStats(await res.json());
      } catch (err) {
        console.error("Failed to fetch property stats:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return { stats, loading };
}

// ── Hook: useFeaturedProperties ─────────────────────

export function useFeaturedProperties(limit = 8) {
  const [featured, setFeatured] = useState<PropertyListing[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/properties/featured?limit=${limit}`);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        setFeatured(await res.json());
      } catch (err) {
        console.error("Failed to fetch featured properties:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [limit]);

  return { featured, loading };
}
