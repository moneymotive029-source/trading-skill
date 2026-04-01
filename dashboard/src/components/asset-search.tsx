"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, ArrowRight } from "lucide-react";

export function AssetSearch({ onSelect }: { onSelect: (asset: string) => void }) {
  const [query, setQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSelect(query.toUpperCase());
      setQuery("");
    }
  };

  return (
    <motion.form
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      onSubmit={handleSearch}
      className="relative"
    >
      <div className="relative group">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search asset..."
          className="w-48 pl-10 pr-10 py-2 bg-[#0f0f15]/80 border border-white/5 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all"
        />
        <motion.button
          type="submit"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg text-white opacity-0 group-focus-within:opacity-100 transition-opacity"
        >
          <ArrowRight className="w-3.5 h-3.5" />
        </motion.button>
      </div>
    </motion.form>
  );
}
