import {
  Bitcoin, TrendingUp, Shield, Zap, Wallet,
  ArrowUpRight, ArrowDownRight,
} from "lucide-react";
import { useLanguage } from "@/context/language-context";
import { BTC_RESERVE } from "@/data/static-metrics";
import { fmtUsd } from "./helpers";
import { Skeleton } from "./metric-cards";

interface BtcReserveSectionProps {
  btcLoading: boolean;
  btcPrice: number | null;
  btcChange24h: number;
  reserveValue: number;
  unrealizedPnl: number;
  pnlPercent: number;
}

export function BtcReserveSection({
  btcLoading, btcPrice, btcChange24h,
  reserveValue, unrealizedPnl, pnlPercent,
}: BtcReserveSectionProps) {
  const { t } = useLanguage();

  return (
    <section className="border-b border-gray-200 py-12 lg:py-16" id="btc-reserve">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-orange-200 bg-orange-50 text-[#f7931a]"><Bitcoin className="h-5 w-5" /></div>
          <div>
            <h2 className="font-serif text-2xl font-extrabold text-sv-950">{t("dash.btcReserve")}</h2>
            <p className="text-xs text-gray-400">{t("dash.btcReserveDesc")} {BTC_RESERVE.firstBuy}</p>
          </div>
        </div>

        <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Total Holdings */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
            <div className="mb-2 flex items-center justify-between"><span className="text-xs font-medium text-gray-500">{t("dash.totalHoldings")}</span><Wallet className="h-4 w-4 text-[#f7931a]" /></div>
            <div className="text-3xl font-extrabold text-sv-950">{BTC_RESERVE.totalBtc.toLocaleString()}</div>
            <div className="mt-1 text-sm font-semibold text-[#f7931a]">BTC</div>
            <div className="mt-2 text-[11px] text-gray-400">+1 BTC/day since {BTC_RESERVE.dailyBuySince}</div>
          </div>

          {/* Reserve Value */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
            <div className="mb-2 flex items-center justify-between"><span className="text-xs font-medium text-gray-500">{t("dash.reserveValue")}</span><TrendingUp className="h-4 w-4 text-emerald-600" /></div>
            <div className="text-3xl font-extrabold text-sv-950">{btcLoading ? <Skeleton w="w-32" h="h-9" /> : fmtUsd(reserveValue)}</div>
            <div className="mt-1 flex items-center gap-1 text-sm">
              {pnlPercent >= 0
                ? <span className="flex items-center gap-1 font-semibold text-emerald-600"><ArrowUpRight className="h-3.5 w-3.5" />+{pnlPercent.toFixed(1)}%</span>
                : <span className="flex items-center gap-1 font-semibold text-red-600"><ArrowDownRight className="h-3.5 w-3.5" />{pnlPercent.toFixed(1)}%</span>}
              <span className="text-gray-400">{t("dash.unrealized")}</span>
            </div>
          </div>

          {/* BTC Price Live */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
            <div className="mb-2 flex items-center justify-between"><span className="text-xs font-medium text-gray-500">{t("dash.btcPriceLive")}</span><Zap className="h-4 w-4 text-gold-500" /></div>
            <div className="text-3xl font-extrabold text-sv-950">{btcLoading ? <Skeleton w="w-28" h="h-9" /> : `$${btcPrice?.toLocaleString()}`}</div>
            <div className="mt-1 flex items-center gap-1 text-sm">
              {btcChange24h >= 0
                ? <span className="flex items-center gap-1 font-semibold text-emerald-600"><ArrowUpRight className="h-3.5 w-3.5" />+{btcChange24h.toFixed(2)}%</span>
                : <span className="flex items-center gap-1 font-semibold text-red-600"><ArrowDownRight className="h-3.5 w-3.5" />{btcChange24h.toFixed(2)}%</span>}
              <span className="text-gray-400">24h</span>
            </div>
          </div>

          {/* Avg Buy Price */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-md">
            <div className="mb-2 flex items-center justify-between"><span className="text-xs font-medium text-gray-500">{t("dash.avgBuyPrice")}</span><Shield className="h-4 w-4 text-sv-500" /></div>
            <div className="text-3xl font-extrabold text-sv-950">${BTC_RESERVE.avgBuyPrice.toLocaleString()}</div>
            <div className="mt-1 text-sm">
              <span className="text-gray-400">P&L: </span>
              <span className={`font-semibold ${unrealizedPnl >= 0 ? "text-emerald-600" : "text-red-600"}`}>
                {unrealizedPnl >= 0 ? "+" : ""}{fmtUsd(Math.abs(unrealizedPnl))}
              </span>
            </div>
          </div>
        </div>

        {/* Detail grid */}
        <div className="rounded-lg border border-orange-200 bg-orange-50 p-5">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div><div className="mb-1 text-xs font-medium text-gray-500">{t("dash.firstPurchase")}</div><div className="text-sm font-bold text-sv-950">{BTC_RESERVE.firstBuy}</div><div className="text-[11px] text-gray-400">200 BTC @ ~$46,000</div></div>
            <div><div className="mb-1 text-xs font-medium text-gray-500">{t("dash.managedBy")}</div><div className="text-sm font-bold text-sv-950">{BTC_RESERVE.managedBy}</div><div className="text-[11px] text-gray-400">{BTC_RESERVE.directors}</div></div>
            <div><div className="mb-1 text-xs font-medium text-gray-500">{t("dash.imfStatus")}</div><div className="text-sm font-bold text-sv-950">{BTC_RESERVE.imfStatus}</div><div className="text-[11px] text-gray-400">{BTC_RESERVE.imfLoan}</div></div>
            <div><div className="mb-1 text-xs font-medium text-gray-500">{t("dash.dailyPurchase")}</div><div className="text-sm font-bold text-sv-950">1 BTC / day</div><div className="text-[11px] text-gray-400">Since {BTC_RESERVE.dailyBuySince}</div></div>
          </div>
        </div>
      </div>
    </section>
  );
}
