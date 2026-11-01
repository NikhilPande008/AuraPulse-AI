"use client";

import React from "react";
import { Calendar as CalendarIcon, CheckSquare, Square } from "lucide-react";
import type { PlanningMilestone } from "../../lib/api";

interface MilestonesRoadmapViewProps {
  computedMilestones: PlanningMilestone[];
  eventDate: string;
  onDateChange: (newDate: string) => void;
  progressPercent: number;
  onToggle: (id: string) => void;
  phases: string[];
  getCategoryBadge: (category: string) => React.ReactNode;
}

export default function MilestonesRoadmapView({
  computedMilestones,
  eventDate,
  onDateChange,
  progressPercent,
  onToggle,
  phases,
  getCategoryBadge,
}: MilestonesRoadmapViewProps) {
  return (
    <div
      id="panel-timeline-milestones"
      role="tabpanel"
      aria-labelledby="tab-timeline-milestones"
      className="space-y-6"
    >
      {/* Milestone Controls & Progress Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center gap-3">
          <label className="text-xs font-mono text-slate-300 flex items-center gap-1.5">
            <CalendarIcon className="w-4 h-4 text-purple-400" />
            Target Event Date:
          </label>
          <input
            type="date"
            value={eventDate}
            onChange={(e) => onDateChange(e.target.value)}
            className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white font-mono focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Progress Bar */}
        <div className="flex items-center gap-3 w-full sm:w-64">
          <div className="flex-1 bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
            <div
              className="bg-gradient-to-r from-purple-500 to-cyan-400 h-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <span className="text-xs font-mono font-bold text-cyan-300 shrink-0">
            {progressPercent}% Complete
          </span>
        </div>
      </div>

      {/* Chronological Milestone Phase Groups */}
      <div className="space-y-5">
        {phases.map((phase) => {
          const items = computedMilestones.filter((m) => m.phase === phase);
          if (items.length === 0) return null;

          return (
            <div key={phase} className="rounded-xl bg-slate-900/40 p-4 border border-slate-800/80">
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800/60">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-purple-400" />
                  <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-purple-300">
                    {phase} Horizon
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">
                    (Deadline: {items[0]?.due_date})
                  </span>
                </div>
                <span className="text-xs font-mono text-slate-400">
                  {items.filter((i) => i.completed).length}/{items.length} Ready
                </span>
              </div>

              <div className="space-y-2.5">
                {items.map((ms) => (
                  <div
                    key={ms.id}
                    onClick={() => onToggle(ms.id)}
                    className={`p-3 rounded-lg border transition-all cursor-pointer flex items-start gap-3 ${
                      ms.completed
                        ? "bg-emerald-950/15 border-emerald-500/30 opacity-75"
                        : "bg-slate-950/60 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div className="mt-0.5 text-slate-400 hover:text-white shrink-0">
                      {ms.completed ? (
                        <CheckSquare className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <Square className="w-4 h-4 text-slate-400" />
                      )}
                    </div>

                    <div className="flex-1">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p
                          className={`text-xs font-semibold ${
                            ms.completed ? "line-through text-slate-400" : "text-slate-100"
                          }`}
                        >
                          {ms.title}
                        </p>
                        <div className="flex items-center gap-2">
                          {getCategoryBadge(ms.category)}
                          <span className="text-xs font-mono text-slate-400">
                            Due: {ms.due_date}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                        {ms.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
