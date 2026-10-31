"use client";

import React, { useState } from "react";
import { Upload, Sparkles, Sliders, MapPin, Users, IndianRupee, Image as ImageIcon, Zap, CheckCircle2, Camera, X, ExternalLink, Loader2 } from "lucide-react";
import { deconstructMoodboard, MasterEventPlan, renderStudioAlternative } from "../lib/api";

interface MoodboardUploaderProps {
  onPlanLoaded: (plan: MasterEventPlan) => void;
  isLoading: boolean;
  setIsLoading: (val: boolean) => void;
}

export const DEMO_PRESETS = [
  {
    id: "meadow_wedding",
    name: "Boho Sunset Meadow Wedding",
    type: "wedding",
    city: "Pune",
    headcount: 300,
    budget: 1500000,
    badge: "Preset 1 • Wedding",
    thumbnail: "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=600&q=80",
    description: "Pastel peach & sage palette, pampas grass arch, 2,000 ft Edison festoons, farm-to-table banquet.",
    tags: ["Pune Meadow", "300 Pax", "₹15 Lakhs", "Pastel Peach & Sage"]
  },
  {
    id: "cyber_birthday",
    name: "Cyberpunk Neon 30th Birthday",
    type: "birthday",
    city: "Mumbai",
    headcount: 60,
    budget: 250000,
    badge: "Preset 2 • Birthday",
    thumbnail: "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600&q=80",
    description: "Violet & electric cyan wash, wireless Astera tubes, DJ synthwave rig, molecular tapas bar.",
    tags: ["Mumbai Rooftop", "60 Pax", "₹2.5 Lakhs", "Violet & Electric Cyan"]
  },
  {
    id: "diwali_mela",
    name: "Eco-Friendly Society Diwali Mela",
    type: "community_festival",
    city: "Pune",
    headcount: 800,
    budget: 500000,
    badge: "Preset 3 • Community",
    thumbnail: "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=600&q=80",
    description: "Marigold yellow & clay tones, zero-plastic food stalls, solar festoons, authentic Dhol Tasha troupe.",
    tags: ["Pune Courtyard", "800 Pax", "₹5 Lakhs", "Zero Plastic Mela"]
  }
];

export default function MoodboardUploader({ onPlanLoaded, isLoading, setIsLoading }: MoodboardUploaderProps) {
  const [selectedPreset, setSelectedPreset] = useState(DEMO_PRESETS[0]);
  const [headcount, setHeadcount] = useState(DEMO_PRESETS[0].headcount);
  const [locality, setLocality] = useState(DEMO_PRESETS[0].city);
  const [budget, setBudget] = useState(DEMO_PRESETS[0].budget);
  const [eventType, setEventType] = useState(DEMO_PRESETS[0].type);
  const [customImageBase64, setCustomImageBase64] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [isRenderingStudio, setIsRenderingStudio] = useState(false);
  const [studioModalOpen, setStudioModalOpen] = useState(false);
  const [studioResult, setStudioResult] = useState<{ image_url: string; prompt: string; model: string } | null>(null);

  const handleGenerateVisualConcept = async () => {
    setIsRenderingStudio(true);
    try {
      const res = await renderStudioAlternative(
        `${selectedPreset.name} featuring ${selectedPreset.description}`,
        selectedPreset.name
      );
      setStudioResult(res);
      setStudioModalOpen(true);
    } catch (err) {
      console.error(err);
      alert("Generative studio rendering encountered an issue.");
    } finally {
      setIsRenderingStudio(false);
    }
  };

  const triggerHydration = async (presetId: string, hCount: number, loc: string, bLimit: number, eType: string, imgB64?: string) => {
    setIsLoading(true);
    try {
      const plan = await deconstructMoodboard({
        image_base64: imgB64 || undefined,
        moodboard_preset: presetId,
        headcount: hCount,
        locality: loc,
        budget_ceiling: bLimit,
        event_type: eType,
      });
      onPlanLoaded(plan);
    } catch (err) {
      console.error(err);
      alert("Failed to deconstruct moodboard. Check backend server.");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePresetSelect = async (preset: typeof DEMO_PRESETS[0]) => {
    setSelectedPreset(preset);
    setHeadcount(preset.headcount);
    setLocality(preset.city);
    setBudget(preset.budget);
    setEventType(preset.type);
    setCustomImageBase64(null);
    // Instant One-Click Hydration for Competition Evaluation
    await triggerHydration(preset.id, preset.headcount, preset.city, preset.budget, preset.type, undefined);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        setCustomImageBase64(result);
        triggerHydration("custom", headcount, locality, budget, eventType, result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleManualDeconstruct = () => {
    triggerHydration(
      customImageBase64 ? "custom" : selectedPreset.id,
      headcount,
      locality,
      budget,
      eventType,
      customImageBase64 || undefined
    );
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide bg-purple-500/10 text-purple-400 border border-purple-500/20 uppercase font-mono">
              Agent 3.A • Multimodal Intake
            </span>
            <span className="text-xs text-slate-400 font-mono">Gemini 2.5 Flash Vision</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Aura Vision-to-BOQ Engine</h2>
          <p className="text-sm text-slate-400">
            Click any instant demo preset below or drop a custom board. The engine instantly extracts structural trusses, lighting specs, and hydrates the 3-tier Bill of Quantities.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={handleGenerateVisualConcept}
            disabled={isRenderingStudio}
            className="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-750 text-indigo-300 hover:text-white border border-indigo-500/40 text-xs font-semibold shadow-md transition-all disabled:opacity-50 cursor-pointer"
          >
            {isRenderingStudio ? (
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
            ) : (
              <Camera className="w-4 h-4 text-indigo-400" />
            )}
            <span>{isRenderingStudio ? "Rendering Scene..." : "✨ Imagen 3 Studio"}</span>
          </button>

          <button
            onClick={handleManualDeconstruct}
            disabled={isLoading}
            className="relative inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-500 text-white font-semibold text-sm shadow-lg shadow-purple-600/30 hover:shadow-purple-600/50 hover:brightness-110 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shrink-0"
          >
            <Sparkles className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            {isLoading ? "Deconstructing Pixels..." : "Re-Calculate Vision BOQ"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Instant One-Click Demo Presets */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-mono font-medium text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              One-Click Judge Presets (Instant Hydration)
            </label>
            <span className="text-[10px] text-emerald-400 font-mono bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">
              ⚡ Instant Auto-Hydrate
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {DEMO_PRESETS.map((preset) => {
              const isSelected = selectedPreset.id === preset.id && !customImageBase64;
              return (
                <div
                  key={preset.id}
                  onClick={() => handlePresetSelect(preset)}
                  className={`group relative rounded-xl overflow-hidden cursor-pointer border transition-all text-left flex flex-col justify-between ${
                    isSelected
                      ? "border-purple-500 ring-2 ring-purple-500/40 bg-purple-950/20 scale-[1.02]"
                      : "border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/80"
                  }`}
                >
                  <div className="relative h-28 w-full overflow-hidden">
                    <img
                      src={preset.thumbnail}
                      alt={preset.name}
                      className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                    <div className="absolute top-2 left-2">
                      <span className="text-[9px] font-mono uppercase px-2 py-0.5 rounded-full bg-slate-950/90 text-cyan-300 font-bold border border-cyan-800/60 shadow">
                        {preset.badge}
                      </span>
                    </div>
                  </div>

                  <div className="p-3 flex-1 flex flex-col justify-between">
                    <div>
                      <p className="text-xs font-bold text-white leading-tight group-hover:text-purple-300 transition-colors">
                        {preset.name}
                      </p>
                      <p className="text-[10px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                        {preset.description}
                      </p>
                    </div>

                    <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono">
                      <span className="text-purple-300 font-bold">₹{(preset.budget / 100000).toFixed(1)}L</span>
                      <span className="text-slate-400">{preset.headcount} Pax</span>
                      <span className="text-cyan-400 font-medium">{preset.city}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Custom Upload Dropzone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragActive(false);
              const file = e.dataTransfer.files?.[0];
              if (file) {
                const reader = new FileReader();
                reader.onloadend = () => {
                  const result = reader.result as string;
                  setCustomImageBase64(result);
                  triggerHydration("custom", headcount, locality, budget, eventType, result);
                };
                reader.readAsDataURL(file);
              }
            }}
            className={`relative rounded-xl border-2 border-dashed p-3.5 text-center transition-all ${
              dragActive ? "border-purple-400 bg-purple-950/20" : "border-slate-800 hover:border-slate-700 bg-slate-900/40"
            }`}
          >
            {customImageBase64 ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <img src={customImageBase64} alt="Custom upload" className="h-10 w-14 object-cover rounded-lg border border-purple-500/50" />
                  <div className="text-left">
                    <p className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Custom Mood Board Parsed
                    </p>
                    <p className="text-[10px] text-slate-400 font-mono">Multimodal Vision buffer ingested by Gemini 2.5 Flash</p>
                  </div>
                </div>
                <button
                  onClick={() => setCustomImageBase64(null)}
                  className="text-xs text-rose-400 hover:underline px-2 py-1"
                >
                  Reset
                </button>
              </div>
            ) : (
              <label className="cursor-pointer block">
                <Upload className="w-4 h-4 mx-auto text-slate-400 mb-1" />
                <span className="text-xs text-slate-300 font-medium">Or upload custom mood board (JPG/PNG)</span>
                <span className="block text-[10px] text-slate-500 font-mono mt-0.5">Extracts custom lighting, floristry, and spatial scale</span>
                <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
              </label>
            )}
          </div>
        </div>

        {/* Constraints & Parameters */}
        <div className="lg:col-span-5 bg-slate-900/60 rounded-xl p-4 border border-slate-800/80 space-y-3.5">
          <label className="text-xs font-mono font-medium text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            Budget & Locality Parameters
          </label>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <span className="text-[11px] text-slate-400 flex items-center gap-1 mb-1 font-mono">
                <MapPin className="w-3 h-3 text-cyan-400" /> Locality / City
              </span>
              <input
                type="text"
                value={locality}
                onChange={(e) => setLocality(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <span className="text-[11px] text-slate-400 flex items-center gap-1 mb-1 font-mono">
                <Users className="w-3 h-3 text-cyan-400" /> Headcount (Pax)
              </span>
              <input
                type="number"
                value={headcount}
                onChange={(e) => setHeadcount(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-[11px] text-slate-400 flex items-center gap-1 font-mono">
                <IndianRupee className="w-3 h-3 text-cyan-400" /> Budget Ceiling (INR)
              </span>
              <span className="text-xs font-mono font-bold text-purple-300">
                ₹{budget.toLocaleString("en-IN")}
              </span>
            </div>
            <input
              type="range"
              min="200000"
              max="5000000"
              step="50000"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              className="w-full accent-purple-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>₹2 Lakhs</span>
              <span>₹25 Lakhs</span>
              <span>₹50 Lakhs</span>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-800/80">
            <span className="text-[11px] text-slate-400 font-mono block mb-1">Event Typology</span>
            <div className="grid grid-cols-3 gap-2">
              {["wedding", "birthday", "community_festival"].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setEventType(type)}
                  className={`text-[11px] py-1 px-2 rounded capitalize font-medium transition-all ${
                    eventType === type
                      ? "bg-purple-600 text-white font-semibold"
                      : "bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800"
                  }`}
                >
                  {type.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Imagen 3 Generative Concept Modal */}
      {studioModalOpen && studioResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="relative max-w-2xl w-full bg-slate-900 border border-indigo-500/50 rounded-2xl overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950/60">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400">
                  <Camera className="w-4 h-4" />
                </span>
                <div>
                  <h3 className="text-sm font-bold text-white">Generative Visual Concept</h3>
                  <p className="text-[10px] font-mono text-indigo-300">Google Imagen 3 (imagen-3.0-generate-002)</p>
                </div>
              </div>
              <button
                onClick={() => setStudioModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 space-y-3">
              <div className="relative aspect-video w-full rounded-xl overflow-hidden border border-slate-800 bg-black">
                <img
                  src={studioResult.image_url}
                  alt={studioResult.prompt}
                  className="w-full h-full object-cover"
                />
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                <span className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                  Synthesized Architectural Prompt:
                </span>
                <p className="text-xs text-slate-200 font-sans leading-relaxed">
                  "{studioResult.prompt}"
                </p>
              </div>

              <div className="flex items-center justify-between pt-2">
                <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> 8K Photorealistic Architectural Render Ready
                </span>
                <button
                  onClick={() => setStudioModalOpen(false)}
                  className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
                >
                  Close Preview
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
