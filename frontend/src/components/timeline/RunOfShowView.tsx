"use client";

import React from "react";
import { Clock, Shield, Sun, UserCheck } from "lucide-react";
import type { ScheduleBlock } from "../../lib/api";

interface RunOfShowViewProps {
  schedule: ScheduleBlock[];
}

export default function RunOfShowView({ schedule }: RunOfShowViewProps) {
  return (
    <div
      id="panel-timeline-run-of-show"
      role="tabpanel"
      aria-labelledby="tab-timeline-run-of-show"
      className="relative border-l border-slate-800 ml-4 space-y-6"
    >
      {schedule.map((block, index) => (
        <div key={block.block_id || index} className="relative pl-6 group">
          {/* Timeline marker */}
          <div
            className={`absolute -left-2.5 top-1.5 h-5 w-5 rounded-full border-2 flex items-center justify-center transition-transform group-hover:scale-125 ${
              block.is_outdoor
                ? "border-amber-400 bg-amber-950 text-amber-300"
                : "border-purple-500 bg-purple-950 text-purple-300"
            }`}
          >
            <div className="h-1.5 w-1.5 rounded-full bg-current" />
          </div>

          <div className="rounded-xl bg-slate-900/60 p-4 border border-slate-800 hover:border-slate-700 transition-all">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800/40 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {block.start_time_iso} - {block.end_time_iso}
                </span>
                <span className="text-xs font-semibold text-white px-2 py-0.5 rounded bg-slate-800">
                  {block.phase}
                </span>
              </div>

              {block.is_outdoor ? (
                <span className="inline-flex items-center gap-1 text-xs font-mono px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  <Sun className="w-3 h-3 text-amber-400" />
                  Outdoor Zone (Weather Watch)
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                  <Shield className="w-3 h-3 text-indigo-400" />
                  Covered / Indoor Zone
                </span>
              )}
            </div>

            <p className="text-sm font-medium text-slate-200">{block.activity}</p>

            <div className="mt-2 flex items-center gap-1 text-xs text-slate-400 font-mono">
              <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
              <span>Lead: {block.responsible_party}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
