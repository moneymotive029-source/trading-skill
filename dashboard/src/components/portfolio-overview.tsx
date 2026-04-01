"use client";

import { motion } from "framer-motion";
import { Card, CardContent } from "./ui/card";
import { DollarSign, Briefcase, TrendingUp, Gauge } from "lucide-react";

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

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut",
    },
  },
};

export function PortfolioOverview() {
  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-4 gap-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {portfolioData.map((item, index) => (
        <motion.div
          key={item.label}
          variants={itemVariants}
          whileHover={{ scale: 1.03, y: -4 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <Card className="relative overflow-hidden bg-slate-900/50 border-slate-800 backdrop-blur-xl group hover:border-slate-600 transition-colors">
            {/* Gradient glow effect */}
            <div className={`absolute -top-20 -right-20 w-40 h-40 bg-gradient-to-br ${item.gradient} opacity-10 rounded-full blur-2xl group-hover:opacity-20 transition-opacity`} />

            <CardContent className="p-4 relative z-10">
              <div className="flex items-center justify-between">
                <div className="text-slate-400 text-sm">{item.label}</div>
                <div className={`p-2 bg-gradient-to-br ${item.gradient} rounded-lg text-white shadow-lg`}>
                  {item.icon}
                </div>
              </div>

              <div className="text-2xl font-bold text-white mt-3">{item.value}</div>

              <div className={`text-xs mt-2 flex items-center gap-1 ${
                item.changeUp === true ? 'text-green-400' :
                item.changeUp === false ? 'text-red-400' :
                'text-slate-500'
              }`}>
                {item.changeUp === true && (
                  <motion.span
                    animate={{ y: [0, -2, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  >
                    ↑
                  </motion.span>
                )}
                {item.change}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  );
}
