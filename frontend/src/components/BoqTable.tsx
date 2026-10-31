"use client";

import React from "react";
import { BOQItem, MasterEventPlan } from "../lib/api";
import { Lock, ShieldAlert, Sparkles, Layers, DollarSign, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

interface BoqTableProps {
  plan: MasterEventPlan;
  onItemUpdate?: (updatedItem: BOQItem) => void;
}

export default function BoqTable({ plan, onItemUpdate }: BoqTableProps) {
  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "Critical":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30">
            <Lock className="w-3 h-3 text-rose-400" />
            Tier-1 Critical
          </span>
        );
      case "Operational":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
            <Layers className="w-3 h-3 text-amber-400" />
            Tier-2 Operational
          </span>
        );
      case "Discretionary":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            Tier-3 Discretionary
          </span>
        );
      default:
        return <span>{priority}</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" /> ACTIVE
          </span>
        );
      case "MODIFIED":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
            <AlertTriangle className="w-3 h-3" /> MODIFIED
          </span>
        );
      case "DROPPED":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-rose-500/15 text-rose-300 border border-rose-500/30 line-through">
            <XCircle className="w-3 h-3" /> DROPPED
          </span>
        );
      default:
        return <span className="text-xs text-slate-400">{status}</span>;
    }
  };

  const budgetDelta = plan.total_budget_limit - plan.current_estimated_total;
  const isOverBudget = budgetDelta < 0;

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800">
      {/* Header and Summary Ribbon */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase font-mono">
              Component 2.1 • Bill of Quantities
            </span>
            <span className="text-xs text-slate-400 font-mono">Strict Pydantic Validation</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Itemized Procurement Matrix (BOQ)</h2>
          <p className="text-sm text-slate-400">
            {plan.title} • {plan.boq.length} procurement line items calibrated in {plan.currency}
          </p>
        </div>

        {/* Financial Stat Pills */}
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-right">
            <p className="text-[10px] text-slate-400 uppercase font-mono">Budget Ceiling</p>
            <p className="text-sm font-mono font-bold text-slate-200">
              ₹{plan.total_budget_limit.toLocaleString("en-IN")}
            </p>
          </div>

          <div className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-right">
            <p className="text-[10px] text-slate-400 uppercase font-mono">Current Estimated</p>
            <p className="text-sm font-mono font-bold text-purple-400">
              ₹{plan.current_estimated_total.toLocaleString("en-IN")}
            </p>
          </div>

          <div className={`px-4 py-2 rounded-xl border text-right ${
            isOverBudget
              ? "bg-rose-950/30 border-rose-500/30 text-rose-300"
              : "bg-emerald-950/30 border-emerald-500/30 text-emerald-300"
          }`}>
            <p className="text-[10px] uppercase font-mono">{isOverBudget ? "Over Budget" : "Reserve Buffer"}</p>
            <p className="text-sm font-mono font-bold">
              {isOverBudget ? "-" : "+"}₹{Math.abs(budgetDelta).toLocaleString("en-IN")}
            </p>
          </div>
        </div>
      </div>

      {/* Responsive Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/90 text-slate-400 font-mono text-[11px] uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">Line Item / Specification</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-3">Priority Tier</th>
              <th className="py-3 px-3 text-right">Qty</th>
              <th className="py-3 px-3">Unit</th>
              <th className="py-3 px-4 text-right">Rate (INR)</th>
              <th className="py-3 px-4 text-right">Total (INR)</th>
              <th className="py-3 px-4 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {plan.boq.map((item) => {
              const isDropped = item.status === "DROPPED";
              const isModified = item.status === "MODIFIED";
              const isEmergencyAdded = item.item_id.includes("emerg") || item.item_id.includes("canopy");
              return (
                <tr
                  key={item.item_id}
                  className={`transition-all ${
                    isDropped
                      ? "bg-rose-950/20 opacity-50 border-l-2 border-rose-500"
                      : isModified
                      ? "bg-amber-950/25 border-l-2 border-amber-500 hover:bg-amber-950/35"
                      : isEmergencyAdded
                      ? "bg-emerald-950/25 border-l-2 border-emerald-400 hover:bg-emerald-950/35 animate-pulse"
                      : "hover:bg-slate-800/40"
                  }`}
                >
                  <td className="py-3 px-4 max-w-xs">
                    <p className={`font-semibold text-slate-100 ${isDropped ? "line-through text-slate-500" : ""}`}>
                      {item.name}
                    </p>
                    <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
                      {item.specification}
                    </p>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-300 font-medium border border-slate-700/50">
                      {item.category}
                    </span>
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    {getPriorityBadge(item.priority)}
                  </td>
                  <td className="py-3 px-3 text-right font-mono font-medium text-slate-300">
                    {item.quantity.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-400">
                    {item.unit}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-slate-300">
                    ₹{item.estimated_rate_inr.toLocaleString("en-IN")}
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-slate-100">
                    ₹{item.total_cost_inr.toLocaleString("en-IN")}
                  </td>
                  <td className="py-3 px-4 text-center whitespace-nowrap">
                    {getStatusBadge(item.status)}
                  </td>
                </tr>
              );
            })}
          </tbody>
          <tfoot className="bg-slate-900/90 font-mono border-t border-slate-700">
            <tr>
              <td colSpan={6} className="py-3 px-4 text-right font-bold text-slate-300 uppercase tracking-wider text-xs">
                Active Grand Total (INR):
              </td>
              <td className="py-3 px-4 text-right font-bold text-sm text-cyan-300">
                ₹{plan.current_estimated_total.toLocaleString("en-IN")}
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
