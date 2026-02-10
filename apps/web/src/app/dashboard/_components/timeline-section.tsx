import { useState } from "react";
import { Clock } from "lucide-react";
import { useLanguage } from "@/context/language-context";
import { TIMELINE } from "@/data/static-metrics";
import { TIMELINE_CAT_COLORS } from "./helpers";

export function TimelineSection() {
  const { t } = useLanguage();
  const [filter, setFilter] = useState<string | null>(null);
  const filtered = filter ? TIMELINE.filter((tl) => tl.category === filter) : TIMELINE;

  return (
    <section className="py-12 lg:py-16" id="timeline">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-sv-200 bg-sv-50 text-sv-600"><Clock className="h-5 w-5" /></div>
          <div>
            <h2 className="font-serif text-2xl font-extrabold text-sv-950">{t("dash.timelineTitle")}</h2>
            <p className="text-xs text-gray-400">{t("dash.timelineDesc")}</p>
          </div>
        </div>

        {/* Filter buttons */}
        <div className="mb-6 flex flex-wrap gap-2">
          <button onClick={() => setFilter(null)}
            className={`rounded-md px-4 py-1.5 text-xs font-semibold transition-all ${!filter ? "bg-sv-950 text-white" : "bg-gray-100 text-gray-500 hover:bg-gray-200"}`}>
            {t("dash.all")} ({TIMELINE.length})
          </button>
          {Object.entries(TIMELINE_CAT_COLORS).map(([cat, cls]) => {
            const count = TIMELINE.filter((tl) => tl.category === cat).length;
            return (
              <button key={cat} onClick={() => setFilter(filter === cat ? null : cat)}
                className={`rounded-md border px-4 py-1.5 text-xs font-semibold capitalize transition-all ${filter === cat ? cls : "border-gray-200 bg-gray-50 text-gray-400 hover:bg-gray-100"}`}>
                {cat} ({count})
              </button>
            );
          })}
        </div>

        {/* Timeline */}
        <div className="relative">
          <div className="absolute bottom-0 left-5 top-0 w-px bg-gray-200" />
          <div className="space-y-1">
            {filtered.map((item, i) => (
              <div key={i} className="group relative flex gap-4 py-3 pl-1">
                <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-gray-200 bg-white text-base transition-all group-hover:border-sv-300 group-hover:bg-sv-50">
                  {item.icon}
                </div>
                <div className="min-w-0 flex-1 pt-0.5">
                  <div className="mb-0.5 flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gold-500">{item.date}</span>
                    <span className={`rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${TIMELINE_CAT_COLORS[item.category]}`}>
                      {item.category}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-sv-950 transition-colors group-hover:text-sv-600">{item.title}</h4>
                  <p className="mt-0.5 text-xs leading-relaxed text-gray-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
