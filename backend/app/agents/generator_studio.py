"""Generator Studio: Visual alternative rendering using Imagen 3 or curated fallback references."""

import base64
from typing import Any

import google.api_core.exceptions

from ..config import settings

genai: Any = None
types: Any = None
_GENAI_AVAILABLE = False

try:
    import google.genai as _genai
    import google.genai.types as _types

    genai = _genai
    types = _types
    _GENAI_AVAILABLE = True
except (ImportError, KeyError):
    pass

STOCK_REFERENCES: dict[str, str] = {
    "marquee": "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80",
    "indoor": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80",
    "floral": "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?auto=format&fit=crop&w=1200&q=80",
    "default": "https://images.unsplash.com/photo-1545232979-8bf68ee9b1af?auto=format&fit=crop&w=1200&q=80",
}


def _select_stock_image(prompt_description: str) -> str:
    p_lower = prompt_description.lower()
    if any(k in p_lower for k in ("marquee", "canopy", "rain")):
        return STOCK_REFERENCES["marquee"]
    if any(k in p_lower for k in ("indoor", "ballroom")):
        return STOCK_REFERENCES["indoor"]
    if "floral" in p_lower:
        return STOCK_REFERENCES["floral"]
    return STOCK_REFERENCES["default"]


async def _generate_with_imagen(
    prompt_description: str, aspect_ratio: str, event_theme: str, api_key: str
) -> dict[str, Any] | None:
    if not (_GENAI_AVAILABLE and genai):
        return None
    try:
        client = genai.Client(api_key=api_key)
        prompt_text = (
            f"Photorealistic architectural render of {prompt_description}, {event_theme}, "
            f"professional event lighting, cinematic composition"
        )
        result = await client.aio.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt_text,
            config={"number_of_images": 1, "aspect_ratio": aspect_ratio, "person_generation": "allow_adult"},
        )
        if result.generated_images:
            img_bytes = result.generated_images[0].image.image_bytes
            b64_data = base64.b64encode(img_bytes).decode("utf-8")
            return {
                "image_url": f"data:image/png;base64,{b64_data}",
                "prompt": prompt_description,
                "model": "imagen-3.0-generate-002",
                "status": "GENERATED",
                "is_generated": True,
                "source": "Google Imagen 3 (imagen-3.0-generate-002)",
                "error": None,
            }
    except (google.api_core.exceptions.GoogleAPIError, ValueError, KeyError, OSError, RuntimeError):
        pass
    return None


async def generate_visual_alternative(
    prompt_description: str, aspect_ratio: str = "16:9", event_theme: str = "Royal Wedding Canopy"
) -> dict[str, Any]:
    """Generate visual renders for event staging using Imagen 3 or curated fallback imagery.

    Args:
        prompt_description: Descriptive prompt of the scene to generate.
        aspect_ratio: Image aspect ratio (e.g., '16:9', '1:1', '4:3').
        event_theme: Overall aesthetic theme to guide rendering style.

    Returns:
        Dict containing image_url, generation metadata, status, and source attribution.
    """
    api_key = str(settings.GEMINI_API_KEY)
    if api_key:
        generated = await _generate_with_imagen(prompt_description, aspect_ratio, event_theme, api_key)
        if generated is not None:
            return generated

    selected_url = _select_stock_image(prompt_description)
    return {
        "image_url": selected_url,
        "prompt": prompt_description,
        "model": None,
        "status": "FALLBACK",
        "is_generated": False,
        "source": "Unsplash sample image",
        "error": "Imagen generation unavailable; using sample image.",
    }
