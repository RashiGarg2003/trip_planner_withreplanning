from services.foursquare_service import search_hotels_foursquare, format_hotel_suggestions


result = search_hotels_foursquare("Goa", limit=5)

print("\nRAW RESULT:")
print(result)

print("\nFORMATTED HOTEL INFO:")
print(format_hotel_suggestions(result.get("hotels", [])))