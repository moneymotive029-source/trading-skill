"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles } from "lucide-react";

interface PriceUpdate {
  symbol: string;
  price: string;
  change: string;
  timestamp: string;
}

const symbols = ["BTC", "ETH", "AAPL", "TSLA", "EURUSD", "XAUUSD"];

export function LivePrices() {
  const [prices, setPrices] = useState<Record<string, PriceUpdate>>({});
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const url = `/api/ws/prices?symbols=${symbols.join(",")}`;

    const eventSource = new EventSource(url);

    eventSource.onopen = () => setConnected(true);

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

    eventSource.onerror = () => {
      setConnected(false);
      eventSource.close();
    };

    return () => eventSource.close();
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-center gap-3 bg-[#0f0f15]/80 backdrop-blur-xl px-4 py-2 rounded-xl border border-white/5"
    >
      {/* Connection indicator */}
      <motion.div
        className="flex items-center gap-2"
        animate={{ opacity: connected ? 1 : 0.5 }}
      >
        <div className="relative">
          <div className={`w-2 h-2 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
          {connected && (
            <motion.div
              className="absolute inset-0 w-2 h-2 rounded-full bg-green-500"
              animate={{ scale: [1, 1.5, 1], opacity: [1, 0, 0] }}
              transition={{ repeat: Infinity, duration: 2 }}
            />
          )}
        </div>
      </motion.div>

      {/* Price tickers */}
      <div className="flex gap-2 overflow-hidden">
        <AnimatePresence>
          {Object.entries(prices).map(([symbol, data], index) => {
            const change = parseFloat(data.change);
            const isUp = change >= 0;

            return (
              <motion.div
                key={symbol}
                initial={{ opacity: 0, x: -10, scale: 0.9 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 10, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-1.5 px-2.5 py-1.5 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-colors"
              >
                <span className="text-xs font-semibold text-slate-300">{symbol}</span>
                <motion.span
                  key={data.price}
                  initial={{ scale: 1.1 }}
                  animate={{ scale: 1 }}
                  className="text-xs text-white font-mono"
                >
                  ${data.price}
                </motion.span>
                <motion.span
                  className={`text-xs font-medium ${isUp ? 'text-green-400' : 'text-red-400'}`}
                  animate={isUp ? { y: [0, -1, 0] } : {}}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                >
                  {isUp ? '+' : ''}{data.change}%
                </motion.span>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {!connected && (
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xs text-slate-500 flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3" />
            Connecting...
          </motion.span>
        )}
      </div>
    </motion.div>
  );
}
