# Antigravity Agent Rules for AuraPulse AI

1. Architecture Consistency:
   - Always use Pydantic models with `strict=True` for any JSON exchanged with Gemini.
   - Never write mock placeholder logic for Google API endpoints; use standard Google Client libraries.
   - Keep data flows strictly decoupled: Client -> FastAPI Gateway -> Reasoning Core / Tool Fabric.

2. Code Quality:
   - Backend: Async FastAPI endpoints with typed error handling (HTTPException) and SSE streaming.
   - Frontend: Clean React functional components, strictly typed TypeScript props, and Tailwind utility classes. Avoid heavy external UI component suites.
   - State: Maintain single source of truth for MasterEventPlan and deterministic ContingencyDiff tracking.

3. Verification Protocol:
   - After creating or modifying any backend route, run an automated pytest or curl check to verify response structure.
   - After creating frontend components, verify compilation, asset loading, and UI interactivity.
   - Ensure complete end-to-end flow executes from visual input to BOQ generation to crisis simulation.
