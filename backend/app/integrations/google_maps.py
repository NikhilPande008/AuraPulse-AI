"""Google Maps Places API (New) integration for verified local vendor search."""

import logging
from typing import Any

import httpx

from ..config import settings

logger = logging.getLogger("aurapulse.integrations.google_maps")


def _unconfigured_response() -> dict[str, Any]:
    return {
        "vendors": [],
        "is_configured": False,
        "status": "SIMULATED",
    }


def _parse_place_item(item: dict[str, Any], rating: float, city: str, query: str) -> dict[str, Any]:
    display_name = item.get("displayName", {})
    name = display_name.get("text", "") if isinstance(display_name, dict) else str(display_name)
    return {
        "place_id": item.get("id"),
        "name": name,
        "address": item.get("formattedAddress", f"{city}, India"),
        "rating": rating,
        "user_ratings_total": item.get("userRatingCount", 0),
        "phone": item.get("nationalPhoneNumber", ""),
        "google_maps_uri": item.get(
            "googleMapsUri",
            f"https://www.google.com/maps/search/?api=1&query={httpx.URL(name).path}",
        ),
        "locality": city,
        "query_matched": query,
        "is_verified": True,
    }


def _filter_places(raw_places: list[dict[str, Any]], min_rating: float, city: str, query: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in raw_places:
        rating = float(item.get("rating", 0.0))
        if rating >= min_rating:
            results.append(_parse_place_item(item, rating, city, query))
    return results[:6]


async def fetch_verified_vendors(query: str, city: str, min_rating: float = 4.0) -> dict[str, Any]:
    """Fetch verified local vendors using Google Maps Places API (New).

    Queries Google Places SearchText endpoint with rating filtering and phone/maps link parsing.
    Returns honest unconfigured status if GOOGLE_MAPS_API_KEY is missing.

    Args:
        query: Vendor search query (e.g., "mandap decorator", "caterer").
        city: Destination or event host city.
        min_rating: Minimum user rating cutoff (default 4.0).

    Returns:
        Dict with vendor records, is_configured flag, and status ('ACTIVE' or 'SIMULATED').
    """
    api_key = str(settings.GOOGLE_MAPS_API_KEY)
    if not api_key:
        logger.info("Google Maps API key not configured. Returning unconfigured status.")
        return _unconfigured_response()

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
    body = {"textQuery": f"{query} in {city}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(endpoint, headers=headers, json=body)
            if response.status_code == 200:
                raw_places = response.json().get("places", [])
                return {
                    "vendors": _filter_places(raw_places, min_rating, city, query),
                    "is_configured": True,
                    "status": "ACTIVE",
                }
            logger.warning(f"Google Places API responded with status {response.status_code}: {response.text}")
            return _unconfigured_response()
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Google Places API (New) search failed: {e}")
        return _unconfigured_response()
