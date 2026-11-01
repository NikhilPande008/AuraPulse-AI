# AuraPulse AI: Multimodal Event Planning & Reactive Contingency Engine

> **Hack2Skill Google PromptWars — Challenge 5: GenAI-Powered Planning Assistant**  
> *Version: 2.2.0 | Platform: Google Cloud Run*

[![Hack2Skill Google PromptWars](https://img.shields.io/badge/Hack2Skill-Google%20PromptWars%20(Challenge%205)-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://hack2skill.com)
[![Google Gemini 2.5 Flash](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-8E75C4?style=for-the-badge&logo=googlebard&logoColor=white)](https://ai.google.dev)
[![Google Places API New](https://img.shields.io/badge/Google%20Maps-Places%20API%20(New)-34A853?style=for-the-badge&logo=googlemaps&logoColor=white)](https://developers.google.com/maps/documentation/places/web-service/op-overview)
[![Next.js 15](https://img.shields.io/badge/Next.js-15%20App%20Router-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.12-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pytest 91/91 Passing](https://img.shields.io/badge/Pytest-91%2F91%20Passing%20(100%25)-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](#-automated-testing--verification)
[![Vitest 13/13 Passing](https://img.shields.io/badge/Vitest-13%2F13%20Passing-brightgreen?style=for-the-badge&logo=vitest&logoColor=white)](#-automated-testing--verification)
[![Playwright 4/4 Passing](https://img.shields.io/badge/Playwright-4%2F4%20Passing-brightgreen?style=for-the-badge&logo=playwright&logoColor=white)](#-automated-testing--verification)

---

> [!TIP]
> **Live Production Deployment & Video Walkthrough**:
> - 🌐 **Live Web Application**: [https://aurapulse-web-gwe45twb3q-uc.a.run.app](https://aurapulse-web-gwe45twb3q-uc.a.run.app)
> - 🎬 **YouTube Demo Video Walkthrough**: [https://youtu.be/DQr9v43w94c](https://youtu.be/DQr9v43w94c)
> - ⚡ **Backend API Gateway**: [https://aurapulse-backend-gwe45twb3q-uc.a.run.app](https://aurapulse-backend-gwe45twb3q-uc.a.run.app)
> - 🩺 **API Health Check**: [https://aurapulse-backend-gwe45twb3q-uc.a.run.app/api/health](https://aurapulse-backend-gwe45twb3q-uc.a.run.app/api/health)
> - 📖 **Cloud Run Deployment Guide**: [`docs/DEPLOY.md`](docs/DEPLOY.md)

---

## Chosen Vertical: Celebration & Event Planner (Challenge 5)

AuraPulse AI is purpose-built for the **Celebration & Event Planner** vertical under Hack2Skill Google PromptWars Challenge 5. Indian event management involves high operational complexity: multi-vendor coordination, tight multi-tier budget constraints, cultural ritual milestones (e.g. Sakhar Puda, Baraat), weather vulnerability, and dynamic run-of-show synchronization across hosts, venue managers, and vendors. AuraPulse AI provides a multimodal planner and reactive contingency copilot that transforms visual moodboards into itemized procurement matrices, backwards roadmaps, and deterministic contingency plans.

## Approach and Logic

AuraPulse AI combines **generative aesthetic extraction** with **deterministic operational constraint solving**:

1. **Aesthetic Deconstruction**: Deconstructs user-uploaded moodboards or presets using Google Gemini 2.5 Flash into typed, itemized Bill of Quantities (`BOQItem`) with unit pricing, quantities, and priority tiers (`Critical`, `Operational`, `Discretionary`).
2. **Backwards Temporal Scheduling**: Working backwards from a user-specified event date, milestones are pegged to canonical planning horizons (`T-6 Months`, `T-3 Months`, `T-1 Month`, `T-2 Weeks`, `T-1 Week`, `Day-Of`). Short-horizon compression shifts past milestones into `"Do Immediately"` action items without fabricating past dates.
3. **Deterministic Constraint-Preserving Contingency**: During disruptions (rain alerts, 20% budget cuts, timeline slippage, vendor cancellations), the Pulse Engine preserves Tier-1 Critical safety, food, and power lines, dynamically trimming Tier-3 Discretionary embellishments to balance budget deltas while enforcing strict budget ceilings.
4. **Conversational Tool Dispatch**: Natural language user prompts are dispatched via Gemini function calling into typed tool executions (`scale_budget`, `add_item`, `remove_item`, `set_event_date`, `change_headcount`), emitting actionable atomic diffs (+Added, ~Modified, -Removed) with Hindi and Marathi language sensitivity.

## How the Solution Works

1. **Multimodal Vision Intake**: The user submits event date, city, headcount, and budget ceiling, uploading a decor image or selecting a demo preset. Gemini 2.5 Flash extracts color palettes, decor elements, and cultural context, generating a typed `MasterEventPlan`. When Gemini is offline or unconfigured, curated preset event plans ensure instant, resilient demonstrations.
2. **Backwards Roadmap & Run-of-Show Generation**: The backend timeline service computes concrete calendar deadlines for critical milestones and hourly day-of schedule blocks. Run-of-show blocks track indoor vs outdoor zones for weather monitoring.
3. **Reactive Contingency Simulation (Pulse Engine)**: The user triggers crisis scenarios (`Rain Storm Alert`, `Cut 20% Budget`, `2hr Timeline Delay`, `Caterer Cancelled`). The engine adapts the plan: injecting emergency structures (e.g. German Pagoda Marquee), adjusting schedules, and rebalancing costs against the budget ceiling.
4. **Localized Vendor Grounding**: Google Maps Places API (New) searches for verified caterers, decorators, and technicians with field masks for authentic ratings, addresses, and contacts. When unconfigured, an honest inactive banner appears with zero synthetic contacts.
5. **Universal Workspace Export**: Planners can export spreadsheets via optional Google Sheets API v4 credentials (`=SUM(...)`, `=SUMIF(...)`), download standard RFC-5545 `.ics` calendars, or add events directly to Google Calendar via zero-permission web intents.

## Assumptions Made

1. **Currency & Metropolitan Localization**: Costs are denominated in Indian Rupees (INR) calibrated for Tier-1 and Tier-2 Indian metropolitan markets (Mumbai, Pune, Delhi, Bengaluru, Jaipur).
2. **Tier-1 Critical Immutability**: Core infrastructure, guest safety assets (weatherproofing marquee, electrical distribution, emergency shelter), sanitary food catering, and primary sound systems are designated as Tier-1 Critical and protected from arbitrary cuts during budget compression.
3. **Zero-Hallucination Vendor Integrity**: When Google Maps Places API keys are unconfigured, AuraPulse AI never fabricates synthetic phone numbers or fictitious vendors; it renders honest unconfigured badges and fallback procurement checklists.
4. **Zero-OAuth Friction**: Calendar export prioritizes RFC-5545 `.ics` downloads and Google Calendar web intents to ensure immediate zero-permission interoperability for clients and venue coordinators without requiring Google Cloud Workspace administrator approvals.
5. **Optional Google Sheets & Imagen Studio**: Google Sheets export requires a service account JSON; without it, the endpoint returns an explicit `503 SHEETS_NOT_CONFIGURED` error. The Imagen Studio provides creative decor visual staging with curated fallback image assets when unconfigured.

---

## 🚀 Run Locally

### Prerequisites
- Python 3.12+ (or 3.14)
- Node.js v20+ & npm

### Step 1: Clone Repository & Configure Environment
```bash
git clone https://github.com/NikhilPande008/AuraPulse-AI.git
cd AuraPulse-AI
cp .env.example .env
```

### Environment Settings (`Settings` in `backend/app/config.py`)
| Variable | Type | Default | Description |
|---|---|---|---|
| `PROJECT_NAME` | String | `"AuraPulse AI"` | Application service name |
| `VERSION` | String | `"2.2.0"` | Semantic service version |
| `API_V1_STR` | String | `"/api/v1"` | API v1 route prefix |
| `GEMINI_API_KEY` | SecretStr | `""` | Gemini API key for Flash generation and Copilot |
| `GEMINI_FLASH_MODEL` | String | `"gemini-2.5-flash"` | Gemini model identifier used for event plan generation |
| `GOOGLE_MAPS_API_KEY` | SecretStr | `""` | Google Maps API key for Places API (New) verified vendor search |
| `GOOGLE_APPLICATION_CREDENTIALS` | String | `""` | Optional path to service account JSON for Google Sheets API v4 export |
| `RATE_LIMIT_PER_MINUTE` | Integer | `10` | Sliding window request rate limit per minute per client IP |
| `RATE_LIMIT_PER_DAY` | Integer | `100` | Sliding window request rate limit per day per client IP |
| `TRUSTED_PROXY_HOPS` | Integer | `1` | Upstream proxy hops to trust when resolving client IP from `X-Forwarded-For` |
| `DISABLE_RATE_LIMIT` | Boolean | `false` | Disable rate limiting for testing suites |
| `PORT` | Integer | `8000` | Port number to bind backend HTTP server |
| `HOST` | String | `"0.0.0.0"` | Host interface address to bind HTTP server |
| `ALLOWED_ORIGIN` | String | `""` | Additional comma-separated origins for CORS header whitelist |

### Step 2: Start Backend Gateway
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Status: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Step 3: Start Frontend Web Client
In a separate terminal:
```bash
cd frontend
npm ci
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser. Next.js automatically proxies `/api/*` requests to the FastAPI backend.

---

## 🧪 Automated Testing & Verification

AuraPulse AI maintains comprehensive test suites verifying backend invariants, backwards timelines, Gemini generation, contingency solvers, Places API grounding, Vitest frontend components, and Playwright end-to-end accessibility scans:

### Backend Testing (Pytest: 91 Passing)
```bash
pytest backend/tests -v -m "not live"
# 91 passed, 1 deselected, 100% green
```

### Backend Quality Gates (Ruff, Xenon, Mypy)
```bash
ruff format --check backend
ruff check backend
(cd backend && mypy app)
xenon --max-absolute B --max-modules A --max-average A backend/app
```

### Frontend Testing (Vitest: 13 Passing)
```bash
cd frontend && npx vitest run
# Test Files: 5 passed (5) | Tests: 13 passed (13)
```

### End-to-End & WCAG 2.1 AA Accessibility (Playwright: 4 Passing)
```bash
cd frontend && npx playwright test
# 4 passed (Core Flow, 503 Error Path, Keyboard Navigation, WCAG 2.1 AA scan)
```

---

## 📁 Repository Layout

```
AuraPulse-AI/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application gateway & middleware
│   │   ├── config.py                   # Pydantic BaseSettings configuration
│   │   ├── api/                        # HTTP route controllers (health, aura, pulse, integrations, export, studio)
│   │   ├── agents/                     # Autonomous agent workflows (aura_vision, copilot/, generator_studio, pulse/)
│   │   ├── core/                       # Constants, error mapping, and rate limiting middleware
│   │   ├── fixtures/                   # Modular preset fixtures (meadow_wedding, cyber_birthday, diwali_mela)
│   │   ├── integrations/               # Google Maps Places API, Google Calendar (.ics), optional Google Sheets
│   │   ├── llm/                        # Async Gemini GenAI client with retry backoff & error taxonomy
│   │   ├── prompts/                    # Versioned markdown prompts (plan_generation, copilot_system, pulse_narrative)
│   │   ├── schemas/                    # Pydantic v2 schemas (MasterEventPlan, BOQItem, ContingencyDiff)
│   │   └── services/                   # Budget rebalancing and backwards milestone timeline engines
│   ├── tests/                          # 91 automated pytest tests
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                        # Next.js 15 App Router (layout, page, globals.css)
│   │   ├── components/                 # UI components (intake/, vendor/, timeline/, export/, BoqTable, etc.)
│   │   ├── fixtures/                   # Fallback master plan fixtures
│   │   ├── hooks/                      # Unified plan state and history management (usePlanState)
│   │   ├── lib/                        # Typed API clients, date utilities, and export helpers
│   │   └── types/                      # TypeScript domain definitions
│   ├── e2e/                            # Playwright end-to-end and WCAG 2.1 AA accessibility specs
│   ├── package.json
│   └── tsconfig.json
├── docs/
│   ├── DEPLOY.md                       # Google Cloud Run production deployment guide
│   └── submission/                     # Technical blog, video script, and metadata
└── README.md
```

---

## 🏆 Hack2Skill Google PromptWars Submission Pack

* **Deployment Guide**: [`docs/DEPLOY.md`](docs/DEPLOY.md)
* **Technical Blog**: [`docs/submission/TECHNICAL_BLOG.md`](docs/submission/TECHNICAL_BLOG.md)
* **LinkedIn Post**: [`docs/submission/LINKEDIN_POST.md`](docs/submission/LINKEDIN_POST.md)
* **Submission Metadata**: [`docs/submission/SUBMISSION_METADATA.json`](docs/submission/SUBMISSION_METADATA.json)

---

*Crafted for Hack2Skill Google PromptWars (Challenge 5) | Powered by Google Gemini 2.5 Flash & Google Places API.*
