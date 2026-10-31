import logging
import httpx
from typing import List, Dict, Any, Optional
from ..config import settings

logger = logging.getLogger("aurapulse.integrations.google_maps")


async def fetch_verified_vendors(
    query: str,
    city: str,
    min_rating: float = 4.0
) -> Dict[str, Any]:
    """
    Vendor Discovery via Google Maps Places API (New) (CR-13):
    Queries https://places.googleapis.com/v1/places:searchText with field masks.
    If GOOGLE_MAPS_API_KEY is unset or invalid:
    Returns an empty vendor list with status: 'SIMULATED' and is_configured: false.
    Never marks unverified or mock vendors with is_verified: True.
    """
    api_key = settings.GOOGLE_MAPS_API_KEY

    # 1. Honest Fallback if Key is Missing
    if not api_key:
        logger.info("Google Maps API key not configured. Returning unconfigured status.")
        return {
            "vendors": [],
            "is_configured": False,
            "status": "SIMULATED",
        }

    search_query = f"{query} in {city}"
    endpoint = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.userRatingCount,"
            "places.nationalPhoneNumber,"
            "places.googleMapsUri"
        ),
    }
    body = {
        "textQuery": search_query,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(endpoint, headers=headers, json=body)
            if response.status_code == 200:
                data = response.json()
                raw_places = data.get("places", [])
                results: List[Dict[str, Any]] = []

                for item in raw_places:
                    rating = float(item.get("rating", 0.0))
                    if rating >= min_rating:
                        display_name = item.get("displayName", {})
                        name = display_name.get("text", "") if isinstance(display_name, dict) else str(display_name)
                        results.append({
                            "place_id": item.get("id"),
                            "name": name,
                            "address": item.get("formattedAddress", f"{city}, India"),
                            "rating": rating,
                            "user_ratings_total": item.get("userRatingCount", 0),
                            "phone": item.get("nationalPhoneNumber", ""),
                            "google_maps_uri": item.get(
                                "googleMapsUri",
                                f"https://www.google.com/maps/search/?api=1&query={httpx.URL(name).path}"
                            ),
                            "locality": city,
                            "query_matched": query,
                            "is_verified": True,
                        })

                return {
                    "vendors": results[:6],
                    "is_configured": True,
                    "status": "ACTIVE",
                }
            else:
                logger.warning(
                    f"Google Places API (New) responded with status {response.status_code}: {response.text}"
                )
                return {
                    "vendors": [],
                    "is_configured": False,
                    "status": "SIMULATED",
                }
    except Exception as e:
        logger.warning(f"Google Places API (New) search failed: {e}")
        return {
            "vendors": [],
            "is_configured": False,
            "status": "SIMULATED",
        }
