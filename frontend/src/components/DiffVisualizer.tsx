"use client";

import React from "react";
import type { ContingencyDiff } from "../lib/api";
import {
  PlusCircle,
  Edit3,
  Trash2,
  ArrowRight,
  ShieldCheck,
  Cpu,
  CheckCircle,
  TrendingDown,
  TrendingUp,
  Equal,
  RotateCcw,
} from "lucide-react";

interface DiffVisualizerProps {
  diff: ContingencyDiff;
  onReset?: () => void;
}

export default function DiffVisualizer({ diff, onReset }: DiffVisualizerProps) {
  const getActionBadge = (action: string) => {
    switch (action) {
      case "ADDED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 animate-pulse">
            <PlusCircle className="w-3.5 h-3.5 text-emerald-400" />+ ADDED
          </span>
        );
      case "MODIFIED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
            <Edit3 className="w-3.5 h-3.5 text-amber-400" />~ MODIFIED
          </span>
        );
      case "REMOVED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
            <Trash2 className="w-3.5 h-3.5 text-rose-400" />- REMOVED
          </span>
        );
      default:
        return <span>{action}</span>;
    }
  };

  const delta = diff.budget_delta_inr;
  const isSavings = delta < 0;
  const isNeutral = delta === 0;

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800 space-y-6">
      {/* Header and Delta summary */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide bg-purple-500/10 text-purple-400 border border-purple-500/20 uppercase font-mono">
              Diff Visualizer • State Alteration Engine
            </span>
            <span className="text-xs text-slate-400 font-mono">Diff ID: {diff.diff_id}</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">
            Reactive Plan Alterations ({diff.trigger.trigger_type})
          </h2>
          <p className="text-sm text-slate-400">{diff.trigger.description}</p>
        </div>

        {/* Side-by-Side Cost Delta Indicator & Reset Action */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="grid grid-cols-3 sm:flex sm:items-center gap-3">
            {/* Card 1: Original Total */}
            <div className="px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-right">
              <p className="text-xs text-slate-400 uppercase font-mono tracking-wider">
                Original Total
              </p>
              <p className="text-sm font-mono font-bold text-slate-200">
                ₹{diff.original_total_inr.toLocaleString("en-IN")}
              </p>
            </div>

            <div className="hidden sm:block">
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </div>

            {/* Card 2: Simulated Total */}
            <div className="px-3.5 py-2.5 rounded-xl bg-slate-900 border border-purple-800/40 text-right shadow-sm shadow-purple-950">
              <p className="text-xs text-purple-300 uppercase font-mono tracking-wider">
                Simulated Total
              </p>
              <p className="text-sm font-mono font-bold text-cyan-300">
                ₹{diff.new_total_inr.toLocaleString("en-IN")}
              </p>
            </div>

            <div className="hidden sm:block">
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </div>

            {/* Card 3: Contingency Buffer Variance */}
            <div
              className={`px-3.5 py-2.5 rounded-xl border text-right transition-all ${
                isSavings
                  ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300 shadow-sm shadow-emerald-950"
                  : isNeutral
                    ? "bg-cyan-950/40 border-cyan-500/40 text-cyan-300 shadow-sm shadow-cyan-950"
                    : "bg-amber-950/40 border-amber-500/40 text-amber-300 shadow-sm shadow-amber-950"
              }`}
            >
              <p className="text-xs uppercase font-mono tracking-wider flex items-center justify-end gap-1">
                {isSavings ? (
                  <TrendingDown className="w-3 h-3 text-emerald-400" />
                ) : isNeutral ? (
                  <Equal className="w-3 h-3 text-cyan-400" />
                ) : (
                  <TrendingUp className="w-3 h-3 text-amber-400" />
                )}
                Contingency Buffer Variance
              </p>
              <p className="text-sm font-mono font-bold">
                {isSavings ? "Released +" : isNeutral ? "Neutral " : "Absorbed -"}₹
                {Math.abs(delta).toLocaleString("en-IN")}
              </p>
            </div>
          </div>

          {onReset && (
            <button
              type="button"
              onClick={onReset}
              className="px-4 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 hover:text-white border border-rose-500/30 text-xs font-semibold font-mono flex items-center justify-center gap-1.5 transition-all shadow-sm cursor-pointer shrink-0"
              title="Revert simulation changes and restore the baseline plan"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Simulation</span>
            </button>
          )}
        </div>
      </div>

      {/* Gemini 2.5 Pro Reasoner Narrative */}
      <div className="rounded-xl bg-gradient-to-r from-purple-950/30 via-slate-900 to-indigo-950/30 p-5 border border-purple-500/20">
        <div className="flex items-center gap-2 mb-2">
          <Cpu className="w-4 h-4 text-purple-400" />
          <h3 className="text-xs font-mono font-bold uppercase text-purple-300 tracking-wider">
            Gemini 2.5 Pro Decision Rationale
          </h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line font-sans">
          {diff.summary_narrative}
        </p>
      </div>

      {/* BOQ Line Item Diff Stream */}
      <div>
        <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
          BOQ Line Item Mutations ({diff.boq_diffs.length} Alterations)
        </h3>

        <div className="space-y-3">
          {diff.boq_diffs.map((d) => (
            <div
              key={d.item_id}
              className={`p-4 rounded-xl border transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                d.action === "ADDED"
                  ? "bg-emerald-950/15 border-emerald-500/30 hover:border-emerald-500/50"
                  : d.action === "MODIFIED"
                    ? "bg-amber-950/15 border-amber-500/30 hover:border-amber-500/50"
                    : "bg-rose-950/15 border-rose-500/30 hover:border-rose-500/50 opacity-70"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">{getActionBadge(d.action)}</div>
                <div>
                  <p className="text-sm font-semibold text-slate-100">
                    {d.updated_item ? d.updated_item.name : d.original_item?.name}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">{d.reason}</p>
                  {d.original_item && d.updated_item && d.action === "MODIFIED" && (
                    <div className="mt-1 flex items-center gap-2 text-xs font-mono text-slate-400">
                      <span>
                        Rate: ₹{d.original_item.estimated_rate_inr.toLocaleString("en-IN")}
                      </span>
                      <ArrowRight className="w-3 h-3 text-slate-400" />
                      <span className="text-amber-300 font-bold">
                        ₹{d.updated_item.estimated_rate_inr.toLocaleString("en-IN")}
                      </span>
                      <span>
                        • New Line Total: ₹{d.updated_item.total_cost_inr.toLocaleString("en-IN")}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <div className="text-right font-mono text-xs whitespace-nowrap">
                {d.action === "ADDED" && (
                  <span className="text-emerald-400 font-bold">
                    +₹{d.updated_item?.total_cost_inr.toLocaleString("en-IN")}
                  </span>
                )}
                {d.action === "REMOVED" && (
                  <span className="text-rose-400 font-bold line-through">
                    -₹{d.original_item?.total_cost_inr.toLocaleString("en-IN")}
                  </span>
                )}
                {d.action === "MODIFIED" && d.original_item && d.updated_item && (
                  <span className="text-amber-400 font-bold">
                    {d.updated_item.total_cost_inr - d.original_item.total_cost_inr < 0 ? "-" : "+"}
                    ₹
                    {Math.abs(
                      d.updated_item.total_cost_inr - d.original_item.total_cost_inr
                    ).toLocaleString("en-IN")}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actionable Mitigations */}
      {diff.actionable_mitigations.length > 0 && (
        <div className="pt-2 border-t border-slate-800">
          <h3 className="text-xs font-mono font-bold uppercase text-slate-400 tracking-wider mb-2 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> Actionable Mitigation Protocols
          </h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-300">
            {diff.actionable_mitigations.map((mit, i) => (
              <li
                key={i}
                className="flex items-start gap-2 bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/60"
              >
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <span>{mit}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
