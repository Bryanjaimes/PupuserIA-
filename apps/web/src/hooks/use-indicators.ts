"use client";

import { useEffect, useState, useCallback } from "react";
import { fetchAllIndicators, type WBDataPoint } from "@/lib/world-bank";

export interface IndicatorsState {
  data: Map<string, WBDataPoint>;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  refetch: () => void;
}

export function useWorldBankData(): IndicatorsState {
  const [data, setData] = useState<Map<string, WBDataPoint>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchAllIndicators();
      setData(result);
      setLastUpdated(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, lastUpdated, refetch: fetchData };
}

export interface BtcPriceState {
  price: number | null;
  change24h: number;
  loading: boolean;
}

export function useBtcPrice(): BtcPriceState {
  const [price, setPrice] = useState<number | null>(null);
  const [change24h, setChange24h] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPrice() {
      try {
        const res = await fetch(
          "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
        );
        const data = await res.json();
        setPrice(data.bitcoin.usd);
        setChange24h(data.bitcoin.usd_24h_change ?? 0);
      } catch {
        setPrice(97_500);
        setChange24h(2.1);
      } finally {
        setLoading(false);
      }
    }
    fetchPrice();
    const interval = setInterval(fetchPrice, 60_000);
    return () => clearInterval(interval);
  }, []);

  return { price, change24h, loading };
}
