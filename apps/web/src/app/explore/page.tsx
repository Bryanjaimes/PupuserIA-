"use client";

import dynamic from "next/dynamic";

// Dynamic import to avoid SSR issues with Mapbox GL
const InteractiveMap = dynamic(() => import("@/components/interactive-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-screen w-full items-center justify-center bg-sv-950">
      <div className="flex flex-col items-center gap-4">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-sv-300 border-t-sv-500" />
        <p className="text-sm font-medium text-white/70">Loading map…</p>
      </div>
    </div>
  ),
});

export default function ExplorePage() {
  return <InteractiveMap />;
}
