"""
Context-Aware Description Generation

This module provides functions to modify event descriptions based on context
parameters. It handles placeholder replacement, space-specific tactical notes,
and party status flavor text.
"""

from event_context import EventContext


def get_space_description(space_type: str) -> str:
    """
    Get descriptive text for a space type.
    
    Args:
        space_type: Type of space
    
    Returns:
        Descriptive text for the space
    """
    space_descriptions = {
        "hallway": "a narrow corridor",
        "large_room": "a spacious chamber",
        "small_room": "a cramped room",
        "outside": "the open area",
        "vertical_space": "a vertical shaft",
        "water": "the flooded passage",
        "unknown": "the area"
    }
    return space_descriptions.get(space_type, "the area")


def apply_context_to_description(description: str, context: EventContext) -> str:
    """
    Apply context-specific modifications to description.
    
    Replaces placeholders in description with context-appropriate text:
    - {space}: Replaced with space description
    - {combat_context}: Replaced with combat reference or empty string
    
    Args:
        description: Original description with optional placeholders
        context: Context parameters
    
    Returns:
        Modified description with placeholders replaced
    """
    # Replace space placeholder
    if "{space}" in description:
        description = description.replace("{space}", get_space_description(context.space_type))
    
    # Replace combat context placeholder
    if "{combat_context}" in description:
        if context.recent_combat:
            description = description.replace("{combat_context}", "from the recent skirmish")
        else:
            description = description.replace("{combat_context}", "")
    
    return description


def apply_space_tactics(tactical_notes: str, space_type: str) -> str:
    """
    Apply space-specific tactical modifications.
    
    Adds space-appropriate tactical considerations to existing tactical notes.
    
    Args:
        tactical_notes: Original tactical notes
        space_type: Type of space
    
    Returns:
        Enhanced tactical notes with space-specific information
    """
    space_tactics = {
        "hallway": "Limited flanking. Reach weapons effective. Single-file movement.",
        "large_room": "Flanking opportunities. Use cover. Multiple approach vectors.",
        "vertical_space": "Height advantage matters. Climbing required. Fall hazards.",
        "outside": "Weather effects. Long sight lines. Open terrain.",
        "water": "Swimming required. Drowning risk. Aquatic advantage.",
        "small_room": "Cramped quarters. Limited movement. Close combat.",
        "unknown": ""
    }
    
    space_note = space_tactics.get(space_type, "")
    if space_note:
        return f"{tactical_notes} {space_note}".strip()
    return tactical_notes


def add_status_flavor(description: str, party_status: str) -> str:
    """
    Add party status flavor to description.
    
    Adds a prefix to the description based on party condition.
    Only adds flavor for non-healthy statuses.
    
    Args:
        description: Original description
        party_status: Party condition (healthy, injured, low_resources)
    
    Returns:
        Description with status flavor prefix (if applicable)
    """
    status_prefixes = {
        "injured": "Despite your wounds, ",
        "low_resources": "With supplies running low, "
    }
    
    prefix = status_prefixes.get(party_status, "")
    if prefix:
        return f"{prefix}{description}"
    return description


def apply_all_context(event: dict, context: EventContext) -> dict:
    """
    Apply all context modifications to an event.
    
    Modifies event description, tactical notes, and adds status flavor
    based on context parameters. This is a convenience function that
    applies all context modifications in the correct order.
    
    Args:
        event: Event dictionary with description and optional tactical_notes
        context: Context parameters
    
    Returns:
        Modified event dictionary
    """
    # Make a copy to avoid modifying original
    event = event.copy()
    
    # Apply context to description
    if 'description' in event:
        event['description'] = apply_context_to_description(
            event['description'],
            context
        )
    
    # Apply space tactics to tactical notes
    if 'tactical_notes' in event:
        event['tactical_notes'] = apply_space_tactics(
            event['tactical_notes'],
            context.space_type
        )
    
    # Apply party status flavor
    if context.party_status != "healthy" and 'description' in event:
        event['description'] = add_status_flavor(
            event['description'],
            context.party_status
        )
    
    return event
