import pytest
from restaurant_client.client import RestaurantClient


def test_search_places_validates_inputs(monkeypatch):
    monkeypatch.setenv("FOURSQUARE_API_KEY", "fake")
    client = RestaurantClient()

    with pytest.raises(ValueError):
        client.search_places(query="", near="Atlanta, GA")

    with pytest.raises(ValueError):
        client.search_places(query="ramen", near="")

    with pytest.raises(ValueError):
        client.search_places(query="ramen", near="Atlanta, GA", limit=0)
