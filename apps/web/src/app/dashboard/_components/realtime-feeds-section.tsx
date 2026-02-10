"use client";

import {
  Cloud, Thermometer, Wind, Droplets, Sun,
  Activity, Radio, Globe, Newspaper,
  ArrowUpRight, ExternalLink, DollarSign,
  AlertTriangle,
} from "lucide-react";
import { useLanguage } from "@/context/language-context";
import {
  useEarthquakes,
  useWeather,
  useAirQuality,
  useExchangeRates,
  useGdeltNews,
  weatherCodeToDesc,
  weatherCodeToEmoji,
  aqiToLabel,
} from "@/hooks/use-live-feeds";
import { Skeleton } from "./metric-cards";

/* ── tiny helpers ── */

function timeAgo(epoch: number): string {
  const diff = Date.now() - epoch;
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function updatedLabel(d: Date | null): string {
  if (!d) return "";
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/* ── Main Component ── */

export function RealtimeFeedsSection() {
  const { t } = useLanguage();
  const eq = useEarthquakes();
  const wx = useWeather();
  const aq = useAirQuality();
  const fx = useExchangeRates();
  const news = useGdeltNews();

  return (
    <section className="border-b border-gray-200 py-12 lg:py-16" id="realtime-feeds">
      <div className="mx-auto max-w-7xl px-6">
        {/* Section Header */}
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-emerald-200 bg-emerald-50 text-emerald-600">
            <Radio className="h-5 w-5" />
          </div>
          <div>
            <h2 className="font-serif text-2xl font-extrabold text-sv-950">
              {t("dash.realtimeTitle")}
            </h2>
            <p className="text-xs text-gray-400">{t("dash.realtimeDesc")}</p>
          </div>
          <span className="ml-auto flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[11px] font-semibold text-emerald-700">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            LIVE
          </span>
        </div>

        {/* Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {/* ────── 1. Weather ────── */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Cloud className="h-4 w-4 text-sky-500" />
                <span className="text-xs font-medium text-gray-500">{t("dash.weatherTitle")}</span>
              </div>
              {wx.lastUpdated && (
                <span className="text-[10px] text-gray-300">{updatedLabel(wx.lastUpdated)}</span>
              )}
            </div>

            {wx.loading ? (
              <div className="space-y-2"><Skeleton w="w-full" h="h-6" /><Skeleton w="w-2/3" h="h-4" /></div>
            ) : wx.error ? (
              <p className="text-xs text-red-500">{wx.error}</p>
            ) : wx.weather ? (
              <>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-extrabold text-sv-950">
                    {wx.weather.temperature.toFixed(0)}°C
                  </span>
                  <span className="text-2xl">{weatherCodeToEmoji(wx.weather.weatherCode)}</span>
                </div>
                <p className="mt-1 text-sm text-gray-500">{weatherCodeToDesc(wx.weather.weatherCode)}</p>
                <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-gray-500">
                  <span className="flex items-center gap-1"><Thermometer className="h-3 w-3" /> {t("dash.feelsLike")} {wx.weather.feelsLike.toFixed(0)}°C</span>
                  <span className="flex items-center gap-1"><Droplets className="h-3 w-3" /> {t("dash.humidity")} {wx.weather.humidity}%</span>
                  <span className="flex items-center gap-1"><Wind className="h-3 w-3" /> {t("dash.wind")} {wx.weather.windSpeed} km/h</span>
                  <span className="flex items-center gap-1"><Sun className="h-3 w-3" /> UV {wx.weather.uvIndex}</span>
                </div>
                <p className="mt-2 text-[10px] text-gray-300">San Salvador · Open-Meteo</p>
              </>
            ) : null}
          </div>

          {/* ────── 2. Air Quality ────── */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Wind className="h-4 w-4 text-teal-500" />
                <span className="text-xs font-medium text-gray-500">{t("dash.aqTitle")}</span>
              </div>
              {aq.lastUpdated && (
                <span className="text-[10px] text-gray-300">{updatedLabel(aq.lastUpdated)}</span>
              )}
            </div>

            {aq.loading ? (
              <div className="space-y-2"><Skeleton w="w-full" h="h-6" /><Skeleton w="w-2/3" h="h-4" /></div>
            ) : aq.error ? (
              <p className="text-xs text-red-500">{aq.error}</p>
            ) : aq.aq ? (
              <>
                {(() => {
                  const { label, color } = aqiToLabel(aq.aq.usAqi);
                  return (
                    <>
                      <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-extrabold text-sv-950">{aq.aq.usAqi}</span>
                        <span className={`text-sm font-semibold ${color}`}>{label}</span>
                      </div>
                      <p className="mt-1 text-xs text-gray-400">US AQI</p>
                    </>
                  );
                })()}
                <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-gray-500">
                  <span>PM2.5: {aq.aq.pm25?.toFixed(1)} µg/m³</span>
                  <span>PM10: {aq.aq.pm10?.toFixed(1)} µg/m³</span>
                  <span>O₃: {aq.aq.o3?.toFixed(0)} µg/m³</span>
                  <span>NO₂: {aq.aq.no2?.toFixed(0)} µg/m³</span>
                </div>
                <p className="mt-2 text-[10px] text-gray-300">San Salvador · Open-Meteo Air Quality</p>
              </>
            ) : null}
          </div>

          {/* ────── 3. Seismic Activity ────── */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-red-500" />
                <span className="text-xs font-medium text-gray-500">{t("dash.quakeTitle")}</span>
              </div>
              {eq.lastUpdated && (
                <span className="text-[10px] text-gray-300">{updatedLabel(eq.lastUpdated)}</span>
              )}
            </div>

            {eq.loading ? (
              <div className="space-y-2"><Skeleton w="w-full" h="h-6" /><Skeleton w="w-2/3" h="h-4" /></div>
            ) : eq.error ? (
              <p className="text-xs text-red-500">{eq.error}</p>
            ) : eq.quakes.length === 0 ? (
              <p className="text-sm text-gray-400">{t("dash.noRecentQuakes")}</p>
            ) : (
              <>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-extrabold text-sv-950">
                    M{eq.quakes[0].magnitude.toFixed(1)}
                  </span>
                  <span className="text-xs text-gray-400">{t("dash.latest")}</span>
                </div>
                <p className="mt-1 truncate text-sm text-gray-500">{eq.quakes[0].place}</p>
                <p className="text-xs text-gray-400">{timeAgo(eq.quakes[0].time)} · {eq.quakes[0].depth.toFixed(0)} km {t("dash.depth")}</p>
                {eq.quakes.length > 1 && (
                  <div className="mt-3 space-y-1">
                    {eq.quakes.slice(1, 4).map((q) => (
                      <div key={q.id} className="flex items-center justify-between text-[11px] text-gray-500">
                        <span className="flex items-center gap-1">
                          <span className={`inline-block h-1.5 w-1.5 rounded-full ${q.magnitude >= 4 ? "bg-red-500" : q.magnitude >= 3 ? "bg-orange-400" : "bg-yellow-400"}`} />
                          M{q.magnitude.toFixed(1)}
                        </span>
                        <span className="truncate max-w-[140px]">{q.place}</span>
                        <span className="text-gray-300">{timeAgo(q.time)}</span>
                      </div>
                    ))}
                  </div>
                )}
                <p className="mt-2 text-[10px] text-gray-300">USGS · {eq.quakes.length} {t("dash.recentEvents")}</p>
              </>
            )}
          </div>

          {/* ────── 4. Exchange Rates ────── */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-emerald-500" />
                <span className="text-xs font-medium text-gray-500">{t("dash.fxTitle")}</span>
              </div>
              {fx.lastUpdated && (
                <span className="text-[10px] text-gray-300">{updatedLabel(fx.lastUpdated)}</span>
              )}
            </div>

            {fx.loading ? (
              <div className="space-y-2"><Skeleton w="w-full" h="h-6" /><Skeleton w="w-2/3" h="h-4" /></div>
            ) : fx.error ? (
              <p className="text-xs text-red-500">{fx.error}</p>
            ) : fx.rates ? (
              <>
                <p className="mb-3 text-xs text-gray-400">{t("dash.fxBase")}</p>
                <div className="space-y-2">
                  {[
                    { flag: "🇬🇹", code: "GTQ", name: "Quetzal", rate: fx.rates.USDGTQ },
                    { flag: "🇭🇳", code: "HNL", name: "Lempira", rate: fx.rates.USDHNL },
                    { flag: "🇲🇽", code: "MXN", name: "Peso", rate: fx.rates.USDMXN },
                    { flag: "🇪🇺", code: "EUR", name: "Euro", rate: fx.rates.USDEUR },
                  ].map((c) => (
                    <div key={c.code} className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 text-gray-600">
                        <span>{c.flag}</span>
                        <span className="font-medium">{c.code}</span>
                        <span className="text-xs text-gray-400">{c.name}</span>
                      </span>
                      <span className="font-semibold text-sv-950">{c.rate.toFixed(c.code === "EUR" ? 4 : 2)}</span>
                    </div>
                  ))}
                </div>
                <p className="mt-3 text-[10px] text-gray-300">{t("dash.fxNote")}</p>
              </>
            ) : null}
          </div>

          {/* ────── 5. News Feed ────── */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md sm:col-span-2">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Newspaper className="h-4 w-4 text-indigo-500" />
                <span className="text-xs font-medium text-gray-500">{t("dash.newsTitle")}</span>
              </div>
              {news.lastUpdated && (
                <span className="text-[10px] text-gray-300">{updatedLabel(news.lastUpdated)}</span>
              )}
            </div>

            {news.loading ? (
              <div className="space-y-3">
                {[...Array(4)].map((_, i) => <Skeleton key={i} w="w-full" h="h-5" />)}
              </div>
            ) : news.error ? (
              <p className="text-xs text-red-500">{news.error}</p>
            ) : news.articles.length === 0 ? (
              <p className="text-sm text-gray-400">{t("dash.noNews")}</p>
            ) : (
              <div className="space-y-3">
                {news.articles.slice(0, 6).map((a, i) => (
                  <a
                    key={i}
                    href={a.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-start gap-3 rounded-md p-2 transition-colors hover:bg-gray-50"
                  >
                    <span className="mt-0.5 text-xs text-gray-300">{String(i + 1).padStart(2, "0")}</span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-gray-700 group-hover:text-sv-600">
                        {a.title}
                      </p>
                      <p className="text-[11px] text-gray-400">
                        {a.source} · {a.publishedAt ? new Date(
                          // GDELT dates are YYYYMMDDHHMMSS
                          a.publishedAt.length === 14
                            ? `${a.publishedAt.slice(0,4)}-${a.publishedAt.slice(4,6)}-${a.publishedAt.slice(6,8)}T${a.publishedAt.slice(8,10)}:${a.publishedAt.slice(10,12)}:00Z`
                            : a.publishedAt
                        ).toLocaleDateString() : ""}
                      </p>
                    </div>
                    <ExternalLink className="mt-1 h-3 w-3 flex-shrink-0 text-gray-300 group-hover:text-sv-500" />
                  </a>
                ))}
              </div>
            )}
            <p className="mt-3 text-[10px] text-gray-300">GDELT Project · {t("dash.autoRefresh")}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
