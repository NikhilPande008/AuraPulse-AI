"use client";

import React, { useState, useMemo } from "react";
import { ScheduleBlock, PlanningMilestone } from "../lib/api";
import { Clock, Sun, UserCheck, Shield, Calendar as CalendarIcon, CheckSquare, Square, Tag, ArrowRight, Sparkles } from "lucide-react";

interface ScheduleTimelineProps {
  schedule: ScheduleBlock[];
  milestones?: PlanningMilestone[];
  onMilestoneToggle?: (milestoneId: string) => void;
}

export default function ScheduleTimeline({
  schedule,
  milestones = [],
  onMilestoneToggle,
}: ScheduleTimelineProps) {
  const [activeTab, setActiveTab] = useState<"milestones" | "run_of_show">("milestones");
  const [eventDate, setEventDate] = useState<string>("2026-11-15");
  const [localMilestones, setLocalMilestones] = useState<PlanningMilestone[]>(milestones);

  // Sync prop changes
  React.useEffect(() => {
    if (milestones && milestones.length > 0) {
      setLocalMilestones(milestones);
    }
  }, [milestones]);

  // Recalculate due dates backwards whenever user changes eventDate
  const computedMilestones = useMemo(() => {
    return localMilestones.map((ms) => {
      let daysBefore = 0;
      if (ms.phase === "T-6 Months") daysBefore = 180;
      else if (ms.phase === "T-3 Months") daysBefore = 90;
      else if (ms.phase === "T-1 Month") daysBefore = 30;
      else if (ms.phase === "T-2 Weeks") daysBefore = 14;
      else if (ms.phase === "T-1 Week") daysBefore = 7;
      else if (ms.phase === "Day-Of") daysBefore = 0;

      try {
        const d = new Date(eventDate);
        if (!isNaN(d.getTime())) {
          d.setDate(d.getDate() - daysBefore);
          const computedStr = d.toISOString().split("T")[0];
          return { ...ms, due_date: computedStr };
        }
      } catch (e) {
        // Fallback
      }
      return ms;
    });
  }, [localMilestones, eventDate]);

  const handleToggle = (id: string) => {
    setLocalMilestones((prev) =>
      prev.map((m) => (m.id === id ? { ...m, completed: !m.completed } : m))
    );
    if (onMilestoneToggle) {
      onMilestoneToggle(id);
    }
  };

  const completedCount = computedMilestones.filter((m) => m.completed).length;
  const progressPercent = computedMilestones.length > 0 ? Math.round((completedCount / computedMilestones.length) * 100) : 0;

  // Group milestones by phase
  const phases = ["T-6 Months", "T-3 Months", "T-1 Month", "T-2 Weeks", "T-1 Week", "Day-Of"];

  const getCategoryBadge = (category: string) => {
    const colors: Record<string, string> = {
      Venue: "bg-purple-950/80 text-purple-300 border-purple-800/60",
      Catering: "bg-amber-950/80 text-amber-300 border-amber-800/60",
      Decor: "bg-cyan-950/80 text-cyan-300 border-cyan-800/60",
      "Attire & Invites": "bg-pink-950/80 text-pink-300 border-pink-800/60",
      Logistics: "bg-blue-950/80 text-blue-300 border-blue-800/60",
      Rituals: "bg-emerald-950/80 text-emerald-300 border-emerald-800/60",
    };
    const c = colors[category] || "bg-slate-800 text-slate-300 border-slate-700";
    return (
      <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${c}`}>
        {category}
      </span>
    );
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800 space-y-6">
      {/* Top Header & Tab Toggle */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase font-mono">
              Challenge 5 Core • Temporal Engine
            </span>
            <span className="text-xs text-slate-400 font-mono">Backwards Roadmap & Run-of-Show</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Timeline & Backwards Planning Matrix</h2>
          <p className="text-sm text-slate-400">
            Track multi-month vendor milestones backwards from event date and review day-of hourly execution blocks.
          </p>
        </div>

        {/* View Mode Toggle Buttons */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 self-start md:self-auto">
          <button
            type="button"
            onClick={() => setActiveTab("milestones")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              activeTab === "milestones"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <CalendarIcon className="w-3.5 h-3.5" />
            Backwards Milestones ({completedCount}/{computedMilestones.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("run_of_show")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              activeTab === "run_of_show"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            Day-Of Run-of-Show ({schedule.length} Blocks)
          </button>
        </div>
      </div>

      {/* VIEW 1: BACKWARDS PLANNING MILESTONES ROADMAP */}
      {activeTab === "milestones" && (
        <div className="space-y-6">
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
                onChange={(e) => setEventDate(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white font-mono focus:outline-none focus:border-purple-500"
              />
            </div>

            {/* Progress Bar */}
            <div className="flex items-center gap-3 w-full sm:w-64">
              <div className="flex-1 bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                <div
                  className="bg-gradient-to-r from-purple-500 to-cyan-400 h-full transition-all duration-500"
                  style={{ width: `${progressPercent}%` }}
                ></div>
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
                      <span className="h-2 w-2 rounded-full bg-purple-400"></span>
                      <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-purple-300">
                        {phase} Horizon
                      </h3>
                      <span className="text-[10px] text-slate-500 font-mono">
                        (Deadline: {items[0]?.due_date})
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">
                      {items.filter((i) => i.completed).length}/{items.length} Ready
                    </span>
                  </div>

                  <div className="space-y-2.5">
                    {items.map((ms) => (
                      <div
                        key={ms.id}
                        onClick={() => handleToggle(ms.id)}
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
                            <Square className="w-4 h-4 text-slate-500" />
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
                              <span className="text-[10px] font-mono text-slate-400">
                                Due: {ms.due_date}
                              </span>
                            </div>
                          </div>
                          <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
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
      )}

      {/* VIEW 2: DAY-OF RUN-OF-SHOW TIMELINE */}
      {activeTab === "run_of_show" && (
        <div className="relative border-l border-slate-800 ml-4 space-y-6">
          {schedule.map((block, index) => {
            return (
              <div key={block.block_id || index} className="relative pl-6 group">
                {/* Timeline marker */}
                <div
                  className={`absolute -left-2.5 top-1.5 h-5 w-5 rounded-full border-2 flex items-center justify-center transition-transform group-hover:scale-125 ${
                    block.is_outdoor
                      ? "border-amber-400 bg-amber-950 text-amber-300"
                      : "border-purple-500 bg-purple-950 text-purple-300"
                  }`}
                >
                  <div className="h-1.5 w-1.5 rounded-full bg-current"></div>
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
                      <span className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
                        <Sun className="w-3 h-3 text-amber-400" />
                        Outdoor Zone (Weather Watch)
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                        <Shield className="w-3 h-3 text-indigo-400" />
                        Covered / Indoor Zone
                      </span>
                    )}
                  </div>

                  <p className="text-sm font-medium text-slate-200">
                    {block.activity}
                  </p>

                  <div className="mt-2 flex items-center gap-1 text-xs text-slate-400 font-mono">
                    <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Lead: {block.responsible_party}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
