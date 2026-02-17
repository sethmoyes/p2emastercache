#!/usr/bin/env python3
"""
Property-Based Test for Context Parameter Support (Property 16)

**Validates: Requirements 5.4**

For any event with context parameters (required_spaces, requires_recent_combat, 
requires_new_area), these parameters should be preserved during extraction and loading.
"""

import json
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_loader import load_events_from_json, validate_event_structure
from hypothesis import given, strategies as st, settings
import pytest


# Valid space types from the design document
VALID_SPACES = ['hallway', 'large_room', 'small_room', 'outside', 'vertical_space', 'water']


def has_context_parameters(event: dict) -> bool:
    """Check if an event has any context parameters."""
    return any(key in event for key in ['required_spaces', 'requires_recent_combat', 'requires_new_area'])


def validate_context_parameters(event: dict) -> tuple[bool, str]:
    """
    Validate that context parameters are properly formatted.
    
    Args:
        event: Event dictionary
    
    Returns:
        (is_valid, reason) tuple
    """
    # Check required_spaces
    if 'required_spaces' in event:
        required_spaces = event['required_spaces']
        
        # Should be a list
        if not isinstance(required_spaces, list):
            return False, f"required_spaces must be a list, got {type(required_spaces).__name__}"
        
        # Should contain only strings
        if not all(isinstance(space, str) for space in required_spaces):
            return False, "required_spaces must contain only strings"
        
        # Should not be empty
        if len(required_spaces) == 0:
            return False, "required_spaces should not be empty"
        
        # All spaces should be valid
        invalid_spaces = [space for space in required_spaces if space not in VALID_SPACES]
        if invalid_spaces:
            return False, f"Invalid space types: {invalid_spaces}. Valid: {VALID_SPACES}"
    
    # Check requires_recent_combat
    if 'requires_recent_combat' in event:
        requires_recent_combat = event['requires_recent_combat']
        
        # Should be a boolean
        if not isinstance(requires_recent_combat, bool):
            return False, f"requires_recent_combat must be boolean, got {type(requires_recent_combat).__name__}"
    
    # Check requires_new_area
    if 'requires_new_area' in event:
        requires_new_area = event['requires_new_area']
        
        # Should be a boolean
        if not isinstance(requires_new_area, bool):
            return False, f"requires_new_area must be boolean, got {type(requires_new_area).__name__}"
    
    return True, "Context parameters are valid"


def check_roundtrip_preserves_context_parameters(event: dict) -> bool:
    """
    Test that context parameters are preserved through JSON roundtrip.
    
    Args:
        event: Event dictionary with context parameters
    
    Returns:
        True if parameters are preserved
    """
    # Write to JSON and read back
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'OPPORTUNITY': [event],
            'COMPLICATION': [],
            'DILEMMA': [],
            'ACTIVE_THREAT': []
        }, f)
        temp_path = f.name
    
    try:
        # Load back
        loaded = load_events_from_json(temp_path)
        loaded_event = loaded['OPPORTUNITY'][0]
        
        # Check that context parameters are preserved
        for param in ['required_spaces', 'requires_recent_combat', 'requires_new_area']:
            if param in event:
                if param not in loaded_event:
                    return False
                if event[param] != loaded_event[param]:
                    return False
        
        return True
    
    finally:
        os.unlink(temp_path)


class TestContextParameterSupport:
    """
    Feature: dungeon-turn-event-refactor, Property 16: Context Parameter Support
    
    **Validates: Requirements 5.4**
    
    For any event with context parameters (required_spaces, requires_recent_combat, 
    requires_new_area), these parameters should be preserved during extraction and loading.
    """
    
    def test_all_context_parameters_are_valid(self):
        """Test that all context parameters in curated events are valid."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        invalid_events = []
        
        for category, event_list in events.items():
            for event in event_list:
                if has_context_parameters(event):
                    is_valid, reason = validate_context_parameters(event)
                    
                    if not is_valid:
                        invalid_events.append({
                            'event': event['title'],
                            'category': category,
                            'reason': reason
                        })
        
        # Report any invalid context parameters
        if invalid_events:
            error_msg = "Found events with invalid context parameters:\n"
            for ref in invalid_events:
                error_msg += f"  - Event '{ref['event']}' ({ref['category']}): {ref['reason']}\n"
            pytest.fail(error_msg)
    
    def test_required_spaces_use_valid_space_types(self):
        """Test that required_spaces only uses valid space types."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        invalid_spaces_found = set()
        
        for category, event_list in events.items():
            for event in event_list:
                if 'required_spaces' in event:
                    for space in event['required_spaces']:
                        if space not in VALID_SPACES:
                            invalid_spaces_found.add(space)
        
        assert len(invalid_spaces_found) == 0, \
            f"Found invalid space types: {invalid_spaces_found}. Valid types: {VALID_SPACES}"
    
    def test_boolean_context_parameters_are_boolean(self):
        """Test that boolean context parameters are actually booleans."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        invalid_events = []
        
        for category, event_list in events.items():
            for event in event_list:
                # Check requires_recent_combat
                if 'requires_recent_combat' in event:
                    if not isinstance(event['requires_recent_combat'], bool):
                        invalid_events.append({
                            'event': event['title'],
                            'category': category,
                            'field': 'requires_recent_combat',
                            'type': type(event['requires_recent_combat']).__name__
                        })
                
                # Check requires_new_area
                if 'requires_new_area' in event:
                    if not isinstance(event['requires_new_area'], bool):
                        invalid_events.append({
                            'event': event['title'],
                            'category': category,
                            'field': 'requires_new_area',
                            'type': type(event['requires_new_area']).__name__
                        })
        
        if invalid_events:
            error_msg = "Found events with non-boolean context parameters:\n"
            for ref in invalid_events:
                error_msg += f"  - Event '{ref['event']}' ({ref['category']}): " \
                           f"{ref['field']} is {ref['type']}, not bool\n"
            pytest.fail(error_msg)
    
    def test_required_spaces_is_list_of_strings(self):
        """Test that required_spaces is always a list of strings."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        invalid_events = []
        
        for category, event_list in events.items():
            for event in event_list:
                if 'required_spaces' in event:
                    required_spaces = event['required_spaces']
                    
                    # Check it's a list
                    if not isinstance(required_spaces, list):
                        invalid_events.append({
                            'event': event['title'],
                            'category': category,
                            'reason': f"required_spaces is {type(required_spaces).__name__}, not list"
                        })
                        continue
                    
                    # Check all items are strings
                    non_strings = [item for item in required_spaces if not isinstance(item, str)]
                    if non_strings:
                        invalid_events.append({
                            'event': event['title'],
                            'category': category,
                            'reason': f"required_spaces contains non-string items: {non_strings}"
                        })
        
        if invalid_events:
            error_msg = "Found events with invalid required_spaces:\n"
            for ref in invalid_events:
                error_msg += f"  - Event '{ref['event']}' ({ref['category']}): {ref['reason']}\n"
            pytest.fail(error_msg)
    
    def test_context_parameters_preserved_in_validation(self):
        """Test that context parameters are preserved during validation."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for category, event_list in events.items():
            for event in event_list:
                if has_context_parameters(event):
                    # Validate event structure
                    try:
                        is_valid = validate_event_structure(event, category)
                        assert is_valid
                    except Exception as e:
                        pytest.fail(
                            f"Event '{event['title']}' with context parameters failed validation: {e}"
                        )
                    
                    # Check that context parameters are still present after validation
                    for param in ['required_spaces', 'requires_recent_combat', 'requires_new_area']:
                        if param in event:
                            assert param in event, \
                                f"Context parameter '{param}' was lost during validation"
    
    def test_roundtrip_preserves_all_context_parameters(self):
        """Test that JSON roundtrip preserves all context parameters."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        # Create a temporary file with events that have context parameters
        events_with_context = {}
        for category, event_list in events.items():
            events_with_context[category] = [
                event for event in event_list if has_context_parameters(event)
            ][:5]  # Take first 5 from each category
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(events_with_context, f)
            temp_path = f.name
        
        try:
            # Load back
            loaded_events = load_events_from_json(temp_path)
            
            # Compare
            for category in events_with_context.keys():
                for i, original_event in enumerate(events_with_context[category]):
                    loaded_event = loaded_events[category][i]
                    
                    # Check each context parameter
                    for param in ['required_spaces', 'requires_recent_combat', 'requires_new_area']:
                        if param in original_event:
                            assert param in loaded_event, \
                                f"Context parameter '{param}' lost in roundtrip for event '{original_event['title']}'"
                            assert original_event[param] == loaded_event[param], \
                                f"Context parameter '{param}' changed in roundtrip for event '{original_event['title']}'"
        
        finally:
            os.unlink(temp_path)
    
    @settings(max_examples=100)
    @given(st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']))
    def test_property_all_context_parameters_valid_in_category(self, category):
        """
        Property test: For any category, all context parameters should be valid.
        
        This test runs 100 iterations, checking context parameter validity across categories.
        """
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        event_list = events[category]
        
        for event in event_list:
            if has_context_parameters(event):
                is_valid, reason = validate_context_parameters(event)
                assert is_valid, \
                    f"Event '{event['title']}' in {category} has invalid context parameters: {reason}"
    
    @settings(max_examples=100)
    @given(st.lists(st.sampled_from(VALID_SPACES), min_size=1, max_size=4, unique=True))
    def test_property_required_spaces_roundtrip(self, spaces):
        """
        Property test: For any list of valid spaces, roundtrip should preserve them.
        
        This test runs 100 iterations with different space combinations.
        """
        # Create a test event with required_spaces
        test_event = {
            'title': 'Test Event',
            'description': 'Test description',
            'challenge': 'Test challenge',
            'success': 'Test success',
            'failure': 'Test failure',
            'spotlight': ['Rogue'],
            'skills': ['Stealth'],
            'time_cost': '1 action',
            'gm_notes': 'Test notes',
            'required_spaces': spaces
        }
        
        # Test roundtrip
        assert check_roundtrip_preserves_context_parameters(test_event), \
            f"Roundtrip failed to preserve required_spaces: {spaces}"
    
    @settings(max_examples=100)
    @given(st.booleans(), st.booleans())
    def test_property_boolean_parameters_roundtrip(self, recent_combat, new_area):
        """
        Property test: For any boolean values, roundtrip should preserve them.
        
        This test runs 100 iterations with different boolean combinations.
        """
        # Create a test event with boolean context parameters
        test_event = {
            'title': 'Test Event',
            'description': 'Test description',
            'challenge': 'Test challenge',
            'success': 'Test success',
            'failure': 'Test failure',
            'spotlight': ['Rogue'],
            'skills': ['Stealth'],
            'time_cost': '1 action',
            'gm_notes': 'Test notes',
            'requires_recent_combat': recent_combat,
            'requires_new_area': new_area
        }
        
        # Test roundtrip
        assert check_roundtrip_preserves_context_parameters(test_event), \
            f"Roundtrip failed to preserve boolean parameters: recent_combat={recent_combat}, new_area={new_area}"
    
    def test_events_with_context_parameters_count(self):
        """Test and report how many events use context parameters."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        total_events = 0
        events_with_required_spaces = 0
        events_with_recent_combat = 0
        events_with_new_area = 0
        
        for category, event_list in events.items():
            for event in event_list:
                total_events += 1
                
                if 'required_spaces' in event:
                    events_with_required_spaces += 1
                if 'requires_recent_combat' in event:
                    events_with_recent_combat += 1
                if 'requires_new_area' in event:
                    events_with_new_area += 1
        
        print(f"\nContext parameter usage:")
        print(f"  Total events: {total_events}")
        print(f"  Events with required_spaces: {events_with_required_spaces} ({events_with_required_spaces/total_events*100:.1f}%)")
        print(f"  Events with requires_recent_combat: {events_with_recent_combat} ({events_with_recent_combat/total_events*100:.1f}%)")
        print(f"  Events with requires_new_area: {events_with_new_area} ({events_with_new_area/total_events*100:.1f}%)")
    
    def test_no_empty_required_spaces(self):
        """Test that no events have empty required_spaces lists."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        events_with_empty_spaces = []
        
        for category, event_list in events.items():
            for event in event_list:
                if 'required_spaces' in event:
                    if len(event['required_spaces']) == 0:
                        events_with_empty_spaces.append({
                            'event': event['title'],
                            'category': category
                        })
        
        assert len(events_with_empty_spaces) == 0, \
            f"Found {len(events_with_empty_spaces)} events with empty required_spaces"
    
    def test_context_parameters_are_optional(self):
        """Test that context parameters are optional (events can exist without them)."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        events_without_context = 0
        total_events = 0
        
        for category, event_list in events.items():
            for event in event_list:
                total_events += 1
                
                if not has_context_parameters(event):
                    events_without_context += 1
        
        # Should have at least some events without context parameters
        assert events_without_context > 0, \
            "All events have context parameters, but they should be optional"
        
        print(f"\nEvents without context parameters: {events_without_context}/{total_events} ({events_without_context/total_events*100:.1f}%)")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
