"use client";

import React, { useState } from "react";
import {
  Sparkles,
  Send,
  Loader2,
  Lightbulb,
  CheckCircle2,
  MessageSquare,
  ArrowRight,
  RefreshCw,
} from "lucide-react";
import type { MasterEventPlan, CopilotResponse, ContingencyDiff } from "../lib/api";
import { chatCopilot } from "../lib/api";
import { reportError } from "../lib/client";
import InlineError from "./InlineError";

interface AICopilotBarProps {
  plan: MasterEventPlan;
  onPlanUpdate: (updatedPlan: MasterEventPlan) => void;
  onDiffGenerated?: (diff: ContingencyDiff) => void;
}

export default function AICopilotBar({ plan, onPlanUpdate, onDiffGenerated }: AICopilotBarProps) {
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<CopilotResponse | null>(null);
  const [history, setHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const quickPrompts = [
    { label: "📉 Cut Budget by 20%", query: "Cut budget by 20% across non-critical items" },
    {
      label: "🍽️ Authentic Puneri Cuisine",
      query: "Switch catering to authentic Puneri Maharashtrian cuisine with Puran Poli and Modaks",
    },
    {
      label: "🎷 Cut Florals 20% & Add Sax",
      query: "Cut floral decor by 20% and add a live solo saxophonist for the sunset hour",
    },
    { label: "🌿 मेनू शाकाहारी करा", query: "मेनू पूर्णपणे शाकाहारी करा आणि पुरणपोळी जोडा" },
    {
      label: "🎮 5 Interactive Party Games",
      query: "Suggest 5 high-energy interactive games and add a Game Master coordinator",
    },
    {
      label: "🪔 Sakhar Puda & Pre-Ceremony Rituals",
      query: "Add Sakhar Puda pre-ceremony rituals and pooja samagri audit to timeline",
    },
  ];

  const handleSendPrompt = async (queryText?: string) => {
    const textToSend = queryText || prompt;
    if (!textToSend.trim() || isLoading) return;

    setIsLoading(true);
    setErrorMsg(null);
    const updatedHistory = [...history, { role: "user", content: textToSend }].slice(-6);
    try {
      const res = await chatCopilot(plan, textToSend, updatedHistory);
      setLastResponse(res);
      if (res.copilot_reply) {
        setHistory([...updatedHistory, { role: "model", content: res.copilot_reply }].slice(-6));
      }
      if (res.updated_plan) {
        onPlanUpdate(res.updated_plan);
      }
      if (res.diff && onDiffGenerated) {
        onDiffGenerated(res.diff);
      }
      setPrompt("");
    } catch (err: unknown) {
      reportError(err, "AICopilotBar");
      setErrorMsg("Co-Pilot encountered an issue. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl border border-indigo-500/30 bg-gradient-to-br from-indigo-950/40 via-slate-900/60 to-purple-950/40">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4 pb-3 border-b border-indigo-500/20">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase font-mono flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-indigo-400" />
              GenAI Ideas & Budget Co-Pilot
            </span>
            <span className="text-xs text-indigo-300/70 font-mono">Gemini 2.5 Flash</span>
          </div>
          <h2 className="text-lg font-bold text-white mt-1 flex items-center gap-2">
            Conversational Event Architect
          </h2>
          <p className="text-xs text-slate-300">
            Converse directly with Gemini to adapt themes, swap regional menus, optimize line-item
            budgets, and brainstorm activities. Changes automatically mutate the live BOQ and
            timeline.
          </p>
        </div>

        {isLoading && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-500/20 border border-indigo-500/40 text-indigo-200 text-xs font-mono animate-pulse">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
            Gemini Reasoning & Recalculating Plan...
          </div>
        )}
      </div>

      {errorMsg && (
        <InlineError
          message={errorMsg}
          onRetry={() => handleSendPrompt()}
          onDismiss={() => setErrorMsg(null)}
          className="mb-4"
        />
      )}

      {/* Quick Prompt Chips */}
      <div
        className="flex items-center gap-2 mb-4 overflow-x-auto pb-1 scrollbar-thin"
        role="toolbar"
        aria-label="Co-Pilot quick suggestion prompts"
      >
        <span className="text-xs font-mono text-indigo-300/80 uppercase shrink-0">
          Quick Prompts:
        </span>
        {quickPrompts.map((qp, idx) => {
          const isDevanagari = /[\u0900-\u097F]/.test(qp.label);
          return (
            <button
              key={idx}
              type="button"
              lang={isDevanagari ? "mr" : undefined}
              onClick={() => handleSendPrompt(qp.query)}
              disabled={isLoading}
              className="shrink-0 text-xs px-3 py-1.5 rounded-full bg-slate-800/80 hover:bg-indigo-600/30 text-slate-200 hover:text-white border border-slate-700 hover:border-indigo-500/50 transition-all flex items-center gap-1.5 disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:outline-none"
            >
              {qp.label}
            </button>
          );
        })}
      </div>

      {/* Input Field */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendPrompt();
        }}
        className="flex items-center gap-2"
      >
        <div className="relative flex-1">
          <MessageSquare className="w-4 h-4 text-indigo-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="E.g., 'Switch menu to Marathi cuisine with Puran Poli', 'Trim floral budget by 20%', 'Suggest 5 games'..."
            disabled={isLoading}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-indigo-500/40 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-indigo-400 disabled:opacity-60 font-sans shadow-inner"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-sm flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          <span>Ask Co-Pilot</span>
        </button>
      </form>

      {/* Response Panel */}
      {lastResponse && (
        <div
          aria-live="polite"
          className="mt-4 p-4 rounded-xl bg-slate-900/90 border border-indigo-500/40 shadow-inner"
        >
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Sparkles className="w-3.5 h-3.5" />
              </span>
              <span className="text-xs font-semibold text-indigo-300 font-mono">
                AuraPulse Co-Pilot Response
              </span>
              {lastResponse.mode === "offline_rules" && (
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                  Offline rules mode (Gemini not configured)
                </span>
              )}
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Live BOQ & Plan Mutated
            </span>
          </div>

          <p
            lang={/[\u0900-\u097F]/.test(lastResponse.copilot_reply) ? "mr" : undefined}
            className="text-sm text-slate-200 leading-relaxed pl-8 pr-2 mb-3"
          >
            {lastResponse.copilot_reply}
          </p>

          {lastResponse.suggested_ideas && lastResponse.suggested_ideas.length > 0 && (
            <div className="pl-8 pt-2 border-t border-slate-800">
              <span className="text-xs font-mono font-medium text-amber-300/90 flex items-center gap-1.5 mb-2">
                <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
                Actionable Strategic Ideas & Innovations:
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {lastResponse.suggested_ideas.map((idea, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300"
                  >
                    <ArrowRight className="w-3 h-3 text-indigo-400 shrink-0 mt-0.5" />
                    <span>{idea}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
