"use client";

import React from "react";
import type { VendorChecklistItem } from "../../types/plan";
import VendorChecklistTable from "./VendorChecklistTable";

interface VendorChecklistProps {
  checklist: VendorChecklistItem[];
  onStatusChange: (id: string, newStatus: VendorChecklistItem["status"]) => void;
  getStatusBadge: (status: VendorChecklistItem["status"]) => string;
}

export default function VendorChecklist({
  checklist,
  onStatusChange,
  getStatusBadge,
}: VendorChecklistProps) {
  const totalCommitted = checklist
    .filter((v) => v.status === "Booked" || v.status === "Paid")
    .reduce((sum, v) => sum + v.estimated_cost, 0);

  return (
    <div
      id="panel-vendor-checklist"
      role="tabpanel"
      aria-labelledby="tab-vendor-checklist"
      className="space-y-4"
    >
      {/* Summary Strip */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-mono">
        <div className="flex items-center gap-4">
          <span>
            Total Vendors: <strong className="text-white">{checklist.length}</strong>
          </span>
          <span>
            Paid:{" "}
            <strong className="text-emerald-400">
              {checklist.filter((v) => v.status === "Paid").length}
            </strong>
          </span>
          <span>
            Booked:{" "}
            <strong className="text-cyan-400">
              {checklist.filter((v) => v.status === "Booked").length}
            </strong>
          </span>
          <span>
            Quoted:{" "}
            <strong className="text-amber-400">
              {checklist.filter((v) => v.status === "Quoted").length}
            </strong>
          </span>
          <span>
            To Contact:{" "}
            <strong className="text-slate-400">
              {checklist.filter((v) => v.status === "To Contact").length}
            </strong>
          </span>
        </div>
        <div className="text-right">
          <span className="text-slate-400">Committed Capital: </span>
          <strong className="text-purple-300 text-sm">
            ₹{totalCommitted.toLocaleString("en-IN")}
          </strong>
        </div>
      </div>

      <VendorChecklistTable
        items={checklist}
        onStatusChange={onStatusChange}
        getStatusBadge={getStatusBadge}
      />
    </div>
  );
}
