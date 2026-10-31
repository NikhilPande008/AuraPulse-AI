"use client";

import React, { useState } from "react";
import {
  Upload,
  Sparkles,
  Sliders,
  MapPin,
  Users,
  IndianRupee,
  Zap,
  CheckCircle2,
  Camera,
  X,
  Loader2,
  Calendar,
  Globe,
  Palette,
  AlertCircle,
} from "lucide-react";
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
    badge: "Sample Plan • Wedding",
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
    badge: "Sample Plan • Birthday",
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
    badge: "Sample Plan • Community",
    thumbnail: "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=600&q=80",
    description: "Marigold yellow & clay tones, zero-plastic food stalls, solar festoons, authentic Dhol Tasha troupe.",
    tags: ["Pune Courtyard", "800 Pax", "₹5 Lakhs", "Zero Plastic Mela"]
  }
];

export default function MoodboardUploader({ onPlanLoaded, isLoading, setIsLoading }: MoodboardUploaderProps) {
  const tomorrowStr = new Date(Date.now() + 86400000).toISOString().split("T")[0];
  const [activePresetId, setActivePresetId] = useState<string | null>(DEMO_PRESETS[0].id);
  const [selectedPreset, setSelectedPreset] = useState(DEMO_PRESETS[0]);
  const [headcount, setHeadcount] = useState(DEMO_PRESETS[0].headcount);
  const [locality, setLocality] = useState(DEMO_PRESETS[0].city);
  const [budget, setBudget] = useState(DEMO_PRESETS[0].budget);
  const [eventType, setEventType] = useState(DEMO_PRESETS[0].type);
  const [eventDate, setEventDate] = useState("2026-11-15");
  const [cultureRegion, setCultureRegion] = useState("Maharashtrian / Contemporary");
  const [theme, setTheme] = useState("Pastel Peach & Sage");
  const [customImageBase64, setCustomImageBase64] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [isRenderingStudio, setIsRenderingStudio] = useState(false);
  const [studioModalOpen, setStudioModalOpen] = useState(false);
  const [studioResult, setStudioResult] = useState<{
    image_url: string;
    prompt: string;
    model: string | null;
    status?: string;
    is_generated?: boolean;
    source?: string;
    error?: string | null;
  } | null>(null);

  const [generationError, setGenerationError] = useState<{
    code?: string;
    message: string;
  } | null>(null);

  const clearPresetHighlight = () => {
    setActivePresetId(null);
    setGenerationError(null);
  };

  const handleGenerateVisualConcept = async () => {
    setIsRenderingStudio(true);
    setGenerationError(null);
    try {
      const res = await renderStudioAlternative(
        `${selectedPreset.name} featuring ${selectedPreset.description}`,
        selectedPreset.name
      );
      setStudioResult(res);
      setStudioModalOpen(true);
    } catch (err: any) {
      console.error(err);
      setGenerationError({
        code: "STUDIO_FAILED",
        message: "Generative studio rendering encountered an issue.",
      });
    } finally {
      setIsRenderingStudio(false);
    }
  };

  const triggerHydration = async (
    presetId?: string,
    hCount?: number,
    loc?: string,
    bLimit?: number,
    eType?: string,
    imgB64?: string,
    eDate?: string,
    cRegion?: string,
    eTheme?: string
  ) => {
    setIsLoading(true);
    setGenerationError(null);
    try {
      const plan = await deconstructMoodboard({
        image_base64: imgB64 || undefined,
        moodboard_preset: presetId,
        headcount: hCount ?? headcount,
        city: loc ?? locality,
        budget: bLimit ?? budget,
        event_type: eType ?? eventType,
        event_date: eDate || eventDate,
        culture_region: cRegion || cultureRegion,
        theme: eTheme || theme,
      });
      onPlanLoaded(plan);
    } catch (err: any) {
      console.error(err);
      setGenerationError({
        code: err?.code || (err?.message?.includes("503") ? "GENERATION_FAILED" : undefined),
        message: err?.message || "Failed to generate event plan via Gemini. Please retry or choose a preset.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePresetSelect = async (preset: typeof DEMO_PRESETS[0]) => {
    setActivePresetId(preset.id);
    setSelectedPreset(preset);
    setHeadcount(preset.headcount);
    setLocality(preset.city);
    setBudget(preset.budget);
    setEventType(preset.type);
    setCustomImageBase64(null);
    setGenerationError(null);
    // Instant One-Click Hydration for Competition Evaluation
    await triggerHydration(
      preset.id,
      preset.headcount,
      preset.city,
      preset.budget,
      preset.type,
      undefined,
      eventDate,
      cultureRegion,
      theme
    );
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        setCustomImageBase64(result);
        clearPresetHighlight();
        triggerHydration(undefined, headcount, locality, budget, eventType, result, eventDate, cultureRegion, theme);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleManualDeconstruct = async () => {
    // The main button ALWAYS routes to Gemini with moodboard_preset undefined
    clearPresetHighlight();
    await triggerHydration(
      undefined,
      headcount,
      locality,
      budget,
      eventType,
      customImageBase64 || undefined,
      eventDate,
      cultureRegion,
      theme
    );
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-800 space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide bg-purple-500/10 text-purple-400 border border-purple-500/20 uppercase font-mono">
              Agent 3.A • Multimodal Intake
            </span>
            <span className="text-xs text-slate-400 font-mono">Gemini 2.5 Flash Vision</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Aura Vision-to-BOQ Engine</h2>
          <p className="text-xs text-slate-400">
            Click any instant demo preset below or customize fields to generate live with Gemini 2.5 Flash.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={handleGenerateVisualConcept}
            disabled={isRenderingStudio}
            className="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-750 text-indigo-300 hover:text-white border border-indigo-500/40 text-xs font-semibold shadow-md transition-all disabled:opacity-50 cursor-pointer focus-visible:ring-2 focus-visible:ring-indigo-400"
          >
            {isRenderingStudio ? (
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" aria-hidden="true" />
            ) : (
              <Camera className="w-4 h-4 text-indigo-400" aria-hidden="true" />
            )}
            <span>{isRenderingStudio ? "Rendering Scene..." : "✨ Imagen 3 Studio"}</span>
          </button>

          <button
            type="button"
            onClick={handleManualDeconstruct}
            disabled={isLoading}
            className="relative inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-500 text-white font-semibold text-xs shadow-lg shadow-purple-600/30 hover:shadow-purple-600/50 hover:brightness-110 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shrink-0 focus-visible:ring-2 focus-visible:ring-purple-400"
          >
            <Sparkles className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} aria-hidden="true" />
            <span>{isLoading ? "Generating plan…" : "Generate plan with Gemini ✨"}</span>
          </button>
        </div>
      </div>

      {/* Inline Alert / Error Notice */}
      {generationError && (
        <div
          role="alert"
          className="p-4 rounded-xl bg-rose-950/70 border border-rose-500/50 text-rose-200 text-xs space-y-2 animate-fadeIn"
        >
          <div className="flex items-center gap-2 font-semibold">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" aria-hidden="true" />
            <span>{generationError.message}</span>
          </div>
          <div className="flex items-center gap-3 pt-1">
            <button
              type="button"
              onClick={handleManualDeconstruct}
              className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs transition-colors focus-visible:ring-2 focus-visible:ring-white cursor-pointer"
            >
              Try again
            </button>
            <button
              type="button"
              onClick={() => handlePresetSelect(DEMO_PRESETS[0])}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 font-medium text-xs border border-slate-700 transition-colors focus-visible:ring-2 focus-visible:ring-white cursor-pointer"
            >
              Load sample plan ({DEMO_PRESETS[0].name})
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Instant One-Click Demo Presets */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-mono font-medium text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
              One-Click Presets (Pre-calibrated Sample Plans)
            </label>
            <span className="text-xs text-emerald-400 font-mono bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">
              ⚡ Instant Sample Plan
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {DEMO_PRESETS.map((preset) => {
              const isSelected = activePresetId === preset.id;
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
                      <span className="text-xs font-mono uppercase px-2 py-0.5 rounded-full bg-slate-950/90 text-cyan-300 font-bold border border-cyan-800/60 shadow">
                        {preset.badge}
                      </span>
                    </div>
                  </div>

                  <div className="p-3 flex-1 flex flex-col justify-between">
                    <div>
                      <p className="text-xs font-bold text-white leading-tight group-hover:text-purple-300 transition-colors">
                        {preset.name}
                      </p>
                      <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                        {preset.description}
                      </p>
                    </div>

                    <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                      <span className="text-purple-300 font-bold">₹{(preset.budget / 100000).toFixed(1)}L</span>
                      <span className="text-slate-400">{preset.headcount} Pax</span>
                      <span className="text-cyan-400 font-medium">{preset.city}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Multimodal File Drop Zone */}
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
                  clearPresetHighlight();
                  triggerHydration(undefined, headcount, locality, budget, eventType, result, eventDate, cultureRegion, theme);
                };
                reader.readAsDataURL(file);
              }
            }}
            className={`relative rounded-xl border-2 border-dashed p-4 text-center transition-all ${
              dragActive ? "border-purple-400 bg-purple-950/20" : "border-slate-800 hover:border-slate-700 bg-slate-900/40"
            }`}
          >
            {customImageBase64 ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <img src={customImageBase64} alt="Custom upload" className="h-10 w-14 object-cover rounded-lg border border-purple-500/50" />
                  <div className="text-left">
                    <p className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" /> Custom Mood Board Parsed
                    </p>
                    <p className="text-xs text-slate-400 font-mono">Multimodal Vision buffer ingested by Gemini 2.5 Flash</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setCustomImageBase64(null)}
                  className="text-xs text-rose-400 hover:underline px-2 py-1 cursor-pointer"
                >
                  Reset
                </button>
              </div>
            ) : (
              <label
                htmlFor="moodboard-file-input"
                tabIndex={0}
                role="button"
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    document.getElementById("moodboard-file-input")?.click();
                  }
                }}
                className="cursor-pointer block focus-visible:ring-2 focus-visible:ring-purple-400 rounded-lg p-2"
              >
                <Upload className="w-5 h-5 mx-auto text-slate-400 mb-1" aria-hidden="true" />
                <span className="text-xs text-slate-300 font-medium">Or upload custom mood board (JPG/PNG/WebP)</span>
                <span className="block text-xs text-slate-400 font-mono mt-0.5">Extracts lighting, floristry, and scale</span>
                <input
                  id="moodboard-file-input"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFileUpload}
                  className="sr-only"
                />
              </label>
            )}
          </div>
        </div>

        {/* Constraints & Parameters */}
        <div className="lg:col-span-5 bg-slate-900/60 rounded-xl p-4 border border-slate-800/80 space-y-3.5">
          <label className="text-xs font-mono font-medium text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" aria-hidden="true" />
            Budget & Intake Parameters
          </label>
          <p className={`text-xs font-mono px-2 py-1 rounded border ${
            activePresetId
              ? "text-amber-300 bg-amber-950/40 border-amber-800/60"
              : "text-emerald-300 bg-emerald-950/40 border-emerald-800/60"
          }`}>
            {activePresetId
              ? `Sample preset active: ${selectedPreset.name}. Edit any field to generate live via Gemini.`
              : "Custom parameters active: click 'Generate plan with Gemini' to generate."}
          </p>

          {/* Event Date & Locality */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="event-date-input" className="text-xs text-slate-400 flex items-center gap-1 mb-1 font-mono cursor-pointer">
                <Calendar className="w-3 h-3 text-cyan-400" aria-hidden="true" /> Event Date
              </label>
              <input
                id="event-date-input"
                type="date"
                min={tomorrowStr}
                value={eventDate}
                onChange={(e) => { setEventDate(e.target.value); clearPresetHighlight(); }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label htmlFor="locality-input" className="text-xs text-slate-400 flex items-center gap-1 mb-1 font-mono cursor-pointer">
                <MapPin className="w-3 h-3 text-cyan-400" aria-hidden="true" /> Locality / City
              </label>
              <input
                id="locality-input"
                type="text"
                value={locality}
                onChange={(e) => { setLocality(e.target.value); clearPresetHighlight(); }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>
          </div>

          {/* Culture / Region & Aesthetic Theme */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="culture-input" className="text-xs text-slate-400 flex items-center gap-1 mb-1 font-mono cursor-pointer">
                <Globe className="w-3 h-3 text-indigo-400" aria-hidden="true" /> Culture / Region
              </label>
              <input
                id="culture-input"
                type="text"
                placeholder="e.g. Maharashtrian"
                value={cultureRegion}
                onChange={(e) => { setCultureRegion(e.target.value); clearPresetHighlight(); }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label htmlFor="theme-input" className="text-xs text-slate-400 flex items-center gap-1 mb-1 font-mono cursor-pointer">
                <Palette className="w-3 h-3 text-indigo-400" aria-hidden="true" /> Theme / Aesthetic
              </label>
              <input
                id="theme-input"
                type="text"
                placeholder="e.g. Pastel Meadow"
                value={theme}
                onChange={(e) => { setTheme(e.target.value); clearPresetHighlight(); }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>
          </div>

          {/* Headcount */}
          <div>
            <label htmlFor="headcount-input" className="text-xs text-slate-400 flex items-center gap-1 mb-1 font-mono cursor-pointer">
              <Users className="w-3 h-3 text-cyan-400" aria-hidden="true" /> Headcount (Pax: 1 to 10,000)
            </label>
            <input
              id="headcount-input"
              type="number"
              min="1"
              max="10000"
              value={headcount}
              onChange={(e) => { setHeadcount(Number(e.target.value)); clearPresetHighlight(); }}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:border-purple-500 focus:outline-none font-mono"
            />
          </div>

          {/* Budget Ceiling Input & Slider (₹20,000 to ₹5,00,00,000) */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label htmlFor="budget-input" className="text-xs text-slate-400 flex items-center gap-1 font-mono cursor-pointer">
                <IndianRupee className="w-3 h-3 text-cyan-400" aria-hidden="true" /> Budget Ceiling (INR)
              </label>
              <input
                id="budget-input"
                type="number"
                min="20000"
                max="50000000"
                step="5000"
                value={budget}
                onChange={(e) => { setBudget(Math.max(0, Number(e.target.value))); clearPresetHighlight(); }}
                className="w-32 bg-slate-950 border border-slate-800 rounded px-2 py-0.5 text-right text-xs font-mono font-bold text-purple-300 focus:border-purple-500 focus:outline-none"
              />
            </div>
            <input
              id="budget-slider"
              type="range"
              min="20000"
              max="50000000"
              step="25000"
              value={Math.min(budget, 50000000)}
              onChange={(e) => { setBudget(Number(e.target.value)); clearPresetHighlight(); }}
              className="w-full accent-purple-500 cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-400 font-mono">
              <span>₹20 Thousand</span>
              <span>₹2.5 Crores</span>
              <span>₹5 Crores</span>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-800/80">
            <span className="text-xs text-slate-400 font-mono block mb-1">Event Typology</span>
            <div className="grid grid-cols-3 gap-2">
              {["wedding", "birthday", "community_festival"].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => { setEventType(type); clearPresetHighlight(); }}
                  className={`text-xs py-1 px-2 rounded capitalize font-medium transition-all cursor-pointer ${
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
                  <Camera className="w-4 h-4" aria-hidden="true" />
                </span>
                <div>
                  <h3 className="text-sm font-bold text-white">Generative Visual Concept</h3>
                  <p className="text-xs font-mono text-indigo-300">
                    {studioResult.is_generated
                      ? `Google Imagen 3 (${studioResult.model})`
                      : "Sample preview — stock reference photo (not AI-generated)"}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setStudioModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" aria-hidden="true" />
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
                <span className="text-xs font-mono uppercase text-slate-400 block mb-1">
                  Concept Prompt:
                </span>
                <p className="text-xs text-slate-200 font-sans leading-relaxed">
                  "{studioResult.prompt}"
                </p>
              </div>

              {studioResult.error && (
                <p className="text-xs font-mono text-amber-400/90 bg-amber-950/30 px-3 py-1.5 rounded border border-amber-900/50">
                  ℹ {studioResult.error}
                </p>
              )}
            </div>

            <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
              <button
                type="button"
                onClick={() => setStudioModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors cursor-pointer"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
