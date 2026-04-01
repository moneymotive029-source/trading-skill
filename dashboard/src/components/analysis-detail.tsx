"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { SignalBadge, ConfidenceBadge } from "./signal-badge";
import { X } from "lucide-react";

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

export function AnalysisDetail({ symbol, onClose }: AnalysisDetailProps) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<AnalysisData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useState(() => {
    fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol }),
    })
      .then((res) => res.json())
      .then((result) => {
        if (result.success) {
          setData(result.data);
        } else {
          setError(result.error || "Failed to load analysis");
        }
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to connect to analysis service");
        setLoading(false);
      });
  });

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
        <Card className="bg-slate-900 border-slate-800 w-full max-w-4xl mx-4">
          <CardContent className="p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto" />
            <p className="text-white mt-4">
              Running multi-agent analysis on {symbol}...
            </p>
            <p className="text-slate-500 text-sm mt-2">
              This may take up to 60 seconds
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
        <Card className="bg-slate-900 border-slate-800 w-full max-w-4xl mx-4">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-white">Analysis Error</CardTitle>
              <button onClick={onClose} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-red-400">{error || "Failed to load analysis"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/80 overflow-y-auto z-50 p-4">
      <div className="max-w-6xl mx-auto my-8">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <CardTitle className="text-white text-2xl">{symbol}</CardTitle>
                <SignalBadge signal={data.signal.direction as any} />
                <ConfidenceBadge confidence={data.signal.confidence as any} />
              </div>
              <button onClick={onClose} className="text-slate-400 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Trade Parameters */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-slate-400 text-sm">Entry Zone</div>
                <div className="text-white font-medium">{data.signal.entryZone}</div>
              </div>
              <div>
                <div className="text-slate-400 text-sm">Stop Loss</div>
                <div className="text-red-400 font-medium">{data.signal.stopLoss}</div>
              </div>
              <div>
                <div className="text-slate-400 text-sm">Take Profit 1</div>
                <div className="text-green-400 font-medium">{data.signal.takeProfit1}</div>
              </div>
              <div>
                <div className="text-slate-400 text-sm">Risk/Reward</div>
                <div className="text-white font-medium">{data.signal.riskReward}</div>
              </div>
            </div>

            {/* Trade Thesis */}
            <div>
              <h4 className="text-white font-semibold mb-2">Trade Thesis</h4>
              <p className="text-slate-300">{data.thesis}</p>
            </div>

            {/* Technical Analysis */}
            <div>
              <h4 className="text-white font-semibold mb-3">Technical Analysis</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 p-3 rounded">
                  <div className="text-slate-400 text-xs">RSI</div>
                  <div className={`text-lg font-bold ${data.technicals.rsi > 70 ? 'text-red-400' : data.technicals.rsi < 30 ? 'text-green-400' : 'text-white'}`}>
                    {data.technicals.rsi}
                  </div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <div className="text-slate-400 text-xs">MACD</div>
                  <div className={`text-lg font-bold ${data.technicals.macd.signal === 'Bullish' ? 'text-green-400' : 'text-red-400'}`}>
                    {data.technicals.macd.signal}
                  </div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <div className="text-slate-400 text-xs">20 SMA</div>
                  <div className="text-lg font-bold text-white">{data.technicals.movingAverages.sma20}</div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <div className="text-slate-400 text-xs">200 SMA</div>
                  <div className="text-lg font-bold text-white">{data.technicals.movingAverages.sma200}</div>
                </div>
              </div>
            </div>

            {/* Sentiment & PESTLE */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-white font-semibold mb-3">Sentiment</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Score</span>
                    <span className={data.sentiment.score > 60 ? 'text-green-400' : 'text-red-400'}>{data.sentiment.score}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Classification</span>
                    <span className="text-white">{data.sentiment.classification}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Social Volume</span>
                    <span className="text-white">{data.sentiment.socialVolume}</span>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="text-white font-semibold mb-3">PESTLE Summary</h4>
                <div className="space-y-2">
                  {Object.entries(data.pestle).map(([factor, rating]) => (
                    <div key={factor} className="flex justify-between">
                      <span className="text-slate-400 capitalize">{factor}</span>
                      <span className={rating === 'Positive' ? 'text-green-400' : rating === 'Negative' ? 'text-red-400' : 'text-slate-400'}>{rating}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Risk Metrics */}
            <div>
              <h4 className="text-white font-semibold mb-3">Risk Metrics</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 p-3 rounded">
                  <div className="text-slate-400 text-xs">VaR (95%)</div>
                  <div className="text-white font-medium">{data.riskMetrics.var95}</div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <div className="text-slate-400 text-xs">CVaR (95%)</div>
                  <div className="text-white font-medium">{data.riskMetrics.cvar95}</div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <div className="text-slate-400 text-xs">Kelly Position</div>
                  <div className="text-white font-medium">{data.riskMetrics.kellyPosition}</div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <div className="text-slate-400 text-xs">Recommended</div>
                  <div className="text-white font-medium">{data.riskMetrics.recommendedPosition}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
