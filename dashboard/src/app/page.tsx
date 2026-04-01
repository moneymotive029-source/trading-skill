"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SignalBadge } from "@/components/signal-badge";
import { AssetSearch } from "@/components/asset-search";
import { SignalTable } from "@/components/signal-table";
import { PortfolioOverview } from "@/components/portfolio-overview";
import { ActivityFeed } from "@/components/activity-feed";
import { LivePrices } from "@/components/live-prices";
import { TrendingUp, Activity, Zap, Shield, BarChart3 } from "lucide-react";

export default function Dashboard() {
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      {/* Animated background gradient */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto space-y-6 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-between"
        >
          <div>
            <motion.div
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Trading Dashboard
                </h1>
                <p className="text-slate-400 text-sm mt-0.5">
                  AI-powered multi-agent trading signals
                </p>
              </div>
            </motion.div>
          </div>
          <div className="flex items-center gap-6">
            <LivePrices />
            <AssetSearch onSelect={setSelectedAsset} />
          </div>
        </motion.div>

        {/* Portfolio Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <PortfolioOverview />
        </motion.div>

        {/* Stats Row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          <StatCard
            icon={<TrendingUp className="w-5 h-5" />}
            label="Active Signals"
            value="12"
            trend="+3 today"
            trendUp={true}
            delay={0.4}
          />
          <StatCard
            icon={<Activity className="w-5 h-5" />}
            label="Win Rate"
            value="68.5%"
            trend="+2.1%"
            trendUp={true}
            delay={0.5}
          />
          <StatCard
            icon={<Shield className="w-5 h-5" />}
            label="Risk Score"
            value="Medium"
            trend="-5%"
            trendUp={true}
            delay={0.6}
          />
          <StatCard
            icon={<BarChart3 className="w-5 h-5" />}
            label="Portfolio Beta"
            value="1.12"
            trend="+0.03"
            trendUp={false}
            delay={0.7}
          />
        </motion.div>

        {/* Main Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          {/* Signals Panel - 2 columns */}
          <div className="lg:col-span-2">
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-xl overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 pointer-events-none" />
              <CardHeader className="border-b border-slate-800/50">
                <CardTitle className="text-white flex items-center gap-3">
                  <motion.div
                    className="w-2 h-2 bg-green-500 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  />
                  <span className="bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
                    Live Trading Signals
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <SignalTable selectedAsset={selectedAsset} />
              </CardContent>
            </Card>
          </div>

          {/* Activity Feed - 1 column */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9, duration: 0.5 }}
          >
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-xl h-full">
              <CardHeader className="border-b border-slate-800/50">
                <CardTitle className="text-white text-lg">Activity Feed</CardTitle>
              </CardHeader>
              <CardContent>
                <ActivityFeed />
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>

        {/* Detailed Analysis Modal */}
        <AnimatePresence>
          {selectedAsset && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={() => setSelectedAsset(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                className="w-full max-w-4xl"
              >
                <Card className="bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 border-slate-700 shadow-2xl shadow-purple-500/10">
                  <CardHeader className="border-b border-slate-700">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-white text-2xl">
                          Select an asset to analyze
                        </CardTitle>
                        <p className="text-slate-400 text-sm mt-1">
                          Click &quot;Analyze&quot; on any signal to view full multi-agent analysis
                        </p>
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => setSelectedAsset(null)}
                        className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                      >
                        <span className="text-2xl text-slate-400">×</span>
                      </motion.button>
                    </div>
                  </CardHeader>
                  <CardContent className="p-8">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                      <div className="p-4 bg-slate-800/50 rounded-xl">
                        <div className="text-3xl mb-2">📊</div>
                        <div className="text-white font-semibold">Technical</div>
                        <div className="text-slate-400 text-sm">RSI, MACD, Bands</div>
                      </div>
                      <div className="p-4 bg-slate-800/50 rounded-xl">
                        <div className="text-3xl mb-2">📈</div>
                        <div className="text-white font-semibold">Fundamental</div>
                        <div className="text-slate-400 text-sm">Metrics & On-chain</div>
                      </div>
                      <div className="p-4 bg-slate-800/50 rounded-xl">
                        <div className="text-3xl mb-2">🧠</div>
                        <div className="text-white font-semibold">AI Analysis</div>
                        <div className="text-slate-400 text-sm">Sentiment + PESTLE</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, trend, trendUp, delay }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  trend: string;
  trendUp: boolean;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ scale: 1.02, y: -2 }}
    >
      <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-xl hover:border-slate-600 transition-colors">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="text-slate-400 text-sm">{label}</div>
            <div className="p-2 bg-slate-800 rounded-lg text-slate-300">
              {icon}
            </div>
          </div>
          <div className="text-2xl font-bold text-white mt-2">{value}</div>
          <div className={`text-xs mt-1 ${trendUp ? 'text-green-400' : 'text-red-400'}`}>
            {trend}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
