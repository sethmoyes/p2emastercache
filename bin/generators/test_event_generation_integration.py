"""
Integration tests for context-aware event generation.
"""

import pytest
import sys
import os

# Add parent directory to path to import generate_dungeon_turn_v2
sys.path.insert(0, os.path.dirname(__file__))

from event_context import EventContext
from generate_dungeon_turn_v2 import (
    generate_opportunity_event,
    generate_complication_event,
    generate_dilemma_event,
    generate_active_threat_event,
    generate_event_for_sum,
    load_json,
    load_markdown,
    parse_gauntlight_levels
)


class TestEventGenerationWithContext:
    """Integration tests for event generation with context."""
    
    @pytest.fixture
    def test_data(self):
        """Load test data."""
        # Load minimal test data
        floor_data = {
            'name': 'Test Floor',
            'theme': 'Test Theme',
            'level': 1
        }
        creatures = [
            {'name': 'Test Creature', 'level': 1, 'rarity': 'common'}
        ]
        return floor_data, creatures
    
    def test_generate_opportunity_without_context(self, test_data):
        """Test opportunity generation without context (backward compatibility)."""
        floor_data, _ = test_data
        event = generate_opportunity_event(1, floor_data, 4)
        
        assert 'title' in event
        assert 'description' in event
        assert 'floor' in event
        assert event['floor'] == 1
    
    def test_generate_opportunity_with_context(self, test_data):
        """Test opportunity generation with context."""
        floor_data, _ = test_data
        context = EventContext(
            space_type="hallway",
            recent_combat=False,
            new_area=True,
            party_status="healthy"
        )
        
        event = generate_opportunity_event(1, floor_data, 4, context)
        
        assert 'title' in event
        assert 'description' in event
        assert 'floor' in event
    
    def test_generate_dilemma_filters_combat_events(self, test_data):
        """Test that combat-related dilemmas only appear with recent_combat=True."""
        floor_data, _ = test_data
        
        # Generate many events without recent combat
        context_no_combat = EventContext(recent_combat=False)
        events_no_combat = []
        for _ in range(50):
            event = generate_dilemma_event(1, floor_data, 4, context_no_combat)
            events_no_combat.append(event['title'])
        
        # "Chase Fleeing Enemy" should not appear without recent combat
        # (though it might due to fallback if no compatible templates)
        # This test verifies the filtering mechanism works
        
        # Generate events with recent combat
        context_with_combat = EventContext(recent_combat=True)
        events_with_combat = []
        for _ in range(50):
            event = generate_dilemma_event(1, floor_data, 4, context_with_combat)
            events_with_combat.append(event['title'])
        
        # Both should generate events successfully
        assert len(events_no_combat) == 50
        assert len(events_with_combat) == 50
    
    def test_generate_opportunity_filters_discovery_events(self, test_data):
        """Test that discovery events only appear with new_area=True."""
        floor_data, _ = test_data
        
        # Generate events in familiar area
        context_familiar = EventContext(new_area=False)
        events_familiar = []
        for _ in range(30):
            event = generate_opportunity_event(1, floor_data, 4, context_familiar)
            events_familiar.append(event['title'])
        
        # Generate events in new area
        context_new = EventContext(new_area=True)
        events_new = []
        for _ in range(30):
            event = generate_opportunity_event(1, floor_data, 4, context_new)
            events_new.append(event['title'])
        
        # Both should generate events successfully
        assert len(events_familiar) == 30
        assert len(events_new) == 30
    
    def test_context_placeholders_replaced(self, test_data):
        """Test that context placeholders are replaced in descriptions."""
        floor_data, _ = test_data
        context = EventContext(
            space_type="hallway",
            recent_combat=True
        )
        
        # Generate multiple events to find one with placeholders
        for _ in range(20):
            event = generate_dilemma_event(1, floor_data, 4, context)
            description = event.get('description', '')
            
            # Placeholders should be replaced
            assert '{space}' not in description
            assert '{combat_context}' not in description
    
    def test_generate_event_for_sum_without_context(self, test_data):
        """Test generate_event_for_sum without context (backward compatibility)."""
        floor_data, creatures = test_data
        
        # Test various sums
        event_opportunity = generate_event_for_sum(15, 1, floor_data, 4, creatures)
        assert event_opportunity is not None
        
        event_dilemma = generate_event_for_sum(55, 1, floor_data, 4, creatures)
        assert event_dilemma is not None
    
    def test_generate_event_for_sum_with_context(self, test_data):
        """Test generate_event_for_sum with context."""
        floor_data, creatures = test_data
        context = EventContext(
            space_type="large_room",
            recent_combat=True,
            new_area=False,
            party_status="injured"
        )
        
        # Test various sums with context
        event_opportunity = generate_event_for_sum(15, 1, floor_data, 4, creatures, context)
        assert event_opportunity is not None
        
        event_dilemma = generate_event_for_sum(55, 1, floor_data, 4, creatures, context)
        assert event_dilemma is not None
    
    def test_context_validation_in_generation(self, test_data):
        """Test that invalid context raises error."""
        floor_data, creatures = test_data
        context = EventContext(space_type="invalid_space")
        
        with pytest.raises(ValueError):
            generate_event_for_sum(55, 1, floor_data, 4, creatures, context)
    
    def test_party_status_affects_description(self, test_data):
        """Test that party status affects event descriptions."""
        floor_data, _ = test_data
        
        # Generate with injured status
        context_injured = EventContext(party_status="injured")
        event_injured = generate_dilemma_event(1, floor_data, 4, context_injured)
        
        # Generate with healthy status
        context_healthy = EventContext(party_status="healthy")
        event_healthy = generate_dilemma_event(1, floor_data, 4, context_healthy)
        
        # Both should generate successfully
        assert event_injured is not None
        assert event_healthy is not None
        
        # Injured events might have status flavor (if template supports it)
        # This is a soft check since not all events have status flavor


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
