from typing import Set
 
FIELD_AGENT_MAP = {
    "trip_place":  {"weather", "destination", "transport", "budget", "itinerary"},
    "trip_dates":  {"weather", "destination", "itinerary"},
    "trip_days":   {"destination", "budget", "itinerary"},
    "trip_budget": {"budget", "itinerary"},
    "trip_style":  {"destination", "itinerary"},
}
 
ALL_AGENTS = ["weather", "destination", "transport", "budget", "itinerary"]
 
 
def detect_changed_fields(prev_state: dict, new_state: dict) -> Set[str]:
    changed = set()
 
    for field in FIELD_AGENT_MAP.keys():
        old_val = prev_state.get(field)
        new_val = new_state.get(field)
 
        if isinstance(old_val, str):
            old_val = old_val.strip().lower()
        if isinstance(new_val, str):
            new_val = new_val.strip().lower()
 
        if old_val != new_val:
           
            if new_val is not None:
                changed.add(field)
 
    return changed
 
 
def agents_to_run(changed_fields: Set[str], is_first_run: bool) -> list:
    if is_first_run:
        return ALL_AGENTS
 
    if not changed_fields:
        return []
 
    needed = set()
    for field in changed_fields:
        needed |= FIELD_AGENT_MAP.get(field, set())
 
    if needed - {"itinerary"}:
        needed.add("itinerary")
 
    return [a for a in ALL_AGENTS if a in needed]
 
 
def describe_replan(changed_fields: Set[str], agents: list) -> str:
    if not changed_fields:
        return "No changes detected — skipping all agents."
 
    field_labels = {
        "trip_place":  "destination",
        "trip_dates":  "travel dates",
        "trip_days":   "trip duration",
        "trip_budget": "budget",
        "trip_style":  "trip style",
    }
 
    changed_readable = [field_labels.get(f, f) for f in changed_fields]
    skipped = [a for a in ALL_AGENTS if a not in agents]
 
    msg = f"Changed: {', '.join(changed_readable)}. "
    msg += f"Re-running: {', '.join(agents)}."
    if skipped:
        msg += f" Skipping: {', '.join(skipped)}."
    return msg
 