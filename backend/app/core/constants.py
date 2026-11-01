"""AuraPulse core architectural constants and thresholds."""

# Budget & Rebalancing Thresholds
OPERATIONAL_FLOOR: float = 0.50
EMERGENCY_MARQUEE_COST_INR: float = 185_000.0

# Rate Limiting
RATE_LIMIT_PER_MINUTE: int = 10
RATE_LIMIT_PER_DAY: int = 100

# Network & Payload Constraints
MAX_BODY_BYTES: int = 6 * 1024 * 1024  # 6 MB
MAX_IMAGE_BYTES: int = 4 * 1024 * 1024  # 4 MB decoded limit

# Gemini LLM Timeouts (seconds)
PLAN_GENERATION_TIMEOUT: float = 30.0
COPILOT_TIMEOUT: float = 12.0
CRISIS_NARRATIVE_TIMEOUT: float = 10.0
STUDIO_TIMEOUT: float = 10.0
