import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import Dashboard from "../app/page";

describe("Workspace Tabs Keyboard Navigation", () => {
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

  it("navigates tabs using ArrowRight and ArrowLeft keyboard keys", () => {
    render(<Dashboard />);

    const boqTab = screen.getByRole("tab", { name: /Master BOQ/i });
    const scheduleTab = screen.getByRole("tab", { name: /Milestones & Timeline/i });
    const vendorsTab = screen.getByRole("tab", { name: /Vendor Action Center/i });
    const exportTab = screen.getByRole("tab", { name: /Google Workspace Exporter/i });

    // Initial state: BOQ is selected
    expect(boqTab).toHaveAttribute("aria-selected", "true");
    expect(scheduleTab).toHaveAttribute("aria-selected", "false");

    const tablist = screen.getByRole("tablist", { name: /Event plan workspaces/i });

    // ArrowRight -> Schedule Tab
    fireEvent.keyDown(tablist, { key: "ArrowRight" });
    expect(scheduleTab).toHaveAttribute("aria-selected", "true");
    expect(boqTab).toHaveAttribute("aria-selected", "false");
    expect(document.activeElement).toBe(scheduleTab);

    // ArrowRight -> Vendors Tab
    fireEvent.keyDown(tablist, { key: "ArrowRight" });
    expect(vendorsTab).toHaveAttribute("aria-selected", "true");
    expect(scheduleTab).toHaveAttribute("aria-selected", "false");
    expect(document.activeElement).toBe(vendorsTab);

    // ArrowRight -> Export Tab
    fireEvent.keyDown(tablist, { key: "ArrowRight" });
    expect(exportTab).toHaveAttribute("aria-selected", "true");
    expect(document.activeElement).toBe(exportTab);

    // ArrowLeft -> Back to Vendors Tab
    fireEvent.keyDown(tablist, { key: "ArrowLeft" });
    expect(vendorsTab).toHaveAttribute("aria-selected", "true");
    expect(document.activeElement).toBe(vendorsTab);
  });
});
