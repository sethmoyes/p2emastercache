#!/usr/bin/env python3
"""
Event Validation Module

Validates event templates based on quality criteria defined in the design document.
Filters events to ensure they are self-contained, create their own context, and work
within the existing dungeon structure.
"""

import re
from typing import Tuple


def validate_event(event: dict) -> Tuple[bool, str]:
    """
    Validate event against quality criteria.
    
    Args:
        event: Event dictionary to validate
        
    Returns:
        (is_valid, reason) tuple
        
    Rejection criteria:
    - Assumes NPCs present without creating them
    - Assumes specific actions being taken
    - Assumes enemies present without creating them
    - Overly specific prerequisites without context creation
    - Creates new dungeon features (secret passages, shortcuts)
    - Modifies fixed dungeon map
    - Creates passages that don't exist
    
    Acceptance criteria:
    - Works in any context with space parameters
    - Creates own context
    - Clear choices and consequences
    - Rewards clever play
    - Works within the existing, fixed dungeon map
    """
    # Get all text fields to check
    text_fields = _get_text_fields(event)
    combined_text = ' '.join(text_fields).lower()
    
    # Check for invalid patterns
    invalid_result = _check_invalid_patterns(event, combined_text)
    if not invalid_result[0]:
        return invalid_result
    
    # Check for valid patterns
    valid_result = _check_valid_patterns(event, combined_text)
    
    # Return the valid result (which includes the specific reason)
    return valid_result


def _get_text_fields(event: dict) -> list:
    """Extract all text fields from an event for analysis."""
    text_fields = []
    
    # Common fields
    for field in ['title', 'description', 'challenge', 'success', 'failure', 
                  'choice_a', 'choice_b', 'choice_c', 'consequence',
                  'immediate_action', 'gm_notes']:
        if field in event and isinstance(event[field], str):
            text_fields.append(event[field])
    
    return text_fields


def _check_invalid_patterns(event: dict, combined_text: str) -> Tuple[bool, str]:
    """
    Check for invalid patterns that should exclude an event.
    
    Returns:
        (is_valid, reason) - is_valid is False if invalid pattern found
    """
    # Pattern 1: Assumes NPCs present without creating them
    npc_patterns = [
        r'\bthe npc\b',
        r'\ban npc you\b',
        r'\byour npc\b',
        r'\bthe guide\b',
        r'\byour guide\b',
        r'\bthe merchant\b',
        r'\byour ally\b',
        r'\bthe ally\b',
        r'\byour companion\b',
        r'\bthe companion\b',
        r'\bthe prisoner you\b',
        r'\bthe captive you\b',
    ]
    
    for pattern in npc_patterns:
        if re.search(pattern, combined_text):
            return False, f"Assumes NPC present: matched pattern '{pattern}'"
    
    # Pattern 2: Assumes specific actions being taken
    action_patterns = [
        r'\bthe spell you\'?re? casting\b',
        r'\bthe ritual you\'?re? performing\b',
        r'\bthe ward you\'?re? examining\b',
        r'\bthe (magical )?ward you\'?re? examining\b',
        r'\bthe item you\'?re? using\b',
        r'\bthe potion you\'?re? drinking\b',
        r'\bthe scroll you\'?re? reading\b',
        r'\bwhile you\'?re? casting\b',
        r'\bas you cast\b',
        r'\bwhile casting\b',
    ]
    
    for pattern in action_patterns:
        if re.search(pattern, combined_text):
            return False, f"Assumes specific action: matched pattern '{pattern}'"
    
    # Pattern 3: Assumes enemies present without creating them
    enemy_patterns = [
        r'\ban enemy breaks away\b',
        r'\bthe enemy you\'?re? fighting\b',
        r'\byour enemy\b',
        r'\bthe creature you\'?re? fighting\b',
        r'\bone of the enemies\b',
        r'\ban enemy flees\b',
        r'\bthe enemies retreat\b',
    ]
    
    for pattern in enemy_patterns:
        if re.search(pattern, combined_text):
            return False, f"Assumes enemy present: matched pattern '{pattern}'"
    
    # Pattern 4: Creates new dungeon features (secret passages, shortcuts)
    dungeon_modification_patterns = [
        r'\bsecret passage\b',
        r'\bhidden passage\b',
        r'\bshortcut\b',
        r'\bbypass\w* (the|next|several|some)?\s*(room|area|encounter|floor)\b',
        r'\bskip\w* (the|next|several|some)?\s*(room|area|encounter)\b',
        r'\bhidden tunnel\b',
        r'\bsecret tunnel\b',
        r'\bconcealed door that leads\b',
        r'\bpassage that leads to\b',
        r'\btunnel that connects\b',
        r'\bshortcut to\b',
        r'\bbypass to\b',
        r'\bway to bypass\b',
        r'\bskip ahead\b',
    ]
    
    for pattern in dungeon_modification_patterns:
        if re.search(pattern, combined_text):
            return False, f"Creates dungeon feature: matched pattern '{pattern}'"
    
    # Pattern 5: Overly specific prerequisites without context
    # Check for events that require very specific conditions
    if 'requires_recent_combat' in event and event['requires_recent_combat']:
        # These are okay if they create their own context
        if not _creates_own_context(combined_text):
            return False, "Requires recent combat without creating context"
    
    return True, "No invalid patterns found"


def _check_valid_patterns(event: dict, combined_text: str) -> Tuple[bool, str]:
    """
    Check for valid patterns that indicate a good event.
    
    Returns:
        (is_valid, reason) - is_valid is True if valid patterns found
    """
    # Check in order of specificity: most specific to most general
    
    # 1. Check if event rewards clever play (very specific)
    if _rewards_clever_play(event, combined_text):
        return True, "Rewards clever play"
    
    # 2. Check if event works in any context (uses space parameters)
    if 'required_spaces' in event and event['required_spaces']:
        return True, "Works with space parameters"
    
    # 3. Check if event creates its own context (specific pattern)
    if _creates_own_context(combined_text):
        return True, "Creates own context"
    
    # 4. Check if event has clear choices and consequences (more general)
    if _has_clear_choices(event):
        return True, "Has clear choices and consequences"
    
    # 5. If no specific valid pattern found, check if it's a basic valid event
    # (has required fields and no invalid patterns)
    if _has_required_fields(event):
        return True, "Basic valid event structure"
    
    return False, "No valid patterns found"


def _creates_own_context(text: str) -> bool:
    """Check if event creates its own context."""
    context_creation_patterns = [
        r'\byou find\b',
        r'\byou discover\b',
        r'\byou notice\b',
        r'\byou hear\b',
        r'\byou see\b',
        r'\byou smell\b',
        r'\ba .* appears\b',
        r'\ba .* emerges\b',
        r'\ba .* stumbles\b',
        r'\ba .* approaches\b',
        r'\bsuddenly,?\b',
        r'\bwithout warning\b',
        r'\bthe .* (collapses|crumbles|shakes|trembles)\b',
        r'\bthe environment\b',
        r'\bthe room\b',
        r'\bthe hallway\b',
        r'\bthe area\b',
    ]
    
    for pattern in context_creation_patterns:
        if re.search(pattern, text):
            return True
    
    return False


def _has_clear_choices(event: dict) -> bool:
    """Check if event has clear choices and consequences."""
    # DILEMMA events should have choice_a and choice_b
    if 'choice_a' in event and 'choice_b' in event:
        return True
    
    # OPPORTUNITY/COMPLICATION events should have success and failure
    if 'success' in event and 'failure' in event:
        return True
    
    # ACTIVE_THREAT events should have immediate_action and outcomes
    if 'immediate_action' in event and 'success' in event and 'failure' in event:
        return True
    
    return False


def _rewards_clever_play(event: dict, text: str) -> bool:
    """Check if event rewards clever play."""
    reward_patterns = [
        r'\bremove .* dice\b',
        r'\bdice removal\b',
        r'\bsaves? time\b',
        r'\btime benefit\b',
        r'\bavoid\w* encounter\b',
        r'\btactical advantage\b',
        r'\bsurprise round\b',
        r'\badvantage on\b',
    ]
    
    for pattern in reward_patterns:
        if re.search(pattern, text):
            return True
    
    # Check reward field
    if 'reward' in event and event['reward']:
        return True
    
    return False


def _has_required_fields(event: dict) -> bool:
    """Check if event has all required fields."""
    required_fields = {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'}
    return required_fields.issubset(event.keys())


def filter_events(events: dict) -> Tuple[dict, dict]:
    """
    Filter events into valid and invalid collections.
    
    Args:
        events: Dictionary of events by category
        
    Returns:
        (valid_events, invalid_events) tuple of dictionaries
    """
    valid_events = {
        'OPPORTUNITY': [],
        'COMPLICATION': [],
        'DILEMMA': [],
        'ACTIVE_THREAT': []
    }
    
    invalid_events = {
        'OPPORTUNITY': [],
        'COMPLICATION': [],
        'DILEMMA': [],
        'ACTIVE_THREAT': []
    }
    
    for category, event_list in events.items():
        for event in event_list:
            is_valid, reason = validate_event(event)
            
            if is_valid:
                valid_events[category].append(event)
            else:
                # Store event with rejection reason
                event_with_reason = event.copy()
                event_with_reason['_rejection_reason'] = reason
                invalid_events[category].append(event_with_reason)
    
    return valid_events, invalid_events


def get_validation_stats(valid_events: dict, invalid_events: dict) -> dict:
    """
    Get statistics about validation results.
    
    Args:
        valid_events: Dictionary of valid events by category
        invalid_events: Dictionary of invalid events by category
        
    Returns:
        Dictionary with validation statistics
    """
    stats = {
        'total_valid': sum(len(events) for events in valid_events.values()),
        'total_invalid': sum(len(events) for events in invalid_events.values()),
        'by_category': {}
    }
    
    for category in valid_events.keys():
        stats['by_category'][category] = {
            'valid': len(valid_events[category]),
            'invalid': len(invalid_events[category]),
            'total': len(valid_events[category]) + len(invalid_events[category])
        }
    
    # Collect rejection reasons
    rejection_reasons = {}
    for category, event_list in invalid_events.items():
        for event in event_list:
            reason = event.get('_rejection_reason', 'Unknown')
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
    
    stats['rejection_reasons'] = rejection_reasons
    
    return stats
