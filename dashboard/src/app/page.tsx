"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { SignalBadge, ConfidenceBadge } from "@/components/signal-badge";
import { AssetSearch } from "@/components/asset-search";
import { SignalTable, type Signal } from "@/components/signal-table";
import { PortfolioOverview } from "@/components/portfolio-overview";
import { ActivityFeed } from "@/components/activity-feed";
import { LivePrices } from "@/components/live-prices";
import { AnalysisDetail } from "@/components/analysis-detail";
import {
  Zap,
  TrendingUp,
  Activity,
  Shield,
  BarChart3,
  Bell,
  Settings,
  Search,
  Menu,
  X,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  Layers,
  Brain,
  Globe,
  Clock,
} from "lucide-react";

const mockSignals: Signal[] = [
  { id: "1", symbol: "BTC/USD", assetClass: "Crypto", direction: "LONG", confidence: "High", entryZone: "$94,200 - $95,500", stopLoss: "$91,800", takeProfit: "$102,000", riskReward: "1:3.2", timestamp: "2m ago" },
  { id: "2", symbol: "AAPL", assetClass: "Stock", direction: "SHORT", confidence: "Medium", entryZone: "$228 - $230", stopLoss: "$235", takeProfit: "$215", riskReward: "1:2.1", timestamp: "8m ago" },
  { id: "3", symbol: "EUR/USD", assetClass: "Forex", direction: "LONG", confidence: "High", entryZone: "1.0850 - 1.0870", stopLoss: "1.0820", takeProfit: "1.0950", riskReward: "1:2.7", timestamp: "15m ago" },
  { id: "4", symbol: "XAU/USD", assetClass: "Commodity", direction: "NEUTRAL", confidence: "Low", entryZone: "-", stopLoss: "-", takeProfit: "-", riskReward: "-", timestamp: "32m ago" },
  { id: "5", symbol: "ETH/USD", assetClass: "Crypto", direction: "LONG", confidence: "Medium", entryZone: "$3,180 - $3,220", stopLoss: "$3,050", takeProfit: "$3,500", riskReward: "1:2.5", timestamp: "45m ago" },
  { id: "6", symbol: "TSLA", assetClass: "Stock", direction: "SHORT", confidence: "High", entryZone: "$248 - $252", stopLoss: "$260", takeProfit: "$225", riskReward: "1:2.0", timestamp: "1h ago" },
];

export default function Dashboard() {
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [analyzingSymbol, setAnalyzingSymbol] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("signals");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-hidden relative">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[128px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-full blur-[200px]" />

        {/* Grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: "64px 64px"
          }}
        />
      </div>

      {/* Main Layout */}
      <div className="relative z-10 flex h-screen">
        {/* Sidebar */}
        <motion.aside
          initial={{ x: -280 }}
          animate={{ x: sidebarOpen ? 0 : -280 }}
          className="fixed lg:relative lg:translate-x-0 w-72 h-full bg-[#0f0f15]/80 backdrop-blur-2xl border-r border-white/5 flex flex-col"
        >
          {/* Logo */}
          <div className="p-6 border-b border-white/5">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <div className="p-2.5 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl shadow-lg shadow-purple-500/25">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  TradingAI
                </h1>
                <p className="text-xs text-slate-500">Multi-Agent System</p>
              </div>
            </motion.div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            <NavItem icon={<BarChart3 />} label="Signals" active={activeTab === "signals"} onClick={() => setActiveTab("signals")} />
            <NavItem icon={<Brain />} label="Analysis" active={activeTab === "analysis"} onClick={() => setActiveTab("analysis")} />
            <NavItem icon={<Layers />} label="Portfolio" active={activeTab === "portfolio"} onClick={() => setActiveTab("portfolio")} />
            <NavItem icon={<Globe />} label="Markets" active={activeTab === "markets"} onClick={() => setActiveTab("markets")} />
            <NavItem icon={<Clock />} label="History" active={activeTab === "history"} onClick={() => setActiveTab("history")} />
          </nav>

          {/* Bottom actions */}
          <div className="p-4 border-t border-white/5 space-y-1">
            <NavItem icon={<Bell />} label="Alerts" badge="3" />
            <NavItem icon={<Settings />} label="Settings" />
          </div>
        </motion.aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Bar */}
          <header className="h-16 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-xl flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 hover:bg-white/5 rounded-lg transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>

              {/* Breadcrumb */}
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <span className="text-white font-medium">Dashboard</span>
                <ChevronRight className="w-4 h-4" />
                <span className="capitalize">{activeTab}</span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <LivePrices />
              <AssetSearch onSelect={setSelectedAsset} />
            </div>
          </header>

          {/* Content Area */}
          <div className="flex-1 overflow-auto p-6">
            <div className="max-w-[1800px] mx-auto space-y-6">
              {/* Portfolio Stats */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <PortfolioOverview />
              </motion.div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  icon={<TrendingUp className="w-5 h-5" />}
                  label="Active Signals"
                  value="12"
                  trend="+3 today"
                  trendUp={true}
                  delay={0.1}
                />
                <StatCard
                  icon={<Activity className="w-5 h-5" />}
                  label="Win Rate"
                  value="68.5%"
                  trend="+2.1%"
                  trendUp={true}
                  delay={0.2}
                />
                <StatCard
                  icon={<Shield className="w-5 h-5" />}
                  label="Risk Score"
                  value="Medium"
                  trend="-5%"
                  trendUp={true}
                  delay={0.3}
                />
                <StatCard
                  icon={<BarChart3 className="w-5 h-5" />}
                  label="Portfolio Beta"
                  value="1.12"
                  trend="+0.03"
                  trendUp={false}
                  delay={0.4}
                />
              </div>

              {/* Main Content Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Signals Table - 2 columns */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5, duration: 0.5 }}
                  className="lg:col-span-2"
                >
                  <Card className="bg-[#0f0f15]/60 border-white/5 backdrop-blur-xl overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 pointer-events-none" />
                    <div className="p-5 border-b border-white/5 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <h2 className="text-lg font-semibold">Live Trading Signals</h2>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-400">
                        <span className="px-2 py-1 bg-white/5 rounded">Auto-refresh: 15s</span>
                      </div>
                    </div>
                    <SignalTable
                      signals={mockSignals}
                      onAnalyze={setAnalyzingSymbol}
                    />
                  </Card>
                </motion.div>

                {/* Activity Feed - 1 column */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6, duration: 0.5 }}
                >
                  <Card className="bg-[#0f0f15]/60 border-white/5 backdrop-blur-xl h-full">
                    <div className="p-5 border-b border-white/5">
                      <h2 className="text-lg font-semibold">Activity Feed</h2>
                    </div>
                    <CardContent className="p-4">
                      <ActivityFeed />
                    </CardContent>
                  </Card>
                </motion.div>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Analysis Modal */}
      <AnimatePresence>
        {analyzingSymbol && (
          <AnalysisDetail
            symbol={analyzingSymbol}
            onClose={() => setAnalyzingSymbol(null)}
          />
        )}
      </AnimatePresence>

      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function NavItem({
  icon,
  label,
  active = false,
  badge,
  onClick
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  badge?: string;
  onClick?: () => void;
}) {
  return (
    <motion.button
      whileHover={{ x: 4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl transition-all ${
        active
          ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white border border-blue-500/20"
          : "text-slate-400 hover:text-white hover:bg-white/5"
      }`}
    >
      <div className="flex items-center gap-3">
        <span className={active ? "text-blue-400" : "text-slate-500"}>{icon}</span>
        <span className="text-sm font-medium">{label}</span>
      </div>
      {badge && (
        <span className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded-full">
          {badge}
        </span>
      )}
    </motion.button>
  );
}

function StatCard({
  icon,
  label,
  value,
  trend,
  trendUp,
  delay
}: {
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
      whileHover={{ scale: 1.02, y: -4 }}
    >
      <Card className="bg-[#0f0f15]/60 border-white/5 backdrop-blur-xl hover:border-white/10 transition-all group">
        <CardContent className="p-4 relative overflow-hidden">
          {/* Gradient glow */}
          <div className="absolute -top-10 -right-10 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-full blur-2xl group-hover:opacity-100 opacity-50 transition-opacity" />

          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">{label}</span>
              <div className="p-2 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg text-blue-400">
                {icon}
              </div>
            </div>

            <div className="text-2xl font-bold mt-2">{value}</div>

            <div className={`text-xs mt-2 flex items-center gap-1 ${
              trendUp ? 'text-green-400' : 'text-red-400'
            }`}>
              {trendUp ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
              {trend}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
