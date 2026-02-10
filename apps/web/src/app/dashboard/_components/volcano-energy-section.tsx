import { Bitcoin, Pickaxe } from "lucide-react";
import { useLanguage } from "@/context/language-context";

export function VolcanoEnergySection() {
  const { t } = useLanguage();

  return (
    <section className="border-b border-gray-200 py-12 lg:py-16" id="volcano-energy">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-orange-200 bg-orange-50 text-orange-600"><Pickaxe className="h-5 w-5" /></div>
          <div>
            <h2 className="font-serif text-2xl font-extrabold text-sv-950">{t("dash.volcanoTitle")}</h2>
            <p className="text-xs text-gray-400">{t("dash.volcanoDesc")}</p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="text-3xl font-extrabold text-orange-600">204.4 MW</div>
            <div className="mt-1 text-xs text-gray-500">{t("dash.geothermalCapacity")}</div>
            <div className="mt-1 text-[11px] text-gray-400">{t("dash.largestCA")}</div>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="text-3xl font-extrabold text-emerald-600">24%</div>
            <div className="mt-1 text-xs text-gray-500">{t("dash.nationalGrid")}</div>
            <div className="mt-1 text-[11px] text-gray-400">{t("dash.renewableSource")}</div>
          </div>
          <div className="col-span-1 sm:col-span-2 rounded-lg border border-gray-200 bg-white p-6">
            <div className="mb-2 text-xs font-medium text-gray-500">{t("dash.geothermalPlants")}</div>
            <div className="space-y-2">
              {["Ahuachapán (95 MW)", "Berlín (109.4 MW)"].map((p) => (
                <div key={p} className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-orange-500" />
                  <span className="text-sm font-medium text-gray-700">{p}</span>
                </div>
              ))}
            </div>
            <div className="mt-3 rounded-md border border-orange-200 bg-orange-50 px-4 py-2">
              <div className="flex items-center gap-2">
                <Bitcoin className="h-4 w-4 text-[#f7931a]" />
                <span className="text-xs font-semibold text-orange-700">{t("dash.volcanoMining")}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
