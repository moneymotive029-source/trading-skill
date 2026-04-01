"use client";

import { motion } from "framer-motion";
import { Card, CardContent } from "./ui/card";
import { DollarSign, Briefcase, TrendingUp, Gauge, ArrowUpRight, ArrowDownRight } from "lucide-react";

const portfolioData = [
  {
    label: "Total Value",
    value: "$100,000",
    change: "+$2,450 (2.5%)",
    changeUp: true,
    icon: <DollarSign className="w-5 h-5" />,
    gradient: "from-emerald-500 to-teal-500",
  },
  {
    label: "Open Positions",
    value: "7",
    change: "3 long, 4 short",
    changeUp: null,
    icon: <Briefcase className="w-5 h-5" />,
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    label: "Day P&L",
    value: "+$1,847",
    change: "+1.87%",
    changeUp: true,
    icon: <TrendingUp className="w-5 h-5" />,
    gradient: "from-green-500 to-emerald-500",
  },
  {
    label: "Risk Exposure",
    value: "6.2%",
    change: "Moderate",
    changeUp: null,
    icon: <Gauge className="w-5 h-5" />,
    gradient: "from-purple-500 to-pink-500",
  },
];

export function PortfolioOverview() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {portfolioData.map((item, index) => (
        <motion.div
          key={item.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1, duration: 0.4 }}
          whileHover={{ scale: 1.02, y: -4 }}
        >
          <Card className="bg-[#0f0f15]/60 border-white/5 backdrop-blur-xl hover:border-white/10 transition-all group relative overflow-hidden">
            {/* Animated gradient glow */}
            <div className={`absolute -top-20 -right-20 w-40 h-40 bg-gradient-to-br ${item.gradient} opacity-10 rounded-full blur-3xl group-hover:opacity-20 transition-all duration-500`} />

            <CardContent className="p-5 relative z-10">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-slate-400 text-sm">{item.label}</div>
                  <div className="text-3xl font-bold mt-1 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                    {item.value}
                  </div>
                </div>
                <div className={`p-3 bg-gradient-to-br ${item.gradient} rounded-xl text-white shadow-lg`}>
                  {item.icon}
                </div>
              </div>

              {item.change && (
                <div className={`flex items-center gap-1.5 mt-3 text-sm ${
                  item.changeUp === true ? 'text-green-400' :
                  item.changeUp === false ? 'text-red-400' :
                  'text-slate-500'
                }`}>
                  {item.changeUp === true && <ArrowUpRight className="w-4 h-4" />}
                  {item.changeUp === false && <ArrowDownRight className="w-4 h-4" />}
                  <span className="font-medium">{item.change}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
