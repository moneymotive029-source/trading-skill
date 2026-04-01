"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { SignalBadge, ConfidenceBadge } from "./signal-badge";
import { AnalysisDetail } from "./analysis-detail";

interface Signal {
  id: string;
  symbol: string;
  assetClass: string;
  direction: "LONG" | "SHORT" | "NEUTRAL";
  confidence: "High" | "Medium" | "Low";
  entryZone: string;
  stopLoss: string;
  takeProfit: string;
  riskReward: string;
  timestamp: string;
}

const mockSignals: Signal[] = [
  {
    id: "1",
    symbol: "BTC/USD",
    assetClass: "Crypto",
    direction: "LONG",
    confidence: "High",
    entryZone: "$94,200 - $95,500",
    stopLoss: "$91,800",
    takeProfit: "$102,000",
    riskReward: "1:3.2",
    timestamp: "2 min ago",
  },
  {
    id: "2",
    symbol: "AAPL",
    assetClass: "Stock",
    direction: "SHORT",
    confidence: "Medium",
    entryZone: "$228 - $230",
    stopLoss: "$235",
    takeProfit: "$215",
    riskReward: "1:2.1",
    timestamp: "8 min ago",
  },
  {
    id: "3",
    symbol: "EUR/USD",
    assetClass: "Forex",
    direction: "LONG",
    confidence: "High",
    entryZone: "1.0850 - 1.0870",
    stopLoss: "1.0820",
    takeProfit: "1.0950",
    riskReward: "1:2.7",
    timestamp: "15 min ago",
  },
  {
    id: "4",
    symbol: "XAU/USD",
    assetClass: "Commodity",
    direction: "NEUTRAL",
    confidence: "Low",
    entryZone: "-",
    stopLoss: "-",
    takeProfit: "-",
    riskReward: "-",
    timestamp: "32 min ago",
  },
  {
    id: "5",
    symbol: "ETH/USD",
    assetClass: "Crypto",
    direction: "LONG",
    confidence: "Medium",
    entryZone: "$3,180 - $3,220",
    stopLoss: "$3,050",
    takeProfit: "$3,500",
    riskReward: "1:2.5",
    timestamp: "45 min ago",
  },
  {
    id: "6",
    symbol: "TSLA",
    assetClass: "Stock",
    direction: "SHORT",
    confidence: "High",
    entryZone: "$248 - $252",
    stopLoss: "$260",
    takeProfit: "$225",
    riskReward: "1:2.0",
    timestamp: "1h ago",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
    },
  },
};

const rowVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
    },
  },
};

export function SignalTable({ selectedAsset }: { selectedAsset: string | null }) {
  const [analyzingSymbol, setAnalyzingSymbol] = useState<string | null>(null);

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3 pl-4">
                Asset
              </th>
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3">
                Signal
              </th>
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3">
                Confidence
              </th>
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3">
                Entry
              </th>
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3">
                Stop
              </th>
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3">
                Target
              </th>
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3">
                R/R
              </th>
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3">
                Age
              </th>
              <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider pb-3 pr-4">
                Action
              </th>
            </tr>
          </thead>
          <motion.tbody
            className="divide-y divide-slate-800"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {mockSignals.map((signal, index) => (
              <motion.tr
                key={signal.id}
                variants={rowVariants}
                whileHover={{
                  backgroundColor: "rgba(59, 130, 246, 0.05)",
                  scale: 1.005,
                }}
                className="cursor-pointer transition-colors"
              >
                <td className="py-3 pl-4">
                  <div className="flex flex-col">
                    <span className="font-medium text-white">{signal.symbol}</span>
                    <span className="text-xs text-slate-500">{signal.assetClass}</span>
                  </div>
                </td>
                <td className="py-3">
                  <SignalBadge signal={signal.direction} />
                </td>
                <td className="py-3">
                  <ConfidenceBadge confidence={signal.confidence} />
                </td>
                <td className="py-3 text-slate-300 text-sm">{signal.entryZone}</td>
                <td className="py-3 text-red-400 text-sm">{signal.stopLoss}</td>
                <td className="py-3 text-green-400 text-sm">{signal.takeProfit}</td>
                <td className="py-3 text-slate-300 text-sm">{signal.riskReward}</td>
                <td className="py-3 text-slate-500 text-sm">{signal.timestamp}</td>
                <td className="py-3 pr-4">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-3 py-1.5 text-xs bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all shadow-lg shadow-blue-500/20"
                    onClick={() => setAnalyzingSymbol(signal.symbol.split("/")[0])}
                  >
                    Analyze
                  </motion.button>
                </td>
              </motion.tr>
            ))}
          </motion.tbody>
        </table>
      </div>

      {analyzingSymbol && (
        <AnalysisDetail
          symbol={analyzingSymbol}
          onClose={() => setAnalyzingSymbol(null)}
        />
      )}
    </>
  );
}
