"use client";

import React from "react";
import AICopilotBar from "../components/AICopilotBar";
import BoqTable from "../components/BoqTable";
import ContingencyControls from "../components/ContingencyControls";
import DiffVisualizer from "../components/DiffVisualizer";
import ExportActions from "../components/ExportActions";
import MoodboardUploader from "../components/MoodboardUploader";
import ScheduleTimeline from "../components/ScheduleTimeline";
import VendorFinder from "../components/VendorFinder";
import { usePlanState } from "../hooks/usePlanState";
import { RefreshCw, RotateCcw, WifiOff } from "lucide-react";

export default function Dashboard() {
  const {
    currentPlan,
    setCurrentPlan,
    activeDiff,
    eventDate,
    setEventDate,
    healthStatus,
    isLoading,
    setIsLoading,
    isSimulating,
    setIsSimulating,
    isOfflineFallback,
    activeTab,
    setActiveTab,
    liveAnnouncement,
    handleTabKeyDown,
    handlePlanLoaded,
    handleDiffGenerated,
    handleResetSimulation,
    handleResetToFreshPlan,
    handleMilestoneToggle,
    handleChecklistUpdate,
  } = usePlanState();

  return (
    <div className="space-y-8 pb-16">
      {/* Screen reader live announcements */}
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {liveAnnouncement}
      </div>

      {/* Clean Dynamic System Status Strip based on GET /api/health */}
      <div className="glass-card rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 border border-slate-800">
        <div className="flex items-center gap-3">
          <div
            className={`h-2.5 w-2.5 rounded-full ${healthStatus ? "bg-emerald-400" : "bg-amber-400"}`}
          ></div>
          <span className="text-xs font-mono font-semibold text-white">
            Backend: {healthStatus ? "Online" : "Unreachable"}
          </span>
          <span className="text-xs text-slate-400 hidden sm:inline">•</span>
          <span className="text-xs text-slate-400 font-mono hidden sm:inline">
            Version: {healthStatus?.version || process.env.NEXT_PUBLIC_APP_VERSION || "2.2.0"}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <span
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${
              healthStatus?.gemini_configured
                ? "bg-purple-950/60 border-purple-800/60 text-purple-300"
                : "bg-amber-950/40 border-amber-800/60 text-amber-300"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                healthStatus?.gemini_configured ? "bg-purple-400" : "bg-amber-400"
              }`}
            ></span>
            Gemini Flash: {healthStatus?.gemini_configured ? "Active" : "API Key Required"}
          </span>

          <span
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${
              healthStatus?.google_apis?.places_maps
                ? "bg-cyan-950/60 border-cyan-800/60 text-cyan-300"
                : "bg-slate-900 border-slate-800 text-slate-400"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                healthStatus?.google_apis?.places_maps ? "bg-cyan-400" : "bg-slate-500"
              }`}
            ></span>
            Places Grounding: {healthStatus?.google_apis?.places_maps ? "Ready" : "Inactive"}
          </span>

          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-emerald-300">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
            RFC-5545 Calendar: Ready
          </span>

          <button
            type="button"
            onClick={handleResetToFreshPlan}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition-colors cursor-pointer border border-slate-700"
            title="Reset to fresh default plan and clear browser storage"
          >
            <RotateCcw className="w-3 h-3" />
            Reset Plan
          </button>
        </div>
      </div>

      {/* Non-intrusive Offline / Preview Mode Badge */}
      {isOfflineFallback && (
        <div className="px-4 py-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between text-xs text-amber-300 font-mono">
          <div className="flex items-center gap-2">
            <WifiOff className="w-4 h-4 text-amber-400 shrink-0" />
            <span>
              Offline/Preview Mode Active: Displaying cached baseline (Preset 1 • Meadow Wedding).
            </span>
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

      {/* Layer 2: GenAI Ideas & Budget Co-Pilot */}
      {currentPlan && (
        <section>
          <AICopilotBar
            plan={currentPlan}
            onPlanUpdate={handlePlanLoaded}
            onDiffGenerated={handleDiffGenerated}
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
          <div
            role="tablist"
            aria-label="Event plan workspaces"
            onKeyDown={handleTabKeyDown}
            className="flex items-center border-b border-slate-800 gap-2"
          >
            <button
              role="tab"
              id="tab-workspace-boq"
              aria-controls="panel-workspace-boq"
              aria-selected={activeTab === "boq"}
              tabIndex={activeTab === "boq" ? 0 : -1}
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
              role="tab"
              id="tab-workspace-schedule"
              aria-controls="panel-workspace-schedule"
              aria-selected={activeTab === "schedule"}
              tabIndex={activeTab === "schedule" ? 0 : -1}
              onClick={() => setActiveTab("schedule")}
              className={`px-4 py-2.5 text-xs font-bold font-mono transition-all border-b-2 cursor-pointer ${
                activeTab === "schedule"
                  ? "border-indigo-500 text-indigo-300 bg-indigo-500/10 rounded-t-lg"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Milestones & Timeline ({currentPlan.planning_milestones?.length || 0} Milestones •{" "}
              {currentPlan.schedule.length} Blocks)
            </button>
            <button
              role="tab"
              id="tab-workspace-vendors"
              aria-controls="panel-workspace-vendors"
              aria-selected={activeTab === "vendors"}
              tabIndex={activeTab === "vendors" ? 0 : -1}
              onClick={() => setActiveTab("vendors")}
              className={`px-4 py-2.5 text-xs font-bold font-mono transition-all border-b-2 cursor-pointer ${
                activeTab === "vendors"
                  ? "border-cyan-500 text-cyan-300 bg-cyan-500/10 rounded-t-lg"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Vendor Action Center ({currentPlan.vendor_checklist?.length || 0} Checklist •{" "}
              {currentPlan.location_city})
            </button>
            <button
              role="tab"
              id="tab-workspace-export"
              aria-controls="panel-workspace-export"
              aria-selected={activeTab === "export"}
              tabIndex={activeTab === "export" ? 0 : -1}
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
            {activeTab === "boq" && (
              <div id="panel-workspace-boq" role="tabpanel" aria-labelledby="tab-workspace-boq">
                <BoqTable plan={currentPlan} />
              </div>
            )}
            {activeTab === "schedule" && (
              <div
                id="panel-workspace-schedule"
                role="tabpanel"
                aria-labelledby="tab-workspace-schedule"
              >
                <ScheduleTimeline
                  schedule={currentPlan.schedule}
                  milestones={currentPlan.planning_milestones}
                  onMilestoneToggle={handleMilestoneToggle}
                  eventDate={eventDate}
                  onEventDateChange={(d) => {
                    setEventDate(d);
                    setCurrentPlan((prev) => ({ ...prev, event_date: d }));
                  }}
                />
              </div>
            )}
            {activeTab === "vendors" && (
              <div
                id="panel-workspace-vendors"
                role="tabpanel"
                aria-labelledby="tab-workspace-vendors"
              >
                <VendorFinder
                  city={currentPlan.location_city}
                  checklist={currentPlan.vendor_checklist}
                  onChecklistUpdate={handleChecklistUpdate}
                />
              </div>
            )}
            {activeTab === "export" && (
              <div
                id="panel-workspace-export"
                role="tabpanel"
                aria-labelledby="tab-workspace-export"
              >
                <ExportActions plan={currentPlan} />
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
