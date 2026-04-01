"use client";

import { motion } from "framer-motion";
import { SignalBadge, ConfidenceBadge } from "./signal-badge";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

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

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const rowVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
};

export function SignalTable({
  signals,
  onAnalyze,
}: {
  signals: Signal[];
  onAnalyze: (symbol: string) => void;
}) {
  return (
    <div className="overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/5">
            <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4">
              Asset
            </th>
            <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4">
              Signal
            </th>
            <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4">
              Confidence
            </th>
            <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4 hidden md:table-cell">
              Entry Zone
            </th>
            <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4 hidden lg:table-cell">
              Stop Loss
            </th>
            <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4 hidden xl:table-cell">
              Target
            </th>
            <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4">
              R/R
            </th>
            <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4">
              Age
            </th>
            <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider py-3 px-4">
              Action
            </th>
          </tr>
        </thead>
        <motion.tbody
          className="divide-y divide-white/5"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {signals.map((signal, index) => (
            <motion.tr
              key={signal.id}
              variants={rowVariants}
              whileHover={{ backgroundColor: "rgba(59, 130, 246, 0.03)" }}
              className="cursor-pointer transition-colors group"
            >
              <td className="py-3 px-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center border border-white/5">
                    {signal.assetClass === "Crypto" && "₿"}
                    {signal.assetClass === "Stock" && "📈"}
                    {signal.assetClass === "Forex" && "💱"}
                    {signal.assetClass === "Commodity" && "🏆"}
                  </div>
                  <div>
                    <div className="font-medium text-white">{signal.symbol}</div>
                    <div className="text-xs text-slate-500">{signal.assetClass}</div>
                  </div>
                </div>
              </td>
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  {signal.direction === "LONG" && (
                    <ArrowUpRight className="w-4 h-4 text-green-400" />
                  )}
                  {signal.direction === "SHORT" && (
                    <ArrowDownRight className="w-4 h-4 text-red-400" />
                  )}
                  {signal.direction === "NEUTRAL" && (
                    <Minus className="w-4 h-4 text-slate-400" />
                  )}
                  <SignalBadge signal={signal.direction} />
                </div>
              </td>
              <td className="py-3 px-4">
                <ConfidenceBadge confidence={signal.confidence} />
              </td>
              <td className="py-3 px-4 text-slate-300 text-sm hidden md:table-cell">
                {signal.entryZone}
              </td>
              <td className="py-3 px-4 text-red-400 text-sm hidden lg:table-cell">
                {signal.stopLoss}
              </td>
              <td className="py-3 px-4 text-green-400 text-sm hidden xl:table-cell">
                {signal.takeProfit}
              </td>
              <td className="py-3 px-4">
                <span className="text-slate-300 text-sm font-mono">{signal.riskReward}</span>
              </td>
              <td className="py-3 px-4">
                <span className="text-slate-500 text-sm">{signal.timestamp}</span>
              </td>
              <td className="py-3 px-4 text-right">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => onAnalyze(signal.symbol.split("/")[0])}
                  className="px-4 py-2 text-sm bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all shadow-lg shadow-blue-500/20 font-medium"
                >
                  Analyze
                </motion.button>
              </td>
            </motion.tr>
          ))}
        </motion.tbody>
      </table>

      {signals.length === 0 && (
        <div className="text-center py-12">
          <div className="text-slate-500">No active signals</div>
          <div className="text-slate-600 text-sm mt-1">Signals will appear here when generated</div>
        </div>
      )}
    </div>
  );
}
