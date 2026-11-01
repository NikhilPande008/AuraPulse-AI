"use client";

import React, { useState } from "react";
import { AlertCircle, Camera, Loader2, Sparkles } from "lucide-react";
import { defaultEventDate } from "@/lib/dates";
import { deconstructMoodboard, renderStudioAlternative } from "../lib/api";
import { reportError } from "../lib/client";
import type { MasterEventPlan, StudioResponse } from "../types/plan";
import ImageDropzone from "./intake/ImageDropzone";
import IntakeForm from "./intake/IntakeForm";
import type { DemoPreset } from "./intake/PresetSelector";
import PresetSelector, { DEMO_PRESETS } from "./intake/PresetSelector";
import StudioModal from "./intake/StudioModal";

export { DEMO_PRESETS };

interface MoodboardUploaderProps {
  onPlanLoaded: (plan: MasterEventPlan) => void;
  isLoading: boolean;
  setIsLoading: (val: boolean) => void;
}

export default function MoodboardUploader({
  onPlanLoaded,
  isLoading,
  setIsLoading,
}: MoodboardUploaderProps) {
  const [activePresetId, setActivePresetId] = useState<string | null>(DEMO_PRESETS[0].id);
  const [selectedPreset, setSelectedPreset] = useState<DemoPreset>(DEMO_PRESETS[0]);
  const [headcount, setHeadcount] = useState(DEMO_PRESETS[0].headcount);
  const [locality, setLocality] = useState(DEMO_PRESETS[0].city);
  const [budget, setBudget] = useState(DEMO_PRESETS[0].budget);
  const [eventType, setEventType] = useState(DEMO_PRESETS[0].type);
  const [eventDate, setEventDate] = useState(defaultEventDate());
  const [cultureRegion, setCultureRegion] = useState("Maharashtrian / Contemporary");
  const [theme, setTheme] = useState("Pastel Peach & Sage");
  const [customImageBase64, setCustomImageBase64] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [isRenderingStudio, setIsRenderingStudio] = useState(false);
  const [studioModalOpen, setStudioModalOpen] = useState(false);
  const [studioResult, setStudioResult] = useState<StudioResponse | null>(null);
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
    } catch (err: unknown) {
      reportError(err, "MoodboardUploader");
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
    } catch (err: unknown) {
      reportError(err, "MoodboardUploader");
      const errorObj = err as { code?: string; message?: string };
      setGenerationError({
        code:
          errorObj?.code || (errorObj?.message?.includes("503") ? "GENERATION_FAILED" : undefined),
        message:
          errorObj?.message ||
          "Failed to generate event plan via Gemini. Please retry or choose a preset.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePresetSelect = async (preset: DemoPreset) => {
    setActivePresetId(preset.id);
    setSelectedPreset(preset);
    setHeadcount(preset.headcount);
    setLocality(preset.city);
    setBudget(preset.budget);
    setEventType(preset.type);
    setCustomImageBase64(null);
    setGenerationError(null);
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

  const handleCustomImage = (base64: string | null) => {
    setCustomImageBase64(base64);
    clearPresetHighlight();
    if (base64) {
      triggerHydration(
        undefined,
        headcount,
        locality,
        budget,
        eventType,
        base64,
        eventDate,
        cultureRegion,
        theme
      );
    }
  };

  const handleManualDeconstruct = async () => {
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
            Click any instant demo preset below or customize fields to generate live with Gemini 2.5
            Flash.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={handleGenerateVisualConcept}
            disabled={isRenderingStudio}
            className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-purple-500/40 text-purple-300 hover:text-white text-xs font-mono font-semibold flex items-center gap-2 transition-all cursor-pointer shadow-md disabled:opacity-50"
          >
            {isRenderingStudio ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-400" aria-hidden="true" />
                <span>Imagen 3 Rendering...</span>
              </>
            ) : (
              <>
                <Camera className="w-3.5 h-3.5 text-purple-400" aria-hidden="true" />
                <span>Imagen 3 Decor Render</span>
              </>
            )}
          </button>
        </div>
      </div>

      {generationError && (
        <div
          role="alert"
          aria-live="assertive"
          className="p-4 rounded-xl bg-red-950/60 border border-red-500/50 flex items-start gap-3 text-red-200 animate-fadeIn"
        >
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" aria-hidden="true" />
          <div className="flex-1 text-xs">
            <p className="font-bold text-red-100">
              {generationError.code === "GENERATION_FAILED"
                ? "Gemini Plan Generation Failed"
                : "Generation Error"}
            </p>
            <p className="mt-0.5 text-red-300 leading-relaxed">{generationError.message}</p>
          </div>
          <button
            type="button"
            onClick={handleManualDeconstruct}
            className="px-3 py-1.5 rounded-lg bg-red-800/80 hover:bg-red-700 text-white text-xs font-semibold cursor-pointer shrink-0 transition-colors"
          >
            Retry Gemini
          </button>
        </div>
      )}

      {/* Preset Cards */}
      <PresetSelector
        activePresetId={activePresetId}
        onSelect={handlePresetSelect}
        isLoading={isLoading}
      />

      {/* Custom Image Dropzone */}
      <ImageDropzone
        customImageBase64={customImageBase64}
        onImageSelected={handleCustomImage}
        dragActive={dragActive}
        setDragActive={setDragActive}
      />

      {/* Input Tuning Parameters */}
      <IntakeForm
        eventType={eventType}
        setEventType={setEventType}
        eventDate={eventDate}
        setEventDate={setEventDate}
        headcount={headcount}
        setHeadcount={setHeadcount}
        locality={locality}
        setLocality={setLocality}
        budget={budget}
        setBudget={setBudget}
        cultureRegion={cultureRegion}
        setCultureRegion={setCultureRegion}
        theme={theme}
        setTheme={setTheme}
        onSubmit={handleManualDeconstruct}
        isLoading={isLoading}
        onFieldChange={clearPresetHighlight}
      />

      {/* Studio Modal */}
      <StudioModal
        isOpen={studioModalOpen}
        onClose={() => setStudioModalOpen(false)}
        result={studioResult}
      />
    </div>
  );
}
