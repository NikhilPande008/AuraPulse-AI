"use client";

import React from "react";
import { AlertCircle, RefreshCw, X } from "lucide-react";

interface InlineErrorProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export default function InlineError({
  message,
  onRetry,
  onDismiss,
  className = "",
}: InlineErrorProps) {
  if (!message) return null;

  return (
    <div
      role="alert"
      className={`px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-200 text-xs flex items-center justify-between gap-3 ${className}`}
    >
      <div className="flex items-center gap-2">
        <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
        <span>{message}</span>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="px-2.5 py-1 rounded bg-red-500/20 hover:bg-red-500/30 text-red-200 hover:text-white font-mono text-xs transition-colors flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        )}
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            aria-label="Dismiss alert"
            className="p-1 rounded hover:bg-red-500/20 text-red-300 hover:text-white transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
}
