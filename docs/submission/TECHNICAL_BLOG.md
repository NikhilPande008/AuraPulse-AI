# Building AuraPulse AI: Multimodal Vision-to-BOQ Deconstruction & Real-Time Crisis Rebalancing with Google Gemini & Workspace APIs

**System Classification**: Autonomous Multimodal Event Planning & Reactive Contingency Engine  
**Platform Paradigm**: Agentic Development via Google Antigravity  
**Hackathon Target**: Hack2Skill Google PromptWars  
**Architecture Version**: `2.0.0-PROD`

---

## 1. The Problem: The Fragility of Modern Event Planning

Events—whether high-stakes destination weddings, tech conferences, or vibrant community festivals—are multi-variable operational minefields. Traditional event planning suffers from three systemic vulnerabilities:

1. **The Visual-to-Procurement Translation Gap**: Clients communicate aesthetic dreams through Pinterest boards, Instagram reels, and mood boards. Planners spend dozens of manual hours translating "warm meadow sunset vibes" into rigid procurement line items: 2,000 feet of warm Edison festoon lighting, IP65 waterproof audio line arrays, or fire-retardant structural pergolas.
2. **Pricing Opacity & Budget Bleed**: Discretionary aesthetics (exotic imported orchids, cold spark fountains, custom LED neon) frequently balloon costs without transparency, leaving zero financial buffer when emergency infrastructure is required.
3. **Contingency Paralysis**: When a real-time crisis hits—such as sudden torrential downpour, an unexpected 20% budget reduction, a 1-hour delay in the arrival procession, or an abrupt caterer cancellation—human organizers panic. They lack deterministic mathematical models to rebalance budgets, shift temporal run-of-shows, and source verified local replacements in minutes.

**AuraPulse AI** solves this by unifying **Multimodal Gemini Vision**, **Deterministic Graph Solving with Gemini 2.5 Pro Reasoning**, and the **Google Services Tool Fabric (Maps, Sheets, Calendar)** into a resilient, autonomous event operating system.

---

## 2. Architectural Deep Dive: The Five-Layer Symphony

AuraPulse AI coordinates five decoupled architectural layers using an ephemeral, reactive client-state model backed by FastAPI Pydantic v2 validation contracts:

```
+-----------------------------------------------------------------------------------+
|                              1. CLIENT SURFACE                                    |
|   Next.js 15 (App Router) + Tailwind CSS + Lucide Icons + React Reactive Diff     |
|   Hosted on: Firebase App Hosting / Cloud CDN                                     |
+------------------------------------------+----------------------------------------+
                                           | HTTPS / Ephemeral Reactive State Calls
                                           v
+-----------------------------------------------------------------------------------+
|                        2. API GATEWAY & SESSION MANAGER                           |
|   FastAPI (Python 3.12) / Cloud Run (Serverless, Autoscaling 0 -> 3)              |
|   • Ephemeral Reactive Client-State Model & Pydantic v2 Strict Contracts          |
|   • Optional Developer Telemetry Hook (/api/v1/pulse/events/stream)               |
+---------------------+--------------------+----------------------------------------+
                      |                    |
        +-------------+                    +-------------+
        | Reasoning Cluster Dispatch                     | Structured Integration Calls
        v                                                v
+------------------------------------+   +------------------------------------------+
|  3. GEMINI REASONING CLUSTER       |   |  4. GOOGLE TOOL FABRIC & INTEGRATIONS    |
|  (Vertex AI / Google GenAI SDK)    |   |                                          |
|                                    |   |  • Google Maps Places API (Grounding)   |
|  A. Aura Deconstruct Agent        |   |    Nearby venue, caterer, decor search   |
|     (Gemini 2.5 Flash Multimodal)  |   |                                          |
|     Visual parsing -> BOQ mapping  |   |  • Google Sheets API v4                  |
|                                    |   |    Dynamic formulas, budgeting sheets    |
|  B. Pulse Dynamic Engine          |   |                                          |
|     (Gemini 2.5 Pro Reasoner)      |   |  • Google Calendar API v3                |
|     Multi-constraint graph solver  |   |    Run-of-show dispatch & rescheduling   |
|                                    |   |                                          |
|  C. Generative Studio              |   |  • Google Cloud Storage                  |
|     (Imagen 3 Endpoint)            |   |    Raw mood board assets & renders       |
|     Decor visual alternatives      |   |                                          |
+------------------------------------+   +------------------------------------------+
```

### 2.1 Aura Vision-to-BOQ Engine (Gemini 2.5 Flash)
Visual intake is handled by **Gemini 2.5 Flash Multimodal**. Rather than outputting conversational summaries, the engine enforces strict structural typings via `google-genai` and Pydantic (`strict=True`). 
The agent analyzes pixels to identify:
* **Structural Rigging**: Aluminium box trusses, clear-span timber pergolas, and stage decks.
* **Lighting Density**: Moving beam fixtures, PAR ambiences, festoon light runs.
* **Botanical Hierarchy**: Fresh seasonal vs. imported blooms, floral archways, ceiling clouds.
* **Guest Comfort**: Seating ratios (VIP sofas vs. Chiavari/benches), audio coverage line arrays.

Every line item is categorized into a deterministic three-tier hierarchy:
* **Tier-1 (Critical)**: Non-negotiable infrastructure, safety licenses, primary electrical feeds, and baseline catering.
* **Tier-2 (Operational)**: Key functional elements (audio arrays, stage lighting, guest dining seating).
* **Tier-3 (Discretionary)**: Discretionary aesthetic embellishments (imported orchids, cold spark jets, 360 photo booths).

### 2.2 Pulse Dynamic Contingency Engine (Gemini 2.5 Pro Reasoner)
When a crisis occurs, the **Pulse Dynamic Engine** executes a multi-constraint optimization pass:
1. **Locks Tier-1 Items**: Guarantees that guest safety, electrical earthing, food safety, and sound permits can never be compromised.
2. **Evaluates Tier-2 Substitutions**: Searches Google Maps Places API for verified local alternates if supply chains break.
3. **Trims or Downscales Tier-3 Items**: Dynamically extracts savings from discretionary aesthetic lines to fund emergency mitigation assets (e.g., all-weather German Pagoda marquees during rainstorms).
4. **Cascades Schedule Blocks**: Timeline graph solver shifts ceremony and reception milestones while respecting banquet holding temperatures and sound curfew constraints.
5. **Generates State Diff Graph**: Emits an atomic `ContingencyDiff` with `+ ADDED`, `~ MODIFIED`, and `- REMOVED` records alongside a comprehensive Gemini 2.5 Pro reasoning narrative.

---

## 3. Google Tech Stack & API Fabric Highlights

### Structured Pydantic Outputs with Gemini 2.5
In production, loose LLM JSON outputs cause downstream frontend hydration failures. AuraPulse AI enforces strict type safety:
```python
class BOQItem(BaseModel):
    model_config = ConfigDict(strict=True)

    item_id: str
    category: str
    name: str
    specification: str
    quantity: float
    unit: str
    estimated_rate_inr: float
    total_cost_inr: float
    priority: PriorityTier
    status: str = Field(default="ACTIVE")
```
Every response returned by Gemini 2.5 Flash and Pro is validated against Pydantic models before reaching the client surface.

### Formula-Driven Google Sheets API v4 Integration
Instead of exporting static text tables, AuraPulse AI generates living, calculation-ready Google Spreadsheets using the official Google Client Library:
* **Dynamic Grand Total**: Populates `=SUM(H2:H{n})` directly into the sheet summary.
* **Priority Breakdown Analytics**: Injects dynamic `=SUMIF(I2:I{n}, "Critical", H2:H{n})` and `=SUMIF(I2:I{n}, "Discretionary", H2:H{n})` formulas so event directors can edit line items live in Google Drive and watch category totals update automatically.

### Real-Time Grounding via Google Maps Places API
When an emergency vendor failure occurs (e.g., caterer truck breakdown 4 hours before guest arrival), AuraPulse AI queries the Google Maps Places API for verified vendors in the event's target city (e.g., Pune, Mumbai, Jaipur). Only vendors with confirmed high Google ratings (`>= 4.0`), operational phone numbers, and physical addresses are selected for automated hot-swapping.

### Google Calendar API v3 Temporal Synchronization
Run-of-show schedule blocks are formatted as RFC3339 timestamps and synced directly to Google Calendar. Outdoor blocks vulnerable to precipitation triggers receive high-visibility contingency tags and microclimate warning flags.

---

## 4. What Google Antigravity Enabled

Building AuraPulse AI in **Google Antigravity** fundamentally shifted our development paradigm:

1. **Agent-First Full-Stack Scaffolding**: Antigravity autonomously orchestrated the entire monorepo—provisioning FastAPI, Next.js 15, Tailwind CSS, and unit tests simultaneously.
2. **Deterministic Rules Enforcement**: Using `.antigravity/rules.md`, Antigravity prevented common developer pitfalls: it enforced strict Pydantic mode (`strict=True`), prohibited fragile mock endpoints in favor of authentic Google Client SDKs, and ensured clean separation of concerns between API gateway and reasoning cores.
3. **Continuous Background Verification**: Antigravity's autonomous skills (`test-gemini-schemas.yaml` and `verify-google-apis.yaml`) continuously executed automated pytest test suites and headless Chrome browser validation runs, capturing live UI screenshots and confirming zero rendering errors before final submission.

---

## 5. Lessons Learned & Production Roadmap

### Key Learnings
* **Tiered Prioritization is Crucial**: Prompting LLMs to "cut budget" without strict tier definitions leads to erratic hallucinations (e.g., cutting sound systems or dinner entirely). Enforcing Tier-1 (Critical) locks programmatically provides the boundary conditions the reasoner needs.
* **Hybrid Deterministic + LLM Architecture**: Pure LLMs struggle with exact arithmetic across 50 line items. By letting deterministic Python algorithms calculate exact currency deltas and assigning Gemini 2.5 Pro to multi-variable constraint reasoning, we achieved 100% mathematical precision with human-like contextual adaptability.

### Future Roadmap
* **WhatsApp / SMS Crisis Dispatch**: Instant broadcast of updated run-of-show schedules to vendor crews via Twilio/WhatsApp Business.
* **Live Weather Radar Webhooks**: Auto-triggering the Pulse Engine 3 hours prior to an event based on real-time Doppler radar rainfall predictions.
* **Imagen 3 Augmented Reality (AR) Previews**: Allowing clients to view generative staging alternatives in 3D AR on mobile devices.

---

*Submitted to Hack2Skill Google PromptWars | Powered by Google Gemini 2.5 & Google Antigravity.*
