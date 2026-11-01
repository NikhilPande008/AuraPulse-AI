export interface BOQItem {
  item_id: string;
  category: string;
  name: string;
  specification: string;
  quantity: number;
  unit: string;
  estimated_rate_inr: number;
  total_cost_inr: number;
  priority: "Critical" | "Operational" | "Discretionary";
  status: string; // ACTIVE, MODIFIED, DROPPED
}

export interface ScheduleBlock {
  block_id: string;
  phase: string;
  start_time_iso: string;
  end_time_iso: string;
  activity: string;
  responsible_party: string;
  is_outdoor: boolean;
}

export interface PlanningMilestone {
  id: string;
  phase:
    | "T-6 Months"
    | "T-3 Months"
    | "T-1 Month"
    | "T-2 Weeks"
    | "T-1 Week"
    | "Day-Of"
    | "Do Immediately";
  title: string;
  description: string;
  due_date: string;
  category: "Venue" | "Catering" | "Decor" | "Attire & Invites" | "Logistics" | "Rituals";
  completed: boolean;
}

export interface VendorChecklistItem {
  id: string;
  category: string;
  vendor_name: string;
  estimated_cost: number;
  status: "To Contact" | "Quoted" | "Booked" | "Paid";
  notes: string;
  google_maps_place_id?: string;
}

export interface MasterEventPlan {
  event_id: string;
  event_type: string;
  title: string;
  location_city: string;
  currency: string;
  total_budget_limit: number;
  current_estimated_total: number;
  headcount?: number;
  event_date?: string;
  culture_region?: string;
  theme?: string;
  ideas?: Array<{ title: string; rationale: string; estimated_cost?: number }>;
  boq: BOQItem[];
  schedule: ScheduleBlock[];
  planning_milestones?: PlanningMilestone[];
  vendor_checklist?: VendorChecklistItem[];
}

export interface CrisisTrigger {
  trigger_type: "WEATHER_RISK" | "BUDGET_COMPRESSION" | "SUPPLY_FAILURE" | "TIMELINE_SLIPPAGE";
  description: string;
  budget_cut_percent?: number;
  weather_condition?: string;
  delay_minutes?: number;
  affected_vendor_category?: string;
}

export interface BOQDiffItem {
  item_id: string;
  action: "ADDED" | "MODIFIED" | "REMOVED" | "UNCHANGED";
  original_item?: BOQItem;
  updated_item?: BOQItem;
  reason: string;
}

export interface ScheduleDiffItem {
  block_id: string;
  action: "ADDED" | "MODIFIED" | "REMOVED" | "UNCHANGED";
  original_block?: ScheduleBlock;
  updated_block?: ScheduleBlock;
  reason: string;
}

export interface ContingencyDiff {
  diff_id: string;
  trigger: CrisisTrigger;
  timestamp_iso: string;
  summary_narrative: string;
  original_total_inr: number;
  new_total_inr: number;
  budget_delta_inr: number;
  boq_diffs: BOQDiffItem[];
  schedule_diffs: ScheduleDiffItem[];
  updated_plan: MasterEventPlan;
  actionable_mitigations: string[];
}

export interface CopilotResponse {
  copilot_reply: string;
  updated_plan: MasterEventPlan;
  suggested_ideas: string[];
  diff?: ContingencyDiff;
  mode?: string;
  declined?: boolean;
}

export interface PlaceVendor {
  place_id?: string;
  name: string;
  address?: string;
  rating?: number;
  user_ratings_total?: number;
  phone?: string;
  google_maps_uri?: string;
  locality?: string;
  query_matched?: string;
  is_verified?: boolean;
}

export interface VendorSearchResponse {
  city: string;
  query: string;
  count: number;
  vendors: PlaceVendor[];
  is_configured: boolean;
  status: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  engine_flash: string;
  gemini_configured: boolean;
  places_configured: boolean;
  sheets_configured: boolean;
  google_apis: {
    gemini: boolean;
    places_maps: boolean;
    sheets_v4: boolean;
    calendar_ics: boolean;
  };
}

export interface StudioResponse {
  image_url: string;
  prompt: string;
  model: string | null;
  status: string;
  is_generated: boolean;
  source: string;
  error?: string | null;
}

export interface SheetsExportResult {
  status: string;
  spreadsheet_id?: string;
  spreadsheet_title?: string;
  spreadsheet_url?: string;
  title?: string;
  rows_written?: number;
  total_rows_created?: number;
  grand_total_formula?: string;
  priority_formulas?: Record<string, string>;
  items_exported?: number;
  currency?: string;
  message?: string;
}

export interface ApiError extends Error {
  code?: string;
  status?: number;
}

export function isApiError(err: unknown): err is ApiError {
  return typeof err === "object" && err !== null && "message" in err;
}
