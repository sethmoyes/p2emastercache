#!/usr/bin/env python3
"""
Property-based tests for JSON loading functionality.

**Validates: Requirements 4.1, 4.3, 9.2**
"""

import json
import os
import tempfile
from hypothesis import given, strategies as st, settings
from event_loader import load_events_from_json, organize_events_by_category


# Strategy for generating valid event dictionaries
def event_strategy(category: str):
    """Generate a valid event for the given category."""
    # Common fields for all events
    common = {
        'title': st.text(min_size=1, max_size=100),
        'description': st.text(min_size=1, max_size=500),
        'spotlight': st.lists(st.sampled_from(['Rogue', 'Fighter', 'Wizard', 'Cleric', 'Monk', 'All']), min_size=1, max_size=3),
        'skills': st.lists(st.sampled_from(['Perception', 'Stealth', 'Athletics', 'Thievery', 'Arcana', 'Religion']), min_size=1, max_size=3),
        'time_cost': st.sampled_from(['1 action', '2 actions', '10 minutes', '30 minutes', '1 round']),
        'gm_notes': st.text(min_size=1, max_size=200)
    }
    
    # Category-specific fields
    if category in ['OPPORTUNITY', 'COMPLICATION']:
        category_fields = {
            'challenge': st.text(min_size=1, max_size=100),
            'success': st.text(min_size=1, max_size=200),
            'failure': st.text(min_size=1, max_size=200)
        }
    elif category == 'DILEMMA':
        category_fields = {
            'choice_a': st.text(min_size=1, max_size=200),
            'choice_b': st.text(min_size=1, max_size=200),
            'consequence': st.text(min_size=1, max_size=200)
        }
    elif category == 'ACTIVE_THREAT':
        category_fields = {
            'immediate_action': st.text(min_size=1, max_size=200),
            'success': st.text(min_size=1, max_size=200),
            'failure': st.text(min_size=1, max_size=200),
            'threat_level': st.sampled_from(['Low', 'Moderate', 'High', 'Critical'])
        }
    else:
        category_fields = {}
    
    # Combine common and category-specific fields
    all_fields = {**common, **category_fields}
    
    return st.fixed_dictionaries(all_fields)


# Strategy for generating a complete events dictionary
@st.composite
def events_dict_strategy(draw):
    """Generate a dictionary with all event categories."""
    return {
        'OPPORTUNITY': draw(st.lists(event_strategy('OPPORTUNITY'), min_size=0, max_size=10)),
        'COMPLICATION': draw(st.lists(event_strategy('COMPLICATION'), min_size=0, max_size=10)),
        'DILEMMA': draw(st.lists(event_strategy('DILEMMA'), min_size=0, max_size=10)),
        'ACTIVE_THREAT': draw(st.lists(event_strategy('ACTIVE_THREAT'), min_size=0, max_size=10))
    }


@given(events_dict_strategy())
@settings(max_examples=100)
def test_property_successful_json_loading(events):
    """
    **Property 9: Successful JSON Loading**
    **Validates: Requirements 4.1, 4.3, 9.2**
    
    For any valid JSON event file, the generator script should successfully load it
    and organize events into category-specific lists matching the original structure.
    
    This test verifies that:
    1. Valid JSON files can be loaded without errors
    2. Events are organized into the correct category lists
    3. All event data is preserved during the load process
    4. The structure matches the expected format
    """
    # Create a temporary JSON file with the generated events
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(events, f)
        temp_path = f.name
    
    try:
        # Load the events from JSON
        loaded_events = load_events_from_json(temp_path)
        
        # Property 1: All expected categories should be present
        assert 'OPPORTUNITY' in loaded_events, "OPPORTUNITY category missing"
        assert 'COMPLICATION' in loaded_events, "COMPLICATION category missing"
        assert 'DILEMMA' in loaded_events, "DILEMMA category missing"
        assert 'ACTIVE_THREAT' in loaded_events, "ACTIVE_THREAT category missing"
        
        # Property 2: Event counts should match
        assert len(loaded_events['OPPORTUNITY']) == len(events['OPPORTUNITY']), \
            f"OPPORTUNITY count mismatch: expected {len(events['OPPORTUNITY'])}, got {len(loaded_events['OPPORTUNITY'])}"
        assert len(loaded_events['COMPLICATION']) == len(events['COMPLICATION']), \
            f"COMPLICATION count mismatch: expected {len(events['COMPLICATION'])}, got {len(loaded_events['COMPLICATION'])}"
        assert len(loaded_events['DILEMMA']) == len(events['DILEMMA']), \
            f"DILEMMA count mismatch: expected {len(events['DILEMMA'])}, got {len(loaded_events['DILEMMA'])}"
        assert len(loaded_events['ACTIVE_THREAT']) == len(events['ACTIVE_THREAT']), \
            f"ACTIVE_THREAT count mismatch: expected {len(events['ACTIVE_THREAT'])}, got {len(loaded_events['ACTIVE_THREAT'])}"
        
        # Property 3: Event data should be preserved
        for category in ['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']:
            for i, original_event in enumerate(events[category]):
                loaded_event = loaded_events[category][i]
                
                # Check that all original fields are present and match
                for field, value in original_event.items():
                    assert field in loaded_event, \
                        f"Field '{field}' missing in loaded event from category {category}"
                    assert loaded_event[field] == value, \
                        f"Field '{field}' value mismatch in category {category}: expected {value}, got {loaded_event[field]}"
        
        # Property 4: organize_events_by_category should work with loaded events
        organized = organize_events_by_category(loaded_events)
        
        # Verify organization preserves structure
        assert set(organized.keys()) == {'OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT'}, \
            "Organized events should have all four categories"
        
        for category in organized.keys():
            assert len(organized[category]) == len(loaded_events[category]), \
                f"Organization changed event count for {category}"
    
    finally:
        # Clean up temporary file
        os.unlink(temp_path)


@given(events_dict_strategy())
@settings(max_examples=100)
def test_property_json_roundtrip_preserves_data(events):
    """
    **Property 9: Successful JSON Loading (Round-trip variant)**
    **Validates: Requirements 4.1, 4.3, 9.2**
    
    For any valid events dictionary, writing it to JSON and loading it back
    should preserve all data exactly.
    """
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(events, f)
        temp_path = f.name
    
    try:
        # Load the events back
        loaded_events = load_events_from_json(temp_path)
        
        # Verify complete data preservation
        assert loaded_events == events, \
            "Round-trip through JSON should preserve all event data exactly"
    
    finally:
        os.unlink(temp_path)


@given(st.lists(event_strategy('OPPORTUNITY'), min_size=1, max_size=20))
@settings(max_examples=100)
def test_property_loading_preserves_event_order(opportunity_events):
    """
    **Property 9: Successful JSON Loading (Order preservation)**
    **Validates: Requirements 4.1, 4.3, 9.2**
    
    For any list of events in a category, loading from JSON should preserve
    the order of events.
    """
    events = {
        'OPPORTUNITY': opportunity_events,
        'COMPLICATION': [],
        'DILEMMA': [],
        'ACTIVE_THREAT': []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(events, f)
        temp_path = f.name
    
    try:
        loaded_events = load_events_from_json(temp_path)
        
        # Verify order is preserved
        for i, original_event in enumerate(opportunity_events):
            loaded_event = loaded_events['OPPORTUNITY'][i]
            assert loaded_event['title'] == original_event['title'], \
                f"Event order not preserved: position {i} has wrong event"
    
    finally:
        os.unlink(temp_path)


def test_property_loading_real_curated_file():
    """
    **Property 9: Successful JSON Loading (Real file test)**
    **Validates: Requirements 4.1, 4.3, 9.2**
    
    The actual curated events file should load successfully and have the
    expected structure.
    """
    curated_file = '/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events.json'
    
    # Skip if file doesn't exist (for CI environments)
    if not os.path.exists(curated_file):
        return
    
    # Load the real curated file
    loaded_events = load_events_from_json(curated_file)
    
    # Verify structure
    assert 'OPPORTUNITY' in loaded_events
    assert 'COMPLICATION' in loaded_events
    assert 'DILEMMA' in loaded_events
    assert 'ACTIVE_THREAT' in loaded_events
    
    # Verify all categories have events (should have 500+ total)
    total_events = sum(len(events) for events in loaded_events.values())
    assert total_events >= 500, \
        f"Curated file should have at least 500 events, found {total_events}"
    
    # Verify events are organized correctly
    organized = organize_events_by_category(loaded_events)
    assert organized == loaded_events, \
        "Loaded events should already be properly organized"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
