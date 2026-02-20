import {
  Ship, Landmark, Leaf, Building2, Plane, Bitcoin, Heart, School,
} from "lucide-react";
import { createElement } from "react";

/* ── Formatting ── */

export function fmtUsd(n: number) {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  return `$${n.toLocaleString()}`;
}

/* ── Icon map for investment cards ── */

const iconClass = "h-5 w-5";
export const ICON_MAP: Record<string, React.ReactNode> = {
  Ship: createElement(Ship, { className: iconClass }),
  Landmark: createElement(Landmark, { className: iconClass }),
  Leaf: createElement(Leaf, { className: iconClass }),
  Building2: createElement(Building2, { className: iconClass }),
  Plane: createElement(Plane, { className: iconClass }),
  Bitcoin: createElement(Bitcoin, { className: iconClass }),
  Heart: createElement(Heart, { className: iconClass }),
  School: createElement(School, { className: iconClass }),
};

/* ── Status & timeline color maps ── */

export const STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-50 text-emerald-700 border-emerald-200",
  approved: "bg-white/5 text-sv-400 border-white/10",
  construction: "bg-orange-50 text-orange-700 border-orange-200",
  executed: "bg-gold-500/10 text-gold-400 border-gold-200",
  planned: "bg-[#111] text-gray-500 border-white/10",
};

export const TIMELINE_CAT_COLORS: Record<string, string> = {
  bitcoin: "text-[#f7931a] bg-orange-50 border-orange-200",
  security: "text-red-600 bg-red-50 border-red-200",
  infrastructure: "text-sv-400 bg-white/5 border-white/10",
  finance: "text-emerald-700 bg-emerald-50 border-emerald-200",
  governance: "text-gold-400 bg-gold-500/10 border-gold-200",
  social: "text-purple-600 bg-purple-50 border-purple-200",
};

/* ── Regional comparison benchmarks ── */

export const REGIONAL_BENCH: Record<string, { label: string; value: string }> = {
  "NY.GDP.PCAP.CD": { label: "Central America avg", value: "$5,800" },
  "NY.GDP.MKTP.KD.ZG": { label: "Central America avg", value: "3.2%" },
  "FP.CPI.TOTL.ZG": { label: "Central America avg", value: "4.8%" },
  "SL.UEM.TOTL.ZS": { label: "Central America avg", value: "5.6%" },
  "SP.DYN.LE00.IN": { label: "Central America avg", value: "73.5 yrs" },
  "SE.XPD.TOTL.GD.ZS": { label: "Central America avg", value: "4.2%" },
  "SH.XPD.CHEX.GD.ZS": { label: "Central America avg", value: "6.8%" },
  "EN.ATM.CO2E.KT": { label: "Central America avg", value: "12,000 kt" },
  "IT.NET.USER.ZS": { label: "Central America avg", value: "55%" },
};
