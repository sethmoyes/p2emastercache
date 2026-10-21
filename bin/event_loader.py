"""
Event loader for the dungeon turn event system.
"""

import json
from typing import Dict, List

CATEGORIES = ['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']


def load_events_from_json(filepath: str) -> Dict[str, List[dict]]:
    """
    Load event templates from dungeon_turn_events.json, one list per category
    (OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        events = json.load(f)
    return {category: events.get(category, []) for category in CATEGORIES}
