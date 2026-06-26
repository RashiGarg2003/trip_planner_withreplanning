"""
Weather agent — uses OpenWeather + one Gemini call.

Uses:
1. OpenWeather for live current weather.
2. Gemini for both:
   - travel-friendly weather summary
   - best time guidance

No Serper used here.
Only one Gemini call is made.
"""

from services.weather_service import get_weather
from services.llm import call_gemini


def build_fallback_weather_summary(place: str, dates: str, live: dict) -> str:
    """
    Fallback summary if Gemini fails.
    This keeps the app working even if Gemini quota is over.
    """

    if not isinstance(live, dict) or "error" in live:
        return f"""
Weather summary for {place}:

Current weather:
Weather information not available.

Travel outlook for {dates}:
Weather outlook could not be generated.

Travel advice:
- Check weather again closer to the travel date.
- Keep your itinerary flexible.

Best time guidance:
Best-time information not available.
""".strip()

    temp = live.get("temp_celsius", "N/A")
    description = live.get("description", "N/A")
    humidity = live.get("humidity", "N/A")

    return f"""
Weather summary for {place}:

Current weather:
- Temperature: {temp}°C
- Condition: {description}
- Humidity: {humidity}%

Travel outlook for {dates}:
Live current weather has been fetched using OpenWeather. Exact future forecast may change, so check again closer to the travel date.

Travel advice:
- Carry comfortable clothes based on the current temperature.
- Keep water, sunscreen, and basic weather protection items.
- Plan major outdoor sightseeing during comfortable daylight hours.

Best time guidance:
Best-time information is not available because Gemini cleanup failed.
""".strip()


def extract_best_time_from_output(gemini_output: str) -> str:
    """
    Extracts the 'Best time guidance' section from Gemini output.
    This does not call Gemini again.
    """

    if not gemini_output:
        return "Best-time information not available."

    marker = "Best time guidance:"

    if marker in gemini_output:
        return gemini_output.split(marker, 1)[1].strip()

    return "Best-time information not available."


def weather_agent(state: dict) -> dict:
    print("running weather agent (OpenWeather + one Gemini call)")

    state["current_agent"] = "weather"

    place = state.get("trip_place", "")
    dates = state.get("trip_dates", "Not specified")
    days = state.get("trip_days", 3)
    style = state.get("trip_style", "general")

    warnings = state.setdefault("warnings", [])
    trace = state.setdefault("trace", [])

    if not place:
        state["weather_info"] = "Weather information not available because destination is missing."
        state["best_time"] = "Best-time information not available."

        warnings.append("Destination missing. Could not fetch weather.")

        trace.append({
            "step": "Weather",
            "source": "OpenWeather + Gemini",
            "output": state["weather_info"]
        })

        return state

    # 1. Fetch live weather from OpenWeather
    live = get_weather(place)

    if isinstance(live, dict) and "error" not in live:
        temp = live.get("temp_celsius", "N/A")
        description = live.get("description", "N/A")
        humidity = live.get("humidity", "N/A")

        live_weather_text = f"""
Current live weather in {place}:
- Temperature: {temp}°C
- Condition: {description}
- Humidity: {humidity}%
""".strip()

    else:
        live_weather_text = f"Live weather could not be fetched for {place}."
        warnings.append(f"Could not fetch live weather for {place}.")

    # 2. One Gemini call for both weather_info and best_time
    prompt = f"""
You are a travel weather assistant.

Create a practical weather report for this trip.

Trip details:
- Destination: {place}
- Travel dates: {dates}
- Number of days: {days}
- Trip style: {style}

OpenWeather live weather data:
{live_weather_text}

Important instructions:
- Use Celsius only.
- Do not use Fahrenheit.
- Do not mention that you are an AI.
- Clearly separate current weather, travel outlook, travel advice, and best time guidance.
- If exact future forecast is not available, say that current weather is live data and future weather should be checked closer to travel dates.
- Make it useful for itinerary planning.
- Keep the answer concise and presentation-friendly.

Output format exactly:

Weather summary for {place}:

Current weather:
- Temperature: ...
- Condition: ...
- Humidity: ...

Travel outlook for {dates}:
...

Travel advice:
- ...
- ...
- ...

Best time guidance:
...
"""

    print("===== SENDING OPENWEATHER DATA TO GEMINI =====")

    gemini_output = call_gemini(prompt)

    if gemini_output:
        weather_summary = gemini_output.strip()
        best_time = extract_best_time_from_output(weather_summary)
        source_used = "OpenWeather + Gemini"
    else:
        weather_summary = build_fallback_weather_summary(place, dates, live)
        best_time = extract_best_time_from_output(weather_summary)
        warnings.append("Gemini weather explanation failed or quota exhausted. Used fallback weather summary.")
        source_used = "OpenWeather fallback"

    state["weather_info"] = weather_summary
    state["best_time"] = best_time
    state["warnings"] = warnings

    # Mark weather agent completed for replanning workflow
    completed_agents = state.setdefault("completed_agents", [])

    if "weather" not in completed_agents:
        completed_agents.append("weather")

    trace.append({
        "step": "Weather + best time",
        "source": source_used,
        "output": {
            "weather": state["weather_info"],
            "best_time": state["best_time"]
        }
    })

    print("===== WEATHER STATE UPDATED =====")
    print(state["weather_info"])

    return state

# """
# Weather agent — fetches current weather + month outlook + best time to visit.

# Uses:
# 1. OpenWeather for live current weather.
# 2. Serper for month/season outlook.
# 3. Serper for best time to visit.

# No Gemini call here, to save quota.
# """

# from services.weather_service import get_weather
# from services.serper_service import search_serper


# def clean_snippet(text: str) -> str:
#     """
#     Cleans Serper snippet text.
#     Keeps it simple. No LLM used.
#     """
#     if not text:
#         return ""

#     text = text.strip()

#     # Remove incomplete trailing ...
#     if text.endswith("..."):
#         text = text[:-3].strip()

#     # Ensure it ends cleanly
#     if text and not text.endswith((".", "!", "?")):
#         text += "."

#     return text


# def _first_snippet(data: dict) -> str:
#     """
#     Extracts the first useful snippet from Serper response.
#     Priority:
#     1. answerBox answer
#     2. answerBox snippet
#     3. first organic result snippet
#     """
#     if not isinstance(data, dict) or "error" in data:
#         return ""

#     answer_box = data.get("answerBox") or {}

#     if answer_box.get("answer"):
#         return clean_snippet(answer_box["answer"])

#     if answer_box.get("snippet"):
#         return clean_snippet(answer_box["snippet"])

#     organic_results = data.get("organic") or []

#     if organic_results:
#         return clean_snippet(organic_results[0].get("snippet", ""))

#     return ""


# def build_weather_advice(place: str, dates: str, live: dict, month_txt: str) -> str:
#     """
#     Creates practical travel advice based on available weather information.
#     This is rule-based and does not call Gemini.
#     """

#     advice = []

#     description = ""
#     temp = None
#     humidity = None

#     if isinstance(live, dict) and "error" not in live:
#         description = str(live.get("description", "")).lower()
#         temp = live.get("temp_celsius")
#         humidity = live.get("humidity")

#     # General useful advice
#     advice.append("Check the forecast again closer to the travel date for more accurate planning.")

#     # Temperature-based advice
#     if temp is not None:
#         try:
#             temp_value = float(temp)

#             if temp_value >= 30:
#                 advice.append("Carry light cotton clothes, sunscreen, sunglasses, and stay hydrated.")
#             elif 20 <= temp_value < 30:
#                 advice.append("Weather looks comfortable for sightseeing and outdoor activities.")
#             elif temp_value < 20:
#                 advice.append("Carry a light jacket or warm layer, especially for mornings and evenings.")
#         except Exception:
#             pass

#     # Rain/cloud advice
#     if "rain" in description or "drizzle" in description:
#         advice.append("Carry an umbrella or raincoat and keep some indoor backup activities.")
#     elif "cloud" in description or "overcast" in description:
#         advice.append("Outdoor plans are still possible, but keep a flexible schedule in case weather changes.")

#     # Humidity advice
#     if humidity is not None:
#         try:
#             humidity_value = float(humidity)

#             if humidity_value >= 75:
#                 advice.append("Humidity is high, so prefer morning/evening sightseeing and carry water.")
#         except Exception:
#             pass

#     # Month-specific generic advice
#     if dates:
#         advice.append(f"For {dates}, plan major outdoor sightseeing during comfortable daylight hours.")

#     return advice


# def weather_agent(state: dict) -> dict:
#     print("running weather agent")

#     place = state.get("trip_place", "")
#     dates = state.get("trip_dates", "Not specified")

#     warnings = state.setdefault("warnings", [])
#     trace = state.setdefault("trace", [])

#     if not place:
#         state["weather_info"] = "Weather information not available because destination is missing."
#         state["best_time"] = "Best-time information not available."

#         warnings.append("Destination missing. Could not fetch weather.")

#         trace.append({
#             "step": "Weather",
#             "source": "OpenWeather + Serper",
#             "output": "Destination missing"
#         })

#         return state

#     # 1. Live current conditions from OpenWeather
#     live = get_weather(place)

#     live_txt = ""

#     if isinstance(live, dict) and "error" not in live:
#         temp = live.get("temp_celsius", "N/A")
#         description = live.get("description", "N/A")
#         humidity = live.get("humidity", "N/A")

#         live_txt = (
#             f"Current weather:\n"
#             f"- Temperature: {temp}°C\n"
#             f"- Condition: {description}\n"
#             f"- Humidity: {humidity}%"
#         )
#     else:
#         warnings.append(f"Could not fetch live weather for {place}.")

#     # 2. Month outlook from Serper
#     month_query = f"{place} weather in {dates} in Celsius travel outlook India"
#     month_data = search_serper(month_query, num_results=3)
#     month_txt = _first_snippet(month_data)

#     # 3. Best time to visit from Serper
#     best_time_query = f"best time to visit {place} weather Celsius"
#     best_time_data = search_serper(best_time_query, num_results=3)
#     best_time_txt = _first_snippet(best_time_data)

#     # 4. Practical travel advice
#     advice_list = build_weather_advice(place, dates, live, month_txt)

#     # 5. Create clean formatted weather summary
#     weather_summary_parts = []

#     weather_summary_parts.append(f"Weather summary for {place}:")

#     if live_txt:
#         weather_summary_parts.append(live_txt)

#     if month_txt:
#         weather_summary_parts.append(
#             f"Travel outlook for {dates}:\n{month_txt}"
#         )

#     if advice_list:
#         advice_text = "Travel advice:\n"
#         for advice in advice_list:
#             advice_text += f"- {advice}\n"

#         weather_summary_parts.append(advice_text.strip())

#     weather_summary = "\n\n".join(weather_summary_parts).strip()

#     if not weather_summary:
#         weather_summary = "Weather information not available."

#     state["weather_info"] = weather_summary
#     state["best_time"] = best_time_txt or "Best-time information not available."
#     state["warnings"] = warnings

#     trace.append({
#         "step": "Weather + best time",
#         "source": "OpenWeather + Serper",
#         "queries": {
#             "month_weather_query": month_query,
#             "best_time_query": best_time_query
#         },
#         "output": {
#             "weather": weather_summary,
#             "best_time": state["best_time"]
#         },
#     })

#     print("===== WEATHER STATE UPDATED =====")
#     print(state["weather_info"])

#     return state

