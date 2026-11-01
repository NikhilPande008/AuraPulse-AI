"use client";

import React from "react";
import { Sparkles, X } from "lucide-react";
import type { StudioResponse } from "../../types/plan";

interface StudioModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: StudioResponse | null;
}

export default function StudioModal({ isOpen, onClose, result }: StudioModalProps) {
  if (!isOpen || !result) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="studio-modal-title"
      className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4"
    >
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative animate-fadeIn">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors cursor-pointer"
          aria-label="Close studio rendering"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 id="studio-modal-title" className="text-lg font-bold text-white">
            {result.is_generated
              ? "Google Imagen 3 Architectural Render"
              : "Sample Reference Image"}
          </h3>
        </div>

        <div className="relative aspect-video w-full rounded-xl overflow-hidden border border-slate-800">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={result.image_url} alt={result.prompt} className="w-full h-full object-cover" />
        </div>

        <div className="space-y-1 font-mono text-xs">
          <p className="text-slate-300">
            <strong className="text-white">Prompt: </strong>
            {result.prompt}
          </p>
          <p className="text-slate-400">
            <strong className="text-slate-300">Source: </strong>
            {result.source || "Google Imagen 3"}
          </p>
          {result.error && <p className="text-amber-400/90 text-xs mt-1">{result.error}</p>}
        </div>
      </div>
    </div>
  );
}
