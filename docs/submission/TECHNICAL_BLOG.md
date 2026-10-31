# Building AuraPulse AI: Multimodal Event Planning, Dynamic Milestones & Crisis Rebalancing with Google Gemini 2.5 Flash

**System Classification**: Autonomous Multimodal Event Planning & Reactive Contingency Engine  
**Platform**: Google Antigravity  
**Hackathon Target**: Hack2Skill Google PromptWars (Challenge 5: GenAI-Powered Planning Assistant)  
**Architecture Version**: `v2.1.0-PROD`

---

## 1. The Problem: The Fragility of Modern Event Planning

Events—whether destination weddings, milestone birthdays, or vibrant community festivals—are multi-variable operational challenges. Traditional event planning suffers from three systemic vulnerabilities:

1. **The Visual-to-Procurement Translation Gap**: Clients communicate aesthetic dreams through mood boards and photos. Planners spend hours translating "warm sunset meadow" into procurement line items: aluminium box trusses, 2,000 feet of warm Edison festoons, or waterproof audio line arrays.
2. **Timeline Disconnect**: Milestones set without temporal reference to the event date lead to missed booking windows. Deadlines set in the past or scheduled haphazardly create operational bottlenecks.
3. **Contingency Paralysis**: When a real-time crisis hits—such as sudden torrential downpour, an unexpected 20% budget cut, or supplier cancellations—organizers lack deterministic mathematical models to rebalance budgets, shift timelines, and source verified local replacements in minutes.

**AuraPulse AI** solves this by unifying **Multimodal Gemini 2.5 Flash Vision & Generation**, a **Dynamic Backwards Planning Timeline**, **Function-Calling Conversational Replanning**, and **Google Services (Places API New, RFC-5545 iCal & Google Calendar Web Intents)** into a resilient, production-grade event operating system.

---

## 2. Architectural Deep Dive: 3 Core Layers

AuraPulse AI coordinates 3 decoupled, production-grade layers using strictly typed Pydantic v2 data contracts:

```
+-----------------------------------------------------------------------------------+
|                              1. CLIENT SURFACE                                    |
|   Next.js 15 (App Router) + Tailwind CSS + Lucide Icons + React Reactive Diff     |
|   • Reactive Diff Visualizer (+Added, ~Modified, -Removed)                        |
|   • Dynamic Backwards Timeline with "Do Immediately" near-term compression        |
|   • Multi-Turn AI Co-Pilot Chat Drawer & Responsive Procurement Matrix            |
+------------------------------------------+----------------------------------------+
                                           | HTTPS / REST API
                                           v
+-----------------------------------------------------------------------------------+
|                        2. API GATEWAY & SESSION MANAGER                           |
|   FastAPI (Python 3.12) with Pydantic v2 Strict Data Contracts                    |
|   • MasterEventPlan, BOQItem, PlanningMilestone, ContingencyDiff                  |
|   • Deterministic Cost Recalculation (quantity * rate) & Budget Cap Validation   |
|   • Honest Health & Readiness Monitor (/api/health)                               |
+---------------------+--------------------+----------------------------------------+
                      |                    |
        +-------------+                    +-------------+
        | Asynchronous Generation & Tool Calling         | Grounded Tool Fabric & Exports
        v                                                v
+------------------------------------+   +------------------------------------------+
|  3. GEMINI 2.5 FLASH ENGINE        |   |  GOOGLE SERVICES & EXPORTS               |
|                                    |   |                                          |
|  A. Aura Vision & Generation       |   |  • Google Maps Places API (New)          |
|     (Gemini 2.5 Flash Multimodal)  |   |    Text search with FieldMasks           |
|     Schema-guided JSON extraction  |   |    Authentic rating & phone grounding     |
|                                    |   |                                          |
|  B. Function-Calling Co-Pilot      |   |  • RFC-5545 .ics Calendar Export         |
|     Multi-turn tool execution      |   |    Milestone due dates & day-of blocks   |
|     (scale_budget, add_item, etc.) |   |                                          |
|                                    |   |  • Google Calendar Web Intent Links      |
|  C. Pulse Contingency Solver       |   |    Zero-permission direct calendar sync   |
|     Deterministic tier locking     |   |                                          |
+------------------------------------+   +------------------------------------------+
```

### 2.1 Schema-Guided Generation with Gemini 2.5 Flash
Visual intake and plan generation are powered by **Gemini 2.5 Flash** using the modern `google-genai` SDK (`from google import genai`). Rather than relying on loose natural language prompts, the system guides generation using strict Pydantic schemas:
* **Strict Type Safety**: The schema requires complete `BOQItem` entries specifying `item_id`, `category`, `name`, `specification`, `quantity`, `unit`, `rate`, `total_cost`, and `priority_tier` (`Critical`, `Operational`, `Discretionary`).
* **Deterministic Server-Side Verification**: Line totals are calculated deterministically on the server (`total_cost = round(quantity * rate, 2)`). The engine verifies that the sum of line items strictly respects the user's provided budget ceiling.
* **Regional & Cultural Authenticity**: System instructions mandate regional cultural grounding (e.g., Maharashtrian wedding rituals like Sakhar Puda, specific catering traditions, and community permit logistics).

### 2.2 Dynamic Backwards Planning Timeline
Event planning requires counting backwards from the target event date. AuraPulse AI implements dynamic timeline arithmetic:
* **Target Relative Offsets**: Milestones are computed relative to `event_date` (e.g., `T-90d`, `T-60d`, `T-30d`, `T-14d`, `T-7d`, `T-1d`, `T-0d`).
* **Zero Past Dates & Short-Horizon Compression**: If an event date is close (e.g., 2 weeks away), tasks that would mathematically land in the past are dynamically compressed into high-priority `"Do Immediately"` milestones, ensuring organizers are never presented with impossible deadlines.

### 2.3 Function-Calling AI Co-Pilot
Instead of fragile keyword matching or hardcoded regex, the conversational Co-Pilot utilizes Gemini function/tool calling with schema-backed tool declarations:
* `scale_budget(percentage, preserve_tier1)`: Surgically trims discretionary lines while preserving critical safety, food, and power lines.
* `add_item(category, name, quantity, unit, rate, priority_tier)`: Injects custom vendor lines into the procurement table.
* `remove_item(item_id, item_name)`: Removes specified line items.
* `set_event_date(new_date)`: Recomputes the entire backwards timeline.
* `decline_off_topic()`: Politely deflects non-event-planning questions.
The Co-Pilot maintains multi-turn history (last 6 turns) and supports Hindi and Marathi conversational nuances.

### 2.4 Deterministic Reactive Contingency Solver
When crises occur (e.g., unexpected rainstorms or sudden budget slashes), the contingency engine executes mathematical rebalancing:
1. **Tier-1 (Critical) Locking**: Fire safety, sound permits, primary electrical generators, and food safety lines are strictly immutable.
2. **Emergency Asset Injection**: On rain alert, an all-weather German Pagoda marquee is injected into the BOQ.
3. **Discretionary Trimming**: Cost increases are offset by systematically trimming Tier-3 Discretionary embellishments (e.g., luxury floral arches, imported blooms).
4. **State Diff Generation**: Emits an atomic `ContingencyDiff` with `+ ADDED`, `~ MODIFIED`, and `- REMOVED` records alongside a clear reasoning narrative.

---

## 3. Google Tech Stack & Integrations

### Google Maps Places API (New)
The vendor discovery module queries the modern Places API (New) (`https://places.googleapis.com/v1/places:searchText`) using explicit field masks:
* Requested fields: `places.id`, `places.displayName`, `places.formattedAddress`, `places.rating`, `places.userRatingCount`, `places.nationalPhoneNumber`, `places.googleMapsUri`.
* **Honest Fallback**: When an API key is unconfigured or invalid, the system returns `status: "SIMULATED"` with clear UI indicators, ensuring zero fabricated phone numbers or synthetic vendor listings.

### RFC-5545 Calendar Export & Web Intents
AuraPulse AI provides two frictionless calendar export pathways:
* **Standard RFC-5545 `.ics` Export**: Generates a standard calendar file with milestone due dates as all-day events and day-of schedule blocks configured with `TZID=Asia/Kolkata`.
* **Zero-OAuth Web Intent Links**: Generates standard Google Calendar template links (`https://calendar.google.com/calendar/render?action=TEMPLATE&...`) that open directly in the user's Google Calendar without requiring complex OAuth tokens or cloud permissions.

---

## 4. What Google Antigravity Enabled

Building AuraPulse AI with **Google Antigravity** provided rapid agentic development velocity:

1. **Full-Stack Monorepo Cohesion**: Synchronously developed FastAPI endpoints, Next.js 15 UI components, and TypeScript API clients.
2. **Strict Verification Culture**: Continuous headless test runs and validation passes caught subtle schema mismatches and API payload edge cases before final delivery.
3. **Transparent Architectural Evolution**: Transitioned smoothly from early experimental mocks to a hardened, authentic v2.1-PROD architecture backed by 31 passing unit and integration tests.

---

## 5. Lessons Learned & Production Roadmap

### Key Learnings
* **Tiered Prioritization Eliminates Hallucinations**: Prompting LLMs to reduce budgets without explicit priority tiers leads to erratic choices (like eliminating electricity or guest meals). Explicit tier definitions give the model clear operational boundaries.
* **Hybrid Deterministic + LLM Synergy**: Combining strict deterministic arithmetic (Python calculations) with LLM contextual reasoning (Gemini Flash) guarantees mathematical accuracy while preserving natural language flexibility.

### Roadmap
* **Automated Weather Radar Alerts**: Triggering the contingency engine automatically via real-time meteorological API webhooks.
* **Vendor Contract Dispatch**: Auto-generating PDF purchase orders from finalized BOQ tables for instant vendor signing.

---

*Submitted to Hack2Skill Google PromptWars (Challenge 5) | Powered by Google Gemini 2.5 Flash & Google Places API.*
