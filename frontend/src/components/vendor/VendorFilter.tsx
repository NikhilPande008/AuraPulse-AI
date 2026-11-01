"use client";

import React from "react";
import { RefreshCw, Search } from "lucide-react";

interface VendorFilterProps {
  query: string;
  onQueryChange: (q: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  city: string;
}

export default function VendorFilter({
  query,
  onQueryChange,
  onSubmit,
  loading,
  city,
}: VendorFilterProps) {
  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
      <form onSubmit={onSubmit} className="flex items-center gap-2 w-full sm:w-auto">
        <label htmlFor="vendor-search-input" className="sr-only">
          Search vendors
        </label>
        <div className="relative flex-1 sm:w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            id="vendor-search-input"
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="e.g. canopy rental, caterer, DJ sound..."
            className="bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500 focus-visible:ring-2 focus-visible:ring-cyan-400 w-full"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-3.5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:outline-none"
        >
          {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : "Search Maps"}
        </button>
      </form>
      <span className="text-xs text-slate-400 font-mono self-end sm:self-auto">
        Showing verified vendors in <strong className="text-cyan-300">{city}</strong>
      </span>
    </div>
  );
}
