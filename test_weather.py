from agents.weather_agent import weather_agent


test_state = {
    "trip_place": "Goa",
    "trip_days": 3,
    "trip_dates": "26 June to 30 June",
    "trip_style": "family",
    "warnings": [],
    "trace": []
}

result = weather_agent(test_state)

print("\nWEATHER INFO:")
print(result.get("weather_info"))

print("\nBEST TIME:")
print(result.get("best_time"))

print("\nTRACE:")
print(result.get("trace"))

print("\nWARNINGS:")
print(result.get("warnings"))