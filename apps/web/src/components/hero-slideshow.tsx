"use client";

import { useState, useEffect, useCallback } from "react";

const slides = [
  {
    url: "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1920&q=85&auto=format&fit=crop",
    caption: "Volcanic Highlands",
    position: "center 35%",
  },
  {
    url: "https://images.unsplash.com/photo-1505881502353-a1986add3762?w=1920&q=85&auto=format&fit=crop",
    caption: "Pacific Coast",
    position: "center 55%",
  },
  {
    url: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=1920&q=85&auto=format&fit=crop",
    caption: "City Skyline",
    position: "center 45%",
  },
  {
    url: "https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=1920&q=85&auto=format&fit=crop",
    caption: "Colonial Architecture",
    position: "center 50%",
  },
  {
    url: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=85&auto=format&fit=crop",
    caption: "Mountain Landscape",
    position: "center 40%",
  },
];

export function HeroSlideshow() {
  const [current, setCurrent] = useState(0);
  const [loaded, setLoaded] = useState<boolean[]>(new Array(slides.length).fill(false));

  const markLoaded = useCallback((index: number) => {
    setLoaded((prev) => {
      const next = [...prev];
      next[index] = true;
      return next;
    });
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((prev) => (prev + 1) % slides.length);
    }, 7000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const nextIdx = (current + 1) % slides.length;
    if (!loaded[nextIdx]) {
      const img = new Image();
      img.src = slides[nextIdx].url;
      img.onload = () => markLoaded(nextIdx);
    }
  }, [current, loaded, markLoaded]);

  return (
    <div className="absolute inset-0 z-0">
      {slides.map((slide, i) => (
        <div
          key={slide.url}
          className="absolute inset-0 transition-opacity duration-[2500ms] ease-in-out"
          style={{ opacity: i === current ? 1 : 0 }}
        >
          <img
            src={slide.url}
            alt={slide.caption}
            loading={i <= 1 ? "eager" : "lazy"}
            onLoad={() => markLoaded(i)}
            className="h-full w-full object-cover blur-[1px] scale-[1.03]"
            style={{ objectPosition: slide.position }}
          />
        </div>
      ))}

      {/* Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-sv-950/70 via-sv-950/50 to-sv-950/80" />
      <div className="absolute inset-0 bg-sv-500/8 mix-blend-overlay" />

      {/* Minimal dots */}
      <div className="absolute bottom-20 left-1/2 z-20 flex -translate-x-1/2 gap-1.5">
        {slides.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            className={`h-1 rounded-full transition-all duration-700 ${
              i === current ? "w-6 bg-white/50" : "w-1.5 bg-white/15"
            }`}
            aria-label={`Slide ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
