"use client";

import React from "react";
import { ExternalLink, MapPin, Phone, Plus, ShieldCheck, Star } from "lucide-react";
import type { PlaceVendor } from "../../types/plan";

interface VendorCardProps {
  vendor: PlaceVendor;
  onAdd: (vendor: PlaceVendor) => void;
}

export default function VendorCard({ vendor, onAdd }: VendorCardProps) {
  const rating = vendor.rating ?? 0;

  return (
    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-2 mb-2">
          <h4 className="text-sm font-bold text-white leading-tight">{vendor.name}</h4>
          {rating > 0 && (
            <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-mono font-bold shrink-0">
              <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
              {rating}
            </div>
          )}
        </div>

        <span className="text-xs font-mono text-cyan-400 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40 inline-block mb-2">
          {vendor.query_matched || "Verified Local Supplier"}
        </span>

        <p className="text-xs text-slate-400 flex items-start gap-1.5 mb-2">
          <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
          <span className="line-clamp-2">{vendor.address}</span>
        </p>

        {vendor.phone && (
          <p className="text-xs text-slate-400 flex items-center gap-1.5 mb-2 font-mono">
            <Phone className="w-3 h-3 text-emerald-400 shrink-0" />
            <span>{vendor.phone}</span>
          </p>
        )}

        {vendor.google_maps_uri && (
          <a
            href={vendor.google_maps_uri}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs font-mono text-cyan-400 hover:text-cyan-300 hover:underline mb-2"
          >
            <span>View on Google Maps</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>

      <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
        <span className="flex items-center gap-1 text-emerald-400 font-mono text-xs">
          <ShieldCheck className="w-3.5 h-3.5" /> Google Verified
        </span>
        <button
          type="button"
          onClick={() => onAdd(vendor)}
          className="px-2.5 py-1 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer"
        >
          <Plus className="w-3 h-3" /> Add to Checklist
        </button>
      </div>
    </div>
  );
}
