# AuraPulse AI — Backend Architecture & Invariants

This document outlines the architectural structure, design patterns, and quality invariants governing the FastAPI backend of **AuraPulse AI** (`backend/app`).

---

## 🏗️ 1. Package Layout & Responsibilities

```
backend/app/
├── main.py                        # FastAPI application entrypoint, CORS, exception handlers
├── config.py                      # Pydantic BaseSettings for validated environment configuration
├── api/                           # API Presentation Layer
│   ├── models.py                  # Pydantic request and response models
│   └── routes/                    # Modularized route controllers
│       ├── health.py              # System health and Google API discovery
│       ├── aura.py                # Multimodal vision intake & conversational copilot
│       ├── pulse.py               # Reactive crisis simulation
│       ├── integrations.py        # Maps Places, Sheets export, Calendar sync
│       ├── export.py              # RFC-5545 .ics calendar export
│       └── studio.py              # Imagen 3 generative staging & visual alternatives
├── agents/                        # AI Planning and Copilot Agents
│   ├── aura_vision.py             # Vision-to-BOQ deconstruction agent
│   ├── pulse_engine.py            # Reactive contingency engine & crisis strategy dispatch
│   ├── generator_studio.py        # Generative visual staging agent (Imagen 3)
│   └── copilot/                   # Conversational Ideas & Budget Co-Pilot package
│       ├── service.py             # Chat copilot orchestrator (Gemini path -> offline path)
│       ├── tools.py               # Deterministic replanning tools (scale budget, items, date, headcount)
│       ├── dispatch.py            # Tool registry & Pydantic argument validation
│       ├── gemini_path.py         # Gemini tool-calling execution pipeline
│       ├── diff_builder.py        # Standardized ContingencyDiff constructor
│       ├── models.py              # CopilotResult and wire-format models
│       └── offline/               # Deterministic multilingual intent engine
│           ├── intents.py         # Ordered IntentHandler chain
│           ├── language.py        # Trilingual detector (English, Hindi, Marathi)
│           ├── messages.py        # Grounded multi-turn response templates
│           └── handlers/          # Modularized intent handlers (CC <= 6)
├── core/                          # Cross-Cutting Infrastructure
│   ├── constants.py               # Operational ceilings, timeouts, rate limits, byte limits
│   ├── errors.py                  # Centralized exception handlers & Gemini error mapping
│   ├── middleware.py              # Payload size enforcement (6MB) & sliding-window rate limit
│   └── rate_limit.py              # Sliding-window rate limiter per client IP
├── fixtures/                      # Deterministic Mock Data
│   └── sample_plans.py            # Curated preset event plans for instant offline intake
├── integrations/                  # External Service Adapters
│   ├── google_calendar.py         # RFC-5545 iCalendar (.ics) generation & Web Intent URLs
│   ├── google_maps.py             # Google Places API (New) verified vendor search
│   └── google_sheets.py           # Google Sheets API v4 dynamic formula-driven exporter
├── llm/                           # LLM Infrastructure Layer
│   └── client.py                  # Resilient GenAI client with retry backoff & typed exceptions
├── prompts/                       # Prompt Engineering Layer
│   ├── loader.py                  # In-memory cached Markdown template loader
│   ├── plan_generation.v1.md      # Master event plan system instruction
│   ├── plan_user_payload.v1.md    # Structured user input payload template
│   └── copilot_system.v1.md       # Co-Pilot system instruction
├── schemas/                       # Core Domain Models
│   ├── event_plan.py              # MasterEventPlan, BOQItem, PlanningMilestone, PlanRequest
│   └── contingency.py             # CrisisTrigger, ContingencyDiff, BOQDiffItem
└── services/                      # Deterministic Domain Logic
    ├── budget.py                  # Line-item arithmetic & ceiling rebalancing algorithms
    └── timeline.py                # Backwards planning timeline generator & cultural overrides
```

---

## 🔒 2. Architectural Invariants

Every contribution and refactor must strictly uphold the following invariants:

### A. Complexity Budget (CC $\le 10$)
- **Zero functions $\ge 11$ cyclomatic complexity**: Verified continuously using `radon cc backend/app -s -n C` and `ruff [tool.ruff.lint.mccabe] max-complexity = 10`.
- **Maintainability Index Rank A**: Every module in `backend/app` maintains an index $\ge 20$ (Rank A) via `radon mi`.
- **Enforced via Xenon**: CI enforces `--max-absolute B --max-modules A --max-average A backend/app`.

### B. Strict Static Type Safety
- **Mypy Strict Mode**: The codebase passes `mypy backend/app` with `strict = true` and `plugins = ["pydantic.mypy"]` without error.
- **Zero Untyped Dictionaries on API Boundaries**: All FastAPI route endpoints declare typed Pydantic models for both request bodies and response models.

### C. Deterministic Offline Resilience & Honest Fallbacks
- When external network credentials (`GEMINI_API_KEY`, `GOOGLE_MAPS_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`) are omitted, AuraPulse degrades gracefully:
  * **Aura Vision**: Preset moodboards generate instant, validated plans without network calls. Custom prompts cleanly report 503 instead of fabricating unverified plans.
  * **Co-Pilot**: Offline intent engine handles budget cuts, headcount shifts, date updates, and cultural requests in English, Hindi, and Marathi.
  * **Places API**: Returns `status: "SIMULATED"` and `is_configured: false`, never marking unverified vendors as verified.
  * **Sheets API**: Raises `SheetsNotConfiguredError` (HTTP 503) rather than fabricating fake Google Drive URLs.

### D. Security & Guardrails
- **Payload Size Limit**: Strict 6 MB body limit (`MAX_BODY_BYTES`) rejected via middleware before reading into memory.
- **Image Decompression Check**: 4 MB raw decoded limit on base64 moodboard images with magic-byte validation (`image/jpeg`, `image/png`, `image/webp`).
- **Sliding Window Rate Limiter**: 10 requests/minute and 100 requests/day per client IP on AI-intensive endpoints.
- **Internal Exception Sanitization**: Stack traces and raw internal error strings are scrubbed by `global_exception_handler`.
