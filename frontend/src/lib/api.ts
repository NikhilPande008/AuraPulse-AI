import { addDays, defaultEventDate } from "./dates";

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
  phase: "T-6 Months" | "T-3 Months" | "T-1 Month" | "T-2 Weeks" | "T-1 Week" | "Day-Of" | "Do Immediately";
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

const fallbackDefaultDate = defaultEventDate(90);

export const FALLBACK_PRESET_1: MasterEventPlan = {
  event_id: "evt_fallback_meadow",
  event_type: "wedding",
  title: "Boho Sunset Meadow Wedding (Pastel Peach & Sage)",
  location_city: "Pune",
  currency: "INR",
  total_budget_limit: 1500000,
  current_estimated_total: 1420000,
  headcount: 300,
  event_date: fallbackDefaultDate,
  boq: [
    {
      item_id: "boq_meadow_01",
      category: "Catering",
      name: "Farm-to-Table Organic Banquet & Woodfired Live Stations",
      specification: "300 Pax, live woodfired sourdough pizza, artisanal pasta & farm salads",
      quantity: 300,
      unit: "pax",
      estimated_rate_inr: 1500,
      total_cost_inr: 450000,
      priority: "Critical",
      status: "ACTIVE"
    },
    {
      item_id: "boq_meadow_02",
      category: "Infrastructure",
      name: "Weather-Treated Bamboo Pergolas & Meadow Decking",
      specification: "100% natural bamboo timber pergolas, raised teak wood ceremony deck (24x20 ft)",
      quantity: 1,
      unit: "lot",
      estimated_rate_inr: 180000,
      total_cost_inr: 180000,
      priority: "Critical",
      status: "ACTIVE"
    },
    {
      item_id: "boq_meadow_03",
      category: "Power & Safety",
      name: "82.5 kVA Silent DG Set & Eco Earthing Distribution",
      specification: "Super silent acoustic enclosure, industrial trip switches, 4x CO2 fire extinguishers",
      quantity: 1,
      unit: "unit",
      estimated_rate_inr: 85000,
      total_cost_inr: 85000,
      priority: "Critical",
      status: "ACTIVE"
    },
    {
      item_id: "boq_meadow_04",
      category: "Audio / Visual",
      name: "Warm Acoustic Line Array & Shure Wireless Mics",
      specification: "Compact column array setup tuned for open meadow acoustics, 4 wireless mics",
      quantity: 1,
      unit: "system",
      estimated_rate_inr: 120000,
      total_cost_inr: 120000,
      priority: "Operational",
      status: "ACTIVE"
    },
    {
      item_id: "boq_meadow_05",
      category: "Lighting",
      name: "2,000 ft Warm Edison Festoon Light Canopy",
      specification: "Vintage warm-glow tungsten filament festoon grid suspended over meadow dining",
      quantity: 1,
      unit: "installation",
      estimated_rate_inr: 175000,
      total_cost_inr: 175000,
      priority: "Operational",
      status: "ACTIVE"
    },
    {
      item_id: "boq_meadow_06",
      category: "Furniture & Seating",
      name: "Whitewashed Wooden Benches & Cane Lounge Loungers",
      specification: "30 whitewashed rustic dining tables, 250 wooden benches & woven wicker armchairs",
      quantity: 280,
      unit: "units",
      estimated_rate_inr: 500,
      total_cost_inr: 140000,
      priority: "Operational",
      status: "ACTIVE"
    },
    {
      item_id: "boq_meadow_07",
      category: "Floral Art",
      name: "Pampas Grass Arch, Dried Palms & Peach Hydrangeas",
      specification: "Organic dried floral ceremony arch, eucalyptus aisle runners & rustic meadow accents",
      quantity: 1,
      unit: "installation",
      estimated_rate_inr: 160000,
      total_cost_inr: 160000,
      priority: "Discretionary",
      status: "ACTIVE"
    },
    {
      item_id: "boq_meadow_08",
      category: "Decor & Ambiance",
      name: "Macramé Backdrops & Terracotta Aisle Lanterns",
      specification: "Hand-knotted macramé photo wall, 60 brass lanterns with battery pillar candles",
      quantity: 1,
      unit: "lot",
      estimated_rate_inr: 75000,
      total_cost_inr: 75000,
      priority: "Discretionary",
      status: "ACTIVE"
    },
    {
      item_id: "boq_meadow_09",
      category: "Interactive Experience",
      name: "Polaroid Guestbook Kiosk & Flower Crown Bar",
      specification: "Vintage wooden photo booth station with instant film prints and live floral crown crafter",
      quantity: 1,
      unit: "lot",
      estimated_rate_inr: 35000,
      total_cost_inr: 35000,
      priority: "Discretionary",
      status: "ACTIVE"
    }
  ],
  schedule: [
    {
      block_id: "sch_m01",
      phase: "Setup & Rigging",
      start_time_iso: "09:00",
      end_time_iso: "13:00",
      activity: "Meadow pergola timber assembly & 2,000 ft festoon light stringing",
      responsible_party: "EcoScaffold Productions",
      is_outdoor: true
    },
    {
      block_id: "sch_m02",
      phase: "Guest Arrival",
      start_time_iso: "15:30",
      end_time_iso: "16:45",
      activity: "Sunset meadow welcome, sparkling botanical mocktails & flower crown fitting",
      responsible_party: "Meadow Hospitality Team",
      is_outdoor: true
    },
    {
      block_id: "sch_m03",
      phase: "Main Ceremony",
      start_time_iso: "17:00",
      end_time_iso: "18:30",
      activity: "Vow exchange beneath pampas grass arch during golden hour sunset",
      responsible_party: "Celebrant & Family Leads",
      is_outdoor: true
    },
    {
      block_id: "sch_m04",
      phase: "Sunset Soirée",
      start_time_iso: "18:30",
      end_time_iso: "19:30",
      activity: "Golden hour acoustic guitar & cello performance with woodfired canapés",
      responsible_party: "Acoustic Trio",
      is_outdoor: true
    },
    {
      block_id: "sch_m05",
      phase: "Dinner & Banquet",
      start_time_iso: "19:30",
      end_time_iso: "22:30",
      activity: "Farm-to-table banquet served family-style under warm Edison festoon canopy",
      responsible_party: "Artisan Head Chef",
      is_outdoor: true
    },
    {
      block_id: "sch_m06",
      phase: "Afterparty",
      start_time_iso: "22:30",
      end_time_iso: "01:00",
      activity: "Barnhouse indoor acoustic jam, craft cider bar & midnight bonfire",
      responsible_party: "Night Operations Lead",
      is_outdoor: false
    }
  ],
  planning_milestones: [
    {
      id: "ms_m01",
      phase: "T-6 Months",
      title: "Lock Meadow Estate & Barnhouse Booking",
      description: "Finalize signed agreement for private hillside meadow property with wet weather backup barn.",
      due_date: addDays(fallbackDefaultDate, -180),
      category: "Venue",
      completed: true
    },
    {
      id: "ms_m02",
      phase: "T-3 Months",
      title: "Farm-to-Table Menu Tasting & Live Station Sign-off",
      description: "Culinary tasting of woodfired sourdough pizza, pasta, and organic local wines with head chef.",
      due_date: addDays(fallbackDefaultDate, -90),
      category: "Catering",
      completed: true
    },
    {
      id: "ms_m03",
      phase: "T-1 Month",
      title: "Pampas Floral Arch & Festoon Lighting Mockup",
      description: "Visual review of dried palm installations, peach hydrangeas, and warm Edison stringing geometry.",
      due_date: addDays(fallbackDefaultDate, -30),
      category: "Decor",
      completed: false
    },
    {
      id: "ms_m04",
      phase: "T-2 Weeks",
      title: "Dispatch Linen Digital Invitations & RSVP Lock",
      description: "Confirm final dietary requirements (vegan/gluten-free) and headcounts for 300 guests.",
      due_date: addDays(fallbackDefaultDate, -14),
      category: "Attire & Invites",
      completed: false
    },
    {
      id: "ms_m05",
      phase: "T-1 Week",
      title: "Microclimate Check & Generator Earthing Inspection",
      description: "Review 7-day weather forecast, test 82.5 kVA silent genset, and review rain contingency protocol.",
      due_date: addDays(fallbackDefaultDate, -7),
      category: "Logistics",
      completed: false
    },
    {
      id: "ms_m06",
      phase: "Day-Of",
      title: "Bride Meadow Entry & Sunset Vow Exchange",
      description: "Check flower crown bar setup, acoustic trio soundcheck, and golden hour ceremonial cue.",
      due_date: fallbackDefaultDate,
      category: "Rituals",
      completed: false
    }
  ],
  vendor_checklist: [
    {
      id: "vc_m01",
      category: "Catering & Banquet",
      vendor_name: "Artisan Kitchen Pune (Farm-to-Table)",
      estimated_cost: 450000,
      status: "Booked",
      notes: "Deposit paid (30%). Woodfired ovens mobilization confirmed for 07:00 AM.",
      google_maps_place_id: "ChIJ_pune_artisan_cater"
    },
    {
      id: "vc_m02",
      category: "Floral & Stage Decor",
      vendor_name: "BloomCraft Botanicals (Pampas & Sage)",
      estimated_cost: 160000,
      status: "Quoted",
      notes: "Revised quote for dried palms and local marigold garland substitution submitted.",
      google_maps_place_id: "ChIJ_pune_bloom_craft"
    },
    {
      id: "vc_m03",
      category: "Audio / Visual & Lighting",
      vendor_name: "LumenGlow & AcousticPro Rigging",
      estimated_cost: 295000,
      status: "Booked",
      notes: "Includes 2,000 ft festoons and waterproof column array audio system.",
      google_maps_place_id: "ChIJ_pune_lumenglow"
    },
    {
      id: "vc_m04",
      category: "Power & Safety",
      vendor_name: "PowerGrid Silent DG Sets",
      estimated_cost: 85000,
      status: "To Contact",
      notes: "Need to verify local municipal earthing certificate for hillside lawn.",
      google_maps_place_id: "ChIJ_pune_powergrid"
    },
    {
      id: "vc_m05",
      category: "Photography & Drone",
      vendor_name: "GoldenHour Cinematic Studios",
      estimated_cost: 85000,
      status: "Paid",
      notes: "100% advance paid. 2 cinematographers and 1 drone pilot confirmed.",
      google_maps_place_id: "ChIJ_pune_goldenhour"
    }
  ]
};

export const API_BASE = "/api/v1";

export async function deconstructMoodboard(params: {
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
}): Promise<MasterEventPlan> {
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
      const errData = await res.json().catch(() => ({}));
      console.warn(`Deconstruction API returned status ${res.status}:`, errData);
      const msg = errData?.message || (typeof errData?.detail === "string" ? errData.detail : errData?.detail?.message) || `Generation failed with status ${res.status}`;
      const err = new Error(msg) as any;
      err.code = errData?.code || errData?.detail?.code;
      throw err;
    }
    return await res.json();
  } catch (err: any) {
    if (params.moodboard_preset && params.moodboard_preset !== "custom") {
      console.warn("Network error during preset deconstruct; activating fallback snapshot.", err);
      return FALLBACK_PRESET_1;
    }
    throw err;
  }
}

export async function simulateContingency(
  plan: MasterEventPlan,
  trigger: CrisisTrigger
): Promise<ContingencyDiff> {
  const res = await fetch(`${API_BASE}/pulse/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plan, trigger }),
  });
  if (!res.ok) {
    throw new Error(`Simulation error: ${res.statusText}`);
  }
  return res.json();
}

export async function chatCopilot(
  eventPlan: MasterEventPlan,
  userPrompt: string,
  history?: Array<{ role: string; content: string }>
): Promise<CopilotResponse> {
  const res = await fetch(`${API_BASE}/aura/chat-copilot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event_plan: eventPlan,
      user_prompt: userPrompt,
      history: history || [],
    }),
  });
  if (!res.ok) {
    throw new Error(`Copilot error: ${res.statusText}`);
  }
  return res.json();
}

export async function renderStudioAlternative(
  promptDescription: string,
  theme: string = "Palace Royal Marquee"
) {
  const res = await fetch(`${API_BASE}/studio/render-alternative`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt_description: promptDescription,
      theme,
    }),
  });
  if (!res.ok) {
    throw new Error(`Studio error: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchVendors(query: string, city: string, minRating: number = 4.0) {
  const res = await fetch(
    `${API_BASE}/integrations/vendors?query=${encodeURIComponent(query)}&city=${encodeURIComponent(city)}&min_rating=${minRating}`
  );
  if (!res.ok) {
    throw new Error(`Vendors fetch error: ${res.statusText}`);
  }
  return res.json();
}

export async function exportToSheets(spreadsheetTitle: string, boqItems: BOQItem[]) {
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
      /* non-JSON error body */
    }
    throw new Error(message);
  }
  return res.json();
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

export async function syncToCalendar(eventTitle: string, scheduleBlocks: ScheduleBlock[]) {
  const res = await fetch(`${API_BASE}/integrations/calendar/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event_title: eventTitle,
      schedule_blocks: scheduleBlocks,
    }),
  });
  if (!res.ok) {
    throw new Error(`Calendar sync error: ${res.statusText}`);
  }
  return res.json();
}
