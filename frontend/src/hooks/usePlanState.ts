"use client";

import type React from "react";
import { useEffect, useRef, useState } from "react";
import { FALLBACK_PRESET_1 } from "../fixtures/fallbackPlan";
import { reportWarn } from "../lib/client";
import type {
  ContingencyDiff,
  HealthStatus,
  MasterEventPlan,
  VendorChecklistItem,
} from "../types/plan";

const STORAGE_KEY = "aurapulse_state_v1";

function getInitialEventDate(): string {
  const d = new Date();
  d.setDate(d.getDate() + 90);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export type WorkspaceTab = "boq" | "schedule" | "vendors" | "export";

export function usePlanState() {
  const [currentPlan, setCurrentPlan] = useState<MasterEventPlan>(FALLBACK_PRESET_1);
  const [baselinePlan, setBaselinePlan] = useState<MasterEventPlan>(FALLBACK_PRESET_1);
  const [activeDiff, setActiveDiff] = useState<ContingencyDiff | null>(null);
  const [eventDate, setEventDate] = useState<string>(getInitialEventDate);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isOfflineFallback, setIsOfflineFallback] = useState(false);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>("boq");
  const [liveAnnouncement, setLiveAnnouncement] = useState<string>("");
  const isHydrated = useRef(false);

  const tabKeys: WorkspaceTab[] = ["boq", "schedule", "vendors", "export"];

  const handleTabKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const currentIndex = tabKeys.indexOf(activeTab);
    if (currentIndex === -1) return;

    let targetIndex = -1;
    if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      e.preventDefault();
      targetIndex = (currentIndex + 1) % tabKeys.length;
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      e.preventDefault();
      targetIndex = (currentIndex - 1 + tabKeys.length) % tabKeys.length;
    } else if (e.key === "Home") {
      e.preventDefault();
      targetIndex = 0;
    } else if (e.key === "End") {
      e.preventDefault();
      targetIndex = tabKeys.length - 1;
    }

    if (targetIndex !== -1) {
      const targetTab = tabKeys[targetIndex];
      setActiveTab(targetTab);
      const tabElement = document.getElementById(`tab-workspace-${targetTab}`);
      if (tabElement) {
        tabElement.focus();
      }
    }
  };

  // Restore state from localStorage if available
  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed && parsed.version === 1 && parsed.currentPlan) {
            setCurrentPlan(parsed.currentPlan);
            setBaselinePlan(parsed.baselinePlan || parsed.currentPlan);
            if (parsed.activeDiff) setActiveDiff(parsed.activeDiff);
            if (parsed.eventDate) setEventDate(parsed.eventDate);
            isHydrated.current = true;
          }
        }
      } catch (e) {
        reportWarn("Failed to restore saved plan from localStorage", e);
      }
    }
  }, []);

  // Save state changes to localStorage
  useEffect(() => {
    if (typeof window !== "undefined" && isHydrated.current) {
      try {
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            version: 1,
            currentPlan,
            baselinePlan,
            activeDiff,
            eventDate,
          })
        );
      } catch {
        // Quota exceeded or private browsing
      }
    }
  }, [currentPlan, baselinePlan, activeDiff, eventDate]);

  // Initial load: fetch health status and hydrate default if no saved plan
  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((data: HealthStatus) => setHealthStatus(data))
      .catch((err) => reportWarn("Health check error:", err));

    if (!isHydrated.current) {
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
            const data: MasterEventPlan = await res.json();
            setCurrentPlan(data);
            setBaselinePlan(data);
            setIsOfflineFallback(false);
          } else {
            reportWarn("Backend responded with non-200. Activating embedded fallback.");
            setCurrentPlan(FALLBACK_PRESET_1);
            setBaselinePlan(FALLBACK_PRESET_1);
            setIsOfflineFallback(true);
          }
        } catch (err) {
          clearTimeout(timeoutId);
          reportWarn(
            "Initial hydration timed out or network blocked. Activating embedded fallback.",
            err
          );
          setCurrentPlan(FALLBACK_PRESET_1);
          setBaselinePlan(FALLBACK_PRESET_1);
          setIsOfflineFallback(true);
        } finally {
          isHydrated.current = true;
        }
      };
      init();
    }
  }, []);

  const handlePlanLoaded = (plan: MasterEventPlan) => {
    setCurrentPlan(plan);
    setBaselinePlan(plan);
    if (plan.event_date) {
      setEventDate(plan.event_date);
    }
    setActiveDiff(null);
    setLiveAnnouncement(`Loaded new plan: ${plan.title || "Custom Event Plan"}`);
  };

  const handleDiffGenerated = (diff: ContingencyDiff) => {
    setActiveDiff(diff);
    setCurrentPlan(diff.updated_plan);
    setLiveAnnouncement(
      `Plan updated: ${diff.trigger?.description || diff.trigger?.trigger_type || "Contingency simulation"}`
    );
  };

  const handleResetSimulation = () => {
    setActiveDiff(null);
    setCurrentPlan(baselinePlan);
    setLiveAnnouncement("Simulation reset to baseline plan.");
  };

  const handleResetToFreshPlan = () => {
    if (typeof window !== "undefined") {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch {
        // Ignored
      }
    }
    setCurrentPlan(FALLBACK_PRESET_1);
    setBaselinePlan(FALLBACK_PRESET_1);
    setActiveDiff(null);
    setEventDate(getInitialEventDate());
    setLiveAnnouncement("Plan reset to default template.");
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

  return {
    currentPlan,
    setCurrentPlan,
    baselinePlan,
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
  };
}
