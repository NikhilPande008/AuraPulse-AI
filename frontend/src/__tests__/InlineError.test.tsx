import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import InlineError from "../components/InlineError";

describe("InlineError component", () => {
  it("renders message with role alert", () => {
    render(<InlineError message="Failed to connect to Gemini." />);
    const alertEl = screen.getByRole("alert");
    expect(alertEl).toBeDefined();
    expect(alertEl.textContent).toContain("Failed to connect to Gemini.");
  });

  it("handles retry click", () => {
    const onRetry = vi.fn();
    render(<InlineError message="Error" onRetry={onRetry} />);
    const retryBtn = screen.getByText("Retry");
    fireEvent.click(retryBtn);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("handles dismiss click", () => {
    const onDismiss = vi.fn();
    render(<InlineError message="Error" onDismiss={onDismiss} />);
    const dismissBtn = screen.getByLabelText("Dismiss alert");
    fireEvent.click(dismissBtn);
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });
});
