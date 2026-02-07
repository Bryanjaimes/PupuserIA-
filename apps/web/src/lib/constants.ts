/**
 * Application-wide constants for Gateway El Salvador.
 */

export const SITE_CONFIG = {
  name: "Gateway El Salvador",
  tagline: "Discover, Invest, Transform",
  description:
    "The AI-powered gateway connecting the world to El Salvador.",
  url: "https://gatewayelsvador.com",
  email: "hello@gatewayelsvador.com",
} as const;

/**
 * El Salvador's 14 departments with their codes and approximate centers.
 */
export const ES_DEPARTMENTS = [
  { code: "AH", name: "Ahuachapán", lat: 13.92, lng: -89.85 },
  { code: "CA", name: "Cabañas", lat: 13.86, lng: -88.74 },
  { code: "CH", name: "Chalatenango", lat: 14.04, lng: -88.94 },
  { code: "CU", name: "Cuscatlán", lat: 13.73, lng: -88.93 },
  { code: "LI", name: "La Libertad", lat: 13.49, lng: -89.32 },
  { code: "PA", name: "La Paz", lat: 13.49, lng: -88.95 },
  { code: "UN", name: "La Unión", lat: 13.34, lng: -87.84 },
  { code: "MO", name: "Morazán", lat: 13.77, lng: -88.13 },
  { code: "SM", name: "San Miguel", lat: 13.48, lng: -88.18 },
  { code: "SS", name: "San Salvador", lat: 13.69, lng: -89.19 },
  { code: "SV", name: "San Vicente", lat: 13.64, lng: -88.78 },
  { code: "SA", name: "Santa Ana", lat: 14.0, lng: -89.56 },
  { code: "SO", name: "Sonsonate", lat: 13.72, lng: -89.72 },
  { code: "US", name: "Usulután", lat: 13.35, lng: -88.45 },
] as const;

/**
 * Map configuration defaults.
 */
export const MAP_CONFIG = {
  center: [-88.9, 13.7] as [number, number], // El Salvador center
  zoom: 8,
  minZoom: 7,
  maxZoom: 18,
  bounds: [
    [-90.2, 13.1], // Southwest
    [-87.6, 14.5], // Northeast
  ] as [[number, number], [number, number]],
} as const;

/**
 * Foundation impact allocation targets.
 */
export const FOUNDATION_CONFIG = {
  revenueAllocationPercent: 10, // 10% of gross revenue from Day 1
  targetAllocationPercent: 20, // Scale to 20% at profitability
  programs: [
    "AI Tutoring",
    "Nutrition",
    "Devices",
    "Solar Energy",
    "School Supplies",
  ],
} as const;
