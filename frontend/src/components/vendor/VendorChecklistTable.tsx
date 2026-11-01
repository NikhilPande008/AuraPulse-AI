"use client";

import React from "react";
import { MapPin } from "lucide-react";
import type { VendorChecklistItem } from "../../types/plan";

interface VendorChecklistTableProps {
  items: VendorChecklistItem[];
  onStatusChange: (id: string, newStatus: VendorChecklistItem["status"]) => void;
  getStatusBadge: (status: VendorChecklistItem["status"]) => string;
}

export default function VendorChecklistTable({
  items,
  onStatusChange,
  getStatusBadge,
}: VendorChecklistTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800">
      <table className="w-full text-left text-xs">
        <thead className="bg-slate-900/90 text-slate-400 font-mono text-xs uppercase tracking-wider border-b border-slate-800">
          <tr>
            <th className="py-3 px-4">Category</th>
            <th className="py-3 px-4">Vendor & Specification</th>
            <th className="py-3 px-4 text-right">Estimated (INR)</th>
            <th className="py-3 px-4 text-center">Status</th>
            <th className="py-3 px-4">Operational Notes</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 font-sans">
          {items.map((item) => (
            <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
              <td className="py-3 px-4 whitespace-nowrap">
                <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700/60 font-medium">
                  {item.category}
                </span>
              </td>
              <td className="py-3 px-4">
                <p className="font-semibold text-slate-100">{item.vendor_name}</p>
                {item.google_maps_place_id && (
                  <span className="text-xs text-cyan-400 font-mono flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3 h-3" /> Grounded on Google Maps
                  </span>
                )}
              </td>
              <td className="py-3 px-4 text-right font-mono font-bold text-slate-200">
                ₹{item.estimated_cost.toLocaleString("en-IN")}
              </td>
              <td className="py-3 px-4 text-center">
                <label htmlFor={`vendor-status-${item.id}`} className="sr-only">
                  Status for {item.vendor_name}
                </label>
                <select
                  id={`vendor-status-${item.id}`}
                  value={item.status}
                  onChange={(e) =>
                    onStatusChange(item.id, e.target.value as VendorChecklistItem["status"])
                  }
                  className={`px-2.5 py-1 rounded-lg text-xs font-mono font-semibold border transition-all cursor-pointer bg-slate-900 ${getStatusBadge(
                    item.status
                  )}`}
                >
                  <option value="To Contact">To Contact</option>
                  <option value="Quoted">Quoted</option>
                  <option value="Booked">Booked</option>
                  <option value="Paid">Paid</option>
                </select>
              </td>
              <td className="py-3 px-4 text-slate-400 text-xs max-w-xs leading-relaxed">
                {item.notes}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
