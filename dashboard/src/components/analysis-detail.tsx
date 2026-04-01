"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { SignalBadge, ConfidenceBadge } from "./signal-badge";
import { X, TrendingUp, BarChart3, Brain, Shield, Activity, Target } from "lucide-react";

interface AnalysisDetailProps {
  symbol: string;
  onClose: () => void;
}

interface AnalysisData {
  signal: {
    direction: string;
    confidence: string;
    entryZone: string;
    stopLoss: string;
    takeProfit1: string;
    takeProfit2: string;
    riskReward: string;
  };
  technicals: {
    rsi: number;
    macd: { histogram: number; signal: string };
    movingAverages: Record<string, string>;
    bollingerBands: Record<string, string>;
  };
  fundamentals: Record<string, string>;
  sentiment: {
    score: number;
    classification: string;
    socialVolume: string;
  };
  pestle: Record<string, string>;
  riskMetrics: Record<string, string>;
  thesis: string;
}

// Mock data for demo
const mockAnalysis: AnalysisData = {
  signal: {
    direction: "LONG",
    confidence: "High",
    entryZone: "$94,200 - $95,500",
    stopLoss: "$91,800",
    takeProfit1: "$98,000",
    takeProfit2: "$102,000",
    riskReward: "1:3.2",
  },
  technicals: {
    rsi: 58.4,
    macd: { histogram: 124, signal: "Bullish" },
    movingAverages: { sma20: "$93,100", sma50: "$89,500", sma200: "$72,300" },
    bollingerBands: { upper: "$97,200", middle: "$93,500", lower: "$89,800" },
  },
  fundamentals: {
    marketCap: "$1.87T",
    volume24h: "$42.3B",
    dominance: "54.2%",
  },
  sentiment: {
    score: 72,
    classification: "Greed",
    socialVolume: "High",
  },
  pestle: {
    political: "Neutral",
    economic: "Positive",
    technological: "Positive",
    legal: "Neutral",
    environmental: "Neutral",
  },
  riskMetrics: {
    var95: "$3,200",
    cvar95: "$4,800",
    kellyPosition: "4.2%",
    recommendedPosition: "2.1%",
  },
  thesis: "Bitcoin is breaking above key resistance with strong momentum. RSI showing bullish divergence, MACD crossover confirmed. On-chain metrics indicate accumulation by whales. ETF inflows remain positive and technical setup suggests a move to $102k if $98k resistance clears.",
};

export function AnalysisDetail({ symbol, onClose }: AnalysisDetailProps) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<AnalysisData | null>(null);

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setData(mockAnalysis);
      setLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, [symbol]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-8 max-w-md"
        >
          <div className="flex flex-col items-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"
            />
            <p className="text-white mt-4 font-medium">
              Running multi-agent analysis on {symbol}...
            </p>
            <div className="flex gap-2 mt-3">
              {["Market", "Technical", "Fundamental", "Sentiment", "PESTLE"].map((agent, i) => (
                <motion.div
                  key={agent}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.2 }}
                  className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-400"
                >
                  {agent}
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm overflow-y-auto z-50 p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="max-w-6xl mx-auto my-8"
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 20 }}
        >
          <Card className="bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 border-slate-700 shadow-2xl shadow-purple-500/10">
            <CardHeader className="border-b border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-white text-2xl">{symbol}</CardTitle>
                      <SignalBadge signal={data.signal.direction as any} />
                      <ConfidenceBadge confidence={data.signal.confidence as any} />
                    </div>
                    <p className="text-slate-400 text-sm mt-1">
                      Multi-agent AI analysis
                    </p>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={onClose}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6 text-slate-400" />
                </motion.button>
              </div>
            </CardHeader>

            <CardContent className="p-6 space-y-6">
              {/* Trade Parameters */}
              <div>
                <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4 text-blue-400" />
                  Trade Parameters
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <ParamCard label="Entry Zone" value={data.signal.entryZone} />
                  <ParamCard label="Stop Loss" value={data.signal.stopLoss} color="red" />
                  <ParamCard label="Take Profit 1" value={data.signal.takeProfit1} color="green" />
                  <ParamCard label="Risk/Reward" value={data.signal.riskReward} />
                </div>
              </div>

              {/* Trade Thesis */}
              <div className="p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-xl border border-blue-500/20">
                <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  Trade Thesis
                </h4>
                <p className="text-slate-300 text-sm leading-relaxed">
                  Bitcoin is breaking above key resistance with strong momentum. RSI showing bullish divergence,
                  MACD crossover confirmed. On-chain metrics indicate accumulation by whales. ETF inflows remain
                  positive and technical setup suggests a move to $102k if $98k resistance clears.
                </p>
              </div>

              {/* Technical Analysis */}
              <div>
                <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-green-400" />
                  Technical Analysis
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <TechnicalCard label="RSI" value={data.technicals.rsi.toString()} isNeutral={data.technicals.rsi > 30 && data.technicals.rsi < 70} />
                  <TechnicalCard label="MACD" value={data.technicals.macd.signal} isBullish={data.technicals.macd.signal === "Bullish"} />
                  <TechnicalCard label="20 SMA" value={data.technicals.movingAverages.sma20} />
                  <TechnicalCard label="200 SMA" value={data.technicals.movingAverages.sma200} />
                </div>
              </div>

              {/* Sentiment & PESTLE */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Sentiment */}
                <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                  <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-pink-400" />
                    Sentiment Analysis
                  </h4>
                  <div className="space-y-3">
                    <SentimentRow label="Score" value={data.sentiment.score.toString()} />
                    <SentimentRow label="Classification" value={data.sentiment.classification} />
                    <SentimentRow label="Social Volume" value={data.sentiment.socialVolume} />
                  </div>
                </div>

                {/* PESTLE */}
                <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                  <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-cyan-400" />
                    PESTLE Summary
                  </h4>
                  <div className="space-y-2">
                    {Object.entries(data.pestle).map(([factor, rating]) => (
                      <PestleRow key={factor} factor={factor} rating={rating} />
                    ))}
                  </div>
                </div>
              </div>

              {/* Risk Metrics */}
              <div>
                <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <Shield className="w-4 h-4 text-yellow-400" />
                  Risk Metrics
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <RiskCard label="VaR (95%)" value={data.riskMetrics.var95} />
                  <RiskCard label="CVaR (95%)" value={data.riskMetrics.cvar95} />
                  <RiskCard label="Kelly Position" value={data.riskMetrics.kellyPosition} />
                  <RiskCard label="Recommended" value={data.riskMetrics.recommendedPosition} highlight />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}

function ParamCard({ label, value, color = "white" }: { label: string; value: string; color?: string }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={`p-3 bg-slate-800/50 rounded-xl border border-slate-700`}
    >
      <div className="text-slate-400 text-xs mb-1">{label}</div>
      <div className={`text-lg font-bold ${
        color === "red" ? "text-red-400" :
        color === "green" ? "text-green-400" :
        "text-white"
      }`}>
        {value}
      </div>
    </motion.div>
  );
}

function TechnicalCard({ label, value, isBullish, isNeutral }: { label: string; value: string; isBullish?: boolean; isNeutral?: boolean }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="p-3 bg-slate-800/50 rounded-xl border border-slate-700"
    >
      <div className="text-slate-400 text-xs mb-1">{label}</div>
      <div className={`text-lg font-bold ${
        isBullish ? "text-green-400" :
        isBullish === false ? "text-red-400" :
        isNeutral ? "text-yellow-400" :
        "text-white"
      }`}>
        {value}
      </div>
    </motion.div>
  );
}

function SentimentRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-slate-400 text-sm">{label}</span>
      <span className={`text-sm font-medium ${
        parseInt(value) > 60 ? "text-green-400" :
        parseInt(value) < 40 ? "text-red-400" :
        "text-white"
      }`}>
        {value}
      </span>
    </div>
  );
}

function PestleRow({ factor, rating }: { factor: string; rating: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-slate-400 text-sm capitalize">{factor}</span>
      <span className={`text-xs px-2 py-1 rounded-full ${
        rating === "Positive" ? "bg-green-500/20 text-green-400" :
        rating === "Negative" ? "bg-red-500/20 text-red-400" :
        "bg-slate-500/20 text-slate-400"
      }`}>
        {rating}
      </span>
    </div>
  );
}

function RiskCard({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className={`p-3 rounded-xl border ${
        highlight
          ? "bg-gradient-to-br from-blue-500/20 to-purple-500/20 border-blue-500/30"
          : "bg-slate-800/50 border-slate-700"
      }`}
    >
      <div className="text-slate-400 text-xs mb-1">{label}</div>
      <div className={`text-lg font-bold ${highlight ? "text-white" : "text-white"}`}>
        {value}
      </div>
    </motion.div>
  );
}
