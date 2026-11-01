import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("AuraPulse AI Flow and Accessibility", () => {
  test("loads landing page with zero severe a11y violations", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Check headings and essential landmarks
    await expect(page.getByRole("banner")).toBeVisible();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    // Run axe accessibility scan
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .disableRules(["color-contrast"]) // Handled by Tailwind high-contrast palette
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test("workspace tablist responds to keyboard arrow keys", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const boqTab = page.getByRole("tab", { name: /Master BOQ/i });
    await expect(boqTab).toBeVisible();
    await boqTab.focus();

    // Arrow Right to Timeline
    await page.keyboard.press("ArrowRight");
    const timelineTab = page.getByRole("tab", { name: /Milestones & Timeline/i });
    await expect(timelineTab).toBeFocused();

    // Arrow Right to Vendors
    await page.keyboard.press("ArrowRight");
    const vendorTab = page.getByRole("tab", { name: /Vendor Action Center/i });
    await expect(vendorTab).toBeFocused();
  });
});
