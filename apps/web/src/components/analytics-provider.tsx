"use client";

import { useAnalytics } from "@/hooks/use-analytics";

/**
 * Client-side analytics provider.
 * Mount once in the root layout to auto-track page views.
 * Renders nothing — just initialises the tracking hook.
 */
export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  useAnalytics();          // auto-tracks page_view events on route changes
  return <>{children}</>;
}
