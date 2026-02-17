"""
Event loader module for dungeon turn event system.

Loads and validates event templates from JSON files.
"""

import json
from typing import Dict, List, Optional


class ValidationError(Exception):
    """Raised when event validation fails."""
    pass


def load_events_from_json(filepath: str) -> Dict[str, List[dict]]:
    """
    Load event templates from JSON file.
    
    Args:
        filepath: Path to dungeon_turn_events.json
        
    Returns:
        Dictionary with category keys mapping to event lists:
        - OPPORTUNITY: List of opportunity events
        - COMPLICATION: List of complication events
        - DILEMMA: List of dilemma events
        - ACTIVE_THREAT: List of active threat events
        
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"ERROR: Event file not found: {filepath}\n"
            f"Please ensure dungeon_turn_events.json exists in the etc/ directory"
        )
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"ERROR: Invalid JSON in {filepath}: {e.msg}",
            e.doc,
            e.pos
        )
    
    # Organize by category - ensure all expected categories are present
    expected_categories = ['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']
    organized = {}
    
    for category in expected_categories:
        organized[category] = events.get(category, [])
    
    return organized


def validate_event_structure(event: dict, category: Optional[str] = None) -> bool:
    """
    Validate event has required fields and correct data types.
    
    Args:
        event: Event dictionary to validate
        category: Optional category (OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT)
                 If not provided, will attempt to infer from event fields
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If event is missing required fields or has invalid data types
    """
    # Common required fields for all events
    common_required = {
        'title': str,
        'description': str,
        'spotlight': list,
        'skills': list,
        'time_cost': str,
        'gm_notes': str
    }
    
    # Validate common required fields
    for field, expected_type in common_required.items():
        if field not in event:
            raise ValidationError(
                f"Event '{event.get('title', 'Unknown')}' missing required field '{field}'"
            )
        if not isinstance(event[field], expected_type):
            raise ValidationError(
                f"Event '{event.get('title', 'Unknown')}' field '{field}' must be {expected_type.__name__}, "
                f"got {type(event[field]).__name__}"
            )
    
    # Validate list contents are strings
    for list_field in ['spotlight', 'skills']:
        if not all(isinstance(item, str) for item in event[list_field]):
            raise ValidationError(
                f"Event '{event['title']}' field '{list_field}' must contain only strings"
            )
    
    # Infer category if not provided
    if category is None:
        category = _infer_category(event)
    
    # Validate category-specific required fields
    if category in ['OPPORTUNITY', 'COMPLICATION']:
        category_required = {
            'challenge': str,
            'success': str,
            'failure': str
        }
        for field, expected_type in category_required.items():
            if field not in event:
                raise ValidationError(
                    f"Event '{event['title']}' missing required field '{field}' for category {category}"
                )
            if not isinstance(event[field], expected_type):
                raise ValidationError(
                    f"Event '{event['title']}' field '{field}' must be {expected_type.__name__}, "
                    f"got {type(event[field]).__name__}"
                )
    
    elif category == 'DILEMMA':
        category_required = {
            'choice_a': str,
            'choice_b': str,
            'consequence': str
        }
        for field, expected_type in category_required.items():
            if field not in event:
                raise ValidationError(
                    f"Event '{event['title']}' missing required field '{field}' for category {category}"
                )
            if not isinstance(event[field], expected_type):
                raise ValidationError(
                    f"Event '{event['title']}' field '{field}' must be {expected_type.__name__}, "
                    f"got {type(event[field]).__name__}"
                )
    
    elif category == 'ACTIVE_THREAT':
        category_required = {
            'immediate_action': str,
            'success': str,
            'failure': str,
            'threat_level': str
        }
        for field, expected_type in category_required.items():
            if field not in event:
                raise ValidationError(
                    f"Event '{event['title']}' missing required field '{field}' for category {category}"
                )
            if not isinstance(event[field], expected_type):
                raise ValidationError(
                    f"Event '{event['title']}' field '{field}' must be {expected_type.__name__}, "
                    f"got {type(event[field]).__name__}"
                )
    
    else:
        raise ValidationError(
            f"Unknown event category '{category}'. Valid categories: OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT"
        )
    
    # Validate optional fields if present
    optional_fields = {
        'required_spaces': list,
        'requires_recent_combat': bool,
        'requires_new_area': bool,
        'reward': str,
        'consequence': str,
        'choice_c': str,
        'urgency': str
    }
    
    for field, expected_type in optional_fields.items():
        if field in event and not isinstance(event[field], expected_type):
            raise ValidationError(
                f"Event '{event['title']}' optional field '{field}' must be {expected_type.__name__}, "
                f"got {type(event[field]).__name__}"
            )
    
    # Validate required_spaces contains only strings if present
    if 'required_spaces' in event:
        if not all(isinstance(space, str) for space in event['required_spaces']):
            raise ValidationError(
                f"Event '{event['title']}' field 'required_spaces' must contain only strings"
            )
    
    return True


def _infer_category(event: dict) -> str:
    """
    Infer event category from its fields.
    
    Args:
        event: Event dictionary
        
    Returns:
        Inferred category name
        
    Raises:
        ValidationError: If category cannot be inferred
    """
    # Check for ACTIVE_THREAT fields
    if 'immediate_action' in event and 'threat_level' in event:
        return 'ACTIVE_THREAT'
    
    # Check for DILEMMA fields
    if 'choice_a' in event and 'choice_b' in event:
        return 'DILEMMA'
    
    # Check for OPPORTUNITY/COMPLICATION fields
    if 'challenge' in event:
        # Both use the same fields, default to OPPORTUNITY
        # (caller should provide category if distinction matters)
        return 'OPPORTUNITY'
    
    raise ValidationError(
        f"Cannot infer category for event '{event.get('title', 'Unknown')}'. "
        f"Please provide category parameter."
    )
def organize_events_by_category(events: dict) -> Dict[str, List[dict]]:
    """
    Organize events into category-specific lists with validation.

    Takes a dictionary of events and separates them into category-specific lists.
    Validates that category keys match expected names and returns a dictionary
    with all four required category keys.

    Args:
        events: Dictionary with category keys and event lists

    Returns:
        Dictionary with OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT keys,
        each mapping to a list of events

    Raises:
        ValidationError: If invalid category keys are found
    """
    expected_categories = {'OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT'}

    # Validate category keys
    provided_categories = set(events.keys())
    invalid_categories = provided_categories - expected_categories

    if invalid_categories:
        raise ValidationError(
            f"Invalid category keys found: {', '.join(sorted(invalid_categories))}. "
            f"Valid categories: {', '.join(sorted(expected_categories))}"
        )

    # Organize events by category, ensuring all expected categories are present
    organized = {}
    for category in expected_categories:
        organized[category] = events.get(category, [])

    return organized



