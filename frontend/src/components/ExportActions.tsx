"use client";

import React, { useState } from "react";
import { MasterEventPlan, exportToSheets, syncToCalendar } from "../lib/api";
import { FileSpreadsheet, Calendar, Check, ExternalLink, RefreshCw, CheckCircle2, ArrowUpRight, Clock, ShieldCheck } from "lucide-react";

interface ExportActionsProps {
  plan: MasterEventPlan;
}

export default function ExportActions({ plan }: ExportActionsProps) {
  const [exportingSheets, setExportingSheets] = useState(false);
  const [syncingCalendar, setSyncingCalendar] = useState(false);
  const [sheetResult, setSheetResult] = useState<any | null>(null);
  const [calendarResult, setCalendarResult] = useState<any | null>(null);

  const handleExportSheets = async () => {
    setExportingSheets(true);
    try {
      const res = await exportToSheets(plan.title, plan.boq);
      setSheetResult(res);
    } catch (err) {
      console.error(err);
      alert("Sheets export failed.");
    } finally {
      setExportingSheets(false);
    }
  };

  const handleSyncCalendar = async () => {
    setSyncingCalendar(true);
    try {
      const res = await syncToCalendar(plan.title, plan.schedule);
      setCalendarResult(res);
    } catch (err) {
      console.error(err);
      alert("Calendar sync failed.");
    } finally {
      setSyncingCalendar(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase font-mono">
              Google Workspace Integrations
            </span>
            <span className="text-xs text-slate-400 font-mono">Sheets API v4 & Calendar API v3</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Google Workspace Exporter</h2>
          <p className="text-sm text-slate-400">
            Publish interactive, formula-driven spreadsheets and sync the temporal run-of-show with outdoor weather alarms.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportSheets}
            disabled={exportingSheets}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition-all cursor-pointer disabled:opacity-50"
          >
            {exportingSheets ? <RefreshCw className="w-4 h-4 animate-spin" /> : <FileSpreadsheet className="w-4 h-4" />}
            Export Formula Sheets
          </button>

          <button
            onClick={handleSyncCalendar}
            disabled={syncingCalendar}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all cursor-pointer disabled:opacity-50"
          >
            {syncingCalendar ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Calendar className="w-4 h-4" />}
            Sync Google Calendar
          </button>
        </div>
      </div>

      {/* Results and Formula Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Sheets Result Card */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1.5">
                <FileSpreadsheet className="w-4 h-4" /> Google Sheets API v4
              </span>
              {sheetResult ? (
                <span className="text-[10px] font-mono text-emerald-300 bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-500/40 flex items-center gap-1 font-bold">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Exported ({sheetResult.items_exported} Rows)
                </span>
              ) : (
                <span className="text-[10px] font-mono text-slate-500">Awaiting Export Trigger</span>
              )}
            </div>
            <p className="text-xs text-slate-300">
              Generates multi-tab workbook with automated <code className="text-cyan-300 font-mono">=SUM(H2:H11)</code> grand total and <code className="text-amber-300 font-mono">=SUMIF(...)</code> priority analytics.
            </p>

            {sheetResult && (
              <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5 text-slate-400">
                <p><span className="text-slate-500">Workbook Title:</span> <span className="text-slate-200 font-medium">{sheetResult.spreadsheet_title}</span></p>
                <p><span className="text-slate-500">Grand Total Formula:</span> <span className="text-cyan-400 font-bold">{sheetResult.grand_total_formula}</span></p>
                <p><span className="text-slate-500">Priority SUMIF:</span> <span className="text-amber-300 font-bold">{sheetResult.priority_formulas?.["Critical Tier Formula"] || "=SUMIF(...)"}</span></p>
                <p><span className="text-slate-500">Total Lines:</span> <span className="text-emerald-400 font-bold">{sheetResult.total_rows_created} formatted rows</span></p>
              </div>
            )}
          </div>

          {sheetResult ? (
            <a
              href={sheetResult.spreadsheet_url}
              target="_blank"
              rel="noreferrer"
              className="mt-4 inline-flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white text-xs font-bold shadow-lg shadow-emerald-700/30 hover:brightness-110 transition-all cursor-pointer"
            >
              <FileSpreadsheet className="w-4 h-4" />
              Open Live Google Sheet (Drive Workbook)
              <ArrowUpRight className="w-4 h-4" />
            </a>
          ) : (
            <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 font-mono">
              Click &quot;Export Formula Sheets&quot; to build dynamic Drive document.
            </div>
          )}
        </div>

        {/* Calendar Result Card */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-bold text-blue-400 flex items-center gap-1.5">
                <Calendar className="w-4 h-4" /> Google Calendar API v3
              </span>
              {calendarResult ? (
                <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-500/40 flex items-center gap-1 font-bold">
                  <CheckCircle2 className="w-3 h-3 text-cyan-400" /> {calendarResult.total_blocks_synced} Milestones Synced
                </span>
              ) : (
                <span className="text-[10px] font-mono text-slate-500">Awaiting Calendar Sync</span>
              )}
            </div>
            <p className="text-xs text-slate-300">
              Dispatches {plan.schedule.length} run-of-show timeline blocks with outdoor microclimate flags, responsible vendors, and buffer alarms.
            </p>

            {calendarResult && (
              <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5 text-slate-400">
                <p><span className="text-slate-500">Calendar Target:</span> <span className="text-slate-200 font-medium">{calendarResult.calendar_id}</span></p>
                <p><span className="text-slate-500">Total Blocks Synced:</span> <span className="text-cyan-400 font-bold">{calendarResult.total_blocks_synced} Blocks</span></p>
                <div className="pt-1 flex flex-wrap gap-1.5">
                  <span className="px-2 py-0.5 rounded bg-blue-950/60 text-blue-300 border border-blue-800/60 text-[10px]">
                    RFC3339 Timestamps
                  </span>
                  <span className="px-2 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800/60 text-[10px]">
                    Weather Watch Alarms
                  </span>
                </div>
              </div>
            )}
          </div>

          {calendarResult ? (
            <a
              href="https://calendar.google.com"
              target="_blank"
              rel="noreferrer"
              className="mt-4 inline-flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs font-bold shadow-lg shadow-blue-700/30 hover:brightness-110 transition-all cursor-pointer"
            >
              <Calendar className="w-4 h-4" />
              Open Synced Google Calendar Run-of-Show
              <ArrowUpRight className="w-4 h-4" />
            </a>
          ) : (
            <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 font-mono">
              Click &quot;Sync Google Calendar&quot; to publish schedule blocks to Google Calendar.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
