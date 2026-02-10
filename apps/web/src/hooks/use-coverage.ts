"use client";

import { useEffect, useState, useCallback } from "react";

/* ═══════════════════════════════════════════════════════
   Coverage Gap Hook — fetches data coverage info
   from the FastAPI backend. Falls back to static data
   when backend is unavailable.
   ═══════════════════════════════════════════════════════ */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ────────────────────────────────────────────

export interface CoverageGap {
  id: string;
  municipio_id: number;
  municipio_name: string;
  department_name: string;
  category: string;
  coverage_score: number;
  total_listings: number;
  listings_with_price: number;
  listings_with_images: number;
  listings_with_coordinates: number;
  avg_images_per_listing: number;
  priority: "critical" | "high" | "medium" | "low";
  needs_field_research: boolean;
  field_research_status: string;
  field_researcher: string | null;
  field_research_notes: string | null;
  field_research_date: string | null;
  last_analyzed: string | null;
}

export interface DepartmentCoverage {
  department_id: number;
  department_name: string;
  total_municipios: number;
  population: number | null;
  area_km2: number | null;
  avg_coverage_score: number;
  critical_gaps: number;
  high_gaps: number;
  medium_gaps: number;
  low_gaps: number;
  municipios_needing_research: number;
  categories_covered: Record<string, number>;
}

export interface DataDesertZone {
  zone_name: string;
  department: string;
  municipios: string[];
  notes: string;
  priority: string;
}

export interface CoverageOverview {
  total_departments: number;
  total_municipios: number;
  total_gap_records: number;
  avg_coverage_score: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  municipios_needing_research: number;
  data_desert_zones: DataDesertZone[];
}

// ── Static fallback data (used when API is not running) ────

const STATIC_OVERVIEW: CoverageOverview = {
  total_departments: 14,
  total_municipios: 262,
  total_gap_records: 2096,
  avg_coverage_score: 0.0,
  critical_count: 32,
  high_count: 46,
  medium_count: 61,
  low_count: 123,
  municipios_needing_research: 262,
  data_desert_zones: [
    {
      zone_name: "Northern Morazan Mountains",
      department: "Morazan",
      municipios: ["Perquin", "Arambala", "Meanguera", "Joateca", "Torola", "San Fernando", "Jocoaitique"],
      notes: "Remote mountainous terrain, Ruta de Paz area. Former conflict zone. Very few real estate listings or street imagery.",
      priority: "critical",
    },
    {
      zone_name: "Northern Chalatenango Border",
      department: "Chalatenango",
      municipios: ["Citala", "San Ignacio", "La Palma", "San Fernando", "Dulce Nombre de Maria", "Arcatao", "Las Vueltas", "Las Flores"],
      notes: "Rural highlands near Honduras border. Limited internet. Some ecotourism (La Palma artisan town).",
      priority: "high",
    },
    {
      zone_name: "Cabanas Interior",
      department: "Cabanas",
      municipios: ["Cinquera", "Victoria", "Dolores", "Guacotecti", "San Isidro", "Tejutepeque"],
      notes: "Least-visited department. Former guerrilla territory. Cinquera forest reserve. Very few online listings.",
      priority: "critical",
    },
    {
      zone_name: "La Union Eastern Coast",
      department: "La Union",
      municipios: ["Meanguera del Golfo", "Intipuca", "Conchagua", "Bolivar", "Nueva Esparta"],
      notes: "Islands in Gulf of Fonseca. Intipuca = remittance town. Conchagua volcano area.",
      priority: "high",
    },
    {
      zone_name: "Northern Usulutan / San Miguel",
      department: "San Miguel",
      municipios: ["Carolina", "Nuevo Eden de San Juan", "San Luis de la Reina", "San Antonio", "Sesori"],
      notes: "Remote eastern highlands. Very limited road access. Almost zero online real estate presence.",
      priority: "critical",
    },
    {
      zone_name: "Sonsonate Indigenous Areas",
      department: "Sonsonate",
      municipios: ["Cuisnahuat", "Santa Isabel Ishutan", "Santo Domingo de Guzman", "Santa Catarina Masahuat"],
      notes: "Indigenous Nahua-Pipil communities. Rich cultural heritage but limited digital presence.",
      priority: "high",
    },
  ],
};

const STATIC_DEPARTMENTS: DepartmentCoverage[] = [
  { department_id: 1, department_name: "Ahuachapan", total_municipios: 12, population: 339081, area_km2: 1239.6, avg_coverage_score: 0, critical_gaps: 8, high_gaps: 16, medium_gaps: 24, low_gaps: 48, municipios_needing_research: 12, categories_covered: {} },
  { department_id: 2, department_name: "Santa Ana", total_municipios: 13, population: 588498, area_km2: 2023.2, avg_coverage_score: 0, critical_gaps: 24, high_gaps: 16, medium_gaps: 24, low_gaps: 40, municipios_needing_research: 13, categories_covered: {} },
  { department_id: 3, department_name: "Sonsonate", total_municipios: 16, population: 474400, area_km2: 1225.8, avg_coverage_score: 0, critical_gaps: 16, high_gaps: 24, medium_gaps: 32, low_gaps: 56, municipios_needing_research: 16, categories_covered: {} },
  { department_id: 4, department_name: "Chalatenango", total_municipios: 33, population: 193800, area_km2: 2016.6, avg_coverage_score: 0, critical_gaps: 0, high_gaps: 8, medium_gaps: 40, low_gaps: 216, municipios_needing_research: 33, categories_covered: {} },
  { department_id: 5, department_name: "La Libertad", total_municipios: 22, population: 831300, area_km2: 1652.9, avg_coverage_score: 0, critical_gaps: 48, high_gaps: 32, medium_gaps: 48, low_gaps: 48, municipios_needing_research: 22, categories_covered: {} },
  { department_id: 6, department_name: "San Salvador", total_municipios: 19, population: 2084000, area_km2: 886.2, avg_coverage_score: 0, critical_gaps: 80, high_gaps: 24, medium_gaps: 24, low_gaps: 24, municipios_needing_research: 19, categories_covered: {} },
  { department_id: 7, department_name: "Cuscatlan", total_municipios: 16, population: 258200, area_km2: 756.2, avg_coverage_score: 0, critical_gaps: 16, high_gaps: 16, medium_gaps: 40, low_gaps: 56, municipios_needing_research: 16, categories_covered: {} },
  { department_id: 8, department_name: "La Paz", total_municipios: 22, population: 369600, area_km2: 1223.6, avg_coverage_score: 0, critical_gaps: 8, high_gaps: 24, medium_gaps: 48, low_gaps: 96, municipios_needing_research: 22, categories_covered: {} },
  { department_id: 9, department_name: "Cabanas", total_municipios: 9, population: 168300, area_km2: 1103.5, avg_coverage_score: 0, critical_gaps: 8, high_gaps: 8, medium_gaps: 16, low_gaps: 40, municipios_needing_research: 9, categories_covered: {} },
  { department_id: 10, department_name: "San Vicente", total_municipios: 13, population: 183900, area_km2: 1184.0, avg_coverage_score: 0, critical_gaps: 8, high_gaps: 8, medium_gaps: 32, low_gaps: 56, municipios_needing_research: 13, categories_covered: {} },
  { department_id: 11, department_name: "Usulutan", total_municipios: 23, population: 354000, area_km2: 2130.4, avg_coverage_score: 0, critical_gaps: 16, high_gaps: 16, medium_gaps: 48, low_gaps: 104, municipios_needing_research: 23, categories_covered: {} },
  { department_id: 12, department_name: "San Miguel", total_municipios: 20, population: 496500, area_km2: 2077.1, avg_coverage_score: 0, critical_gaps: 8, high_gaps: 16, medium_gaps: 40, low_gaps: 96, municipios_needing_research: 20, categories_covered: {} },
  { department_id: 13, department_name: "Morazan", total_municipios: 26, population: 190300, area_km2: 1447.4, avg_coverage_score: 0, critical_gaps: 0, high_gaps: 0, medium_gaps: 24, low_gaps: 184, municipios_needing_research: 26, categories_covered: {} },
  { department_id: 14, department_name: "La Union", total_municipios: 18, population: 246900, area_km2: 2074.3, avg_coverage_score: 0, critical_gaps: 0, high_gaps: 16, medium_gaps: 24, low_gaps: 104, municipios_needing_research: 18, categories_covered: {} },
];

// ── Hook ─────────────────────────────────────────────

export function useCoverageOverview() {
  const [data, setData] = useState<CoverageOverview>(STATIC_OVERVIEW);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch_ = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/coverage/overview`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setData(await res.json());
      setError(null);
    } catch {
      // Fall back to static data
      setData(STATIC_OVERVIEW);
      setError("Using offline data — API not available");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch_(); }, [fetch_]);
  return { data, loading, error, refetch: fetch_ };
}

export function useDepartmentCoverage() {
  const [data, setData] = useState<DepartmentCoverage[]>(STATIC_DEPARTMENTS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch_ = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/coverage/departments`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setData(await res.json());
      setError(null);
    } catch {
      setData(STATIC_DEPARTMENTS);
      setError("Using offline data — API not available");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch_(); }, [fetch_]);
  return { data, loading, error, refetch: fetch_ };
}
