"use client";

import { motion } from "framer-motion";
import { TrendingUp, AlertCircle, RefreshCw, Shield, Bell, Zap } from "lucide-react";

const activities = [
  {
    id: 1,
    type: "signal",
    message: "New LONG signal on BTC/USD",
    time: "2m ago",
    icon: <TrendingUp className="w-4 h-4" />,
    gradient: "from-green-500 to-emerald-500",
    bg: "from-green-500/10 to-emerald-500/10",
    border: "border-green-500/20",
  },
  {
    id: 2,
    type: "alert",
    message: "AAPL hit entry zone ($228-230)",
    time: "8m ago",
    icon: <AlertCircle className="w-4 h-4" />,
    gradient: "from-red-500 to-orange-500",
    bg: "from-red-500/10 to-orange-500/10",
    border: "border-red-500/20",
  },
  {
    id: 3,
    type: "update",
    message: "EUR/USD analysis refreshed",
    time: "15m ago",
    icon: <RefreshCw className="w-4 h-4" />,
    gradient: "from-blue-500 to-cyan-500",
    bg: "from-blue-500/10 to-cyan-500/10",
    border: "border-blue-500/20",
  },
  {
    id: 4,
    type: "signal",
    message: "XAU/USD moved to NEUTRAL",
    time: "32m ago",
    icon: <Shield className="w-4 h-4" />,
    gradient: "from-slate-500 to-gray-500",
    bg: "from-slate-500/10 to-gray-500/10",
    border: "border-slate-500/20",
  },
  {
    id: 5,
    type: "risk",
    message: "Portfolio VaR updated: $4,200",
    time: "1h ago",
    icon: <Bell className="w-4 h-4" />,
    gradient: "from-yellow-500 to-amber-500",
    bg: "from-yellow-500/10 to-amber-500/10",
    border: "border-yellow-500/20",
  },
  {
    id: 6,
    type: "system",
    message: "AI agents synchronized",
    time: "1h ago",
    icon: <Zap className="w-4 h-4" />,
    gradient: "from-purple-500 to-pink-500",
    bg: "from-purple-500/10 to-pink-500/10",
    border: "border-purple-500/20",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: { opacity: 1, x: 0 },
};

export function ActivityFeed() {
  return (
    <motion.div
      className="space-y-2"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {activities.map((activity) => (
        <motion.div
          key={activity.id}
          variants={itemVariants}
          whileHover={{ x: 4, backgroundColor: "rgba(255,255,255,0.02)" }}
          className={`p-3 rounded-xl border ${activity.bg} ${activity.border} transition-all cursor-pointer group`}
        >
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg bg-gradient-to-br ${activity.gradient} text-white shadow-lg`}>
              {activity.icon}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-200 truncate group-hover:text-white transition-colors">
                {activity.message}
              </p>
              <p className="text-xs text-slate-500 mt-1">{activity.time}</p>
            </div>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}
