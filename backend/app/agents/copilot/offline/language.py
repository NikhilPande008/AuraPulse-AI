"""Multilingual text processing and language detection for Devanagari and English."""

import re

DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

HINDI_MARKERS = ["है", "हैं", "करो", "करें", "को", "में", "का", "की", "के", "नहीं", "कम करो", "किए", "कीजिए"]
MARATHI_MARKERS = ["आहे", "आहेत", "करा", "करावे", "मध्ये", "ला", "चे", "ची", "नाही", "कमी", "वाजता"]


def normalize_prompt(text: str) -> str:
    """Convert Devanagari numerals to ASCII digits and normalize whitespace.

    Args:
        text: Raw input string containing possible Devanagari numerals.

    Returns:
        Normalized string with ASCII digits.
    """
    return text.translate(DEVANAGARI_DIGITS).strip()


def detect_language(text: str, plan_lang: str | None = None) -> str:
    """Score-based language detection for English, Hindi, and Marathi.

    Args:
        text: Input text prompt.
        plan_lang: Optional plan language override.

    Returns:
        Detected ISO language code: "en", "hi", or "mr".
    """
    if plan_lang in ("hi", "mr", "en"):
        return plan_lang

    has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
    if not has_devanagari:
        return "en"

    hi_score = sum(1 for m in HINDI_MARKERS if m in text)
    mr_score = sum(1 for m in MARATHI_MARKERS if m in text)

    if mr_score > hi_score:
        return "mr"
    return "hi"


# Backward-compatible alias
_detect_language = detect_language
