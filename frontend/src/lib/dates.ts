/**
 * Date arithmetic utilities for AuraPulse AI.
 * Uses local calendar arithmetic to avoid UTC timezone-shift bugs.
 */

export function toLocalISODate(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function addDays(iso: string, n: number): string {
  const [year, month, day] = iso.split("-").map(Number);
  const d = new Date(year, month - 1, day);
  d.setDate(d.getDate() + n);
  return toLocalISODate(d);
}

export function defaultEventDate(daysAhead = 90): string {
  const d = new Date();
  d.setDate(d.getDate() + daysAhead);
  return toLocalISODate(d);
}

export function tomorrow(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return toLocalISODate(d);
}
