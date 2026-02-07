"use client";

import { useEffect, useState, useMemo, useRef } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  ZoomControl,
  GeoJSON,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {
  PLACES,
  CATEGORIES,
  EL_SALVADOR_CENTER,
  type Place,
} from "@/data/el-salvador-places";
import { EL_SALVADOR_BORDER } from "@/data/el-salvador-border";
import {
  X,
  Star,
  Navigation,
  Layers,
  RotateCcw,
  ChevronRight,
  Globe,
  Search,
  Satellite,
  Map as MapIcon,
  Mountain,
  TreePine,
} from "lucide-react";

// ── Tile layer configs (all 100% free, no API key) ──
type MapStyle = "satellite" | "streets" | "topo" | "dark";

const TILE_LAYERS: Record<
  MapStyle,
  { url: string; attribution: string; label: string; icon: React.ReactNode }
> = {
  satellite: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: "Tiles &copy; Esri",
    label: "Satellite",
    icon: <Satellite className="h-4 w-4" />,
  },
  streets: {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    label: "Streets",
    icon: <MapIcon className="h-4 w-4" />,
  },
  topo: {
    url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attribution:
      '&copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
    label: "Terrain",
    icon: <Mountain className="h-4 w-4" />,
  },
  dark: {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://carto.com/">CARTO</a>',
    label: "Dark",
    icon: <TreePine className="h-4 w-4" />,
  },
};

// ── Custom marker icons per category ──
const iconCache = new Map<string, L.DivIcon>();
function getCategoryIcon(category: keyof typeof CATEGORIES) {
  if (iconCache.has(category)) return iconCache.get(category)!;
  const cat = CATEGORIES[category];
  const icon = L.divIcon({
    className: "",
    html: `<div style="
      display:flex;align-items:center;justify-content:center;
      width:38px;height:38px;border-radius:50%;
      background:${cat.color};color:white;font-size:17px;
      box-shadow:0 3px 14px rgba(0,0,0,0.4);
      border:3px solid white;
      transition:transform 0.2s;
    ">${cat.emoji}</div>`,
    iconSize: [38, 38],
    iconAnchor: [19, 19],
    popupAnchor: [0, -22],
  });
  iconCache.set(category, icon);
  return icon;
}

// ── Sub-component: fly to a place ──
function FlyTo({ place }: { place: Place | null }) {
  const map = useMap();
  useEffect(() => {
    if (place) {
      map.flyTo([place.coordinates[1], place.coordinates[0]], 16, {
        duration: 2.5,
      });
    }
  }, [place, map]);
  return null;
}

// ── Main component ──
export default function InteractiveMap() {
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [mapStyle, setMapStyle] = useState<MapStyle>("satellite");
  const [showStylePicker, setShowStylePicker] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [flyTarget, setFlyTarget] = useState<Place | null>(null);
  const [ready, setReady] = useState(false);
  const mapRef = useRef<L.Map | null>(null);

  // Fix Leaflet default icon issue in bundlers
  useEffect(() => {
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    });
    setReady(true);
  }, []);

  const filteredPlaces = useMemo(() => {
    return PLACES.filter((p) => {
      const matchesCat = !activeCategory || p.category === activeCategory;
      const q = searchQuery.toLowerCase();
      const matchesSearch =
        !q ||
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.tags.some((t) => t.toLowerCase().includes(q));
      return matchesCat && matchesSearch;
    });
  }, [activeCategory, searchQuery]);

  const handleSelectPlace = (place: Place) => {
    setSelectedPlace(place);
    setFlyTarget(place);
    setShowSidebar(false);
  };

  const resetView = () => {
    setSelectedPlace(null);
    setFlyTarget(null);
    mapRef.current?.flyTo(
      [EL_SALVADOR_CENTER[1], EL_SALVADOR_CENTER[0]],
      9,
      { duration: 2 }
    );
  };

  if (!ready) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-sv-950">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-sv-300 border-t-gold-400" />
          <p className="text-sm font-medium text-white/70">Loading map…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-screen w-full overflow-hidden bg-sv-950">
      {/* ── Leaflet Map ── */}
      <MapContainer
        center={[EL_SALVADOR_CENTER[1], EL_SALVADOR_CENTER[0]]}
        zoom={9}
        zoomControl={false}
        style={{ height: "100%", width: "100%", position: "absolute", inset: 0, zIndex: 0 }}
        ref={mapRef}
        maxBounds={[
          [12.5, -91.5],
          [15.2, -86.5],
        ]}
        minZoom={8}
      >
        <TileLayer
          key={mapStyle}
          url={TILE_LAYERS[mapStyle].url}
          attribution={TILE_LAYERS[mapStyle].attribution}
          maxZoom={19}
        />
        <ZoomControl position="bottomright" />
        <FlyTo place={flyTarget} />

        {/* Country border outline */}
        <GeoJSON
          data={EL_SALVADOR_BORDER}
          style={{
            color: "#facc15",
            weight: 3,
            opacity: 0.8,
            fillColor: "#facc15",
            fillOpacity: 0.05,
            dashArray: "",
          }}
        />

        {filteredPlaces.map((place) => (
          <Marker
            key={place.id}
            position={[place.coordinates[1], place.coordinates[0]]}
            icon={getCategoryIcon(place.category)}
            eventHandlers={{
              click: () => handleSelectPlace(place),
            }}
          >
            <Popup>
              <div className="min-w-[200px]">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase"
                    style={{
                      background: CATEGORIES[place.category].color + "22",
                      color: CATEGORIES[place.category].color,
                    }}
                  >
                    {CATEGORIES[place.category].emoji}{" "}
                    {CATEGORIES[place.category].label}
                  </span>
                  <span className="flex items-center gap-0.5 text-xs text-amber-500 font-medium">
                    ★ {place.rating}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-gray-900">
                  {place.name}
                </h3>
                <p className="mt-1 text-xs text-gray-500 leading-relaxed">
                  {place.description}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* ── Top Bar: Search + Categories ── */}
      <div className="absolute left-0 right-0 top-0 z-[1000] px-4 pt-20 pb-2 pointer-events-none">
        <div className="mx-auto max-w-5xl pointer-events-auto">
          {/* Search Bar */}
          <div className="glass-dark mb-3 flex items-center gap-3 rounded-2xl px-4 py-3 shadow-2xl">
            <Search className="h-5 w-5 shrink-0 text-gold-400" />
            <input
              type="text"
              placeholder="Search places in El Salvador…"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowSidebar(true);
              }}
              onFocus={() => setShowSidebar(true)}
              className="w-full bg-transparent text-sm text-white placeholder-white/40 outline-none"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="text-white/40 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            )}
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="ml-2 flex items-center gap-1 rounded-lg bg-white/10 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-white/20"
            >
              {filteredPlaces.length} places
              <ChevronRight
                className={`h-3 w-3 transition-transform ${showSidebar ? "rotate-180" : ""}`}
              />
            </button>
          </div>

          {/* Category Pills */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setActiveCategory(null)}
              className={`rounded-full px-3.5 py-1.5 text-xs font-semibold shadow-lg backdrop-blur-md transition ${
                !activeCategory
                  ? "bg-white text-sv-900"
                  : "bg-white/15 text-white hover:bg-white/25"
              }`}
            >
              All
            </button>
            {Object.entries(CATEGORIES).map(([key, cat]) => (
              <button
                key={key}
                onClick={() =>
                  setActiveCategory(activeCategory === key ? null : key)
                }
                className={`flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs font-semibold shadow-lg backdrop-blur-md transition ${
                  activeCategory === key
                    ? "bg-white text-sv-900"
                    : "bg-white/15 text-white hover:bg-white/25"
                }`}
              >
                <span>{cat.emoji}</span>
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Sidebar: Place List ── */}
      <div
        className={`absolute left-0 z-[1000] w-80 transform transition-transform duration-500 ease-in-out ${
          showSidebar ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{ top: "200px", height: "calc(100% - 200px)" }}
      >
        <div className="glass-dark h-full overflow-y-auto rounded-tr-2xl pb-4">
          <div className="sticky top-0 z-10 bg-sv-950/80 px-4 py-3 backdrop-blur-sm">
            <h3 className="text-sm font-semibold text-white/80">
              {filteredPlaces.length} place
              {filteredPlaces.length !== 1 ? "s" : ""} found
            </h3>
          </div>
          <div className="space-y-1 px-2">
            {filteredPlaces.map((place) => (
              <button
                key={place.id}
                onClick={() => handleSelectPlace(place)}
                className={`group flex w-full items-start gap-3 rounded-xl p-3 text-left transition ${
                  selectedPlace?.id === place.id
                    ? "bg-white/15"
                    : "hover:bg-white/8"
                }`}
              >
                <div
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-sm"
                  style={{
                    background: CATEGORIES[place.category].color + "33",
                  }}
                >
                  {CATEGORIES[place.category].emoji}
                </div>
                <div className="min-w-0 flex-1">
                  <h4 className="truncate text-sm font-semibold text-white group-hover:text-gold-300 transition">
                    {place.name}
                  </h4>
                  <p className="mt-0.5 truncate text-xs text-white/40">
                    {place.department}
                  </p>
                  <div className="mt-1 flex items-center gap-1 text-xs text-gold-400">
                    <Star className="h-3 w-3 fill-gold-400" />
                    {place.rating}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right Controls ── */}
      <div className="absolute bottom-24 right-4 z-[1000] flex flex-col gap-2">
        {/* Style Picker */}
        <div className="relative">
          <button
            onClick={() => setShowStylePicker(!showStylePicker)}
            className="glass-dark flex h-10 w-10 items-center justify-center rounded-xl text-white shadow-xl transition hover:bg-white/20"
            title="Map style"
          >
            <Layers className="h-5 w-5" />
          </button>
          {showStylePicker && (
            <div className="absolute bottom-0 right-12 glass-dark rounded-xl p-2 shadow-2xl">
              <div className="flex gap-1.5">
                {Object.entries(TILE_LAYERS).map(([key, style]) => (
                  <button
                    key={key}
                    onClick={() => {
                      setMapStyle(key as MapStyle);
                      setShowStylePicker(false);
                    }}
                    className={`flex flex-col items-center gap-1 rounded-lg px-3 py-2 text-xs transition ${
                      mapStyle === key
                        ? "bg-white/20 text-white"
                        : "text-white/60 hover:bg-white/10 hover:text-white"
                    }`}
                  >
                    {style.icon}
                    <span className="text-[10px]">{style.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Reset View */}
        <button
          onClick={resetView}
          className="glass-dark flex h-10 w-10 items-center justify-center rounded-xl text-white shadow-xl transition hover:bg-white/20"
          title="Reset view"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
      </div>

      {/* ── Selected Place Card ── */}
      {selectedPlace && (
        <div className="absolute bottom-6 left-1/2 z-[1001] w-full max-w-md -translate-x-1/2 px-4">
          <div className="glass-dark overflow-hidden rounded-2xl shadow-2xl">
            <div className="relative p-5">
              <button
                onClick={() => setSelectedPlace(null)}
                className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white/60 transition hover:bg-white/20 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>

              <div className="flex items-start gap-4">
                <div
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl text-xl"
                  style={{
                    background:
                      CATEGORIES[selectedPlace.category].color + "22",
                  }}
                >
                  {CATEGORIES[selectedPlace.category].emoji}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span
                      className="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider"
                      style={{
                        background:
                          CATEGORIES[selectedPlace.category].color + "22",
                        color: CATEGORIES[selectedPlace.category].color,
                      }}
                    >
                      {CATEGORIES[selectedPlace.category].label}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-gold-400">
                      <Star className="h-3 w-3 fill-gold-400" />
                      {selectedPlace.rating}
                    </span>
                  </div>
                  <h3 className="mt-1 text-lg font-bold text-white">
                    {selectedPlace.name}
                  </h3>
                  <p className="text-xs text-white/40">
                    {selectedPlace.nameEs} · {selectedPlace.department}
                  </p>
                </div>
              </div>

              <p className="mt-3 text-sm leading-relaxed text-white/60">
                {selectedPlace.description}
              </p>

              <div className="mt-3 flex flex-wrap gap-1.5">
                {selectedPlace.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-white/8 px-2 py-0.5 text-[10px] font-medium text-white/50"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <div className="mt-4 flex gap-2">
                <a
                  href={`https://www.google.com/maps/@${selectedPlace.coordinates[1]},${selectedPlace.coordinates[0]},17z`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-white/10 px-4 py-2.5 text-xs font-semibold text-white transition hover:bg-white/20"
                >
                  <Navigation className="h-3.5 w-3.5" />
                  Google Maps
                </a>
                <a
                  href={`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${selectedPlace.coordinates[1]},${selectedPlace.coordinates[0]}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gold-500 px-4 py-2.5 text-xs font-bold text-sv-950 transition hover:bg-gold-400"
                >
                  <Globe className="h-3.5 w-3.5" />
                  Street View
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Bottom Info ── */}
      <div className="absolute bottom-6 right-4 z-[999]">
        <div className="glass-dark rounded-xl px-3 py-2 text-[10px] text-white/40">
          El Salvador 🇸🇻 · {TILE_LAYERS[mapStyle].label}
        </div>
      </div>
    </div>
  );
}
