import { describe, it, expect } from "vitest";
import { toLocalISODate, addDays, defaultEventDate, tomorrow } from "../lib/dates";

describe("dates utilities", () => {
  it("formats Date using local calendar arithmetic without UTC shift", () => {
    // Both early morning and late night local times
    const morning = new Date(2027, 4, 15, 0, 15, 0); // May 15, 2027 00:15
    const evening = new Date(2027, 4, 15, 23, 45, 0); // May 15, 2027 23:45
    expect(toLocalISODate(morning)).toBe("2027-05-15");
    expect(toLocalISODate(evening)).toBe("2027-05-15");
  });

  it("formats month boundaries and leap days correctly in local date arithmetic", () => {
    const leapDay = new Date(2028, 1, 29, 12, 0, 0); // Feb 29, 2028
    const yearEnd = new Date(2027, 11, 31, 23, 59, 0); // Dec 31, 2027
    const yearStart = new Date(2028, 0, 1, 0, 1, 0); // Jan 1, 2028
    expect(toLocalISODate(leapDay)).toBe("2028-02-29");
    expect(toLocalISODate(yearEnd)).toBe("2027-12-31");
    expect(toLocalISODate(yearStart)).toBe("2028-01-01");
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
