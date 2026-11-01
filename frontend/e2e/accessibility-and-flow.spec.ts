import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fixturePlan from "./fixtures/plan.json";
import fixturePlanCut20 from "./fixtures/plan_cut20.json";
import fixtureDiffCut20 from "./fixtures/diff_cut20.json";

test.describe("AuraPulse AI Flow and Accessibility", () => {
  test.beforeEach(async ({ page }) => {
    // Route-mock backend endpoints so e2e is deterministic and doesn't need a live backend
    await page.route("**/api/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          status: "healthy",
          gemini_configured: false,
          google_apis: { places_maps: false, sheets: false, calendar: true },
        }),
      });
    });

    await page.route("**/api/v1/aura/deconstruct", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(fixturePlan),
      });
    });

    await page.route("**/api/v1/aura/chat-copilot", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          updated_plan: fixturePlanCut20,
          diff: fixtureDiffCut20,
          copilot_reply: "Budget scaled by -20%. Critical safety & food items locked.",
          actionable_ideas: ["Review updated lines"],
          mode: "offline_rules",
          declined: false,
        }),
      });
    });

    await page.route("**/api/v1/export/calendar-ics", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "text/calendar",
        body: "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//AuraPulse AI//EN\r\nEND:VCALENDAR\r\n",
      });
    });

    await page.route("**/api/v1/integrations/vendors**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          vendors: [],
          is_configured: false,
          count: 0,
          query: "",
          city: "",
        }),
      });
    });
  });

  test("1. Core Flow: generates plan, cuts budget by 20% via copilot, and exports .ics", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Click first preset card to load plan
    const meadowPreset = page.getByText(/Meadow Wedding/i).first();
    await meadowPreset.click();

    // Verify Master BOQ items and budget rendered
    await expect(page.getByRole("tab", { name: /Master BOQ/i })).toBeVisible();
    await expect(page.getByText(/15,00,000/)).toBeVisible();

    // Type "cut budget by 20%" into Co-Pilot
    const copilotInput = page.getByPlaceholder(/Switch menu to Marathi cuisine/i);
    await copilotInput.fill("cut budget by 20%");
    await page.getByRole("button", { name: /Ask Co-Pilot/i }).click();

    // Verify budget updates to new ceiling (12,00,000)
    await expect(page.getByText(/12,00,000/).first()).toBeVisible();

    // Switch to Google Workspace Exporter tab
    const exportTab = page.getByRole("tab", { name: /Google Workspace Exporter/i });
    await exportTab.click();

    // Trigger .ics calendar export download
    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: /Download iCal \(\.ics\)/i }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain(".ics");
  });

  test("2. Error Path: displays 503 error alert and visible Retry button on generation failure", async ({ page }) => {
    // Override deconstruct route to return 503
    await page.route("**/api/v1/aura/deconstruct", async (route) => {
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({
          code: "GENERATION_FAILED",
          message: "Failed to generate event plan via Gemini. Please retry or choose a preset.",
        }),
      });
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Click Generate plan with Gemini button
    const generateBtn = page.getByRole("button", { name: /Generate plan with Gemini/i });
    await generateBtn.click();

    // Verify role="alert" with error message
    const alert = page.getByRole("alert").filter({ hasText: /Failed to generate event plan/i });
    await expect(alert).toBeVisible();
    await expect(alert).toContainText("Failed to generate event plan via Gemini");

    // Verify visible Retry button inside alert
    const retryBtn = alert.getByRole("button", { name: /Retry/i });
    await expect(retryBtn).toBeVisible();
  });

  test("3. Keyboard Navigation: tablist responds to arrow keys with roving focus and aria-selected", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const boqTab = page.getByRole("tab", { name: /Master BOQ/i });
    await expect(boqTab).toBeVisible();
    await boqTab.focus();
    await expect(boqTab).toHaveAttribute("aria-selected", "true");

    // Arrow Right to Schedule
    await page.keyboard.press("ArrowRight");
    const scheduleTab = page.getByRole("tab", { name: /Milestones & Timeline/i });
    await expect(scheduleTab).toBeFocused();
    await expect(scheduleTab).toHaveAttribute("aria-selected", "true");
    await expect(boqTab).toHaveAttribute("aria-selected", "false");

    // Arrow Right to Vendors
    await page.keyboard.press("ArrowRight");
    const vendorTab = page.getByRole("tab", { name: /Vendor Action Center/i });
    await expect(vendorTab).toBeFocused();
    await expect(vendorTab).toHaveAttribute("aria-selected", "true");

    // Arrow Left back to Schedule
    await page.keyboard.press("ArrowLeft");
    await expect(scheduleTab).toBeFocused();
    await expect(scheduleTab).toHaveAttribute("aria-selected", "true");
  });

  test("4. Accessibility: page passes WCAG 2.1 AA scan with color-contrast enabled", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Run AxeBuilder with WCAG 2.0 & 2.1 AA tags and color-contrast rule enabled
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
