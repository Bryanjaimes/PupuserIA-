"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";

/* ═══════════════════════════════════════════════════════
   PupuserIA Dual-Mode Context

   Mode A: "Family & Impact"
     → Gardens, safety, schools, single-story, community
   Mode B: "Investor & ROI"
     → Cap rates, Airbnb, price/m², Surf City, appreciation
   ═══════════════════════════════════════════════════════ */

export type ViewMode = "family" | "investor";

interface ViewModeContextValue {
  mode: ViewMode;
  setMode: (m: ViewMode) => void;
  toggleMode: () => void;
  /** Sort field that best matches current mode */
  defaultSort: string;
  /** Filter presets for current mode */
  filterPresets: FilterPreset[];
  /** Highlight fields for property cards */
  highlightFields: string[];
  /** Tags to surface prominently */
  surfaceTags: string[];
  /** Label for the mode */
  modeLabel: string;
  modeLabelEs: string;
  modeDescription: string;
  modeIcon: string;
}

interface FilterPreset {
  label: string;
  labelEs: string;
  params: Record<string, string>;
}

const FAMILY_PRESETS: FilterPreset[] = [
  {
    label: "Safe family homes",
    labelEs: "Hogares familiares seguros",
    params: { bedrooms: "3", property_type: "house", sort_by: "family_score" },
  },
  {
    label: "Single-story accessible",
    labelEs: "Una planta, accesible",
    params: { property_type: "house", sort_by: "family_score", tags: "retirees" },
  },
  {
    label: "Near schools",
    labelEs: "Cerca de escuelas",
    params: { bedrooms: "2", sort_by: "family_score", tags: "families" },
  },
  {
    label: "Community spaces",
    labelEs: "Espacios comunitarios",
    params: { sort_by: "impact", tags: "community_events" },
  },
];

const INVESTOR_PRESETS: FilterPreset[] = [
  {
    label: "Airbnb-ready",
    labelEs: "Listo para Airbnb",
    params: { sort_by: "price_asc", tags: "airbnb" },
  },
  {
    label: "Surf City deals",
    labelEs: "Ofertas Surf City",
    params: { department: "La Libertad", sort_by: "price_asc" },
  },
  {
    label: "Best price/m²",
    labelEs: "Mejor precio/m²",
    params: { sort_by: "price_per_m2" },
  },
  {
    label: "Fixer-uppers",
    labelEs: "Para remodelar",
    params: { sort_by: "price_asc", tags: "investors" },
  },
  {
    label: "High appreciation",
    labelEs: "Alta plusvalía",
    params: { sort_by: "investment_potential" },
  },
];

const FAMILY_HIGHLIGHT = [
  "bedrooms",
  "bathrooms",
  "is_single_story",
  "garden",
  "family_friendly_score",
  "impact_score",
  "walkability_estimate",
];

const INVESTOR_HIGHLIGHT = [
  "price_per_m2",
  "investment_potential",
  "area_m2",
  "lot_size_m2",
  "needs_remodel",
  "surf_proximity",
  "airbnb_potential",
];

const FAMILY_TAGS = ["families", "retirees", "community_events", "students"];
const INVESTOR_TAGS = ["airbnb", "investors", "digital_nomads", "surfers"];

const ViewModeContext = createContext<ViewModeContextValue | null>(null);

export function ViewModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ViewMode>("family");

  const toggleMode = useCallback(
    () => setMode((m) => (m === "family" ? "investor" : "family")),
    []
  );

  const value: ViewModeContextValue = {
    mode,
    setMode,
    toggleMode,
    defaultSort: mode === "family" ? "family_score" : "price_asc",
    filterPresets: mode === "family" ? FAMILY_PRESETS : INVESTOR_PRESETS,
    highlightFields: mode === "family" ? FAMILY_HIGHLIGHT : INVESTOR_HIGHLIGHT,
    surfaceTags: mode === "family" ? FAMILY_TAGS : INVESTOR_TAGS,
    modeLabel: mode === "family" ? "Family & Impact" : "Investor & ROI",
    modeLabelEs: mode === "family" ? "Familia e Impacto" : "Inversión y ROI",
    modeDescription:
      mode === "family"
        ? "Highlights gardens, safety, schools, community centers"
        : "Highlights cap rates, Airbnb potential, price/m², appreciation",
    modeIcon: mode === "family" ? "👨‍👩‍👧‍👦" : "📈",
  };

  return (
    <ViewModeContext.Provider value={value}>
      {children}
    </ViewModeContext.Provider>
  );
}

export function useViewMode(): ViewModeContextValue {
  const ctx = useContext(ViewModeContext);
  if (!ctx)
    throw new Error("useViewMode must be used within <ViewModeProvider>");
  return ctx;
}
