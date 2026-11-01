import type { MasterEventPlan } from "../types/plan";

const csvEscape = (value: unknown): string => {
  const str = value === null || value === undefined ? "" : String(value);
  return /[",\r\n]/.test(str) ? `"${str.replace(/"/g, '""')}"` : str;
};

export function downloadBoqCsv(plan: MasterEventPlan): void {
  const header = [
    "Item ID",
    "Category",
    "Name",
    "Specification",
    "Quantity",
    "Unit",
    "Rate (INR)",
    "Total (INR)",
    "Priority Tier",
    "Status",
  ];
  const rows: (string | number)[][] = plan.boq.map((it) => [
    it.item_id,
    it.category,
    it.name,
    it.specification,
    it.quantity,
    it.unit,
    it.estimated_rate_inr,
    it.status === "DROPPED" ? 0 : it.total_cost_inr,
    it.priority,
    it.status,
  ]);
  const criticalTotal = plan.boq
    .filter((it) => it.status !== "DROPPED" && it.priority === "Critical")
    .reduce((sum, it) => sum + (it.total_cost_inr || 0), 0);
  const operationalTotal = plan.boq
    .filter((it) => it.status !== "DROPPED" && it.priority === "Operational")
    .reduce((sum, it) => sum + (it.total_cost_inr || 0), 0);
  const discretionaryTotal = plan.boq
    .filter((it) => it.status !== "DROPPED" && it.priority === "Discretionary")
    .reduce((sum, it) => sum + (it.total_cost_inr || 0), 0);
  const activeTotal = plan.boq
    .filter((it) => it.status !== "DROPPED")
    .reduce((sum, it) => sum + (it.total_cost_inr || 0), 0);

  rows.push([
    "",
    "",
    "SUBTOTAL: Critical (Tier 1)",
    "",
    "",
    "",
    "",
    Math.round(criticalTotal * 100) / 100,
    "Critical",
    "",
  ]);
  rows.push([
    "",
    "",
    "SUBTOTAL: Operational (Tier 2)",
    "",
    "",
    "",
    "",
    Math.round(operationalTotal * 100) / 100,
    "Operational",
    "",
  ]);
  rows.push([
    "",
    "",
    "SUBTOTAL: Discretionary (Tier 3)",
    "",
    "",
    "",
    "",
    Math.round(discretionaryTotal * 100) / 100,
    "Discretionary",
    "",
  ]);
  rows.push([
    "",
    "",
    "GRAND TOTAL (Active Items)",
    "",
    "",
    "",
    "",
    Math.round(activeTotal * 100) / 100,
    "",
    "",
  ]);
  rows.push(["", "", "Budget Ceiling", "", "", "", "", plan.total_budget_limit, "", ""]);

  const csv = [header, ...rows].map((r) => r.map(csvEscape).join(",")).join("\r\n");
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${(plan.title || "event").toLowerCase().replace(/[^a-z0-9]/g, "_")}_boq.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
