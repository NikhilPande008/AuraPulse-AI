import { FALLBACK_PRESET_1 } from "../fixtures/fallbackPlan";
import type {
  BOQItem,
  CalendarSyncResult,
  ContingencyDiff,
  CopilotResponse,
  CrisisTrigger,
  HealthStatus,
  MasterEventPlan,
  ScheduleBlock,
  SheetsExportResult,
  StudioResponse,
  VendorSearchResponse,
} from "../types/plan";
import { API_BASE, apiFetch, parseApiError, reportWarn } from "./client";

export interface DeconstructParams {
  image_base64?: string;
  moodboard_preset?: string;
  headcount: number;
  city?: string;
  locality?: string;
  budget?: number;
  budget_ceiling?: number;
  event_type: string;
  event_date?: string;
  culture_region?: string;
  theme?: string;
  dietary?: string[];
  language?: string;
}

export async function deconstructMoodboard(params: DeconstructParams): Promise<MasterEventPlan> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    const res = await fetch(`${API_BASE}/aura/deconstruct`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...params,
        city: params.city || params.locality,
        budget: params.budget || params.budget_ceiling,
      }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      throw await parseApiError(res);
    }
    return (await res.json()) as MasterEventPlan;
  } catch (err: unknown) {
    if (params.moodboard_preset && params.moodboard_preset !== "custom") {
      reportWarn("Network error during preset deconstruct; activating fallback snapshot.", err);
      return FALLBACK_PRESET_1;
    }
    throw err;
  }
}

export async function simulateContingency(
  plan: MasterEventPlan,
  trigger: CrisisTrigger
): Promise<ContingencyDiff> {
  return apiFetch<ContingencyDiff>(`${API_BASE}/pulse/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plan, trigger }),
  });
}

export async function chatCopilot(
  eventPlan: MasterEventPlan,
  userPrompt: string,
  history?: Array<{ role: string; content: string }>
): Promise<CopilotResponse> {
  return apiFetch<CopilotResponse>(`${API_BASE}/aura/chat-copilot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event_plan: eventPlan,
      user_prompt: userPrompt,
      history: history || [],
    }),
  });
}

export async function renderStudioAlternative(
  promptDescription: string,
  theme: string = "Palace Royal Marquee"
): Promise<StudioResponse> {
  return apiFetch<StudioResponse>(`${API_BASE}/studio/render-alternative`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt_description: promptDescription,
      theme,
    }),
  });
}

export async function fetchVendors(
  query: string,
  city: string,
  minRating: number = 4.0
): Promise<VendorSearchResponse> {
  return apiFetch<VendorSearchResponse>(
    `${API_BASE}/integrations/vendors?query=${encodeURIComponent(query)}&city=${encodeURIComponent(city)}&min_rating=${minRating}`
  );
}

export async function exportToSheets(
  spreadsheetTitle: string,
  boqItems: BOQItem[]
): Promise<SheetsExportResult> {
  const res = await fetch(`${API_BASE}/integrations/sheets/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      spreadsheet_title: spreadsheetTitle,
      boq_items: boqItems,
      currency: "INR",
    }),
  });
  if (!res.ok) {
    let message = `Sheets export error: ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.message) message = body.message;
    } catch {
      // Non-JSON response
    }
    throw new Error(message);
  }
  return (await res.json()) as SheetsExportResult;
}

export async function exportCalendarIcs(plan: MasterEventPlan): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/calendar-ics`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(plan),
  });
  if (!res.ok) {
    throw new Error(`ICS export error: ${res.statusText}`);
  }
  return res.blob();
}

export async function syncToCalendar(
  eventTitle: string,
  scheduleBlocks: ScheduleBlock[]
): Promise<CalendarSyncResult> {
  return apiFetch<CalendarSyncResult>(`${API_BASE}/integrations/calendar/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event_title: eventTitle,
      schedule_blocks: scheduleBlocks,
    }),
  });
}

export async function fetchHealth(): Promise<HealthStatus> {
  return apiFetch<HealthStatus>("/api/health");
}
