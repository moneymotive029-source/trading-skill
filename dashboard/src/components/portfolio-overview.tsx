"use client";

import { Card, CardContent } from "./ui/card";

export function PortfolioOverview() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-4">
          <div className="text-slate-400 text-sm">Total Value</div>
          <div className="text-2xl font-bold text-white mt-1">$100,000</div>
          <div className="text-xs text-green-400 mt-1">+$2,450 (2.5%) today</div>
        </CardContent>
      </Card>

      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-4">
          <div className="text-slate-400 text-sm">Open Positions</div>
          <div className="text-2xl font-bold text-white mt-1">7</div>
          <div className="text-xs text-slate-500 mt-1">3 long, 4 short</div>
        </CardContent>
      </Card>

      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-4">
          <div className="text-slate-400 text-sm">Day P&L</div>
          <div className="text-2xl font-bold text-green-400 mt-1">+$1,847</div>
          <div className="text-xs text-green-400 mt-1">+1.87%</div>
        </CardContent>
      </Card>

      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-4">
          <div className="text-slate-400 text-sm">Risk Exposure</div>
          <div className="text-2xl font-bold text-white mt-1">6.2%</div>
          <div className="text-xs text-yellow-400 mt-1">Moderate</div>
        </CardContent>
      </Card>
    </div>
  );
}
