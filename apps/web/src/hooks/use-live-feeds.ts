"use client";

import { useEffect, useState, useCallback } from "react";

/* ═══════════════════════════════════════════════════════
   1. USGS Earthquake Feed
   Real-time seismic activity near El Salvador
   Source: earthquake.usgs.gov — free, no key
   ═══════════════════════════════════════════════════════ */

export interface Earthquake {
  id: string;
  magnitude: number;
  place: string;
  time: number; // epoch ms
  depth: number; // km
  url: string;
  lat: number;
  lng: number;
}

export interface EarthquakeState {
  quakes: Earthquake[];
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export function useEarthquakes(): EarthquakeState {
  const [quakes, setQuakes] = useState<Earthquake[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    async function fetchQuakes() {
      try {
        // Bounding box around El Salvador + nearby region
        const res = await fetch(
          "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minlatitude=12.5&maxlatitude=15.0&minlongitude=-91.5&maxlongitude=-86.5&orderby=time&limit=10&minmagnitude=2"
        );
        const data = await res.json();
        const parsed: Earthquake[] = (data.features ?? []).map((f: any) => ({
          id: f.id,
          magnitude: f.properties.mag,
          place: f.properties.place,
          time: f.properties.time,
          depth: f.geometry.coordinates[2],
          url: f.properties.url,
          lat: f.geometry.coordinates[1],
          lng: f.geometry.coordinates[0],
        }));
        setQuakes(parsed);
        setLastUpdated(new Date());
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to fetch earthquakes");
      } finally {
        setLoading(false);
      }
    }
    fetchQuakes();
    const interval = setInterval(fetchQuakes, 5 * 60_000); // refresh every 5 min
    return () => clearInterval(interval);
  }, []);

  return { quakes, loading, error, lastUpdated };
}

/* ═══════════════════════════════════════════════════════
   2. Open-Meteo Weather
   Current weather for San Salvador — free, no key
   ═══════════════════════════════════════════════════════ */

export interface Weather {
  temperature: number; // °C
  feelsLike: number;
  humidity: number; // %
  windSpeed: number; // km/h
  weatherCode: number;
  uvIndex: number;
  precipitation: number; // mm
  isDay: boolean;
}

export interface WeatherState {
  weather: Weather | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

const WEATHER_DESCRIPTIONS: Record<number, string> = {
  0: "Clear sky",
  1: "Mainly clear",
  2: "Partly cloudy",
  3: "Overcast",
  45: "Foggy",
  48: "Rime fog",
  51: "Light drizzle",
  53: "Moderate drizzle",
  55: "Dense drizzle",
  61: "Slight rain",
  63: "Moderate rain",
  65: "Heavy rain",
  71: "Slight snow",
  73: "Moderate snow",
  75: "Heavy snow",
  80: "Slight rain showers",
  81: "Moderate rain showers",
  82: "Violent rain showers",
  95: "Thunderstorm",
  96: "Thunderstorm w/ hail",
  99: "Thunderstorm w/ heavy hail",
};

export function weatherCodeToDesc(code: number): string {
  return WEATHER_DESCRIPTIONS[code] ?? "Unknown";
}

export function weatherCodeToEmoji(code: number): string {
  if (code === 0) return "☀️";
  if (code <= 2) return "⛅";
  if (code === 3) return "☁️";
  if (code <= 48) return "🌫️";
  if (code <= 55) return "🌦️";
  if (code <= 65) return "🌧️";
  if (code <= 75) return "❄️";
  if (code <= 82) return "🌧️";
  return "⛈️";
}

export function useWeather(): WeatherState {
  const [weather, setWeather] = useState<Weather | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    async function fetchWeather() {
      try {
        // San Salvador coordinates
        const res = await fetch(
          "https://api.open-meteo.com/v1/forecast?latitude=13.6929&longitude=-89.2182&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,uv_index,is_day&timezone=America%2FEl_Salvador"
        );
        const data = await res.json();
        const c = data.current;
        setWeather({
          temperature: c.temperature_2m,
          feelsLike: c.apparent_temperature,
          humidity: c.relative_humidity_2m,
          windSpeed: c.wind_speed_10m,
          weatherCode: c.weather_code,
          uvIndex: c.uv_index,
          precipitation: c.precipitation,
          isDay: c.is_day === 1,
        });
        setLastUpdated(new Date());
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to fetch weather");
      } finally {
        setLoading(false);
      }
    }
    fetchWeather();
    const interval = setInterval(fetchWeather, 10 * 60_000); // refresh every 10 min
    return () => clearInterval(interval);
  }, []);

  return { weather, loading, error, lastUpdated };
}

/* ═══════════════════════════════════════════════════════
   3. Air Quality — Open-Meteo Air Quality API
   Real-time PM2.5, PM10, US AQI — free, no key
   ═══════════════════════════════════════════════════════ */

export interface AirQuality {
  pm25: number;
  pm10: number;
  usAqi: number;
  co: number; // μg/m³
  no2: number;
  o3: number;
}

export interface AirQualityState {
  aq: AirQuality | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export function aqiToLabel(aqi: number): { label: string; color: string } {
  if (aqi <= 50) return { label: "Good", color: "text-emerald-600" };
  if (aqi <= 100) return { label: "Moderate", color: "text-yellow-600" };
  if (aqi <= 150) return { label: "Unhealthy (sensitive)", color: "text-orange-600" };
  if (aqi <= 200) return { label: "Unhealthy", color: "text-red-600" };
  if (aqi <= 300) return { label: "Very Unhealthy", color: "text-purple-600" };
  return { label: "Hazardous", color: "text-rose-800" };
}

export function useAirQuality(): AirQualityState {
  const [aq, setAq] = useState<AirQuality | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    async function fetchAQ() {
      try {
        const res = await fetch(
          "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=13.6929&longitude=-89.2182&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,us_aqi&timezone=America%2FEl_Salvador"
        );
        const data = await res.json();
        const c = data.current;
        setAq({
          pm25: c.pm2_5,
          pm10: c.pm10,
          usAqi: c.us_aqi,
          co: c.carbon_monoxide,
          no2: c.nitrogen_dioxide,
          o3: c.ozone,
        });
        setLastUpdated(new Date());
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to fetch air quality");
      } finally {
        setLoading(false);
      }
    }
    fetchAQ();
    const interval = setInterval(fetchAQ, 10 * 60_000);
    return () => clearInterval(interval);
  }, []);

  return { aq, loading, error, lastUpdated };
}

/* ═══════════════════════════════════════════════════════
   4. Exchange Rates — exchangerate.host (free, no key)
   USD cross-rates relevant for remittances
   ═══════════════════════════════════════════════════════ */

export interface ExchangeRates {
  USDGTQ: number; // Guatemala Quetzal
  USDHNL: number; // Honduras Lempira
  USDMXN: number; // Mexican Peso
  USDEUR: number; // Euro
  USDBTC: number; // BTC
}

export interface ExchangeRateState {
  rates: ExchangeRates | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export function useExchangeRates(): ExchangeRateState {
  const [rates, setRates] = useState<ExchangeRates | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    async function fetchRates() {
      try {
        // Using open.er-api.com (free, no key, 1 req/day per IP but we cache)
        const res = await fetch("https://open.er-api.com/v6/latest/USD");
        const data = await res.json();
        if (data.result === "success" && data.rates) {
          setRates({
            USDGTQ: data.rates.GTQ ?? 0,
            USDHNL: data.rates.HNL ?? 0,
            USDMXN: data.rates.MXN ?? 0,
            USDEUR: data.rates.EUR ?? 0,
            USDBTC: data.rates.BTC ?? 0,
          });
          setLastUpdated(new Date());
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to fetch exchange rates");
      } finally {
        setLoading(false);
      }
    }
    fetchRates();
    const interval = setInterval(fetchRates, 60 * 60_000); // refresh hourly
    return () => clearInterval(interval);
  }, []);

  return { rates, loading, error, lastUpdated };
}

/* ═══════════════════════════════════════════════════════
   5. GDELT — Real-time news/events about El Salvador
   Source: api.gdeltproject.org — free, no key
   ═══════════════════════════════════════════════════════ */

export interface GdeltArticle {
  title: string;
  url: string;
  source: string;
  publishedAt: string;
  imageUrl: string | null;
  language: string;
}

export interface GdeltState {
  articles: GdeltArticle[];
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export function useGdeltNews(): GdeltState {
  const [articles, setArticles] = useState<GdeltArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    async function fetchNews() {
      try {
        const res = await fetch(
          "https://api.gdeltproject.org/api/v2/doc/doc?query=%22El%20Salvador%22&mode=artlist&maxrecords=8&format=json&sort=datedesc"
        );
        const data = await res.json();
        const parsed: GdeltArticle[] = (data.articles ?? []).map((a: any) => ({
          title: a.title ?? "",
          url: a.url ?? "",
          source: a.domain ?? a.source ?? "",
          publishedAt: a.seendate ?? "",
          imageUrl: a.socialimage || null,
          language: a.language ?? "English",
        }));
        setArticles(parsed);
        setLastUpdated(new Date());
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to fetch news");
      } finally {
        setLoading(false);
      }
    }
    fetchNews();
    const interval = setInterval(fetchNews, 15 * 60_000); // refresh every 15 min
    return () => clearInterval(interval);
  }, []);

  return { articles, loading, error, lastUpdated };
}
