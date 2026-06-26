from typing import TypedDict, List, Optional


class TripState(TypedDict, total=False):
    # User input
    user_input: str
    chat_history: List[str]

    # Extracted trip details
    trip_place: str
    trip_dates: str
    trip_days: int
    trip_style: str
    trip_budget: float
    budget_preference: str

    # Agent outputs
    weather_info: str
    best_time: str
    place_info: str
    transport_info: str
    budget_info: str
    cost_breakdown: dict
    final_itinerary: str

    # Clarification
    need_clarification: bool
    missing_fields: List[str]

    # Behind-the-scenes trace (tool / API calls + outputs)
    trace: List[dict]

    # Misc
    warnings: List[str]

    # ── Replanning metadata (added each turn, not persisted across sessions) ──
    _replan_agents: List[str]      # which agents ran this turn
    _replan_message: str           # human-readable replan summary
    _changed_fields: List[str]     # which trip fields changed this turn

    # Snapshot of trip params from the PREVIOUS turn (used by replan logic)
    _prev_trip_place: str
    _prev_trip_dates: str
    _prev_trip_days: int
    _prev_trip_budget: float
    _prev_trip_style: str

    # Hotel outputs
    hotel_info: str
    hotel_options: list