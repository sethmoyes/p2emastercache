#!/usr/bin/env python3
"""
Property-Based Test for Event Validation (Property 12)

**Validates: Requirements 4.6, 6.3, 6.5**

For any loaded event, all required fields for its category should be present,
and all choices should have defined outcomes.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_loader import load_events_from_json, validate_event_structure, ValidationError
from hypothesis import given, strategies as st, settings, assume
import pytest


class TestEventValidation:
    """
    Feature: dungeon-turn-event-refactor, Property 12: Event Validation
    
    **Validates: Requirements 4.6, 6.3, 6.5**
    
    For any loaded event, all required fields for its category should be present,
    and all choices should have defined outcomes.
    """
    
    def test_all_curated_events_have_required_fields(self):
        """Test that all events in curated file have required fields for their category."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Load curated events
        events = load_events_from_json(curated_file)
        
        # Track validation results
        total_events = 0
        validated_events = 0
        
        # Validate each event in each category
        for category, event_list in events.items():
            for event in event_list:
                total_events += 1
                
                # Validate event structure
                try:
                    is_valid = validate_event_structure(event, category)
                    assert is_valid, f"Event '{event['title']}' failed validation"
                    validated_events += 1
                except ValidationError as e:
                    pytest.fail(
                        f"Event '{event.get('title', 'Unknown')}' in category {category} "
                        f"missing required fields: {e}"
                    )
        
        # Ensure we validated all events
        assert total_events > 0, "No events found in curated file"
        assert validated_events == total_events, \
            f"Only {validated_events}/{total_events} events passed validation"
    
    def test_all_opportunity_events_have_outcomes(self):
        """Test that all OPPORTUNITY events have defined success and failure outcomes."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for event in events['OPPORTUNITY']:
            # Check required outcome fields
            assert 'challenge' in event, \
                f"OPPORTUNITY event '{event['title']}' missing 'challenge' field"
            assert 'success' in event, \
                f"OPPORTUNITY event '{event['title']}' missing 'success' field"
            assert 'failure' in event, \
                f"OPPORTUNITY event '{event['title']}' missing 'failure' field"
            
            # Check that outcomes are non-empty strings
            assert isinstance(event['challenge'], str) and len(event['challenge']) > 0, \
                f"OPPORTUNITY event '{event['title']}' has empty challenge"
            assert isinstance(event['success'], str) and len(event['success']) > 0, \
                f"OPPORTUNITY event '{event['title']}' has empty success outcome"
            assert isinstance(event['failure'], str) and len(event['failure']) > 0, \
                f"OPPORTUNITY event '{event['title']}' has empty failure outcome"
    
    def test_all_complication_events_have_outcomes(self):
        """Test that all COMPLICATION events have defined success and failure outcomes."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for event in events['COMPLICATION']:
            # Check required outcome fields
            assert 'challenge' in event, \
                f"COMPLICATION event '{event['title']}' missing 'challenge' field"
            assert 'success' in event, \
                f"COMPLICATION event '{event['title']}' missing 'success' field"
            assert 'failure' in event, \
                f"COMPLICATION event '{event['title']}' missing 'failure' field"
            
            # Check that outcomes are non-empty strings
            assert isinstance(event['challenge'], str) and len(event['challenge']) > 0, \
                f"COMPLICATION event '{event['title']}' has empty challenge"
            assert isinstance(event['success'], str) and len(event['success']) > 0, \
                f"COMPLICATION event '{event['title']}' has empty success outcome"
            assert isinstance(event['failure'], str) and len(event['failure']) > 0, \
                f"COMPLICATION event '{event['title']}' has empty failure outcome"
    
    def test_all_dilemma_events_have_choices_and_outcomes(self):
        """Test that all DILEMMA events have defined choices with outcomes."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for event in events['DILEMMA']:
            # Check required choice fields
            assert 'choice_a' in event, \
                f"DILEMMA event '{event['title']}' missing 'choice_a' field"
            assert 'choice_b' in event, \
                f"DILEMMA event '{event['title']}' missing 'choice_b' field"
            assert 'consequence' in event, \
                f"DILEMMA event '{event['title']}' missing 'consequence' field"
            
            # Check that choices are non-empty strings
            assert isinstance(event['choice_a'], str) and len(event['choice_a']) > 0, \
                f"DILEMMA event '{event['title']}' has empty choice_a"
            assert isinstance(event['choice_b'], str) and len(event['choice_b']) > 0, \
                f"DILEMMA event '{event['title']}' has empty choice_b"
            assert isinstance(event['consequence'], str) and len(event['consequence']) > 0, \
                f"DILEMMA event '{event['title']}' has empty consequence"
            
            # If choice_c exists, it should also be non-empty
            if 'choice_c' in event:
                assert isinstance(event['choice_c'], str) and len(event['choice_c']) > 0, \
                    f"DILEMMA event '{event['title']}' has empty choice_c"
    
    def test_all_active_threat_events_have_outcomes(self):
        """Test that all ACTIVE_THREAT events have defined action and outcomes."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for event in events['ACTIVE_THREAT']:
            # Check required threat fields
            assert 'immediate_action' in event, \
                f"ACTIVE_THREAT event '{event['title']}' missing 'immediate_action' field"
            assert 'success' in event, \
                f"ACTIVE_THREAT event '{event['title']}' missing 'success' field"
            assert 'failure' in event, \
                f"ACTIVE_THREAT event '{event['title']}' missing 'failure' field"
            assert 'threat_level' in event, \
                f"ACTIVE_THREAT event '{event['title']}' missing 'threat_level' field"
            
            # Check that outcomes are non-empty strings
            assert isinstance(event['immediate_action'], str) and len(event['immediate_action']) > 0, \
                f"ACTIVE_THREAT event '{event['title']}' has empty immediate_action"
            assert isinstance(event['success'], str) and len(event['success']) > 0, \
                f"ACTIVE_THREAT event '{event['title']}' has empty success outcome"
            assert isinstance(event['failure'], str) and len(event['failure']) > 0, \
                f"ACTIVE_THREAT event '{event['title']}' has empty failure outcome"
            assert isinstance(event['threat_level'], str) and len(event['threat_level']) > 0, \
                f"ACTIVE_THREAT event '{event['title']}' has empty threat_level"
    
    def test_all_events_have_common_required_fields(self):
        """Test that all events have common required fields."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        common_required_fields = ['title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes']
        
        for category, event_list in events.items():
            for event in event_list:
                for field in common_required_fields:
                    assert field in event, \
                        f"{category} event '{event.get('title', 'Unknown')}' missing required field '{field}'"
                    
                    # Check data types
                    if field in ['spotlight', 'skills']:
                        assert isinstance(event[field], list), \
                            f"{category} event '{event['title']}' field '{field}' must be list"
                        assert len(event[field]) > 0, \
                            f"{category} event '{event['title']}' field '{field}' is empty"
                        assert all(isinstance(item, str) for item in event[field]), \
                            f"{category} event '{event['title']}' field '{field}' must contain only strings"
                    else:
                        assert isinstance(event[field], str), \
                            f"{category} event '{event['title']}' field '{field}' must be string"
                        assert len(event[field]) > 0, \
                            f"{category} event '{event['title']}' field '{field}' is empty"
    
    @settings(max_examples=100)
    @given(st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']))
    def test_property_all_events_in_category_validate(self, category):
        """
        Property test: For any category, all events in that category should pass validation.
        
        This test runs 100 iterations, sampling events from each category.
        """
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        # Get events for this category
        event_list = events[category]
        
        # Skip if category is empty
        assume(len(event_list) > 0)
        
        # Validate all events in this category
        for event in event_list:
            try:
                is_valid = validate_event_structure(event, category)
                assert is_valid, f"Event '{event['title']}' in {category} failed validation"
            except ValidationError as e:
                pytest.fail(
                    f"Event '{event.get('title', 'Unknown')}' in {category} "
                    f"failed validation: {e}"
                )
    
    @settings(max_examples=100)
    @given(st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']))
    def test_property_all_events_have_defined_outcomes(self, category):
        """
        Property test: For any category, all events should have defined outcomes for their choices.
        
        This test runs 100 iterations, verifying that outcomes are present and non-empty.
        """
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        # Get events for this category
        event_list = events[category]
        
        # Skip if category is empty
        assume(len(event_list) > 0)
        
        # Check outcomes based on category
        for event in event_list:
            if category in ['OPPORTUNITY', 'COMPLICATION']:
                # Should have challenge, success, failure
                assert 'challenge' in event and len(event['challenge']) > 0, \
                    f"{category} event '{event['title']}' missing or empty challenge"
                assert 'success' in event and len(event['success']) > 0, \
                    f"{category} event '{event['title']}' missing or empty success"
                assert 'failure' in event and len(event['failure']) > 0, \
                    f"{category} event '{event['title']}' missing or empty failure"
            
            elif category == 'DILEMMA':
                # Should have choice_a, choice_b, consequence
                assert 'choice_a' in event and len(event['choice_a']) > 0, \
                    f"DILEMMA event '{event['title']}' missing or empty choice_a"
                assert 'choice_b' in event and len(event['choice_b']) > 0, \
                    f"DILEMMA event '{event['title']}' missing or empty choice_b"
                assert 'consequence' in event and len(event['consequence']) > 0, \
                    f"DILEMMA event '{event['title']}' missing or empty consequence"
                
                # If choice_c exists, it should be non-empty
                if 'choice_c' in event:
                    assert len(event['choice_c']) > 0, \
                        f"DILEMMA event '{event['title']}' has empty choice_c"
            
            elif category == 'ACTIVE_THREAT':
                # Should have immediate_action, success, failure, threat_level
                assert 'immediate_action' in event and len(event['immediate_action']) > 0, \
                    f"ACTIVE_THREAT event '{event['title']}' missing or empty immediate_action"
                assert 'success' in event and len(event['success']) > 0, \
                    f"ACTIVE_THREAT event '{event['title']}' missing or empty success"
                assert 'failure' in event and len(event['failure']) > 0, \
                    f"ACTIVE_THREAT event '{event['title']}' missing or empty failure"
                assert 'threat_level' in event and len(event['threat_level']) > 0, \
                    f"ACTIVE_THREAT event '{event['title']}' missing or empty threat_level"
    
    def test_validation_consistency_across_runs(self):
        """Test that validation is consistent across multiple runs."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Load events twice
        events1 = load_events_from_json(curated_file)
        events2 = load_events_from_json(curated_file)
        
        # Validate both loads
        for category in events1.keys():
            for i, (event1, event2) in enumerate(zip(events1[category], events2[category])):
                # Both should validate the same way
                try:
                    valid1 = validate_event_structure(event1, category)
                    valid2 = validate_event_structure(event2, category)
                    assert valid1 == valid2, \
                        f"Validation inconsistent for event {i} in {category}"
                except ValidationError as e:
                    pytest.fail(f"Validation failed inconsistently: {e}")
    
    def test_no_events_missing_category_specific_fields(self):
        """Test that no events are missing category-specific required fields."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        # Define category-specific required fields
        category_fields = {
            'OPPORTUNITY': ['challenge', 'success', 'failure'],
            'COMPLICATION': ['challenge', 'success', 'failure'],
            'DILEMMA': ['choice_a', 'choice_b', 'consequence'],
            'ACTIVE_THREAT': ['immediate_action', 'success', 'failure', 'threat_level']
        }
        
        for category, required_fields in category_fields.items():
            for event in events[category]:
                for field in required_fields:
                    assert field in event, \
                        f"{category} event '{event['title']}' missing required field '{field}'"
                    assert isinstance(event[field], str), \
                        f"{category} event '{event['title']}' field '{field}' must be string"
                    assert len(event[field]) > 0, \
                        f"{category} event '{event['title']}' field '{field}' is empty"
    
    def test_optional_fields_have_correct_types(self):
        """Test that optional fields, when present, have correct data types."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        optional_field_types = {
            'required_spaces': list,
            'requires_recent_combat': bool,
            'requires_new_area': bool,
            'reward': str,
            'consequence': str,
            'choice_c': str,
            'urgency': str
        }
        
        for category, event_list in events.items():
            for event in event_list:
                for field, expected_type in optional_field_types.items():
                    if field in event:
                        assert isinstance(event[field], expected_type), \
                            f"{category} event '{event['title']}' optional field '{field}' " \
                            f"must be {expected_type.__name__}, got {type(event[field]).__name__}"
                        
                        # If it's a list, check it contains only strings
                        if expected_type == list:
                            assert all(isinstance(item, str) for item in event[field]), \
                                f"{category} event '{event['title']}' field '{field}' must contain only strings"
                        
                        # If it's a string, check it's non-empty
                        if expected_type == str:
                            assert len(event[field]) > 0, \
                                f"{category} event '{event['title']}' optional field '{field}' is empty"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
