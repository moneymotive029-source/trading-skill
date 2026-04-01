"use client";

import { motion } from "framer-motion";
import { Bell, TrendingUp, AlertCircle, RefreshCw, Shield } from "lucide-react";

const activities = [
  {
    id: 1,
    type: "signal",
    message: "New LONG signal on BTC/USD",
    time: "2m ago",
    color: "green",
    icon: <TrendingUp className="w-4 h-4" />,
  },
  {
    id: 2,
    type: "alert",
    message: "AAPL hit entry zone ($228-230)",
    time: "8m ago",
    color: "red",
    icon: <AlertCircle className="w-4 h-4" />,
  },
  {
    id: 3,
    type: "update",
    message: "EUR/USD analysis refreshed",
    time: "15m ago",
    color: "blue",
    icon: <RefreshCw className="w-4 h-4" />,
  },
  {
    id: 4,
    type: "signal",
    message: "XAU/USD moved to NEUTRAL",
    time: "32m ago",
    color: "slate",
    icon: <Shield className="w-4 h-4" />,
  },
  {
    id: 5,
    type: "risk",
    message: "Portfolio VaR updated: $4,200",
    time: "1h ago",
    color: "yellow",
    icon: <Bell className="w-4 h-4" />,
  },
];

const colorClasses = {
  green: {
    bg: "bg-green-500/10",
    border: "border-green-500/20",
    text: "text-green-400",
    icon: "text-green-400",
  },
  red: {
    bg: "bg-red-500/10",
    border: "border-red-500/20",
    text: "text-red-400",
    icon: "text-red-400",
  },
  blue: {
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
    text: "text-blue-400",
    icon: "text-blue-400",
  },
  slate: {
    bg: "bg-slate-500/10",
    border: "border-slate-500/20",
    text: "text-slate-400",
    icon: "text-slate-400",
  },
  yellow: {
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/20",
    text: "text-yellow-400",
    icon: "text-yellow-400",
  },
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
    },
  },
};

export function ActivityFeed() {
  return (
    <motion.div
      className="space-y-3"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {activities.map((activity, index) => {
        const colors = colorClasses[activity.color as keyof typeof colorClasses];

        return (
          <motion.div
            key={activity.id}
            variants={itemVariants}
            whileHover={{ x: 4, backgroundColor: "rgba(59, 130, 246, 0.05)" }}
            className={`p-3 rounded-xl border ${colors.bg} ${colors.border} transition-all cursor-pointer`}
          >
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-lg ${colors.bg} ${colors.icon}`}>
                {activity.icon}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-300 truncate">{activity.message}</p>
                <p className="text-xs text-slate-500 mt-1">{activity.time}</p>
              </div>
            </div>
          </motion.div>
        );
      })}
    </motion.div>
  );
}
