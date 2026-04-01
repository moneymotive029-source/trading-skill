"use client";

import { useEffect, useState, useRef } from "react";
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
  const [prevPrices, setPrevPrices] = useState<Record<string, string>>({});
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const url = `/api/ws/prices?symbols=${symbols.join(",")}`;

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
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

    eventSource.onerror = () => {
      setConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  // Track price changes for animation
  useEffect(() => {
    Object.entries(prices).forEach(([symbol, data]) => {
      if (prevPrices[symbol] && prevPrices[symbol] !== data.price) {
        // Price changed - could trigger animation
      }
      setPrevPrices((prev) => ({ ...prev, [symbol]: data.price }));
    });
  }, [prices]);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-center gap-4 bg-slate-900/50 backdrop-blur-xl px-4 py-2 rounded-xl border border-slate-800"
    >
      <motion.div
        className="flex items-center gap-2"
        animate={{ opacity: connected ? 1 : 0.5 }}
      >
        <div
          className={`w-2 h-2 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`}
        >
          {connected && (
            <motion.div
              className="w-full h-full rounded-full bg-green-500"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
            />
          )}
        </div>
      </motion.div>

      <div className="flex gap-3 overflow-hidden">
        <AnimatePresence>
          {Object.entries(prices).map(([symbol, data], index) => {
            const change = parseFloat(data.change);
            const isUp = change >= 0;

            return (
              <motion.div
                key={symbol}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-1.5 px-2 py-1 bg-slate-800/50 rounded-lg"
              >
                <span className="text-xs font-medium text-slate-300">{symbol}</span>
                <motion.span
                  key={data.price}
                  initial={{ scale: 1.1, color: isUp ? "#4ade80" : "#f87171" }}
                  animate={{ scale: 1, color: "#e2e8f0" }}
                  transition={{ duration: 0.3 }}
                  className="text-xs text-slate-200"
                >
                  ${data.price}
                </motion.span>
                <motion.span
                  className={`text-xs ${isUp ? 'text-green-400' : 'text-red-400'}`}
                  animate={isUp ? { y: [0, -1, 0] } : {}}
                  transition={{ repeat: Infinity, duration: 1 }}
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
