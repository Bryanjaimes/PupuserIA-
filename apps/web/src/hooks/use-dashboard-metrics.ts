"use client";

/**
 * useDashboardMetrics — fetches platform analytics + foundation impact data.
 * Used by the /dashboard/impact page.
 */

import { useState, useEffect, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

// ── Types ───────────────────────────────────────────

export interface PlatformOverview {
  activeVisitorsNow: number;
  pageViewsToday: number;
  sessionsToday: number;
  visitors7d: number;
  visitors30d: number;
  pageViews7d: number;
  pageViews30d: number;
  propertyViews7d: number;
  propertySearches7d: number;
  tourViews7d: number;
  conciergeChats7d: number;
  mapInteractions7d: number;
  avgSessionDurationSec: number;
  totalListings: number;
  listingsWithValuation: number;
  departmentsCovered: number;
  topCountries: Record<string, number>;
  topDepartments: Record<string, number>;
  dailyVisitors: { date: string; value: number }[];
  dailyPageViews: { date: string; value: number }[];
}

export interface ImpactDashboard {
  totalPlatformRevenueUsd: number;
  foundationAllocationUsd: number;
  allocationRate: number;
  studentsReached: number;
  mealsServed: number;
  devicesDeployed: number;
  schoolsActive: number;
  solarInstallations: number;
  supplyKits: number;
  childrenPerDollar: number;
  programBreakdown: {
    program: string;
    emoji: string;
    allocatedUsd: number;
    [key: string]: unknown;
  }[];
  blockchainVerifiedCount: number;
  fundEfficiencyPct: number;
  monthlyImpact: {
    month: string;
    revenueUsd: number;
    allocationUsd: number;
    studentsReached: number;
  }[];
  impactByDepartment: Record<string, number>;
}

// ── Helpers ─────────────────────────────────────────

function snakeToCamel(obj: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    const camelKey = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
    if (Array.isArray(value)) {
      result[camelKey] = value.map((item) =>
        typeof item === "object" && item !== null
          ? snakeToCamel(item as Record<string, unknown>)
          : item
      );
    } else if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      result[camelKey] = snakeToCamel(value as Record<string, unknown>);
    } else {
      result[camelKey] = value;
    }
  }
  return result;
}

// ── Hook: Platform Overview ─────────────────────────

export function usePlatformOverview(refreshInterval = 60_000) {
  const [data, setData] = useState<PlatformOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/analytics/overview`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const raw = await res.json();
      setData(snakeToCamel(raw) as unknown as PlatformOverview);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchData, refreshInterval]);

  return { data, loading, error, refetch: fetchData };
}

// ── Hook: Impact Dashboard ──────────────────────────

export function useImpactDashboard(refreshInterval = 60_000) {
  const [data, setData] = useState<ImpactDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/analytics/impact`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const raw = await res.json();
      setData(snakeToCamel(raw) as unknown as ImpactDashboard);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchData, refreshInterval]);

  return { data, loading, error, refetch: fetchData };
}
