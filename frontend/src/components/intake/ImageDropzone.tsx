"use client";

import React from "react";
import { Camera, Upload, X } from "lucide-react";

interface ImageDropzoneProps {
  customImageBase64: string | null;
  onImageSelected: (base64: string | null) => void;
  dragActive: boolean;
  setDragActive: (active: boolean) => void;
}

export default function ImageDropzone({
  customImageBase64,
  onImageSelected,
  dragActive,
  setDragActive,
}: ImageDropzoneProps) {
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        onImageSelected(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        onImageSelected(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div>
      <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2 mb-2">
        <Camera className="w-3.5 h-3.5 text-cyan-400" />
        Upload Custom Moodboard / Pinterest Reference (Optional)
      </label>

      {customImageBase64 ? (
        <div className="relative rounded-xl overflow-hidden border border-purple-500/50 bg-slate-900 p-2 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-16 w-16 relative rounded-lg overflow-hidden border border-slate-700 shrink-0">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={customImageBase64}
                alt="Custom Moodboard Upload"
                className="h-full w-full object-cover"
              />
            </div>
            <div>
              <p className="text-xs font-bold text-white">Custom Reference Image Active</p>
              <p className="text-xs text-slate-400">
                Gemini 2.5 Flash Vision will extract palette, decor elements & infrastructure.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => onImageSelected(null)}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer mr-2"
            title="Remove custom image"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-5 text-center transition-all cursor-pointer ${
            dragActive
              ? "border-purple-500 bg-purple-950/20"
              : "border-slate-800 hover:border-slate-700 bg-slate-900/30"
          }`}
        >
          <input
            type="file"
            id="moodboard-file"
            accept="image/*"
            onChange={handleFileInput}
            className="hidden"
          />
          <label htmlFor="moodboard-file" className="cursor-pointer block">
            <Upload className="w-6 h-6 mx-auto mb-2 text-slate-400" />
            <p className="text-xs font-semibold text-white">
              Drag & drop Pinterest moodboard or decor snapshot
            </p>
            <p className="text-xs text-slate-400 mt-0.5">Supports JPG, PNG, WEBP up to 4MB</p>
          </label>
        </div>
      )}
    </div>
  );
}
