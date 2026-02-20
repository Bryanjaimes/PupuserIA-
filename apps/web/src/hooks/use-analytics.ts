"use client";

/**
 * useAnalytics — lightweight, privacy-first event tracking hook.
 *
 * - Generates a random session ID (no cookies, no fingerprinting)
 * - Buffers events and flushes every 5s or on page unload
 * - Tracks page views automatically via pathname changes
 * - Provides `track(event, props)` for custom events
 */

import { useCallback, useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

// ── Config ──────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";
const FLUSH_INTERVAL_MS = 5_000;
const MAX_BUFFER_SIZE = 50;

// ── Types ───────────────────────────────────────────

type EventType =
  | "page_view"
  | "property_view"
  | "property_search"
  | "map_interaction"
  | "tour_view"
  | "concierge_chat"
  | "foundation_click"
  | "share"
  | "signup"
  | "booking_start"
  | "booking_complete";

interface QueuedEvent {
  session_id: string;
  event_type: EventType;
  page_path?: string;
  referrer?: string;
  properties?: Record<string, unknown>;
  device_type?: string;
  browser?: string;
  os?: string;
  language?: string;
  timestamp: string;
}

// ── Helpers ─────────────────────────────────────────

function getSessionId(): string {
  if (typeof window === "undefined") return "ssr";
  let sid = sessionStorage.getItem("ges_sid");
  if (!sid) {
    sid = crypto.randomUUID();
    sessionStorage.setItem("ges_sid", sid);
  }
  return sid;
}

function getDeviceType(): "desktop" | "mobile" | "tablet" {
  if (typeof window === "undefined") return "desktop";
  const w = window.innerWidth;
  if (w < 768) return "mobile";
  if (w < 1024) return "tablet";
  return "desktop";
}

function getBrowser(): string {
  if (typeof navigator === "undefined") return "unknown";
  const ua = navigator.userAgent;
  if (ua.includes("Firefox")) return "Firefox";
  if (ua.includes("Edg/")) return "Edge";
  if (ua.includes("Chrome")) return "Chrome";
  if (ua.includes("Safari")) return "Safari";
  return "other";
}

function getOS(): string {
  if (typeof navigator === "undefined") return "unknown";
  const ua = navigator.userAgent;
  if (ua.includes("Win")) return "Windows";
  if (ua.includes("Mac")) return "macOS";
  if (ua.includes("Linux")) return "Linux";
  if (ua.includes("Android")) return "Android";
  if (ua.includes("iPhone") || ua.includes("iPad")) return "iOS";
  return "other";
}

// ── Hook ────────────────────────────────────────────

export function useAnalytics() {
  const pathname = usePathname();
  const buffer = useRef<QueuedEvent[]>([]);
  const sessionId = useRef<string>("");
  const flushTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastPathname = useRef<string>("");

  // Initialize session
  useEffect(() => {
    sessionId.current = getSessionId();
  }, []);

  // Flush buffered events to the API
  const flush = useCallback(async () => {
    if (buffer.current.length === 0) return;
    const events = [...buffer.current];
    buffer.current = [];

    try {
      const res = await fetch(`${API_BASE}/analytics/track/batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events }),
        keepalive: true, // Survives page unload
      });
      if (!res.ok) {
        // Re-queue on failure (with limit to prevent infinite growth)
        if (buffer.current.length + events.length < MAX_BUFFER_SIZE * 2) {
          buffer.current.push(...events);
        }
      }
    } catch {
      // Silently fail — analytics should never block the user
    }
  }, []);

  // Set up periodic flush + unload flush
  useEffect(() => {
    flushTimer.current = setInterval(flush, FLUSH_INTERVAL_MS);

    const handleUnload = () => {
      flush();
    };

    window.addEventListener("beforeunload", handleUnload);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") flush();
    });

    return () => {
      if (flushTimer.current) clearInterval(flushTimer.current);
      window.removeEventListener("beforeunload", handleUnload);
      flush();
    };
  }, [flush]);

  // Core track function
  const track = useCallback(
    (eventType: EventType, props?: Record<string, unknown>) => {
      const event: QueuedEvent = {
        session_id: sessionId.current,
        event_type: eventType,
        page_path: typeof window !== "undefined" ? window.location.pathname : undefined,
        referrer: typeof document !== "undefined" ? document.referrer || undefined : undefined,
        properties: props,
        device_type: getDeviceType(),
        browser: getBrowser(),
        os: getOS(),
        language: typeof navigator !== "undefined" ? navigator.language.slice(0, 2) : undefined,
        timestamp: new Date().toISOString(),
      };

      buffer.current.push(event);

      // Auto-flush if buffer is full
      if (buffer.current.length >= MAX_BUFFER_SIZE) {
        flush();
      }
    },
    [flush]
  );

  // Auto-track page views on pathname change
  useEffect(() => {
    if (pathname && pathname !== lastPathname.current) {
      lastPathname.current = pathname;
      track("page_view", { path: pathname });
    }
  }, [pathname, track]);

  return { track };
}
