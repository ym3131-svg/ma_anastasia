from __future__ import annotations

import argparse
from typing import Optional

import pandas as pd

from .client import RestaurantClient
from .utils import place_details_to_row, places_to_dataframe


def _print_df(df: pd.DataFrame, max_rows: int = 25) -> None:
    if df.empty:
        print("No results.")
        return
    # terminal-friendly preview
    print(df.head(max_rows).to_string(index=False))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="restaurant-client",
        description="Search restaurants using the Foursquare Places API and return a DataFrame preview.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    search = sub.add_parser("search", help="Search for restaurants/places")
    search.add_argument("--query", required=True, help='Search term, e.g. "ramen"')
    search.add_argument("--near", required=True, help='Location string, e.g. "Atlanta, GA"')
    search.add_argument("--limit", type=int, default=10, help="Number of results (1-50)")
    search.add_argument("--radius", type=int, default=None, help="Radius in meters (optional)")
    search.add_argument("--categories", default=None, help="Comma-separated category IDs (optional)")
    search.add_argument(
        "--details",
        action="store_true",
        help="Fetch details for each place (rating, price, hours) and include them in the output.",
    )

    args = parser.parse_args(argv)

    # Basic format checks (clear errors)
    if not args.query.strip():
        raise ValueError("Invalid format: --query must be a non-empty string.")
    if not args.near.strip():
        raise ValueError('Invalid format: --near must be a non-empty string, e.g. "Atlanta, GA".')
    if args.limit < 1 or args.limit > 50:
        raise ValueError("Invalid format: --limit must be between 1 and 50.")
    if args.radius is not None and args.radius <= 0:
        raise ValueError("Invalid format: --radius must be a positive integer (meters).")

    client = RestaurantClient()

    if args.cmd == "search":
        payload = client.search_places(
            query=args.query,
            near=args.near,
            limit=args.limit,
            radius=args.radius,
            categories=args.categories,
        )

        base_df = places_to_dataframe(payload)

        if not args.details:
            _print_df(base_df)
            return 0

        # Enrich with details (simple + legit)
        rows = []
        for place_id in base_df.get("fsq_place_id", []).dropna().tolist():
            details = client.get_place_details(str(place_id))
            rows.append(place_details_to_row(details))

        df = pd.DataFrame(rows)
        _print_df(df)
        return 0

    return 1
