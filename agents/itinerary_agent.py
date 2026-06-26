"""
Itinerary (composer) agent — final step.

Uses Gemini to write a warm, guided, day-by-day itinerary grounded on data
collected by the previous agents.

Now also uses Foursquare API to fetch hotel suggestions.
No hardcoded hotel names or price ranges are used.
"""

from services.llm import call_gemini
from services.foursquare_service import search_hotels_foursquare, format_hotel_suggestions


def itinerary_agent(state: dict) -> dict:
    print("running itinerary (composer) agent")

    state["current_agent"] = "itinerary"

    place = state.get("trip_place", "")
    dates = state.get("trip_dates", "Not specified")
    days = state.get("trip_days", 3)
    style = state.get("trip_style", "general")
    budget = state.get("trip_budget", 0)

    cb = state.get("cost_breakdown") or {}
    warnings = state.setdefault("warnings", [])
    trace = state.setdefault("trace", [])

    if not place:
        state["final_itinerary"] = "Please provide a destination to generate an itinerary."

        trace.append({
            "step": "Itinerary",
            "source": "Gemini",
            "output": state["final_itinerary"]
        })

        return state

    # 1. Fetch hotel suggestions from Foursquare
    hotel_result = search_hotels_foursquare(
        place=place,
        limit=5
    )

    if "error" in hotel_result:
        warnings.append(
            f"Could not fetch hotel suggestions from Foursquare: {hotel_result.get('error')}"
        )
        hotels = []
    else:
        hotels = hotel_result.get("hotels", [])

    hotel_info = format_hotel_suggestions(hotels)

    # Store hotel data separately for UI/sidebar/debugging
    state["hotel_options"] = hotels
    state["hotel_info"] = hotel_info

    # 2. Prepare per-day cost text
    per_day_txt = ""

    if cb.get("per_day"):
        per_day_txt = (
            "Use these per-day spend figures, they vary by day: "
            + ", ".join(f"Day {i + 1} = Rs {c}" for i, c in enumerate(cb["per_day"]))
        )

    # 3. Gemini prompt for final itinerary
    prompt = f"""
You are a friendly, practical travel planner.

Write a guided, day-by-day itinerary in Markdown for a {days}-day {style} trip to {place} ({dates}).

Use ONLY the real information gathered below.
Do not invent famous attractions that are not present in the destination data.

BEST TIME TO VISIT:
{state.get('best_time', 'Not available')}

WEATHER:
{state.get('weather_info', 'Not available')}

TOP PLACES:
{state.get('place_info', 'Not available')}

TRANSPORT:
{state.get('transport_info', 'Not available')}

BUDGET BREAKDOWN:
{state.get('budget_info', 'Not available')}

HOTEL SUGGESTIONS FROM FOURSQUARE:
{hotel_info}

User's budget: INR {budget if budget and budget > 0 else 'not provided'}.
{per_day_txt}

Important hotel rules:
- Use only the hotels provided in the Foursquare hotel suggestions.
- Do not invent hotel names.
- Do not invent exact hotel prices.
- If Foursquare price information says "Not available", clearly mention that live price was not available from Foursquare.
- If rating or distance is available, you may use it.
- Suggest suitable stay areas based on the itinerary and hotel address/category data.
- Keep hotel recommendations practical for the user's trip style.

FORMAT STRICTLY:

For each day use a header line exactly like:
### Day 1 - <short theme>

Then include:
- **Morning:** what to do and why, 1-2 sentences
- **Afternoon:** what to do and why, 1-2 sentences
- **Evening:** what to do and why, 1-2 sentences
- **Stay:** suggested area or suitable hotel option from Foursquare
- **Approx cost:** Rs <use the per-day figure for that day if available>

Day 1 morning should include arrival/check-in.
The final day should include departure.
Spread the real places sensibly across the days and respect the weather.

After the day-wise plan, add this section:

## 🏨 Suggested Hotels

Create a Markdown table with these columns:
Hotel, Area/Address, Type, Price info from Foursquare, Best for

Use only the Foursquare hotel suggestions.
If price info is not available, write "Not available from Foursquare".

After that, add this section:

## 💰 Expense Summary

Create a Markdown table with:
Accommodation, Food, Local transport, Sightseeing, Intercity travel, Total

Use the budget breakdown figures if available.
Then add one line saying whether the trip fits the user's budget.

End with:

## Why these choices?

Explain the key reasoning in 2-3 lines.
"""

    itinerary = call_gemini(prompt)

    state["final_itinerary"] = itinerary or "Could not generate the itinerary."
    state["warnings"] = warnings

    # Mark itinerary agent completed for replanning workflow
    completed_agents = state.setdefault("completed_agents", [])

    if "itinerary" not in completed_agents:
        completed_agents.append("itinerary")

    trace.append({
        "step": "Itinerary (composer)",
        "source": "Gemini + Foursquare",
        "output": "Final itinerary composed with Foursquare hotel suggestions",
        "hotels_used": [hotel.get("name", "") for hotel in hotels],
        "hotel_count": len(hotels)
    })

    print("===== ITINERARY STATE UPDATED =====")
    print(state["final_itinerary"])

    return state


# """
# Itinerary (composer) agent — final step.

# Uses the LLM to write a warm, guided, day-by-day plan (Morning / Afternoon /
# Evening with explanations), grounded on everything the other agents fetched.
# Per-day costs come from the budget breakdown, so they vary by day.
# """

# from services.llm import call_gemini


# def itinerary_agent(state: dict) -> dict:
#     print("running itinerary (composer) agent")
#     place = state.get("trip_place", "")
#     dates = state.get("trip_dates", "Not specified")
#     days = state.get("trip_days", 3)
#     style = state.get("trip_style", "general")
#     budget = state.get("trip_budget", 0)
#     cb = state.get("cost_breakdown") or {}
#     warnings = state.get("warnings", [])

#     if not place:
#         state["final_itinerary"] = "Please provide a destination to generate an itinerary."
#         return state

#     per_day_txt = ""
#     if cb.get("per_day"):
#         per_day_txt = "Use these per-day spend figures (they vary by day): " + \
#             ", ".join(f"Day {i+1} = Rs {c}" for i, c in enumerate(cb["per_day"]))

#     prompt = f"""
# You are a friendly, practical travel planner. Write a guided, day-by-day itinerary
# in Markdown for a {days}-day {style} trip to {place} ({dates}).

# Use ONLY the real information gathered below (do not invent famous places):

# BEST TIME TO VISIT:
# {state.get('best_time', 'Not available')}

# WEATHER:
# {state.get('weather_info', 'Not available')}

# TOP PLACES (from live search):
# {state.get('place_info', 'Not available')}

# TRANSPORT (from live search):
# {state.get('transport_info', 'Not available')}

# BUDGET BREAKDOWN:
# {state.get('budget_info', 'Not available')}

# User's budget: INR {budget if budget and budget > 0 else 'not provided'}.
# {per_day_txt}

# FORMAT (strict):
# For each day use a header line exactly like '### Day 1 - <short theme>' and then:
# - **Morning:** what to do and why (1-2 sentences)
# - **Afternoon:** ...
# - **Evening:** ...
# - **Stay:** suggested area to stay
# - **Approx cost:** Rs <use the per-day figure for that day>

# Day 1 morning should be arrival/check-in; the final day should include departure.
# Spread the real places sensibly across the days and respect the weather.

# After the days, add a section '## 💰 Expense Summary' with a Markdown table of
# Accommodation, Food, Local transport, Sightseeing, Intercity travel and the Total
# (use the budget breakdown figures), then one line saying whether it fits the budget.

# End with '## Why these choices?' — explain the key reasoning in 2-3 lines.
# """
#     itinerary = call_gemini(prompt)
#     state["final_itinerary"] = itinerary or "Could not generate the itinerary (LLM unavailable)."
#     state["warnings"] = warnings
#     state.setdefault("trace", []).append({
#         "step": "Itinerary (composer)",
#         "source": "Gemini",
#         "output": f"{days}-day itinerary composed",
#     })
#     return state
