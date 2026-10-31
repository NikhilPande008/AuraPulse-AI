"use client";

import React, { useState, useEffect } from "react";
import MoodboardUploader from "../components/MoodboardUploader";
import BoqTable from "../components/BoqTable";
import ContingencyControls from "../components/ContingencyControls";
import DiffVisualizer from "../components/DiffVisualizer";
import ScheduleTimeline from "../components/ScheduleTimeline";
import VendorFinder from "../components/VendorFinder";
import ExportActions from "../components/ExportActions";
import AICopilotBar from "../components/AICopilotBar";
import { MasterEventPlan, ContingencyDiff, FALLBACK_PRESET_1, VendorChecklistItem } from "../lib/api";
import { Activity, ShieldCheck, Zap, Layers, Sparkles, AlertCircle, RefreshCw, WifiOff } from "lucide-react";

export default function Dashboard() {
  const [currentPlan, setCurrentPlan] = useState<MasterEventPlan>(FALLBACK_PRESET_1);
  const [baselinePlan, setBaselinePlan] = useState<MasterEventPlan>(FALLBACK_PRESET_1);
  const [activeDiff, setActiveDiff] = useState<ContingencyDiff | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isOfflineFallback, setIsOfflineFallback] = useState(false);
  const [activeTab, setActiveTab] = useState<"boq" | "schedule" | "vendors" | "export">("boq");

  // Initial load: deconstruct baseline with 3s timeout
  useEffect(() => {
    const init = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      try {
        const res = await fetch("/api/v1/aura/deconstruct", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            moodboard_preset: "meadow_wedding",
            headcount: 300,
            locality: "Pune",
            budget_ceiling: 1500000,
            event_type: "wedding",
          }),
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
        if (res.ok) {
          const data = await res.json();
          setCurrentPlan(data);
          setBaselinePlan(data);
          setIsOfflineFallback(false);
        } else {
          console.warn("Backend responded with non-200. Activating embedded fallback.");
          setCurrentPlan(FALLBACK_PRESET_1);
          setBaselinePlan(FALLBACK_PRESET_1);
          setIsOfflineFallback(true);
        }
      } catch (err) {
        clearTimeout(timeoutId);
        console.warn("Initial hydration timed out or network blocked. Activating embedded fallback.", err);
        setCurrentPlan(FALLBACK_PRESET_1);
        setBaselinePlan(FALLBACK_PRESET_1);
        setIsOfflineFallback(true);
      }
    };
    init();
  }, []);

  const handlePlanLoaded = (plan: MasterEventPlan) => {
    setCurrentPlan(plan);
    setBaselinePlan(plan);
    setActiveDiff(null); // Reset active diff on new baseline
  };

  const handleDiffGenerated = (diff: ContingencyDiff) => {
    setActiveDiff(diff);
    setCurrentPlan(diff.updated_plan); // Update state to reflected plan
  };

  const handleResetSimulation = () => {
    setActiveDiff(null);
    setCurrentPlan(baselinePlan);
  };

  const handleMilestoneToggle = (milestoneId: string) => {
    if (!currentPlan.planning_milestones) return;
    const updatedMilestones = currentPlan.planning_milestones.map((m) =>
      m.id === milestoneId ? { ...m, completed: !m.completed } : m
    );
    setCurrentPlan({ ...currentPlan, planning_milestones: updatedMilestones });
  };

  const handleChecklistUpdate = (updatedChecklist: VendorChecklistItem[]) => {
    setCurrentPlan({ ...currentPlan, vendor_checklist: updatedChecklist });
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Top Banner / System Status Ribbon */}
      <div className="glass-card rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="h-3 w-3 rounded-full bg-emerald-400 animate-ping"></div>
          <span className="text-xs font-mono font-semibold text-white">
            System Topology: 5 Architectural Layers Active
          </span>
          <span className="text-xs text-slate-400 hidden sm:inline">•</span>
          <span className="text-xs text-slate-400 hidden sm:inline">
            Vertex AI / Google GenAI SDK Cluster Connected
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="px-2 py-0.5 rounded bg-purple-950 border border-purple-800/60 text-purple-300">
            Gemini 2.5 Flash
          </span>
          <span className="px-2 py-0.5 rounded bg-indigo-950 border border-indigo-800/60 text-indigo-300">
            Gemini 2.5 Pro Reasoner
          </span>
          <span className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800/60 text-cyan-300">
            Places & Sheets Fabric
          </span>
        </div>
      </div>

      {/* Non-intrusive Offline / Preview Mode Badge */}
      {isOfflineFallback && (
        <div className="px-4 py-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between text-xs text-amber-300 font-mono">
          <div className="flex items-center gap-2">
            <WifiOff className="w-4 h-4 text-amber-400 shrink-0" />
            <span>Offline/Preview Mode Active: Displaying cached baseline (Preset 1 • Meadow Wedding).</span>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="hover:underline flex items-center gap-1 text-amber-200"
          >
            <RefreshCw className="w-3 h-3" /> Retry Sync
          </button>
        </div>
      )}

      {/* Layer 1: Aura Vision Multimodal Intake */}
      <section>
        <MoodboardUploader
          onPlanLoaded={handlePlanLoaded}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
        />
      </section>

      {/* Layer 2: GenAI Ideas & Budget Co-Pilot (Gemini 2.5 Flash) */}
      {currentPlan && (
        <section>
          <AICopilotBar
            plan={currentPlan}
            onPlanUpdate={handlePlanLoaded}
          />
        </section>
      )}

      {/* Layer 3: Pulse Reactive Contingency Engine Controls */}
      {currentPlan && (
        <section>
          <ContingencyControls
            plan={currentPlan}
            onDiffGenerated={handleDiffGenerated}
            isSimulating={isSimulating}
            setIsSimulating={setIsSimulating}
          />
        </section>
      )}

      {/* Layer 4: Reactive State Diff Visualizer (shown when a simulation is executed) */}
      {activeDiff && (
        <section className="animate-fadeIn">
          <DiffVisualizer diff={activeDiff} onReset={handleResetSimulation} />
        </section>
      )}

      {/* Layer 5: Interactive Workspaces Tabs (BOQ, Schedule, Vendors, Google Export) */}
      {currentPlan && (
        <section className="space-y-4">
          <div className="flex items-center border-b border-slate-800 gap-2">
            <button
              onClick={() => setActiveTab("boq")}
              className={`px-4 py-2.5 text-xs font-bold font-mono transition-all border-b-2 cursor-pointer ${
                activeTab === "boq"
                  ? "border-purple-500 text-purple-300 bg-purple-500/10 rounded-t-lg"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Master BOQ ({currentPlan.boq.length} Items)
            </button>
            <button
              onClick={() => setActiveTab("schedule")}
              className={`px-4 py-2.5 text-xs font-bold font-mono transition-all border-b-2 cursor-pointer ${
                activeTab === "schedule"
                  ? "border-indigo-500 text-indigo-300 bg-indigo-500/10 rounded-t-lg"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Milestones & Timeline ({currentPlan.planning_milestones?.length || 0} Milestones • {currentPlan.schedule.length} Blocks)
            </button>
            <button
              onClick={() => setActiveTab("vendors")}
              className={`px-4 py-2.5 text-xs font-bold font-mono transition-all border-b-2 cursor-pointer ${
                activeTab === "vendors"
                  ? "border-cyan-500 text-cyan-300 bg-cyan-500/10 rounded-t-lg"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Vendor Action Center ({currentPlan.vendor_checklist?.length || 0} Checklist • {currentPlan.location_city})
            </button>
            <button
              onClick={() => setActiveTab("export")}
              className={`px-4 py-2.5 text-xs font-bold font-mono transition-all border-b-2 cursor-pointer ${
                activeTab === "export"
                  ? "border-emerald-500 text-emerald-300 bg-emerald-500/10 rounded-t-lg"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Google Workspace Exporter
            </button>
          </div>

          <div>
            {activeTab === "boq" && <BoqTable plan={currentPlan} />}
            {activeTab === "schedule" && (
              <ScheduleTimeline
                schedule={currentPlan.schedule}
                milestones={currentPlan.planning_milestones}
                onMilestoneToggle={handleMilestoneToggle}
              />
            )}
            {activeTab === "vendors" && (
              <VendorFinder
                city={currentPlan.location_city}
                checklist={currentPlan.vendor_checklist}
                onChecklistUpdate={handleChecklistUpdate}
              />
            )}
            {activeTab === "export" && <ExportActions plan={currentPlan} />}
          </div>
        </section>
      )}
    </div>
  );
}
