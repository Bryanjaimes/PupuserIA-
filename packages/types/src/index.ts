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
