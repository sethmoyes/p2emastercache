#!/usr/bin/env python3
"""
Test that event generation functions work correctly with JSON-loaded templates.

This test verifies Requirement 4.5: The Generator_Script SHALL maintain all 
existing functionality for event selection and generation.
"""

import sys
import os

# Add bin directory to path so we can import from generators
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generators'))

import pytest
from generators.generate_dungeon_turn_v2 import (
    generate_opportunity_event,
    generate_complication_event,
    generate_dilemma_event,
    generate_active_threat_event,
    OPPORTUNITY_TEMPLATES,
    COMPLICATION_TEMPLATES,
    DILEMMA_TEMPLATES,
    ACTIVE_THREAT_TEMPLATES
)


def test_templates_loaded():
    """Verify that templates are loaded from JSON."""
    assert len(OPPORTUNITY_TEMPLATES) > 0, "OPPORTUNITY_TEMPLATES should not be empty"
    assert len(COMPLICATION_TEMPLATES) > 0, "COMPLICATION_TEMPLATES should not be empty"
    assert len(DILEMMA_TEMPLATES) > 0, "DILEMMA_TEMPLATES should not be empty"
    assert len(ACTIVE_THREAT_TEMPLATES) > 0, "ACTIVE_THREAT_TEMPLATES should not be empty"
    
    print(f"✓ Loaded {len(OPPORTUNITY_TEMPLATES)} opportunity templates")
    print(f"✓ Loaded {len(COMPLICATION_TEMPLATES)} complication templates")
    print(f"✓ Loaded {len(DILEMMA_TEMPLATES)} dilemma templates")
    print(f"✓ Loaded {len(ACTIVE_THREAT_TEMPLATES)} active threat templates")


def test_generate_opportunity_event():
    """Test generate_opportunity_event with loaded templates."""
    floor_data = {
        'name': 'Test Floor',
        'theme': 'Test Theme',
        'threats': ['Test Threat']
    }
    
    # Generate event
    event = generate_opportunity_event(
        floor_num=2,
        floor_data=floor_data,
        party_level=3,
        context=None
    )
    
    # Verify event structure
    assert event is not None, "Event should not be None"
    assert 'title' in event, "Event should have a title"
    assert 'description' in event, "Event should have a description"
    assert 'floor' in event, "Event should have floor number"
    assert 'floor_name' in event, "Event should have floor name"
    assert 'flavor' in event, "Event should have floor-specific flavor"
    
    # Verify floor data was applied
    assert event['floor'] == 2
    assert event['floor_name'] == 'Test Floor'
    
    print(f"✓ Generated opportunity event: {event['title']}")


def test_generate_complication_event():
    """Test generate_complication_event with loaded templates."""
    floor_data = {
        'name': 'Test Floor',
        'theme': 'Test Theme',
        'threats': ['Test Threat']
    }
    
    # Generate event
    event = generate_complication_event(
        floor_num=3,
        floor_data=floor_data,
        party_level=4,
        context=None
    )
    
    # Verify event structure
    assert event is not None, "Event should not be None"
    assert 'title' in event, "Event should have a title"
    assert 'description' in event, "Event should have a description"
    assert 'floor' in event, "Event should have floor number"
    assert 'floor_name' in event, "Event should have floor name"
    assert 'flavor' in event, "Event should have floor-specific flavor"
    
    # Verify floor data was applied
    assert event['floor'] == 3
    assert event['floor_name'] == 'Test Floor'
    
    print(f"✓ Generated complication event: {event['title']}")


def test_generate_dilemma_event():
    """Test generate_dilemma_event with loaded templates."""
    floor_data = {
        'name': 'Test Floor',
        'theme': 'Test Theme',
        'threats': ['Test Threat']
    }
    
    # Generate event
    event = generate_dilemma_event(
        floor_num=5,
        floor_data=floor_data,
        party_level=6,
        context=None
    )
    
    # Verify event structure
    assert event is not None, "Event should not be None"
    assert 'title' in event, "Event should have a title"
    assert 'description' in event, "Event should have a description"
    assert 'floor' in event, "Event should have floor number"
    assert 'floor_name' in event, "Event should have floor name"
    assert 'context' in event, "Event should have context message"
    
    # Verify floor data was applied
    assert event['floor'] == 5
    assert event['floor_name'] == 'Test Floor'
    
    print(f"✓ Generated dilemma event: {event['title']}")


def test_generate_active_threat_event():
    """Test generate_active_threat_event with loaded templates."""
    floor_data = {
        'name': 'Test Floor',
        'theme': 'Test Theme',
        'threats': ['Test Threat']
    }
    
    # Generate event
    event = generate_active_threat_event(
        floor_num=7,
        floor_data=floor_data,
        party_level=8,
        context=None
    )
    
    # Verify event structure
    assert event is not None, "Event should not be None"
    assert 'title' in event, "Event should have a title"
    assert 'description' in event, "Event should have a description"
    assert 'floor' in event, "Event should have floor number"
    assert 'floor_name' in event, "Event should have floor name"
    assert 'urgency' in event, "Event should have urgency message"
    
    # Verify floor data was applied
    assert event['floor'] == 7
    assert event['floor_name'] == 'Test Floor'
    assert event['urgency'] == "IMMEDIATE ACTION REQUIRED! No time to discuss!"
    
    print(f"✓ Generated active threat event: {event['title']}")


def test_multiple_event_generation():
    """Test generating multiple events to ensure variety."""
    floor_data = {
        'name': 'Test Floor',
        'theme': 'Test Theme',
        'threats': ['Test Threat']
    }
    
    # Generate multiple events of each type
    opportunity_events = [
        generate_opportunity_event(2, floor_data, 3, None)
        for _ in range(5)
    ]
    
    complication_events = [
        generate_complication_event(3, floor_data, 4, None)
        for _ in range(5)
    ]
    
    dilemma_events = [
        generate_dilemma_event(5, floor_data, 6, None)
        for _ in range(5)
    ]
    
    active_threat_events = [
        generate_active_threat_event(7, floor_data, 8, None)
        for _ in range(5)
    ]
    
    # Verify all events were generated
    assert len(opportunity_events) == 5
    assert len(complication_events) == 5
    assert len(dilemma_events) == 5
    assert len(active_threat_events) == 5
    
    # Verify all events have required fields
    for event in opportunity_events + complication_events + dilemma_events + active_threat_events:
        assert 'title' in event
        assert 'description' in event
        assert 'floor' in event
        assert 'floor_name' in event
    
    print(f"✓ Generated 20 events successfully (5 of each type)")


def test_event_has_template_fields():
    """Test that generated events preserve template fields."""
    floor_data = {
        'name': 'Test Floor',
        'theme': 'Test Theme',
        'threats': ['Test Threat']
    }
    
    # Generate one of each type
    opp_event = generate_opportunity_event(2, floor_data, 3, None)
    comp_event = generate_complication_event(3, floor_data, 4, None)
    dilemma_event = generate_dilemma_event(5, floor_data, 6, None)
    threat_event = generate_active_threat_event(7, floor_data, 8, None)
    
    # Check opportunity/complication have challenge/success/failure
    if 'challenge' in OPPORTUNITY_TEMPLATES[0]:
        assert 'challenge' in opp_event or 'success' in opp_event, \
            "Opportunity event should have challenge or success field"
    
    if 'challenge' in COMPLICATION_TEMPLATES[0]:
        assert 'challenge' in comp_event or 'success' in comp_event, \
            "Complication event should have challenge or success field"
    
    # Check dilemma has choices
    if 'choice_a' in DILEMMA_TEMPLATES[0]:
        assert 'choice_a' in dilemma_event or 'choice_b' in dilemma_event, \
            "Dilemma event should have choice fields"
    
    # Check active threat has immediate action
    if 'immediate_action' in ACTIVE_THREAT_TEMPLATES[0]:
        assert 'immediate_action' in threat_event or 'threat_level' in threat_event, \
            "Active threat event should have immediate_action or threat_level field"
    
    print("✓ Generated events preserve template fields")


def test_floor_specific_flavor():
    """Test that events get floor-specific flavor text."""
    floor_data = {
        'name': 'Test Floor',
        'theme': 'Test Theme',
        'threats': ['Test Threat']
    }
    
    # Test different floors
    floors_to_test = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    for floor_num in floors_to_test:
        event = generate_opportunity_event(floor_num, floor_data, 3, None)
        assert 'flavor' in event, f"Floor {floor_num} event should have flavor"
        assert len(event['flavor']) > 0, f"Floor {floor_num} flavor should not be empty"
    
    print("✓ All floors (1-10) generate events with flavor text")


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '-s'])
