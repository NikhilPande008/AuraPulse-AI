"use client";

import React from "react";
import { ArrowUpRight, CheckCircle2, FileSpreadsheet } from "lucide-react";
import type { SheetsExportResult } from "../../types/plan";

interface ExportSheetsCardProps {
  sheetResult: SheetsExportResult | null;
  sheetError: string | null;
  csvDownloaded: boolean;
}

export default function ExportSheetsCard({
  sheetResult,
  sheetError,
  csvDownloaded,
}: ExportSheetsCardProps) {
  return (
    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1.5">
            <FileSpreadsheet className="w-4 h-4" /> Google Sheets API v4
          </span>
          {sheetResult && sheetResult.spreadsheet_url ? (
            <span className="text-xs font-mono text-emerald-300 bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-500/40 flex items-center gap-1 font-bold">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Exported (
              {sheetResult.items_exported} Rows)
            </span>
          ) : sheetError || (sheetResult && sheetResult.status === "NOT_CONFIGURED") ? (
            <span className="text-xs font-mono text-amber-300 bg-amber-950/60 px-2.5 py-0.5 rounded-full border border-amber-700/50">
              Not Configured
            </span>
          ) : (
            <span className="text-xs font-mono text-slate-400">
              Requires service-account credentials
            </span>
          )}
        </div>
        <p className="text-xs text-slate-300">
          Generates multi-tab workbook with automated{" "}
          <code className="text-cyan-300 font-mono">=SUM(H2:H11)</code> grand total and{" "}
          <code className="text-amber-300 font-mono">=SUMIF(...)</code> priority analytics.
        </p>

        {sheetResult && sheetResult.spreadsheet_url && (
          <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5 text-slate-400">
            <p>
              <span className="text-slate-400">Workbook Title:</span>{" "}
              <span className="text-slate-200 font-medium">{sheetResult.spreadsheet_title}</span>
            </p>
            <p>
              <span className="text-slate-400">Grand Total Formula:</span>{" "}
              <span className="text-cyan-400 font-bold">{sheetResult.grand_total_formula}</span>
            </p>
            <p>
              <span className="text-slate-400">Priority SUMIF:</span>{" "}
              <span className="text-amber-300 font-bold">
                {sheetResult.priority_formulas?.["Critical Tier Formula"] || "=SUMIF(...)"}
              </span>
            </p>
            <p>
              <span className="text-slate-400">Total Lines:</span>{" "}
              <span className="text-emerald-400 font-bold">
                {sheetResult.total_rows_created} formatted rows
              </span>
            </p>
          </div>
        )}
        {sheetResult && sheetResult.status === "NOT_CONFIGURED" && (
          <div className="mt-3 p-3 rounded-lg bg-amber-950/30 border border-amber-800/50 text-xs font-mono text-amber-300">
            <p className="font-semibold">Google Sheets export inactive</p>
            <p className="text-xs text-amber-300/80 mt-1">
              {sheetResult.message || "Backend service-account credentials are not configured."}
            </p>
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
            No credentials? Use &quot;Download CSV&quot; and import into Google Sheets (File →
            Import).
            {csvDownloaded && <span className="text-teal-300"> CSV downloaded ✓</span>}
          </p>
        </div>
      )}
    </div>
  );
}
