"""
Template Selection

Picks an event template for a floor: retired templates never roll, a floor's
own templates are preferred, and generic templates (floor 0) fill in.
"""

import random
from typing import List, Dict, Any

# Chance of drawing from a floor's own templates when it has any
FLOOR_SPECIFIC_CHANCE = 0.75


def select_template(templates: List[Dict[str, Any]], floor: int = None) -> Dict[str, Any]:
    """
    Pick a template for this floor.

    Args:
        templates: Event template dictionaries
        floor: Floor number (1-10). If provided, only returns events for
               that floor or generic events (floor=0)

    Raises:
        ValueError: If templates list is empty
    """
    if not templates:
        raise ValueError("Cannot select from empty template list")

    # Retired templates contradict the floor references in common/; keep them on file but never roll them
    templates = [t for t in templates if not t.get('retired')] or templates

    if floor is not None:
        # Events with floor=0 are generic (appear on all floors)
        # Events with floor=1-10 only appear on that specific floor
        on_floor = [t for t in templates if t.get('floor', 0) in (0, floor)]
        templates = on_floor or templates

        # Prefer this floor's own events over generic ones, so the floor's ecology dominates
        floor_specific = [t for t in templates if t.get('floor', 0) == floor]
        if floor_specific and random.random() < FLOOR_SPECIFIC_CHANCE:
            return random.choice(floor_specific)

    return random.choice(templates)
