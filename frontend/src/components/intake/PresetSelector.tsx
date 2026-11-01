"use client";

import React from "react";
import Image from "next/image";
import { CheckCircle2, Sparkles } from "lucide-react";

export interface DemoPreset {
  id: string;
  name: string;
  type: string;
  city: string;
  headcount: number;
  budget: number;
  badge: string;
  thumbnail: string;
  description: string;
  tags: string[];
}

export const DEMO_PRESETS: DemoPreset[] = [
  {
    id: "meadow_wedding",
    name: "Boho Sunset Meadow Wedding",
    type: "wedding",
    city: "Pune",
    headcount: 300,
    budget: 1500000,
    badge: "Sample Plan • Wedding",
    thumbnail:
      "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=600&q=80",
    description:
      "Pastel peach & sage palette, pampas grass arch, 2,000 ft Edison festoons, farm-to-table banquet.",
    tags: ["Pune Meadow", "300 Pax", "₹15 Lakhs", "Pastel Peach & Sage"],
  },
  {
    id: "cyber_birthday",
    name: "Cyberpunk Neon 30th Birthday",
    type: "birthday",
    city: "Mumbai",
    headcount: 60,
    budget: 250000,
    badge: "Sample Plan • Birthday",
    thumbnail:
      "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600&q=80",
    description:
      "Violet & electric cyan wash, wireless Astera tubes, DJ synthwave rig, molecular tapas bar.",
    tags: ["Mumbai Rooftop", "60 Pax", "₹2.5 Lakhs", "Violet & Electric Cyan"],
  },
  {
    id: "diwali_mela",
    name: "Eco-Friendly Society Diwali Mela",
    type: "community_festival",
    city: "Pune",
    headcount: 800,
    budget: 500000,
    badge: "Sample Plan • Community",
    thumbnail:
      "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=600&q=80",
    description:
      "Marigold yellow & clay tones, zero-plastic food stalls, solar festoons, authentic Dhol Tasha troupe.",
    tags: ["Pune Courtyard", "800 Pax", "₹5 Lakhs", "Zero Plastic Mela"],
  },
];

interface PresetSelectorProps {
  activePresetId: string | null;
  onSelect: (preset: DemoPreset) => void;
  isLoading: boolean;
}

export default function PresetSelector({
  activePresetId,
  onSelect,
  isLoading,
}: PresetSelectorProps) {
  return (
    <fieldset className="space-y-3" role="radiogroup" aria-label="Competition Evaluation Presets">
      <legend className="sr-only">Competition Evaluation Presets</legend>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" aria-hidden="true" />
          Competition Evaluation Presets (One-Click Hydration)
        </span>
        <span className="text-xs text-purple-400 font-mono">
          Loads instant validated multi-tier BOQ
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {DEMO_PRESETS.map((preset) => {
          const isSelected = activePresetId === preset.id;
          return (
            <button
              type="button"
              role="radio"
              aria-checked={isSelected}
              aria-label={preset.name}
              key={preset.id}
              onClick={() => onSelect(preset)}
              disabled={isLoading}
              className={`group text-left p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden flex flex-col justify-between focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:outline-none ${
                isSelected
                  ? "bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/30 shadow-lg shadow-purple-900/30"
                  : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/90"
              }`}
            >
              <div className="space-y-3">
                <div className="relative h-28 w-full rounded-lg overflow-hidden border border-slate-800">
                  <Image
                    src={preset.thumbnail}
                    alt={preset.name}
                    fill
                    sizes="(max-width: 768px) 100vw, 33vw"
                    className="object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />
                  <span className="absolute top-2 left-2 text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-950/80 border border-slate-700/80 text-purple-300 backdrop-blur-sm">
                    {preset.badge}
                  </span>
                  {isSelected && (
                    <span className="absolute top-2 right-2 text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-600 text-white flex items-center gap-1 shadow-md">
                      <CheckCircle2 className="w-3 h-3" aria-hidden="true" /> Active
                    </span>
                  )}
                </div>

                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-purple-300 transition-colors">
                    {preset.name}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                    {preset.description}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mt-3 pt-3 border-t border-slate-800/80">
                {preset.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-xs font-mono px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}
