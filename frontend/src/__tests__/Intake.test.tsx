import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MoodboardUploader from "../components/MoodboardUploader";

// Mock fetch
global.fetch = vi.fn();

describe("MoodboardUploader component", () => {
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

    const dateInput = screen.getByLabelText(/Target Event Date/i) as HTMLInputElement;
    expect(dateInput.value).toBeDefined();
    expect(new Date(dateInput.value).getTime()).toBeGreaterThan(Date.now());
  });

  it("displays 503 error using InlineError alert when Gemini generation fails", async () => {
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

    // Switch to Custom / Generate plan tab or button
    const generateBtn = screen.getByText(/Generate Custom AI Plan/i);
    fireEvent.click(generateBtn);

    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert).toBeDefined();
      expect(alert.textContent).toContain("Failed to generate event plan via Gemini");
    });
  });
});
