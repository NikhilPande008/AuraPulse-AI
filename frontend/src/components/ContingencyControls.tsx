"use client";

import React, { useState } from "react";
import { CloudRain, DollarSign, Clock, AlertOctagon, Play, RefreshCw, Zap } from "lucide-react";
import { CrisisTrigger, MasterEventPlan, simulateContingency, ContingencyDiff } from "../lib/api";

interface ContingencyControlsProps {
  plan: MasterEventPlan;
  onDiffGenerated: (diff: ContingencyDiff) => void;
  isSimulating: boolean;
  setIsSimulating: (val: boolean) => void;
}

export default function ContingencyControls({
  plan,
  onDiffGenerated,
  isSimulating,
  setIsSimulating,
}: ContingencyControlsProps) {
  const [activePreset, setActivePreset] = useState<string | null>(null);

  const runPreset = async (presetId: string, trigger: CrisisTrigger) => {
    setActivePreset(presetId);
    setIsSimulating(true);
    try {
      const diff = await simulateContingency(plan, trigger);
      onDiffGenerated(diff);
    } catch (err) {
      console.error(err);
      alert("Failed to simulate contingency.");
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase font-mono">
              Agent 3.B • Pulse Dynamic Engine
            </span>
            <span className="text-xs text-slate-400 font-mono">Gemini 2.5 Pro Reasoner</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Reactive Contingency Engine</h2>
          <p className="text-sm text-slate-400">
            Simulate real-time crisis scenarios. The multi-constraint graph solver protects Tier-1 lines and dynamically balances tradeoffs.
          </p>
        </div>

        {isSimulating && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-mono animate-pulse">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            Executing Multi-Constraint Rebalancer...
          </div>
        )}
      </div>

      {/* Preset Action Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Preset 1: Rain Alert */}
        <button
          type="button"
          onClick={() =>
            runPreset("rain", {
              trigger_type: "WEATHER_RISK",
              description: "Flash thunderstorm alert: 85% probability within 2 hours",
              weather_condition: "Severe Rainstorm & High Wind",
            })
          }
          disabled={isSimulating}
          className={`p-4 rounded-xl text-left border transition-all cursor-pointer relative overflow-hidden group ${
            activePreset === "rain"
              ? "bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/30"
              : "bg-slate-900/60 border-slate-800 hover:border-cyan-500/50 hover:bg-slate-900"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="h-9 w-9 rounded-lg bg-cyan-500/15 text-cyan-400 flex items-center justify-center">
              <CloudRain className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800/60 text-cyan-300">
              Weather Risk
            </span>
          </div>
          <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">
            🌧️ Rain Storm Alert
          </h3>
          <p className="text-[11px] text-slate-400 mt-1 leading-snug">
            Injects emergency German Pagoda marquee, reroutes outdoor schedule, trims discretionary florals.
          </p>
        </button>

        {/* Preset 2: Budget Cut 20% */}
        <button
          type="button"
          onClick={() =>
            runPreset("budget", {
              trigger_type: "BUDGET_COMPRESSION",
              description: "Client demands immediate 20% budget reduction",
              budget_cut_percent: 20.0,
            })
          }
          disabled={isSimulating}
          className={`p-4 rounded-xl text-left border transition-all cursor-pointer relative overflow-hidden group ${
            activePreset === "budget"
              ? "bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/30"
              : "bg-slate-900/60 border-slate-800 hover:border-amber-500/50 hover:bg-slate-900"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="h-9 w-9 rounded-lg bg-amber-500/15 text-amber-400 flex items-center justify-center">
              <DollarSign className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-amber-950 border border-amber-800/60 text-amber-300">
              Compression
            </span>
          </div>
          <h3 className="text-sm font-bold text-white group-hover:text-amber-300 transition-colors">
            💸 Cut 20% Budget
          </h3>
          <p className="text-[11px] text-slate-400 mt-1 leading-snug">
            Preserves Tier-1 critical safety and catering; surgically scales and trims Tier-3 luxury line items.
          </p>
        </button>

        {/* Preset 3: Baraat Delayed 1 Hour */}
        <button
          type="button"
          onClick={() =>
            runPreset("delay", {
              trigger_type: "TIMELINE_SLIPPAGE",
              description: "Procession delayed 60 minutes due to city traffic gridlock",
              delay_minutes: 60,
            })
          }
          disabled={isSimulating}
          className={`p-4 rounded-xl text-left border transition-all cursor-pointer relative overflow-hidden group ${
            activePreset === "delay"
              ? "bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/30"
              : "bg-slate-900/60 border-slate-800 hover:border-indigo-500/50 hover:bg-slate-900"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="h-9 w-9 rounded-lg bg-indigo-500/15 text-indigo-400 flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-indigo-950 border border-indigo-800/60 text-indigo-300">
              Slippage
            </span>
          </div>
          <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
            ⏰ Baraat Delayed 1 Hr
          </h3>
          <p className="text-[11px] text-slate-400 mt-1 leading-snug">
            Graph cascades subsequent ceremony milestones while maintaining buffet kitchen fresh-holding protocols.
          </p>
        </button>

        {/* Preset 4: Caterer Abruptly Cancelled */}
        <button
          type="button"
          onClick={() =>
            runPreset("caterer", {
              trigger_type: "SUPPLY_FAILURE",
              description: "Primary catering vendor truck broke down 4 hours before guest arrival",
              affected_vendor_category: "Catering",
            })
          }
          disabled={isSimulating}
          className={`p-4 rounded-xl text-left border transition-all cursor-pointer relative overflow-hidden group ${
            activePreset === "caterer"
              ? "bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/30"
              : "bg-slate-900/60 border-slate-800 hover:border-rose-500/50 hover:bg-slate-900"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="h-9 w-9 rounded-lg bg-rose-500/15 text-rose-400 flex items-center justify-center">
              <AlertOctagon className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-rose-950 border border-rose-800/60 text-rose-300">
              Supply Fail
            </span>
          </div>
          <h3 className="text-sm font-bold text-white group-hover:text-rose-300 transition-colors">
            🚨 Caterer Cancelled
          </h3>
          <p className="text-[11px] text-slate-400 mt-1 leading-snug">
            Queries Google Maps Places API for verified backup caterer and hot-swaps lines with verified ratings.
          </p>
        </button>
      </div>
    </div>
  );
}
