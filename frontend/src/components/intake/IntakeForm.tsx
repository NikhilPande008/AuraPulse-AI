"use client";

import React from "react";
import {
  Calendar,
  Globe,
  IndianRupee,
  Loader2,
  MapPin,
  Palette,
  Sliders,
  Sparkles,
  Users,
} from "lucide-react";
import { tomorrow } from "@/lib/dates";

interface IntakeFormProps {
  eventType: string;
  setEventType: (v: string) => void;
  eventDate: string;
  setEventDate: (v: string) => void;
  headcount: number;
  setHeadcount: (v: number) => void;
  locality: string;
  setLocality: (v: string) => void;
  budget: number;
  setBudget: (v: number) => void;
  cultureRegion: string;
  setCultureRegion: (v: string) => void;
  theme: string;
  setTheme: (v: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  onFieldChange: () => void;
}

export default function IntakeForm({
  eventType,
  setEventType,
  eventDate,
  setEventDate,
  headcount,
  setHeadcount,
  locality,
  setLocality,
  budget,
  setBudget,
  cultureRegion,
  setCultureRegion,
  theme,
  setTheme,
  onSubmit,
  isLoading,
  onFieldChange,
}: IntakeFormProps) {
  const tomorrowStr = tomorrow();

  const handleInputChange = <T,>(setter: (v: T) => void, val: T) => {
    setter(val);
    onFieldChange();
  };

  return (
    <fieldset className="space-y-4">
      <legend className="sr-only">Event Parameters & Live Tuning</legend>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
          <Sliders className="w-3.5 h-3.5 text-cyan-400" aria-hidden="true" />
          Event Parameters & Live Tuning
        </span>
        <span className="text-xs text-slate-400 font-mono">
          Changes trigger live Gemini re-generation
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Typology */}
        <div>
          <label
            htmlFor="event-type-select"
            className="block text-xs font-mono text-slate-400 mb-1"
          >
            Event Typology
          </label>
          <select
            id="event-type-select"
            value={eventType}
            onChange={(e) => handleInputChange(setEventType, e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500 font-mono"
          >
            <option value="wedding">Wedding</option>
            <option value="birthday">Birthday</option>
            <option value="community_festival">Community Festival / Mela</option>
            <option value="community_event">Community Event</option>
          </select>
        </div>

        {/* Target Event Date */}
        <div>
          <label htmlFor="event-date-input" className="block text-xs font-mono text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3 text-purple-400" aria-hidden="true" /> Target Event Date
            </span>
          </label>
          <input
            id="event-date-input"
            type="date"
            min={tomorrowStr}
            value={eventDate}
            onChange={(e) => handleInputChange(setEventDate, e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500 font-mono cursor-pointer"
          />
        </div>

        {/* Headcount */}
        <div>
          <label htmlFor="headcount-input" className="block text-xs font-mono text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <Users className="w-3 h-3 text-cyan-400" aria-hidden="true" /> Headcount (Guests)
            </span>
          </label>
          <input
            id="headcount-input"
            type="number"
            min={10}
            max={5000}
            step={10}
            value={headcount}
            onChange={(e) => handleInputChange(setHeadcount, Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500 font-mono"
          />
        </div>

        {/* Locality */}
        <div>
          <label htmlFor="locality-input" className="block text-xs font-mono text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3 text-emerald-400" aria-hidden="true" /> City / Locality
            </span>
          </label>
          <input
            id="locality-input"
            type="text"
            value={locality}
            onChange={(e) => handleInputChange(setLocality, e.target.value)}
            placeholder="Pune, Mumbai, Nashik..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Budget */}
        <div>
          <label htmlFor="budget-input" className="block text-xs font-mono text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <IndianRupee className="w-3 h-3 text-amber-400" aria-hidden="true" /> Total Budget
              (INR)
            </span>
          </label>
          <input
            id="budget-input"
            type="number"
            min={50000}
            max={50000000}
            step={25000}
            value={budget}
            onChange={(e) => handleInputChange(setBudget, Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500 font-mono"
          />
        </div>

        {/* Culture / Region */}
        <div>
          <label htmlFor="culture-input" className="block text-xs font-mono text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <Globe className="w-3 h-3 text-indigo-400" aria-hidden="true" /> Culture / Rituals
            </span>
          </label>
          <input
            id="culture-input"
            type="text"
            value={cultureRegion}
            onChange={(e) => handleInputChange(setCultureRegion, e.target.value)}
            placeholder="e.g. Maharashtrian / Contemporary"
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Theme */}
        <div className="col-span-2">
          <label htmlFor="theme-input" className="block text-xs font-mono text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <Palette className="w-3 h-3 text-pink-400" aria-hidden="true" /> Aesthetic Theme &
              Color Palette
            </span>
          </label>
          <input
            id="theme-input"
            type="text"
            value={theme}
            onChange={(e) => handleInputChange(setTheme, e.target.value)}
            placeholder="e.g. Royal Marigold & Terracotta, Violet Cyberpunk..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p className="text-xs text-slate-400 font-mono">
          Calculates backwards roadmap dates, multi-tier BOQ itemization, and run-of-show.
        </p>

        <button
          type="button"
          onClick={onSubmit}
          disabled={isLoading}
          className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-600/30 transition-all cursor-pointer disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:outline-none"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
              <span>Architecting Plan via Gemini 2.5...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" aria-hidden="true" />
              <span>Generate Custom Plan via Gemini 2.5 Flash</span>
            </>
          )}
        </button>
      </div>
    </fieldset>
  );
}
