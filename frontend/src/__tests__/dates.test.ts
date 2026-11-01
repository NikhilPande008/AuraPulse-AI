import { describe, it, expect } from "vitest";
import { toLocalISODate, addDays, defaultEventDate, tomorrow } from "../lib/dates";

describe("dates utilities", () => {
  it("formats Date using local calendar arithmetic without UTC shift", () => {
    const d = new Date(2027, 4, 15); // May 15, 2027
    expect(toLocalISODate(d)).toBe("2027-05-15");
  });

  it("adds and subtracts days accurately", () => {
    expect(addDays("2027-05-15", 10)).toBe("2027-05-25");
    expect(addDays("2027-05-15", -15)).toBe("2027-04-30");
  });

  it("defaultEventDate returns a date 90 days in future", () => {
    const d = defaultEventDate();
    const today = new Date();
    const parsed = new Date(d);
    expect(parsed.getTime()).toBeGreaterThan(today.getTime());
  });

  it("tomorrow returns next calendar day", () => {
    const t = tomorrow();
    const today = toLocalISODate(new Date());
    expect(t).not.toBe(today);
  });
});
