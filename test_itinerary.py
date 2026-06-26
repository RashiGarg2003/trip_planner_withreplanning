from agents.itinerary_agent import itinerary_agent


test_state = {
    "trip_place": "Goa",
    "trip_dates": "December",
    "trip_days": 3,
    "trip_style": "family",
    "trip_budget": 50000,

    "best_time": "December is a good time to visit Goa because the weather is pleasant and suitable for beaches and sightseeing.",
    "weather_info": "Weather is expected to be warm and comfortable. Carry light clothes and sunscreen.",
    "place_info": """
Top places to explore in Goa:

1. Calangute Beach
   Popular for water sports and beach activities.

2. Baga Beach
   Known for beach shacks and nightlife.

3. Fort Aguada
   Historic fort with sea views.

4. Basilica of Bom Jesus
   Famous heritage church in Old Goa.
""",
    "transport_info": "Local transport options include taxis, rented scooters, app cabs, and buses.",
    "budget_info": "Estimated total budget: Rs 50000. Accommodation: Rs 18000, Food: Rs 9000, Local transport: Rs 6000, Sightseeing: Rs 5000, Intercity travel: Rs 12000.",
    "cost_breakdown": {
        "per_day": [16000, 17000, 17000]
    },

    "warnings": [],
    "trace": []
}

result = itinerary_agent(test_state)

print("\nHOTEL INFO:")
print(result.get("hotel_info"))

print("\nFINAL ITINERARY:")
print(result.get("final_itinerary"))

print("\nTRACE:")
print(result.get("trace"))

print("\nWARNINGS:")
print(result.get("warnings"))