"use client";

import React from "react";
import { RotateCcw } from "lucide-react";
import type { HealthStatus } from "../types/plan";

interface SystemStatusStripProps {
  healthStatus: HealthStatus | null;
  onResetPlan: () => void;
}

export default function SystemStatusStrip({ healthStatus, onResetPlan }: SystemStatusStripProps) {
  return (
    <div className="glass-card rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 border border-slate-800">
      <div className="flex items-center gap-3">
        <div
          className={`h-2.5 w-2.5 rounded-full ${healthStatus ? "bg-emerald-400" : "bg-amber-400"}`}
        />
        <span className="text-xs font-mono font-semibold text-white">
          Backend: {healthStatus ? "Online" : "Unreachable"}
        </span>
        <span className="text-xs text-slate-400 hidden sm:inline">•</span>
        <span className="text-xs text-slate-400 font-mono hidden sm:inline">
          Version: {healthStatus?.version || process.env.NEXT_PUBLIC_APP_VERSION || "2.2.0"}
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
        <span
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${
            healthStatus?.gemini_configured
              ? "bg-purple-950/60 border-purple-800/60 text-purple-300"
              : "bg-amber-950/40 border-amber-800/60 text-amber-300"
          }`}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              healthStatus?.gemini_configured ? "bg-purple-400" : "bg-amber-400"
            }`}
          />
          Gemini Flash: {healthStatus?.gemini_configured ? "Active" : "API Key Required"}
        </span>

        <span
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${
            healthStatus?.google_apis?.places_maps
              ? "bg-cyan-950/60 border-cyan-800/60 text-cyan-300"
              : "bg-slate-900 border-slate-800 text-slate-400"
          }`}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              healthStatus?.google_apis?.places_maps ? "bg-cyan-400" : "bg-slate-500"
            }`}
          />
          Places Grounding: {healthStatus?.google_apis?.places_maps ? "Ready" : "Inactive"}
        </span>

        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-emerald-300">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          RFC-5545 Calendar: Ready
        </span>

        <button
          type="button"
          onClick={onResetPlan}
          className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition-colors cursor-pointer border border-slate-700"
          title="Reset to fresh default plan and clear browser storage"
        >
          <RotateCcw className="w-3 h-3" />
          Reset Plan
        </button>
      </div>
    </div>
  );
}
