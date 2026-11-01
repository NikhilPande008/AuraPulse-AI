"""Prompt template loader with in-memory caching."""

import functools
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent


@functools.cache
def load_prompt(name: str) -> str:
    """Load a versioned prompt template from disk with caching.

    Args:
        name: Filename of the prompt template (e.g. "plan_generation.v1.md").

    Returns:
        The stripped string content of the prompt template.

    Raises:
        FileNotFoundError: If the prompt template does not exist in PROMPTS_DIR.
    """
    prompt_file = PROMPTS_DIR / name
    if not prompt_file.is_file():
        raise FileNotFoundError(f"Prompt template '{name}' not found in {PROMPTS_DIR}")
    return prompt_file.read_text(encoding="utf-8").strip()
