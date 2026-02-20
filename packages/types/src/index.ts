/**
 * Gateway El Salvador — Shared Type Definitions
 * ==============================================
 * Types shared between frontend and any TypeScript-based services.
 */

// ── Property Types ──────────────────────────────────

export interface Property {
  id: string;
  title: string;
  titleEs: string;
  description: string;
  descriptionEs: string;
  propertyType: PropertyType;
  department: string;
  municipio: string;
  canton?: string;

  // Pricing
  priceUsd?: number;
  aiValuationUsd?: number;
  aiConfidence?: number;
  rentalYieldEstimate?: number;
  appreciation5yrEstimate?: number;

  // Features
  bedrooms?: number;
  bathrooms?: number;
  areaM2?: number;
  lotSizeM2?: number;
  yearBuilt?: number;
  features: string[];

  // Geospatial
  latitude: number;
  longitude: number;

  // Media
  images: string[];
  thumbnailUrl?: string;
  virtualTourUrl?: string;

  // Scores
  neighborhoodScore?: number;

  // Metadata
  isActive: boolean;
  isFeatured: boolean;
  createdAt: string;
  updatedAt: string;
}

export type PropertyType = "house" | "apartment" | "land" | "commercial" | "condo";

// ── Tour Types ──────────────────────────────────────

export interface Tour {
  id: string;
  title: string;
  titleEs: string;
  description: string;
  descriptionEs: string;
  category: TourCategory;
  department: string;
  priceUsd: number;
  durationHours: number;
  maxParticipants?: number;
  rating?: number;
  reviewCount: number;
  images: string[];
  thumbnailUrl?: string;
  available: boolean;
  latitude?: number;
  longitude?: number;
}

export type TourCategory =
  | "surf"
  | "volcano"
  | "coffee"
  | "culture"
  | "food"
  | "adventure"
  | "nature"
  | "history";

// ── Content Types ───────────────────────────────────

export interface Article {
  id: string;
  slug: string;
  title: string;
  titleEs?: string;
  excerpt: string;
  excerptEs?: string;
  body: string;
  bodyEs?: string;
  category: ContentCategory;
  tags: string[];
  thumbnailUrl?: string;
  readTimeMinutes: number;
  isAiGenerated: boolean;
  isPublished: boolean;
  publishedAt?: string;
  createdAt: string;
}

export type ContentCategory =
  | "travel"
  | "investment"
  | "culture"
  | "safety"
  | "bitcoin"
  | "expat"
  | "education";

// ── Foundation Types ────────────────────────────────

export interface ImpactMetrics {
  totalRevenueGeneratedUsd: number;
  foundationAllocationUsd: number;
  allocationPercentage: number;
  studentsTutored: number;
  mealsServed: number;
  devicesDeployed: number;
  schoolsInNetwork: number;
  solarInstallations: number;
  supplyKitsDistributed: number;
}

export interface School {
  id: string;
  name: string;
  department: string;
  municipio: string;
  canton: string;
  studentCount: number;
  hasDevices: boolean;
  hasSolar: boolean;
  hasConnectivity: boolean;
  latitude: number;
  longitude: number;
}

export type FoundationProgram =
  | "tutoring"
  | "nutrition"
  | "devices"
  | "energy"
  | "supplies";

// ── API Response Types ──────────────────────────────

export interface PaginatedResponse<T> {
  results: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  language: "en" | "es";
}

export interface ChatResponse {
  reply: string;
  conversationId: string;
  sources: string[];
  suggestedActions: string[];
}

// ── Map Types ───────────────────────────────────────

export interface MapMarker {
  id: string;
  latitude: number;
  longitude: number;
  type: "property" | "tour" | "school" | "poi";
  title: string;
  price?: number;
  thumbnailUrl?: string;
}

export interface Department {
  code: string;
  name: string;
  lat: number;
  lng: number;
}

// ── Analytics Types ─────────────────────────────────

export interface AnalyticsEvent {
  sessionId: string;
  eventType: AnalyticsEventType;
  pagePath?: string;
  referrer?: string;
  properties?: Record<string, unknown>;
  deviceType?: "desktop" | "mobile" | "tablet";
  browser?: string;
  os?: string;
  language?: string;
}

export type AnalyticsEventType =
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
  dailyVisitors: DailyDataPoint[];
  dailyPageViews: DailyDataPoint[];
}

export interface DailyDataPoint {
  date: string;
  value: number;
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
  programBreakdown: ProgramBreakdownItem[];
  blockchainVerifiedCount: number;
  fundEfficiencyPct: number;
  monthlyImpact: MonthlyImpactPoint[];
  impactByDepartment: Record<string, number>;
}

export interface ProgramBreakdownItem {
  program: string;
  emoji: string;
  allocatedUsd: number;
  [key: string]: unknown;
}

export interface MonthlyImpactPoint {
  month: string;
  revenueUsd: number;
  allocationUsd: number;
  studentsReached: number;
}
