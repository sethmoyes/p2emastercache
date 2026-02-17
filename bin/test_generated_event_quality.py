#!/usr/bin/env python3
"""
Property-Based Test for Generated Event Quality

Tests that newly generated events follow the same structure and pass the same
validation criteria as existing validated events.

Feature: dungeon-turn-event-refactor, Property 8: Generated Event Quality
**Validates: Requirements 3.10, 3.12**
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_validation import validate_event, filter_events, get_validation_stats

import pytest
from hypothesis import given, strategies as st, settings, assume


class TestGeneratedEventQuality:
    """
    Feature: dungeon-turn-event-refactor, Property 8: Generated Event Quality
    
    **Validates: Requirements 3.10, 3.12**
    
    For any newly generated event, it should follow the same structure and pass 
    the same validation criteria as existing validated events.
    """
    
    def test_all_generated_events_pass_validation(self):
        """Test that all 500 generated events pass validation."""
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Validate all events
        valid_events, invalid_events = filter_events(generated_events)
        
        # Get stats
        stats = get_validation_stats(valid_events, invalid_events)
        
        # All generated events should be valid
        assert stats['total_invalid'] == 0, \
            f"Found {stats['total_invalid']} invalid generated events. " \
            f"Rejection reasons: {stats['rejection_reasons']}"
        
        # Should have exactly 500 valid events
        assert stats['total_valid'] == 500, \
            f"Expected 500 valid events, got {stats['total_valid']}"
        
        # Should have 125 events per category
        for category, counts in stats['by_category'].items():
            assert counts['valid'] == 125, \
                f"Expected 125 valid {category} events, got {counts['valid']}"
    
    def test_generated_events_have_required_fields(self):
        """Test that all generated events have required fields."""
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Required fields for all events
        required_fields = {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'}
        
        # Check each event
        for category, events in generated_events.items():
            for event in events:
                # Check common required fields
                for field in required_fields:
                    assert field in event, \
                        f"Generated event '{event.get('title', 'UNKNOWN')}' in {category} " \
                        f"missing required field '{field}'"
                
                # Check category-specific fields
                if category in ['OPPORTUNITY', 'COMPLICATION']:
                    # Should have challenge, success, failure
                    assert 'challenge' in event, \
                        f"Generated {category} event '{event['title']}' missing 'challenge'"
                    assert 'success' in event, \
                        f"Generated {category} event '{event['title']}' missing 'success'"
                    assert 'failure' in event, \
                        f"Generated {category} event '{event['title']}' missing 'failure'"
                
                elif category == 'DILEMMA':
                    # Should have choice_a and choice_b
                    assert 'choice_a' in event, \
                        f"Generated DILEMMA event '{event['title']}' missing 'choice_a'"
                    assert 'choice_b' in event, \
                        f"Generated DILEMMA event '{event['title']}' missing 'choice_b'"
                
                elif category == 'ACTIVE_THREAT':
                    # Should have immediate_action, success, failure, threat_level
                    assert 'immediate_action' in event, \
                        f"Generated ACTIVE_THREAT event '{event['title']}' missing 'immediate_action'"
                    assert 'success' in event, \
                        f"Generated ACTIVE_THREAT event '{event['title']}' missing 'success'"
                    assert 'failure' in event, \
                        f"Generated ACTIVE_THREAT event '{event['title']}' missing 'failure'"
                    assert 'threat_level' in event, \
                        f"Generated ACTIVE_THREAT event '{event['title']}' missing 'threat_level'"
    
    def test_generated_events_have_correct_data_types(self):
        """Test that generated events have correct data types for fields."""
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Check each event
        for category, events in generated_events.items():
            for event in events:
                # String fields
                string_fields = ['title', 'description', 'time_cost', 'gm_notes']
                for field in string_fields:
                    if field in event:
                        assert isinstance(event[field], str), \
                            f"Event '{event['title']}' field '{field}' should be string, " \
                            f"got {type(event[field])}"
                
                # List fields
                list_fields = ['spotlight', 'skills']
                for field in list_fields:
                    if field in event:
                        assert isinstance(event[field], list), \
                            f"Event '{event['title']}' field '{field}' should be list, " \
                            f"got {type(event[field])}"
                        # Lists should contain strings
                        for item in event[field]:
                            assert isinstance(item, str), \
                                f"Event '{event['title']}' field '{field}' should contain strings, " \
                                f"got {type(item)}"
                
                # Optional list field
                if 'required_spaces' in event:
                    assert isinstance(event['required_spaces'], list), \
                        f"Event '{event['title']}' field 'required_spaces' should be list"
                
                # Optional boolean fields
                if 'requires_recent_combat' in event:
                    assert isinstance(event['requires_recent_combat'], bool), \
                        f"Event '{event['title']}' field 'requires_recent_combat' should be bool"
                
                if 'requires_new_area' in event:
                    assert isinstance(event['requires_new_area'], bool), \
                        f"Event '{event['title']}' field 'requires_new_area' should be bool"
    
    def test_generated_events_avoid_invalid_patterns(self):
        """Test that generated events don't contain invalid patterns."""
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Invalid patterns to check for
        invalid_patterns = {
            'npc_assumption': ['the npc', 'an npc you', 'your npc', 'the guide', 'your guide', 
                              'the merchant', 'your ally', 'the ally', 'your companion'],
            'action_assumption': ['spell you\'re casting', 'ritual you\'re performing', 
                                 'ward you\'re examining', 'potion you\'re drinking'],
            'enemy_assumption': ['enemy breaks away', 'enemy you\'re fighting', 'your enemy',
                                'creature you\'re fighting', 'one of the enemies'],
            'dungeon_modification': ['secret passage', 'hidden passage', 'shortcut', 
                                    'bypass the', 'skip the', 'hidden tunnel', 'secret tunnel']
        }
        
        # Check each event
        for category, events in generated_events.items():
            for event in events:
                # Get all text from event
                text_fields = []
                for field in ['title', 'description', 'challenge', 'success', 'failure',
                            'choice_a', 'choice_b', 'choice_c', 'consequence',
                            'immediate_action', 'gm_notes']:
                    if field in event and isinstance(event[field], str):
                        text_fields.append(event[field])
                
                combined_text = ' '.join(text_fields).lower()
                
                # Check for invalid patterns
                for pattern_type, patterns in invalid_patterns.items():
                    for pattern in patterns:
                        assert pattern not in combined_text, \
                            f"Generated event '{event['title']}' contains invalid pattern " \
                            f"'{pattern}' ({pattern_type})"
    
    def test_generated_events_match_category_distribution(self):
        """Test that generated events are distributed evenly across categories."""
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Check distribution
        expected_per_category = 125
        
        for category in ['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']:
            assert category in generated_events, \
                f"Generated events missing category '{category}'"
            
            count = len(generated_events[category])
            assert count == expected_per_category, \
                f"Expected {expected_per_category} {category} events, got {count}"
    
    def test_generated_events_have_variety(self):
        """Test that generated events have variety in skills and spotlight classes."""
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Collect all skills and spotlight classes
        all_skills = set()
        all_spotlight = set()
        
        for category, events in generated_events.items():
            for event in events:
                if 'skills' in event:
                    all_skills.update(event['skills'])
                if 'spotlight' in event:
                    all_spotlight.update(event['spotlight'])
        
        # Should have variety in skills (at least 5 different skills)
        assert len(all_skills) >= 5, \
            f"Generated events should use at least 5 different skills, got {len(all_skills)}: {all_skills}"
        
        # Should have variety in spotlight classes (at least 4 different classes)
        assert len(all_spotlight) >= 4, \
            f"Generated events should spotlight at least 4 different classes, got {len(all_spotlight)}: {all_spotlight}"
    
    def test_generated_events_have_clear_outcomes(self):
        """Test that generated events have clear outcomes for all choices."""
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Check each event
        for category, events in generated_events.items():
            for event in events:
                if category in ['OPPORTUNITY', 'COMPLICATION']:
                    # Should have non-empty success and failure
                    assert event.get('success', '').strip(), \
                        f"Generated {category} event '{event['title']}' has empty success outcome"
                    assert event.get('failure', '').strip(), \
                        f"Generated {category} event '{event['title']}' has empty failure outcome"
                
                elif category == 'DILEMMA':
                    # Should have non-empty choices
                    assert event.get('choice_a', '').strip(), \
                        f"Generated DILEMMA event '{event['title']}' has empty choice_a"
                    assert event.get('choice_b', '').strip(), \
                        f"Generated DILEMMA event '{event['title']}' has empty choice_b"
                
                elif category == 'ACTIVE_THREAT':
                    # Should have non-empty immediate action and outcomes
                    assert event.get('immediate_action', '').strip(), \
                        f"Generated ACTIVE_THREAT event '{event['title']}' has empty immediate_action"
                    assert event.get('success', '').strip(), \
                        f"Generated ACTIVE_THREAT event '{event['title']}' has empty success"
                    assert event.get('failure', '').strip(), \
                        f"Generated ACTIVE_THREAT event '{event['title']}' has empty failure"
    
    @settings(max_examples=100)
    @given(st.data())
    def test_property_random_generated_event_is_valid(self, data):
        """
        Property test: Any randomly selected generated event should pass validation.
        
        This test uses hypothesis to randomly sample events from the generated file
        and verify they all pass validation criteria.
        """
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Randomly select a category
        category = data.draw(st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']))
        
        # Randomly select an event from that category
        assume(len(generated_events[category]) > 0)
        event_index = data.draw(st.integers(min_value=0, max_value=len(generated_events[category]) - 1))
        event = generated_events[category][event_index]
        
        # Validate the event
        is_valid, reason = validate_event(event)
        
        assert is_valid, \
            f"Randomly selected generated event '{event['title']}' from {category} " \
            f"failed validation: {reason}"
    
    @settings(max_examples=100)
    @given(st.data())
    def test_property_generated_event_structure_matches_schema(self, data):
        """
        Property test: Any generated event should match the expected schema for its category.
        
        This test verifies that the structure of generated events matches the requirements
        defined in the design document.
        """
        generated_file = 'etc/dungeon_turn_events_generated.json'
        
        # Load generated events
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        # Randomly select a category
        category = data.draw(st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']))
        
        # Randomly select an event from that category
        assume(len(generated_events[category]) > 0)
        event_index = data.draw(st.integers(min_value=0, max_value=len(generated_events[category]) - 1))
        event = generated_events[category][event_index]
        
        # Check common required fields
        required_fields = {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'}
        for field in required_fields:
            assert field in event, \
                f"Event '{event.get('title', 'UNKNOWN')}' missing required field '{field}'"
        
        # Check category-specific fields
        if category in ['OPPORTUNITY', 'COMPLICATION']:
            assert 'challenge' in event, f"{category} event missing 'challenge'"
            assert 'success' in event, f"{category} event missing 'success'"
            assert 'failure' in event, f"{category} event missing 'failure'"
        
        elif category == 'DILEMMA':
            assert 'choice_a' in event, "DILEMMA event missing 'choice_a'"
            assert 'choice_b' in event, "DILEMMA event missing 'choice_b'"
        
        elif category == 'ACTIVE_THREAT':
            assert 'immediate_action' in event, "ACTIVE_THREAT event missing 'immediate_action'"
            assert 'success' in event, "ACTIVE_THREAT event missing 'success'"
            assert 'failure' in event, "ACTIVE_THREAT event missing 'failure'"
            assert 'threat_level' in event, "ACTIVE_THREAT event missing 'threat_level'"
    
    def test_generated_events_comparable_to_validated_events(self):
        """Test that generated events are comparable in quality to validated existing events."""
        generated_file = 'etc/dungeon_turn_events_generated.json'
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load both files
        with open(generated_file, 'r', encoding='utf-8') as f:
            generated_events = json.load(f)
        
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Validate both
        gen_valid, gen_invalid = filter_events(generated_events)
        cur_valid, cur_invalid = filter_events(curated_events)
        
        # Get stats
        gen_stats = get_validation_stats(gen_valid, gen_invalid)
        cur_stats = get_validation_stats(cur_valid, cur_invalid)
        
        # Generated events should have same or better validation rate
        gen_total = gen_stats['total_valid'] + gen_stats['total_invalid']
        cur_total = cur_stats['total_valid'] + cur_stats['total_invalid']
        
        if gen_total > 0 and cur_total > 0:
            gen_valid_ratio = gen_stats['total_valid'] / gen_total
            cur_valid_ratio = cur_stats['total_valid'] / cur_total
            
            assert gen_valid_ratio >= cur_valid_ratio * 0.95, \
                f"Generated events validation rate ({gen_valid_ratio:.2%}) should be " \
                f"comparable to curated events ({cur_valid_ratio:.2%})"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
