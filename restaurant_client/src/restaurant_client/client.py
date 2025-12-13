from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import requests


class FoursquareAuthError(RuntimeError):
    """Raised when the API key is missing or invalid (401/403)."""


class FoursquareRequestError(RuntimeError):
    """Raised for non-auth API errors (4xx/5xx)."""


@dataclass
class RestaurantClient:
    api_key: Optional[str] = None
    version: str = "2025-06-17"
    base_url: str = "https://places-api.foursquare.com"

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.getenv("FOURSQUARE_API_KEY")
        if not self.api_key:
            raise FoursquareAuthError(
                "Missing API key. Set env var FOURSQUARE_API_KEY before calling the API."
            )

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Places-Api-Version": self.version,
        }

    def _get(self, url: str, params: Optional[Dict[str, Union[str, int]]] = None) -> Dict[str, Any]:
        try:
            resp = requests.get(url, headers=self._headers(), params=params, timeout=20)
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Network error calling Foursquare: {e}") from e

        if resp.status_code in (401, 403):
            raise FoursquareAuthError(f"Auth error ({resp.status_code}): {resp.text}")
        if resp.status_code >= 400:
            raise FoursquareRequestError(f"API error ({resp.status_code}): {resp.text}")

        try:
            return resp.json()
        except ValueError as e:
            raise FoursquareRequestError(
                f"Invalid JSON response: {e}\nBody: {resp.text[:500]}"
            ) from e

    def search_places(
        self,
        query: str,
        near: str,
        limit: int = 10,
        radius: Optional[int] = None,
        categories: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for places using Foursquare /places/search.

        Note: this returns the raw JSON payload. Use utils.places_to_dataframe(...)
        or the CLI to get a DataFrame.
        """
        if not query or not isinstance(query, str):
            raise ValueError("`query` must be a non-empty string.")
        if not near or not isinstance(near, str):
            raise ValueError("`near` must be a non-empty string, e.g. 'Atlanta, GA'.")
        if limit <= 0 or limit > 50:
            raise ValueError("`limit` must be between 1 and 50.")

        url = f"{self.base_url}/places/search"
        params: Dict[str, Union[str, int]] = {"query": query, "near": near, "limit": limit}
        if radius is not None:
            if radius <= 0:
                raise ValueError("`radius` must be a positive integer (meters).")
            params["radius"] = radius
        if categories is not None:
            params["categories"] = categories

        return self._get(url, params=params)

    def get_place_details(self, fsq_place_id: str) -> Dict[str, Any]:
        """
        Fetch details for a single place.

        We request common useful fields like rating, price, and hours (when available).
        """
        if not fsq_place_id or not isinstance(fsq_place_id, str):
            raise ValueError("`fsq_place_id` must be a non-empty string.")

        url = f"{self.base_url}/places/{fsq_place_id}"

        # Foursquare supports a `fields` query param. If fields are unavailable or vary,
        # this still safely returns whatever the API provides.
        params: Dict[str, Union[str, int]] = {
            "fields": ",".join(
                [
                    "fsq_place_id",
                    "name",
                    "categories",
                    "location",
                    "geocodes",
                    "rating",
                    "price",
                    "hours",
                    "tel",
                    "website",
                ]
            )
        }

        return self._get(url, params=params)
