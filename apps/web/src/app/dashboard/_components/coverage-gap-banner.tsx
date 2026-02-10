"use client";

import Link from "next/link";
import { useLanguage } from "@/context/language-context";

/**
 * A prominent banner on the main dashboard linking to the
 * full Coverage Gap Analysis page.
 */
export function CoverageGapBanner() {
  const { t } = useLanguage();

  return (
    <section className="py-12 bg-gradient-to-r from-red-50 via-orange-50 to-yellow-50">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 rounded-2xl border border-red-200 bg-white p-8 shadow-sm">
          {/* Left */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                {t("coverage.critical")}: 32
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-orange-100 text-orange-800">
                {t("coverage.high")}: 46
              </span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-1">
              {t("coverageBanner.title")}
            </h3>
            <p className="text-gray-600 text-sm max-w-xl">
              {t("coverageBanner.desc")}
            </p>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-6 text-center">
            <div>
              <div className="text-3xl font-bold text-gray-900">262</div>
              <div className="text-xs text-gray-500">{t("coverage.municipios")}</div>
            </div>
            <div className="h-10 w-px bg-gray-200" />
            <div>
              <div className="text-3xl font-bold text-red-600">0%</div>
              <div className="text-xs text-gray-500">{t("coverage.score")}</div>
            </div>
            <div className="h-10 w-px bg-gray-200" />
            <div>
              <div className="text-3xl font-bold text-orange-600">6</div>
              <div className="text-xs text-gray-500">{t("coverageBanner.deserts")}</div>
            </div>
          </div>

          {/* CTA */}
          <Link
            href="/dashboard/coverage"
            className="shrink-0 rounded-lg bg-red-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-red-700 transition-colors"
          >
            {t("coverageBanner.viewGaps")} &rarr;
          </Link>
        </div>
      </div>
    </section>
  );
}
