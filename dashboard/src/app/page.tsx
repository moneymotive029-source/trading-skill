"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SignalBadge } from "@/components/signal-badge";
import { AssetSearch } from "@/components/asset-search";
import { SignalTable } from "@/components/signal-table";
import { PortfolioOverview } from "@/components/portfolio-overview";
import { ActivityFeed } from "@/components/activity-feed";
import { LivePrices } from "@/components/live-prices";

export default function Dashboard() {
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Trading Dashboard</h1>
            <p className="text-slate-400 mt-1">
              AI-powered trading signals from multi-agent analysis
            </p>
          </div>
          <div className="flex items-center gap-6">
            <LivePrices />
            <AssetSearch onSelect={setSelectedAsset} />
          </div>
        </div>

        {/* Portfolio Overview */}
        <PortfolioOverview />

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Signals Panel - 2 columns */}
          <div className="lg:col-span-2">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  Live Trading Signals
                </CardTitle>
              </CardHeader>
              <CardContent>
                <SignalTable selectedAsset={selectedAsset} />
              </CardContent>
            </Card>
          </div>

          {/* Activity Feed - 1 column */}
          <div>
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white">Activity Feed</CardTitle>
              </CardHeader>
              <CardContent>
                <ActivityFeed />
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Detailed Analysis Panel (shown when asset selected) */}
        {selectedAsset && (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">
                Analysis: {selectedAsset}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-slate-400">
                Select &quot;Analyze&quot; from the signals table to view detailed
                multi-agent analysis including technical indicators, fundamentals,
                sentiment scores, and PESTLE+ factors.
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
