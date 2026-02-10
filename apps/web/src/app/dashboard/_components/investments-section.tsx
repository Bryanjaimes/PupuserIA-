import { BarChart3, Building2 } from "lucide-react";
import { useLanguage } from "@/context/language-context";
import { INVESTMENTS } from "@/data/static-metrics";
import { ICON_MAP, STATUS_COLORS } from "./helpers";

export function InvestmentsSection() {
  const { t } = useLanguage();

  return (
    <section className="border-b border-gray-200 bg-[#f8f9fc] py-12 lg:py-16" id="investments">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-gold-200 bg-gold-50 text-gold-600"><BarChart3 className="h-5 w-5" /></div>
          <div>
            <h2 className="font-serif text-2xl font-extrabold text-sv-950">{t("dash.investmentsTitle")}</h2>
            <p className="text-xs text-gray-400">{t("dash.investmentsDesc")}</p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {INVESTMENTS.map((inv) => (
            <div key={inv.title} className="group rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
              <div className="mb-4 flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-gray-200 bg-gray-50 text-gray-600">
                    {ICON_MAP[inv.iconName] ?? <Building2 className="h-5 w-5" />}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-sv-950">{inv.title}</h3>
                    <div className="text-[11px] text-gray-400">{inv.partner}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-extrabold text-gold-500">{inv.amount}</div>
                  <span className={`mt-1 inline-block rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${STATUS_COLORS[inv.status]}`}>
                    {inv.status}
                  </span>
                </div>
              </div>
              <p className="text-sm leading-relaxed text-gray-500">{inv.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
