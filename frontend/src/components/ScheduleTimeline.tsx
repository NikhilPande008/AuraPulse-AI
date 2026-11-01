"use client";

import React, { useState, useMemo } from "react";
import type { ScheduleBlock, PlanningMilestone } from "../lib/api";
import { Calendar as CalendarIcon, Clock } from "lucide-react";
import MilestonesRoadmapView from "./timeline/MilestonesRoadmapView";
import RunOfShowView from "./timeline/RunOfShowView";

interface ScheduleTimelineProps {
  schedule: ScheduleBlock[];
  milestones?: PlanningMilestone[];
  onMilestoneToggle?: (milestoneId: string) => void;
  eventDate?: string;
  onEventDateChange?: (newDate: string) => void;
}

function parseLocalDate(dateStr: string): Date {
  const [y, m, d] = dateStr.split("-").map(Number);
  return new Date(y, (m || 1) - 1, d || 1);
}

function formatLocalDate(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export default function ScheduleTimeline({
  schedule,
  milestones = [],
  onMilestoneToggle,
  eventDate: eventDateProp,
  onEventDateChange,
}: ScheduleTimelineProps) {
  const [activeTab, setActiveTab] = useState<"milestones" | "run_of_show">("milestones");
  const defaultDate = useMemo(() => {
    const d = new Date();
    d.setDate(d.getDate() + 90);
    return formatLocalDate(d);
  }, []);
  const [internalEventDate, setInternalEventDate] = useState<string>(defaultDate);
  const eventDate = eventDateProp || internalEventDate;
  const [localMilestones, setLocalMilestones] = useState<PlanningMilestone[]>(milestones);

  React.useEffect(() => {
    if (milestones && milestones.length > 0) {
      setLocalMilestones(milestones);
    }
  }, [milestones]);

  const handleDateChange = (newDate: string) => {
    setInternalEventDate(newDate);
    if (onEventDateChange) {
      onEventDateChange(newDate);
    }
  };

  const computedMilestones = useMemo(() => {
    const now = new Date();
    const todayStr = formatLocalDate(now);
    const todayTime = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();

    return localMilestones.map((ms) => {
      let daysBefore = 0;
      if (ms.phase === "T-6 Months") daysBefore = 180;
      else if (ms.phase === "T-3 Months") daysBefore = 90;
      else if (ms.phase === "T-1 Month") daysBefore = 30;
      else if (ms.phase === "T-2 Weeks") daysBefore = 14;
      else if (ms.phase === "T-1 Week") daysBefore = 7;
      else if (ms.phase === "Day-Of") daysBefore = 0;

      try {
        const d = parseLocalDate(eventDate);
        if (!isNaN(d.getTime())) {
          d.setDate(d.getDate() - daysBefore);
          const computedStr = formatLocalDate(d);
          if (d.getTime() < todayTime && ms.phase !== "Day-Of") {
            return { ...ms, phase: "Do Immediately" as const, due_date: todayStr };
          }
          return { ...ms, due_date: computedStr };
        }
      } catch {
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
  const progressPercent =
    computedMilestones.length > 0
      ? Math.round((completedCount / computedMilestones.length) * 100)
      : 0;

  const phases = [
    "Do Immediately",
    "T-6 Months",
    "T-3 Months",
    "T-1 Month",
    "T-2 Weeks",
    "T-1 Week",
    "Day-Of",
  ];

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
    return <span className={`text-xs font-mono px-2 py-0.5 rounded border ${c}`}>{category}</span>;
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase font-mono">
              Challenge 5 Core • Temporal Engine
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Backwards Roadmap & Run-of-Show
            </span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">
            Timeline & Backwards Planning Matrix
          </h2>
          <p className="text-sm text-slate-400">
            Track multi-month vendor milestones backwards from event date and review day-of hourly
            execution blocks.
          </p>
        </div>

        <div
          role="tablist"
          aria-label="Timeline views"
          className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 self-start md:self-auto"
        >
          <button
            role="tab"
            id="tab-timeline-milestones"
            aria-controls="panel-timeline-milestones"
            aria-selected={activeTab === "milestones"}
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
            role="tab"
            id="tab-timeline-run-of-show"
            aria-controls="panel-timeline-run-of-show"
            aria-selected={activeTab === "run_of_show"}
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

      {activeTab === "milestones" && (
        <MilestonesRoadmapView
          computedMilestones={computedMilestones}
          eventDate={eventDate}
          onDateChange={handleDateChange}
          progressPercent={progressPercent}
          onToggle={handleToggle}
          phases={phases}
          getCategoryBadge={getCategoryBadge}
        />
      )}

      {activeTab === "run_of_show" && <RunOfShowView schedule={schedule} />}
    </div>
  );
}
