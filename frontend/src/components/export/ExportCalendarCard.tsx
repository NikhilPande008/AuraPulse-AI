"use client";

import React from "react";
import { Calendar, CheckCircle2, Download, ExternalLink } from "lucide-react";
import type { MasterEventPlan } from "../../types/plan";

interface ExportCalendarCardProps {
  plan: MasterEventPlan;
  icsDownloaded: boolean;
  icsError: string | null;
  exportingIcs: boolean;
  onDownloadIcs: () => void;
  calendarWebIntentUrl: string;
}

export default function ExportCalendarCard({
  plan,
  icsDownloaded,
  icsError,
  exportingIcs,
  onDownloadIcs,
  calendarWebIntentUrl,
}: ExportCalendarCardProps) {
  return (
    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-mono font-bold text-blue-400 flex items-center gap-1.5">
            <Calendar className="w-4 h-4" /> RFC-5545 & Web Intent Calendar
          </span>
          {icsDownloaded ? (
            <span className="text-xs font-mono text-cyan-300 bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-500/40 flex items-center gap-1 font-bold">
              <CheckCircle2 className="w-3 h-3 text-cyan-400" /> iCal .ics Downloaded
            </span>
          ) : (
            <span className="text-xs font-mono text-slate-400">Ready for Export</span>
          )}
        </div>
        <p className="text-xs text-slate-300">
          Zero-permission universal calendar export. Includes{" "}
          {plan.planning_milestones?.length || 0} backwards planning milestones as all-day events
          and {plan.schedule.length} run-of-show blocks with IST timezone (
          <code className="text-blue-300 font-mono">TZID=Asia/Kolkata</code>).
        </p>

        <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5 text-slate-400">
          <p>
            <span className="text-slate-400">Target Timezone:</span>{" "}
            <span className="text-slate-200 font-medium">Asia/Kolkata (IST • UTC+05:30)</span>
          </p>
          <p>
            <span className="text-slate-400">Milestone Events:</span>{" "}
            <span className="text-cyan-400 font-bold">
              {plan.planning_milestones?.length || 0} All-Day Milestones
            </span>
          </p>
          <p>
            <span className="text-slate-400">Run-of-Show Blocks:</span>{" "}
            <span className="text-indigo-400 font-bold">
              {plan.schedule.length} Hourly Timed Blocks
            </span>
          </p>
          <div className="pt-1 flex flex-wrap gap-1.5">
            <span className="px-2 py-0.5 rounded bg-blue-950/60 text-blue-300 border border-blue-800/60 text-xs">
              RFC-5545 Standard
            </span>
            <span className="px-2 py-0.5 rounded bg-indigo-950/60 text-indigo-300 border border-indigo-800/60 text-xs">
              Direct Web Intent
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 text-xs">
              Zero OAuth Friction
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={onDownloadIcs}
          disabled={exportingIcs}
          className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-blue-600/30 hover:bg-blue-600/50 text-blue-200 hover:text-white border border-blue-500/40 text-xs font-bold transition-all cursor-pointer"
        >
          <Download className="w-3.5 h-3.5" />
          Download .ics
        </button>
        <a
          href={calendarWebIntentUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 hover:text-white border border-indigo-500/40 text-xs font-bold transition-all cursor-pointer"
        >
          <Calendar className="w-3.5 h-3.5" />
          Google Calendar
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
      {icsError && (
        <p className="mt-2 text-xs font-mono text-rose-300" role="alert">
          {icsError}
        </p>
      )}
    </div>
  );
}
