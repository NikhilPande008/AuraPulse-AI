import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MoodboardUploader from "../components/MoodboardUploader";

describe("MoodboardUploader component", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    global.fetch = vi.fn();
  });

  it("renders with dynamic default event date", () => {
    const onPlanLoaded = vi.fn();
    const setIsLoading = vi.fn();

    render(
      <MoodboardUploader
        onPlanLoaded={onPlanLoaded}
        isLoading={false}
        setIsLoading={setIsLoading}
      />
    );

    const dateInput = screen.getByLabelText(/Event Date/i) as HTMLInputElement;
    expect(dateInput.value).toBeDefined();
    expect(new Date(dateInput.value).getTime()).toBeGreaterThan(Date.now());
  });

  it("displays 503 error with role='alert' and a visible Retry button when Gemini generation fails", async () => {
    const onPlanLoaded = vi.fn();
    const setIsLoading = vi.fn();

    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 503,
      json: async () => ({
        code: "GENERATION_FAILED",
        message: "Failed to generate event plan via Gemini. Please retry or choose a preset.",
      }),
    });

    render(
      <MoodboardUploader
        onPlanLoaded={onPlanLoaded}
        isLoading={false}
        setIsLoading={setIsLoading}
      />
    );

    const generateBtn = screen.getByRole("button", { name: /Generate plan with Gemini/i });
    fireEvent.click(generateBtn);

    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert).toBeInTheDocument();
      expect(alert.textContent).toContain("Failed to generate event plan via Gemini");
      const retryBtn = screen.getByRole("button", { name: /Retry/i });
      expect(retryBtn).toBeInTheDocument();
      expect(retryBtn).toBeVisible();
    });
  });

  it("submitting without selecting a moodboard sends NO moodboard_preset in the request body (R3)", async () => {
    const onPlanLoaded = vi.fn();
    const setIsLoading = vi.fn();

    let capturedBody: any = null;
    (global.fetch as any).mockImplementationOnce(async (_url: string, opts: any) => {
      if (opts && opts.body) {
        capturedBody = JSON.parse(opts.body);
      }
      return {
        ok: true,
        status: 200,
        json: async () => ({
          event_name: "Custom Meadow Celebration",
          total_budget_limit: 1500000,
          current_estimated_total: 1400000,
          boq: [],
          schedule: [],
          planning_milestones: [],
          vendor_checklist: [],
          contingencies: [],
        }),
      };
    });

    render(
      <MoodboardUploader
        onPlanLoaded={onPlanLoaded}
        isLoading={false}
        setIsLoading={setIsLoading}
      />
    );

    const generateBtn = screen.getByRole("button", { name: /Generate plan with Gemini/i });
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    expect(capturedBody).not.toBeNull();
    expect(capturedBody.moodboard_preset).toBeUndefined();
  });
});
