from typing import Any, Dict, Optional

from ..config import settings

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


async def generate_visual_alternative(
    prompt_description: str,
    aspect_ratio: str = "16:9",
    event_theme: str = "Royal Wedding Canopy"
) -> Dict[str, Any]:
    """
    Generative Studio Agent:
    Uses Imagen 3 when configured to render photorealistic
    decor visual alternatives. Otherwise returns a clearly labelled FALLBACK sample image.
    """
    api_key = settings.GEMINI_API_KEY
    imagen_error: Optional[str] = None
    if api_key and genai:
        try:
            client = genai.Client(api_key=api_key)
            result = await client.aio.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=f"Photorealistic architectural render of {prompt_description}, {event_theme}, professional event lighting, cinematic composition",
                config=dict(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                    person_generation="allow_adult"
                )
            )
            if result.generated_images:
                import base64
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
            imagen_error = "Imagen returned no images."
        except Exception as e:
            imagen_error = f"Imagen generation failed: {e}"
    else:
        imagen_error = "GEMINI_API_KEY not configured; Imagen generation unavailable."

    # Honest fallback: an Unsplash sample image, explicitly not AI-generated.
    stock_references = {
        "marquee": "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80",
        "indoor": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80",
        "floral": "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?auto=format&fit=crop&w=1200&q=80",
        "default": "https://images.unsplash.com/photo-1545232979-8bf68ee9b1af?auto=format&fit=crop&w=1200&q=80"
    }

    selected_url = stock_references["default"]
    p_lower = prompt_description.lower()
    if "marquee" in p_lower or "canopy" in p_lower or "rain" in p_lower:
        selected_url = stock_references["marquee"]
    elif "indoor" in p_lower or "ballroom" in p_lower:
        selected_url = stock_references["indoor"]
    elif "floral" in p_lower:
        selected_url = stock_references["floral"]

    return {
        "image_url": selected_url,
        "prompt": prompt_description,
        "model": None,
        "status": "FALLBACK",
        "is_generated": False,
        "source": "Unsplash sample image",
        "error": imagen_error,
    }
