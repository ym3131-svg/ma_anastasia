from restaurant_client.utils import places_to_dataframe, place_details_to_row


def test_places_to_dataframe_empty():
    df = places_to_dataframe({"results": []})
    assert df.empty


def test_places_to_dataframe_basic():
    payload = {
        "results": [
            {
                "fsq_place_id": "abc123",
                "name": "Test Restaurant",
                "distance": 120,
                "location": {"address": "1 Main St", "locality": "Atlanta", "region": "GA"},
                "geocodes": {"main": {"latitude": 33.7, "longitude": -84.3}},
                "categories": [{"name": "Ramen"}],
            }
        ]
    }
    df = places_to_dataframe(payload)
    assert len(df) == 1
    assert df.loc[0, "name"] == "Test Restaurant"
    assert df.loc[0, "category"] == "Ramen"


def test_place_details_to_row_extracts_fields():
    details = {
        "fsq_place_id": "abc123",
        "name": "Test Restaurant",
        "rating": 8.6,
        "price": 2,
        "hours": {"open_now": True, "display": "Mon-Sun 11:00-21:00"},
        "location": {"address": "1 Main St", "locality": "Atlanta", "region": "GA"},
        "geocodes": {"main": {"latitude": 33.7, "longitude": -84.3}},
        "categories": [{"name": "Ramen"}],
    }
    row = place_details_to_row(details)
    assert row["rating"] == 8.6
    assert row["price_tier"] == 2
    assert row["min_price"] == "$$"
    assert row["open_now"] is True
    assert "Mon-Sun" in (row["hours"] or "")
