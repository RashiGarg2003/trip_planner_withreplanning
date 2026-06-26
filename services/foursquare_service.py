import os
import requests
from dotenv import load_dotenv

load_dotenv()

FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")



def foursquare_enabled() -> bool:
    return bool(FOURSQUARE_API_KEY)


def search_hotels_foursquare(place: str, limit: int = 5) -> dict:
    """
    Searches hotels near a destination using Foursquare Places API.

    No hardcoded hotel price ranges are used.
    If price data is present in API response, it is used.
    Otherwise price_range is kept as None.
    """

    if not FOURSQUARE_API_KEY:
        return {
            "error": "FOURSQUARE_API_KEY missing",
            "hotels": []
        }

    if not place:
        return {
            "error": "Destination place is missing",
            "hotels": []
        }

    url = "https://places-api.foursquare.com/places/search"

    headers = {
        "Authorization": f"Bearer{FOURSQUARE_API_KEY}",
        "Accept": "application/json"
    }

    params = {
        "query": "hotel",
        "near": place,
        "limit": limit
    }

    try:
        print("===== FOURSQUARE HOTEL SEARCH CALLED =====")
        print("Hotel search place:", place)

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20
        )

        print("Foursquare status code:", response.status_code)

        if response.status_code != 200:
            print("Foursquare raw response:", response.text)

            return {
                "error": f"Foursquare API failed with status code {response.status_code}",
                "details": response.text,
                "hotels": []
            }

        data = response.json()
        results = data.get("results", [])

        hotels = []

        for item in results:
            location = item.get("location", {})
            categories = item.get("categories", [])

            category_names = []

            for category in categories:
                category_name = category.get("name")
                if category_name:
                    category_names.append(category_name)

            hotels.append({
                "name": item.get("name"),
                "address": (
                    location.get("formatted_address")
                    or location.get("address")
                    or "Address not available"
                ),
                "categories": category_names,

                # No hardcoding:
                # These fields are only used if Foursquare sends them.
                "price": item.get("price"),
                "rating": item.get("rating"),
                "distance": item.get("distance"),
                "fsq_id": item.get("fsq_id")
            })

        return {
            "hotels": hotels
        }

    except Exception as e:
        print("Foursquare hotel search error:", e)

        return {
            "error": str(e),
            "hotels": []
        }


def format_hotel_suggestions(hotels: list) -> str:
    """
    Converts Foursquare hotel results into readable text for itinerary prompt.

    No hardcoded price range is added.
    If price is not provided by Foursquare, we clearly say it is not available.
    """

    if not hotels:
        return "Hotel suggestions are not available."

    hotel_text = "Suggested hotel options from Foursquare:\n\n"

    for index, hotel in enumerate(hotels, start=1):
        name = hotel.get("name") or "Unknown hotel"
        address = hotel.get("address") or "Address not available"
        categories = hotel.get("categories") or []
        price = hotel.get("price")
        rating = hotel.get("rating")
        distance = hotel.get("distance")

        category_text = ", ".join(categories) if categories else "Hotel / Accommodation"

        hotel_text += f"{index}. {name}\n"
        hotel_text += f"   Area/Address: {address}\n"
        hotel_text += f"   Type: {category_text}\n"

        if price:
            hotel_text += f"   Price info from Foursquare: {price}\n"
        else:
            hotel_text += "   Price info from Foursquare: Not available\n"

        if rating:
            hotel_text += f"   Rating: {rating}\n"

        if distance:
            hotel_text += f"   Distance: {distance} meters from searched location\n"

        hotel_text += "\n"

    return hotel_text.strip()