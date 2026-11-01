"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { CheckCircle2, ListChecks, MapPin } from "lucide-react";
import { fetchVendors } from "../lib/api";
import { reportError } from "../lib/client";
import type { PlaceVendor, VendorChecklistItem } from "../types/plan";
import VendorCard from "./vendor/VendorCard";
import VendorChecklistTable from "./vendor/VendorChecklistTable";
import VendorFilter from "./vendor/VendorFilter";

interface VendorFinderProps {
  city: string;
  checklist?: VendorChecklistItem[];
  onChecklistUpdate?: (updatedList: VendorChecklistItem[]) => void;
}

const DEFAULT_CHECKLIST: VendorChecklistItem[] = [
  {
    id: "vc_def_01",
    category: "Catering & Banquet",
    vendor_name: "Artisan Kitchen Pune (Farm-to-Table)",
    estimated_cost: 450000,
    status: "Booked",
    notes: "30% deposit cleared. Live pizza station confirmed.",
  },
  {
    id: "vc_def_02",
    category: "Floral & Stage Decor",
    vendor_name: "BloomCraft Botanicals (Pampas & Sage)",
    estimated_cost: 160000,
    status: "Quoted",
    notes: "Negotiating marigold and local flora substitution.",
  },
  {
    id: "vc_def_03",
    category: "Audio / Visual & Lighting",
    vendor_name: "LumenGlow & AcousticPro Rigging",
    estimated_cost: 295000,
    status: "Booked",
    notes: "2,000 ft festoons + column array audio.",
  },
  {
    id: "vc_def_04",
    category: "Power & Safety",
    vendor_name: "PowerGrid Silent DG Sets",
    estimated_cost: 85000,
    status: "To Contact",
    notes: "Need municipal safety inspection certificate.",
  },
  {
    id: "vc_def_05",
    category: "Photography & Drone",
    vendor_name: "GoldenHour Cinematic Studios",
    estimated_cost: 85000,
    status: "Paid",
    notes: "100% advance paid. 2 cinematographers booked.",
  },
];

export default function VendorFinder({
  city,
  checklist = DEFAULT_CHECKLIST,
  onChecklistUpdate,
}: VendorFinderProps) {
  const [activeTab, setActiveTab] = useState<"checklist" | "maps">("checklist");
  const [localChecklist, setLocalChecklist] = useState<VendorChecklistItem[]>(checklist);
  const [query, setQuery] = useState("floral and sound rental");
  const [vendors, setVendors] = useState<PlaceVendor[]>([]);
  const [isConfigured, setIsConfigured] = useState(true);
  const [loading, setLoading] = useState(false);
  const [addedNotice, setAddedNotice] = useState<string | null>(null);

  useEffect(() => {
    if (checklist && checklist.length > 0) {
      setLocalChecklist(checklist);
    }
  }, [checklist]);

  const queryRef = useRef(query);
  useEffect(() => {
    queryRef.current = query;
  }, [query]);

  const loadVendors = useCallback(async (searchQuery: string, targetCity: string) => {
    setLoading(true);
    try {
      const data = await fetchVendors(searchQuery, targetCity, 4.0);
      setVendors(data.vendors || []);
      setIsConfigured(data.is_configured ?? ((data.vendors && data.vendors.length > 0) || false));
    } catch (err) {
      reportError(err, "VendorFinder");
      setVendors([]);
      setIsConfigured(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadVendors(queryRef.current, city);
  }, [city, loadVendors]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadVendors(query, city);
  };

  const handleStatusChange = (id: string, newStatus: VendorChecklistItem["status"]) => {
    const updated = localChecklist.map((item) => {
      if (item.id === id) {
        return { ...item, status: newStatus };
      }
      return item;
    });
    setLocalChecklist(updated);
    if (onChecklistUpdate) onChecklistUpdate(updated);
  };

  const handleAddVendorFromMaps = (v: PlaceVendor) => {
    const newItem: VendorChecklistItem = {
      id: `vc_${Date.now()}`,
      category: v.query_matched || "General Event Services",
      vendor_name: v.name,
      estimated_cost: 75000,
      status: "To Contact",
      notes: `Discovered via Google Maps (${v.rating || 4.0}★). Address: ${v.address || "Local"}`,
      google_maps_place_id: v.place_id,
    };
    const updated = [newItem, ...localChecklist];
    setLocalChecklist(updated);
    if (onChecklistUpdate) onChecklistUpdate(updated);

    setAddedNotice(`Added "${v.name}" to Vendor Checklist!`);
    setTimeout(() => setAddedNotice(null), 3000);
  };

  const getStatusBadge = (status: VendorChecklistItem["status"]) => {
    switch (status) {
      case "To Contact":
        return "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700";
      case "Quoted":
        return "bg-amber-950/80 text-amber-300 border-amber-600/60 hover:bg-amber-900/80";
      case "Booked":
        return "bg-cyan-950/80 text-cyan-300 border-cyan-600/60 hover:bg-cyan-900/80";
      case "Paid":
        return "bg-emerald-950/80 text-emerald-300 border-emerald-600/60 hover:bg-emerald-900/80";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  const totalCommitted = localChecklist
    .filter((v) => v.status === "Booked" || v.status === "Paid")
    .reduce((sum, v) => sum + v.estimated_cost, 0);

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800 space-y-6">
      {/* Header and Section Toggle */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase font-mono">
              Challenge 5 Core • Vendor Operations
            </span>
            <span className="text-xs text-slate-400 font-mono">Google Maps Grounded Pipeline</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Vendor Action Checklist & Grounding</h2>
          <p className="text-sm text-slate-400">
            Track vendor negotiations from initial contact to payment, and discover verified local
            suppliers in <span className="text-cyan-300 font-medium">{city}</span>.
          </p>
        </div>

        {/* Tab Toggle */}
        <div
          role="tablist"
          aria-label="Vendor views"
          className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 self-start md:self-auto"
        >
          <button
            role="tab"
            id="tab-vendor-checklist"
            aria-controls="panel-vendor-checklist"
            aria-selected={activeTab === "checklist"}
            type="button"
            onClick={() => setActiveTab("checklist")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              activeTab === "checklist"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <ListChecks className="w-3.5 h-3.5" />
            Vendor Checklist ({localChecklist.length})
          </button>
          <button
            role="tab"
            id="tab-vendor-maps"
            aria-controls="panel-vendor-maps"
            aria-selected={activeTab === "maps"}
            type="button"
            onClick={() => setActiveTab("maps")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              activeTab === "maps"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <MapPin className="w-3.5 h-3.5" />
            Google Maps Grounding
          </button>
        </div>
      </div>

      {addedNotice && (
        <div className="px-4 py-2 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs font-mono flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          {addedNotice}
        </div>
      )}

      {/* VIEW 1: VENDOR ACTION CHECKLIST TABLE */}
      {activeTab === "checklist" && (
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
                Total Vendors: <strong className="text-white">{localChecklist.length}</strong>
              </span>
              <span>
                Paid:{" "}
                <strong className="text-emerald-400">
                  {localChecklist.filter((v) => v.status === "Paid").length}
                </strong>
              </span>
              <span>
                Booked:{" "}
                <strong className="text-cyan-400">
                  {localChecklist.filter((v) => v.status === "Booked").length}
                </strong>
              </span>
              <span>
                Quoted:{" "}
                <strong className="text-amber-400">
                  {localChecklist.filter((v) => v.status === "Quoted").length}
                </strong>
              </span>
              <span>
                To Contact:{" "}
                <strong className="text-slate-400">
                  {localChecklist.filter((v) => v.status === "To Contact").length}
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
            items={localChecklist}
            onStatusChange={handleStatusChange}
            getStatusBadge={getStatusBadge}
          />
        </div>
      )}

      {/* VIEW 2: GOOGLE MAPS VENDOR GROUNDING */}
      {activeTab === "maps" && (
        <div
          id="panel-vendor-maps"
          role="tabpanel"
          aria-labelledby="tab-vendor-maps"
          className="space-y-4"
        >
          <VendorFilter
            query={query}
            onQueryChange={setQuery}
            onSubmit={handleSearch}
            loading={loading}
            city={city}
          />

          {/* Transparent Honest Inactive Banner if key is missing or unconfigured */}
          {(!isConfigured || vendors.length === 0) && !loading && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-xs text-amber-300 font-mono">
              <MapPin className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-semibold text-amber-200">
                  Live Google Maps Places grounding inactive (API key not configured). Add custom
                  vendors manually or provide a Maps API key.
                </p>
                <p className="text-xs text-amber-300/80">
                  Places API (New) endpoint:{" "}
                  <code className="text-white">places.googleapis.com/v1/places:searchText</code>.
                  Unverified mock businesses and phone numbers are strictly prohibited.
                </p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {vendors.map((v, i) => (
              <VendorCard key={v.place_id || i} vendor={v} onAdd={handleAddVendorFromMaps} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
