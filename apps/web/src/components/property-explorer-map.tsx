"use client";

import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  GeoJSON,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { EL_SALVADOR_BORDER } from "@/data/el-salvador-border";

/* ═══════════════════════════════════════════════════════
   PropertyExplorerMap — lightweight reusable Leaflet map
   for the department → municipality → property flow.
   ═══════════════════════════════════════════════════════ */

export interface MapMarker {
  lat: number;
  lng: number;
  label: string;
  sub?: string;
  color?: string;
  size?: "sm" | "md" | "lg";
}

interface Props {
  center: [number, number]; // [lat, lng]
  zoom: number;
  markers: MapMarker[];
  onMarkerClick?: (idx: number) => void;
  showBorder?: boolean;
  className?: string;
}

// ── Custom DivIcon factory ──────────────────────────

function createIcon(m: MapMarker): L.DivIcon {
  const c = m.color || "#0047ab";

  if (m.size === "sm") {
    return L.divIcon({
      className: "",
      html: `<div style="
        position:absolute;transform:translate(-50%,-50%);
        width:10px;height:10px;border-radius:50%;
        background:${c};border:2px solid white;
        box-shadow:0 1px 4px rgba(0,0,0,0.4);cursor:pointer;
      "></div>`,
      iconSize: [0, 0],
      iconAnchor: [0, 0],
    });
  }

  const lg = m.size === "lg";
  return L.divIcon({
    className: "",
    html: `<div style="
      position:absolute;transform:translate(-50%,-50%);
      display:inline-flex;flex-direction:column;align-items:center;
      padding:${lg ? "8px 16px" : "5px 10px"};
      border-radius:${lg ? "14" : "10"}px;
      background:${c};color:white;
      font-family:system-ui,sans-serif;text-align:center;
      box-shadow:0 4px 20px rgba(0,0,0,0.35);
      border:2px solid rgba(255,255,255,0.9);
      cursor:pointer;white-space:nowrap;
      transition:transform 0.2s ease;
    ">
      <span style="font-size:${lg ? 13 : 11}px;font-weight:700;line-height:1.2;">${m.label}</span>
      ${m.sub ? `<span style="font-size:${lg ? 10 : 9}px;opacity:0.85;margin-top:1px;">${m.sub}</span>` : ""}
    </div>`,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
  });
}

// ── Set initial view ────────────────────────────────

function SetView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return null;
}

// ── Map Component ───────────────────────────────────

export default function PropertyExplorerMap({
  center,
  zoom,
  markers,
  onMarkerClick,
  showBorder = true,
  className = "",
}: Props) {
  return (
    <MapContainer
      center={center}
      zoom={zoom}
      className={className}
      style={{ width: "100%", height: "100%" }}
      zoomControl={false}
      scrollWheelZoom={true}
      attributionControl={false}
    >
      <SetView center={center} zoom={zoom} />
      <TileLayer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attribution="&copy; Esri"
      />
      {showBorder && (
        <GeoJSON
          data={EL_SALVADOR_BORDER}
          style={{ color: "#fbbf24", weight: 2, fillOpacity: 0 }}
        />
      )}
      {markers.map((m, i) => (
        <Marker
          key={`${m.lat}-${m.lng}-${i}`}
          position={[m.lat, m.lng]}
          icon={createIcon(m)}
          eventHandlers={
            onMarkerClick ? { click: () => onMarkerClick(i) } : {}
          }
        />
      ))}
    </MapContainer>
  );
}
