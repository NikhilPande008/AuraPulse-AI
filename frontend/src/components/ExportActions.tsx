"use client";

import React, { useState } from "react";
import type { MasterEventPlan, SheetsExportResult } from "../types/plan";
import { exportCalendarIcs, exportToSheets } from "../lib/api";
import { reportError } from "../lib/client";
import { downloadBoqCsv } from "../lib/exportCsv";
import ExportSheetsCard from "./export/ExportSheetsCard";
import ExportCalendarCard from "./export/ExportCalendarCard";
import { FileSpreadsheet, Calendar, Download, RefreshCw } from "lucide-react";
import { defaultEventDate } from "@/lib/dates";

interface ExportActionsProps {
  plan: MasterEventPlan;
}

export default function ExportActions({ plan }: ExportActionsProps) {
  const [exportingSheets, setExportingSheets] = useState(false);
  const [exportingIcs, setExportingIcs] = useState(false);
  const [sheetResult, setSheetResult] = useState<SheetsExportResult | null>(null);
  const [icsDownloaded, setIcsDownloaded] = useState(false);
  const [icsError, setIcsError] = useState<string | null>(null);
  const [sheetError, setSheetError] = useState<string | null>(null);
  const [csvDownloaded, setCsvDownloaded] = useState(false);

  const handleDownloadCsv = () => {
    downloadBoqCsv(plan);
    setCsvDownloaded(true);
  };

  const handleExportSheets = async () => {
    setExportingSheets(true);
    setSheetError(null);
    try {
      const res = await exportToSheets(plan.title, plan.boq);
      setSheetResult(res);
      if (res.status === "NOT_CONFIGURED") {
        setSheetError(res.message || "Google Sheets export not configured.");
      }
    } catch (err: unknown) {
      reportError(err, "ExportActions.handleExportSheets");
      setSheetResult(null);
      setSheetError(err instanceof Error ? err.message : "Google Sheets export failed.");
    } finally {
      setExportingSheets(false);
    }
  };

  const handleDownloadIcs = async () => {
    setExportingIcs(true);
    setIcsError(null);
    try {
      const blob = await exportCalendarIcs(plan);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${(plan.title || "event").toLowerCase().replace(/[^a-z0-9]/g, "_")}_schedule.ics`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setIcsDownloaded(true);
    } catch (err: unknown) {
      reportError(err, "ExportActions.handleDownloadIcs");
      setIcsError("Failed to export RFC-5545 .ics calendar. Please try again.");
    } finally {
      setExportingIcs(false);
    }
  };

  const getGoogleCalendarWebIntentUrl = () => {
    const todayPlus90 = defaultEventDate(90);
    const evDate = plan.event_date || todayPlus90;
    const cleanDate = evDate.replace(/-/g, "");
    const startTime = "090000";
    const endTime = "220000";
    const dates = `${cleanDate}T${startTime}/${cleanDate}T${endTime}`;

    const milestoneSummary = (plan.planning_milestones || [])
      .map((m) => `• [${m.phase}] ${m.title} (Due: ${m.due_date})`)
      .join("\n");

    const scheduleSummary = (plan.schedule || [])
      .map((s) => `• ${s.start_time_iso}-${s.end_time_iso}: ${s.activity} (${s.responsible_party})`)
      .join("\n");

    const details = `AuraPulse Event Plan: ${plan.title}\n\nMilestones:\n${milestoneSummary}\n\nDay-Of Schedule:\n${scheduleSummary}`;

    const params = new URLSearchParams({
      action: "TEMPLATE",
      text: plan.title,
      dates: dates,
      details: details,
      location: plan.location_city || "India",
      ctz: "Asia/Kolkata",
    });

    return `https://calendar.google.com/calendar/render?${params.toString()}`;
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase font-mono">
              Workspace & Temporal Export Engine
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Sheets API v4 & RFC-5545 iCalendar
            </span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Export & Calendar Integration</h2>
          <p className="text-sm text-slate-400">
            Publish interactive formula spreadsheets, download standard RFC-5545 (.ics) calendars,
            or add run-of-show directly to Google Calendar.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleDownloadCsv}
            className="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-teal-600/20 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" />
            Download CSV
          </button>

          <button
            onClick={handleExportSheets}
            disabled={exportingSheets}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition-all cursor-pointer disabled:opacity-50"
          >
            {exportingSheets ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="w-4 h-4" />
            )}
            Export to Google Sheets
          </button>

          <button
            onClick={handleDownloadIcs}
            disabled={exportingIcs}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all cursor-pointer disabled:opacity-50"
          >
            {exportingIcs ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            📅 Download iCal (.ics)
          </button>

          <a
            href={getGoogleCalendarWebIntentUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-all cursor-pointer"
          >
            <Calendar className="w-4 h-4" />
            🔗 Add to Google Calendar
          </a>
        </div>
      </div>

      {/* Results and Formula Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ExportSheetsCard
          sheetResult={sheetResult}
          sheetError={sheetError}
          csvDownloaded={csvDownloaded}
        />
        <ExportCalendarCard
          plan={plan}
          icsDownloaded={icsDownloaded}
          icsError={icsError}
          exportingIcs={exportingIcs}
          onDownloadIcs={handleDownloadIcs}
          calendarWebIntentUrl={getGoogleCalendarWebIntentUrl()}
        />
      </div>
    </div>
  );
}
