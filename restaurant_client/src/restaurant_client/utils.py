from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd


def _price_tier_to_min_price(price_tier: Optional[int]) -> Optional[str]:
    """
    Foursquare often returns a price tier (commonly 1-4).
    We'll represent "min price" as the lowest tier symbol.
    """
    if price_tier is None:
        return None
    if not isinstance(price_tier, int):
        return None
    if price_tier <= 0:
        return None
    # 1->"$", 2->"$$", 3->"$$$", 4->"$$$$"
    return "$" * min(price_tier, 4)


def _extract_hours(hours_obj: Any) -> Dict[str, Optional[Any]]:
    """
    Try to extract open-hours info if present.
    Different responses may vary; keep it defensive.
    """
    if not isinstance(hours_obj, dict):
        return {"open_now": None, "hours_display": None}

    open_now = hours_obj.get("open_now")
    display = hours_obj.get("display")

    # Sometimes "display" isn't available; we keep None.
    return {"open_now": open_now, "hours_display": display}


def places_to_dataframe(payload: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert a Foursquare /places/search response JSON into a clean DataFrame.
    """
    results: List[Dict[str, Any]] = payload.get("results", []) or []
    rows: List[Dict[str, Any]] = []

    for r in results:
        loc = r.get("location") or {}
        geos = (r.get("geocodes") or {}).get("main") or {}
        cats = r.get("categories") or []
        category_name: Optional[str] = cats[0].get("name") if cats else None

        rows.append(
            {
                "fsq_place_id": r.get("fsq_place_id") or r.get("fsq_id"),
                "name": r.get("name"),
                "category": category_name,
                "address": loc.get("address"),
                "locality": loc.get("locality"),
                "region": loc.get("region"),
                "postcode": loc.get("postcode"),
                "country": loc.get("country"),
                "distance_m": r.get("distance"),
                "latitude": geos.get("latitude"),
                "longitude": geos.get("longitude"),
            }
        )

    return pd.DataFrame(rows)


def place_details_to_row(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a /places/{id} details response into a flat dict row
    with rating, min_price, and open hours (when available).
    """
    loc = details.get("location") or {}
    geos = (details.get("geocodes") or {}).get("main") or {}
    cats = details.get("categories") or []
    category_name: Optional[str] = cats[0].get("name") if cats else None

    rating = details.get("rating")
    price_tier = details.get("price")
    min_price = _price_tier_to_min_price(price_tier)

    hours_info = _extract_hours(details.get("hours"))

    return {
        "fsq_place_id": details.get("fsq_place_id") or details.get("fsq_id"),
        "name": details.get("name"),
        "category": category_name,
        "address": loc.get("address"),
        "locality": loc.get("locality"),
        "region": loc.get("region"),
        "postcode": loc.get("postcode"),
        "country": loc.get("country"),
        "latitude": geos.get("latitude"),
        "longitude": geos.get("longitude"),
        "rating": rating,
        "price_tier": price_tier,
        "min_price": min_price,              # "$", "$$", "$$$", "$$$$"
        "open_now": hours_info["open_now"],  # True/False/None
        "hours": hours_info["hours_display"], # string or None
        "tel": details.get("tel"),
        "website": details.get("website"),
    }
