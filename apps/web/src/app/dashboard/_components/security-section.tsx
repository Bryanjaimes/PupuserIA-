import { Lock } from "lucide-react";
import { useLanguage } from "@/context/language-context";

export function SecuritySection() {
  const { t } = useLanguage();

  return (
    <section className="border-b border-gray-200 bg-[#f8f9fc] py-12 lg:py-16" id="security-highlight">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-red-200 bg-red-50 text-red-600"><Lock className="h-5 w-5" /></div>
          <div>
            <h2 className="font-serif text-2xl font-extrabold text-sv-950">{t("dash.securityTitle")}</h2>
            <p className="text-xs text-gray-400">{t("dash.securityDesc")}</p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {/* Homicide Rate — large card */}
          <div className="row-span-2 flex flex-col justify-between rounded-lg border border-gray-200 bg-white p-6">
            <div>
              <div className="mb-1 text-xs font-medium text-gray-500">{t("dash.homicideRate")}</div>
              <div className="mt-3">
                <div className="text-[11px] text-gray-400 line-through">103/100k (2015)</div>
                <div className="text-5xl font-extrabold text-emerald-600">1.7</div>
                <div className="text-sm text-gray-400">per 100k (2024)</div>
              </div>
            </div>
            <div className="mt-6">
              <div className="mb-2 flex justify-between text-[10px] text-gray-400"><span>2015</span><span>2024</span></div>
              <div className="relative h-3 w-full overflow-hidden rounded-full bg-gray-100">
                <div className="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-red-500 via-orange-400 to-emerald-500 transition-all duration-1000" style={{ width: "98.3%" }} />
              </div>
              <div className="mt-1 text-center text-xs font-bold text-emerald-600">98.3% {t("dash.reduction")}</div>
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="mb-1 text-xs font-medium text-gray-500">{t("dash.gangArrests")}</div>
            <div className="text-3xl font-extrabold text-sv-950">94,844+</div>
            <div className="mt-1 text-[11px] text-gray-400">State of Exception · 47+ extensions</div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="mb-1 text-xs font-medium text-gray-500">{t("dash.cecotPrison")}</div>
            <div className="text-3xl font-extrabold text-sv-950">40,000</div>
            <div className="mt-1 text-[11px] text-gray-400">World&apos;s largest · Tecoluca, San Vicente</div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="mb-1 text-xs font-medium text-gray-500">{t("dash.reelection")}</div>
            <div className="text-3xl font-extrabold text-gold-500">84.65%</div>
            <div className="mt-1 text-[11px] text-gray-400">Feb 2024 — largest in ES history</div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="mb-1 text-xs font-medium text-gray-500">{t("dash.safetyPerception")}</div>
            <div className="text-3xl font-extrabold text-sv-500">91%</div>
            <div className="mt-1 text-[11px] text-gray-400">Feel safe · CID Gallup 2024</div>
          </div>
        </div>
      </div>
    </section>
  );
}
