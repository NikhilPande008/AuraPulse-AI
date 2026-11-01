import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Dashboard from "../app/page";
import { FALLBACK_PRESET_1 } from "../lib/api";

describe("Dashboard LocalStorage Persistence", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    global.fetch = vi.fn().mockImplementation(async (url: string) => {
      if (url.includes("/api/health")) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            status: "healthy",
            gemini_configured: false,
            google_apis: { places_maps: false, sheets: false, calendar: true },
          }),
        };
      }
      return {
        ok: true,
        status: 200,
        json: async () => ({}),
      };
    });
    localStorage.clear();
  });

  it("loads pre-seeded event plan from localStorage on mount", async () => {
    const savedPlan = {
      ...FALLBACK_PRESET_1,
      title: "Pre-seeded Royal Palace Gala",
      total_budget_limit: 2500000,
      current_estimated_total: 2450000,
      headcount: 500,
    };

    localStorage.setItem(
      "aurapulse_state_v1",
      JSON.stringify({
        version: 1,
        currentPlan: savedPlan,
        baselinePlan: savedPlan,
        activeDiff: null,
        eventDate: "2027-11-20",
      })
    );

    render(<Dashboard />);

    await waitFor(() => {
      // Check that the saved plan title is displayed on screen
      expect(screen.getByText(/Pre-seeded Royal Palace Gala/i)).toBeInTheDocument();
    });
  });
});
