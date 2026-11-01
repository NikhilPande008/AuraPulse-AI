"use client";

import React from "react";
import { MapPin } from "lucide-react";
import type { PlaceVendor } from "../../types/plan";
import VendorCard from "./VendorCard";
import VendorFilter from "./VendorFilter";

interface PlacesSearchProps {
  city: string;
  query: string;
  onQueryChange: (query: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  isConfigured: boolean;
  vendors: PlaceVendor[];
  onAddVendor: (vendor: PlaceVendor) => void;
}

export default function PlacesSearch({
  city,
  query,
  onQueryChange,
  onSubmit,
  loading,
  isConfigured,
  vendors,
  onAddVendor,
}: PlacesSearchProps) {
  return (
    <div
      id="panel-vendor-maps"
      role="tabpanel"
      aria-labelledby="tab-vendor-maps"
      className="space-y-4"
    >
      <VendorFilter
        query={query}
        onQueryChange={onQueryChange}
        onSubmit={onSubmit}
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
          <VendorCard key={v.place_id || i} vendor={v} onAdd={onAddVendor} />
        ))}
      </div>
    </div>
  );
}
