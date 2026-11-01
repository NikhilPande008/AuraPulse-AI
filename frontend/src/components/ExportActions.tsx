"use client";

import React, { useState } from "react";
import { MasterEventPlan, exportToSheets, exportCalendarIcs } from "../lib/api";
import { FileSpreadsheet, Calendar, Download, ExternalLink, RefreshCw, CheckCircle2, ArrowUpRight, Clock, ShieldCheck } from "lucide-react";

import { defaultEventDate } from "@/lib/dates";

interface ExportActionsProps {
  plan: MasterEventPlan;
}

export default function ExportActions({ plan }: ExportActionsProps) {
  const [exportingSheets, setExportingSheets] = useState(false);
  const [exportingIcs, setExportingIcs] = useState(false);
  const [sheetResult, setSheetResult] = useState<any | null>(null);
  const [icsDownloaded, setIcsDownloaded] = useState(false);
  const [icsError, setIcsError] = useState<string | null>(null);
  const [sheetError, setSheetError] = useState<string | null>(null);
  const [csvDownloaded, setCsvDownloaded] = useState(false);

  const csvEscape = (value: unknown): string => {
    const str = value === null || value === undefined ? "" : String(value);
    return /[",\r\n]/.test(str) ? `"${str.replace(/"/g, '""')}"` : str;
  };

  const handleDownloadCsv = () => {
    const header = ["Item ID", "Category", "Name", "Specification", "Quantity", "Unit", "Rate (INR)", "Total (INR)", "Priority Tier", "Status"];
    const rows: (string | number)[][] = plan.boq.map((it) => [
      it.item_id,
      it.category,
      it.name,
      it.specification,
      it.quantity,
      it.unit,
      it.estimated_rate_inr,
      it.status === "DROPPED" ? 0 : it.total_cost_inr,
      it.priority,
      it.status,
    ]);
    const criticalTotal = plan.boq
      .filter((it) => it.status !== "DROPPED" && it.priority === "Critical")
      .reduce((sum, it) => sum + (it.total_cost_inr || 0), 0);
    const operationalTotal = plan.boq
      .filter((it) => it.status !== "DROPPED" && it.priority === "Operational")
      .reduce((sum, it) => sum + (it.total_cost_inr || 0), 0);
    const discretionaryTotal = plan.boq
      .filter((it) => it.status !== "DROPPED" && it.priority === "Discretionary")
      .reduce((sum, it) => sum + (it.total_cost_inr || 0), 0);
    const activeTotal = plan.boq
      .filter((it) => it.status !== "DROPPED")
      .reduce((sum, it) => sum + (it.total_cost_inr || 0), 0);

    rows.push(["", "", "SUBTOTAL: Critical (Tier 1)", "", "", "", "", Math.round(criticalTotal * 100) / 100, "Critical", ""]);
    rows.push(["", "", "SUBTOTAL: Operational (Tier 2)", "", "", "", "", Math.round(operationalTotal * 100) / 100, "Operational", ""]);
    rows.push(["", "", "SUBTOTAL: Discretionary (Tier 3)", "", "", "", "", Math.round(discretionaryTotal * 100) / 100, "Discretionary", ""]);
    rows.push(["", "", "GRAND TOTAL (Active Items)", "", "", "", "", Math.round(activeTotal * 100) / 100, "", ""]);
    rows.push(["", "", "Budget Ceiling", "", "", "", "", plan.total_budget_limit, "", ""]);

    const csv = [header, ...rows].map((r) => r.map(csvEscape).join(",")).join("\r\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(plan.title || "event").toLowerCase().replace(/[^a-z0-9]/g, "_")}_boq.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
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
    } catch (err: any) {
      console.error(err);
      setSheetResult(null);
      setSheetError(err?.message || "Google Sheets export failed.");
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
    } catch (err: any) {
      console.error("ICS download error:", err);
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
            <span className="text-xs text-slate-400 font-mono">Sheets API v4 & RFC-5545 iCalendar</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Export & Calendar Integration</h2>
          <p className="text-sm text-slate-400">
            Publish interactive formula spreadsheets, download standard RFC-5545 (.ics) calendars, or add run-of-show directly to Google Calendar.
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
            {exportingSheets ? <RefreshCw className="w-4 h-4 animate-spin" /> : <FileSpreadsheet className="w-4 h-4" />}
            Export to Google Sheets
          </button>

          <button
            onClick={handleDownloadIcs}
            disabled={exportingIcs}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all cursor-pointer disabled:opacity-50"
          >
            {exportingIcs ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
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
        {/* Sheets Result Card */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1.5">
                <FileSpreadsheet className="w-4 h-4" /> Google Sheets API v4
              </span>
              {sheetResult && sheetResult.spreadsheet_url ? (
                <span className="text-xs font-mono text-emerald-300 bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-500/40 flex items-center gap-1 font-bold">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Exported ({sheetResult.items_exported} Rows)
                </span>
              ) : sheetError || (sheetResult && sheetResult.status === "NOT_CONFIGURED") ? (
                <span className="text-xs font-mono text-amber-300 bg-amber-950/60 px-2.5 py-0.5 rounded-full border border-amber-700/50">
                  Not Configured
                </span>
              ) : (
                <span className="text-xs font-mono text-slate-400">Requires service-account credentials</span>
              )}
            </div>
            <p className="text-xs text-slate-300">
              Generates multi-tab workbook with automated <code className="text-cyan-300 font-mono">=SUM(H2:H11)</code> grand total and <code className="text-amber-300 font-mono">=SUMIF(...)</code> priority analytics.
            </p>

            {sheetResult && sheetResult.spreadsheet_url && (
              <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5 text-slate-400">
                <p><span className="text-slate-400">Workbook Title:</span> <span className="text-slate-200 font-medium">{sheetResult.spreadsheet_title}</span></p>
                <p><span className="text-slate-400">Grand Total Formula:</span> <span className="text-cyan-400 font-bold">{sheetResult.grand_total_formula}</span></p>
                <p><span className="text-slate-400">Priority SUMIF:</span> <span className="text-amber-300 font-bold">{sheetResult.priority_formulas?.["Critical Tier Formula"] || "=SUMIF(...)"}</span></p>
                <p><span className="text-slate-400">Total Lines:</span> <span className="text-emerald-400 font-bold">{sheetResult.total_rows_created} formatted rows</span></p>
              </div>
            )}
            {sheetResult && sheetResult.status === "NOT_CONFIGURED" && (
              <div className="mt-3 p-3 rounded-lg bg-amber-950/30 border border-amber-800/50 text-xs font-mono text-amber-300">
                <p className="font-semibold">Google Sheets export inactive</p>
                <p className="text-xs text-amber-300/80 mt-1">{sheetResult.message || "Backend service-account credentials are not configured."}</p>
              </div>
            )}
          </div>

          {sheetResult && sheetResult.spreadsheet_url ? (
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
            <div className="mt-3 pt-3 border-t border-slate-800/80 text-xs font-mono space-y-1">
              {sheetError && <p className="text-amber-300">{sheetError}</p>}
              <p className="text-slate-400">
                No credentials? Use &quot;Download CSV&quot; and import into Google Sheets (File → Import).
                {csvDownloaded && <span className="text-teal-300"> CSV downloaded ✓</span>}
              </p>
            </div>
          )}
        </div>

        {/* RFC-5545 Calendar Card */}
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
              Zero-permission universal calendar export. Includes {plan.planning_milestones?.length || 0} backwards planning milestones as all-day events and {plan.schedule.length} run-of-show blocks with IST timezone (<code className="text-blue-300 font-mono">TZID=Asia/Kolkata</code>).
            </p>

            <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5 text-slate-400">
              <p><span className="text-slate-400">Target Timezone:</span> <span className="text-slate-200 font-medium">Asia/Kolkata (IST • UTC+05:30)</span></p>
              <p><span className="text-slate-400">Milestone Events:</span> <span className="text-cyan-400 font-bold">{plan.planning_milestones?.length || 0} All-Day Milestones</span></p>
              <p><span className="text-slate-400">Run-of-Show Blocks:</span> <span className="text-indigo-400 font-bold">{plan.schedule.length} Hourly Timed Blocks</span></p>
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
              onClick={handleDownloadIcs}
              disabled={exportingIcs}
              className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-blue-600/30 hover:bg-blue-600/50 text-blue-200 hover:text-white border border-blue-500/40 text-xs font-bold transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Download .ics
            </button>
            <a
              href={getGoogleCalendarWebIntentUrl()}
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
      </div>
    </div>
  );
}
