"use client";

import { useEffect, useState, useRef } from "react";

interface PriceUpdate {
  symbol: string;
  price: string;
  change: string;
  timestamp: string;
}

export function LivePrices() {
  const [prices, setPrices] = useState<Record<string, PriceUpdate>>({});
  const [connected, setConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Connect to SSE stream for real-time prices
    // In production, replace with WebSocket for full-duplex communication
    const symbols = ["BTC", "ETH", "AAPL", "TSLA", "EURUSD", "XAUUSD"];
    const url = `/api/ws/prices?symbols=${symbols.join(",")}`;

    // Use EventSource for SSE (Server-Sent Events)
    // For full WebSocket, use: const ws = new WebSocket('ws://...')
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log("Price stream connected");
      setConnected(true);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "init" || data.type === "update") {
          const newPrices: Record<string, PriceUpdate> = {};
          data.prices.forEach((p: PriceUpdate) => {
            newPrices[p.symbol] = p;
          });
          setPrices(newPrices);
        }
      } catch (err) {
        console.error("Failed to parse price update:", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("Price stream error:", err);
      setConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <div
          className={`w-2 h-2 rounded-full ${connected ? "bg-green-500 animate-pulse" : "bg-red-500"}`}
        />
        <span className="text-xs text-slate-400">
          {connected ? "Live" : "Disconnected"}
        </span>
      </div>

      <div className="flex gap-4">
        {Object.entries(prices).map(([symbol, data]) => (
          <div key={symbol} className="flex items-center gap-2">
            <span className="text-sm font-medium text-white">{symbol}</span>
            <span className="text-sm text-slate-300">${data.price}</span>
            <span
              className={`text-xs ${parseFloat(data.change) >= 0 ? "text-green-400" : "text-red-400"}`}
            >
              {parseFloat(data.change) >= 0 ? "+" : ""}
              {data.change}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
