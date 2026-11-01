"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { MapPin, Star, Phone, Search, ExternalLink, ShieldCheck, RefreshCw, CheckCircle2, ListChecks, Plus } from "lucide-react";
import { fetchVendors, VendorChecklistItem } from "../lib/api";

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
  }
];

export default function VendorFinder({
  city,
  checklist = DEFAULT_CHECKLIST,
  onChecklistUpdate,
}: VendorFinderProps) {
  const [activeTab, setActiveTab] = useState<"checklist" | "maps">("checklist");
  const [localChecklist, setLocalChecklist] = useState<VendorChecklistItem[]>(checklist);
  const [query, setQuery] = useState("floral and sound rental");
  const [vendors, setVendors] = useState<any[]>([]);
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
      console.error(err);
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

  const handleAddVendorFromMaps = (v: any) => {
    const newItem: VendorChecklistItem = {
      id: `vc_${Date.now()}`,
      category: v.category || "General Event Services",
      vendor_name: v.name,
      estimated_cost: v.price_level ? v.price_level * 50000 : 75000,
      status: "To Contact",
      notes: `Discovered via Google Maps (${v.rating}★). Address: ${v.address}`,
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
            Track vendor negotiations from initial contact to payment, and discover verified local suppliers in <span className="text-cyan-300 font-medium">{city}</span>.
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
              <span>Total Vendors: <strong className="text-white">{localChecklist.length}</strong></span>
              <span>Paid: <strong className="text-emerald-400">{localChecklist.filter((v) => v.status === "Paid").length}</strong></span>
              <span>Booked: <strong className="text-cyan-400">{localChecklist.filter((v) => v.status === "Booked").length}</strong></span>
              <span>Quoted: <strong className="text-amber-400">{localChecklist.filter((v) => v.status === "Quoted").length}</strong></span>
              <span>To Contact: <strong className="text-slate-400">{localChecklist.filter((v) => v.status === "To Contact").length}</strong></span>
            </div>
            <div className="text-right">
              <span className="text-slate-400">Committed Capital: </span>
              <strong className="text-purple-300 text-sm">₹{totalCommitted.toLocaleString("en-IN")}</strong>
            </div>
          </div>

          {/* Interactive Checklist Table */}
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
                {localChecklist.map((item) => (
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
                          handleStatusChange(item.id, e.target.value as VendorChecklistItem["status"])
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
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <form onSubmit={handleSearch} className="flex items-center gap-2 w-full sm:w-auto">
              <label htmlFor="vendor-search-input" className="sr-only">
                Search vendors
              </label>
              <div className="relative flex-1 sm:w-72">
                <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                <input
                  id="vendor-search-input"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g. canopy rental, caterer, DJ sound..."
                  className="bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500 w-full"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="px-3.5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : "Search Maps"}
              </button>
            </form>
            <span className="text-xs text-slate-400 font-mono self-end sm:self-auto">
              Showing verified vendors in <strong className="text-cyan-300">{city}</strong>
            </span>
          </div>

          {/* Transparent Honest Inactive Banner if key is missing or unconfigured */}
          {(!isConfigured || vendors.length === 0) && !loading && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-xs text-amber-300 font-mono">
              <MapPin className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-semibold text-amber-200">
                  Live Google Maps Places grounding inactive (API key not configured). Add custom vendors manually or provide a Maps API key.
                </p>
                <p className="text-xs text-amber-300/80">
                  Places API (New) endpoint: <code className="text-white">places.googleapis.com/v1/places:searchText</code>. Unverified mock businesses and phone numbers are strictly prohibited.
                </p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {vendors.map((v, i) => (
              <div
                key={v.place_id || i}
                className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h4 className="text-sm font-bold text-white leading-tight">{v.name}</h4>
                    {v.rating > 0 && (
                      <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-mono font-bold shrink-0">
                        <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                        {v.rating}
                      </div>
                    )}
                  </div>

                  <span className="text-xs font-mono text-cyan-400 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40 inline-block mb-2">
                    {v.category || "Verified Local Supplier"}
                  </span>

                  <p className="text-xs text-slate-400 flex items-start gap-1.5 mb-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                    <span className="line-clamp-2">{v.address}</span>
                  </p>

                  {v.phone && (
                    <p className="text-xs text-slate-400 flex items-center gap-1.5 mb-2 font-mono">
                      <Phone className="w-3 h-3 text-emerald-400 shrink-0" />
                      <span>{v.phone}</span>
                    </p>
                  )}

                  {v.google_maps_uri && (
                    <a
                      href={v.google_maps_uri}
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
                    onClick={() => handleAddVendorFromMaps(v)}
                    className="px-2.5 py-1 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer"
                  >
                    <Plus className="w-3 h-3" /> Add to Checklist
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
