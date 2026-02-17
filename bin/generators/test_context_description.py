"""
Unit tests for context-aware description generation.
"""

import pytest
from event_context import EventContext
from context_description import (
    get_space_description,
    apply_context_to_description,
    apply_space_tactics,
    add_status_flavor,
    apply_all_context
)


class TestGetSpaceDescription:
    """Test suite for get_space_description function."""
    
    def test_all_space_types(self):
        """Test descriptions for all valid space types."""
        expected = {
            "hallway": "a narrow corridor",
            "large_room": "a spacious chamber",
            "small_room": "a cramped room",
            "outside": "the open area",
            "vertical_space": "a vertical shaft",
            "water": "the flooded passage",
            "unknown": "the area"
        }
        for space_type, expected_desc in expected.items():
            assert get_space_description(space_type) == expected_desc
    
    def test_invalid_space_type(self):
        """Test fallback for invalid space type."""
        assert get_space_description("invalid") == "the area"


class TestApplyContextToDescription:
    """Test suite for apply_context_to_description function."""
    
    def test_space_placeholder_replacement(self):
        """Test replacement of {space} placeholder."""
        description = "You discover {space} ahead."
        context = EventContext(space_type="hallway")
        result = apply_context_to_description(description, context)
        assert result == "You discover a narrow corridor ahead."
    
    def test_combat_context_with_recent_combat(self):
        """Test {combat_context} replacement with recent combat."""
        description = "An enemy flees {combat_context}."
        context = EventContext(recent_combat=True)
        result = apply_context_to_description(description, context)
        assert result == "An enemy flees from the recent skirmish."
    
    def test_combat_context_without_recent_combat(self):
        """Test {combat_context} replacement without recent combat."""
        description = "An enemy flees {combat_context}."
        context = EventContext(recent_combat=False)
        result = apply_context_to_description(description, context)
        assert result == "An enemy flees ."
    
    def test_multiple_placeholders(self):
        """Test replacement of multiple placeholders."""
        description = "In {space}, enemies appear {combat_context}."
        context = EventContext(space_type="large_room", recent_combat=True)
        result = apply_context_to_description(description, context)
        assert result == "In a spacious chamber, enemies appear from the recent skirmish."
    
    def test_no_placeholders(self):
        """Test description without placeholders remains unchanged."""
        description = "A simple event occurs."
        context = EventContext()
        result = apply_context_to_description(description, context)
        assert result == "A simple event occurs."


class TestApplySpaceTactics:
    """Test suite for apply_space_tactics function."""
    
    def test_hallway_tactics(self):
        """Test tactical notes for hallway."""
        notes = "Enemy ahead."
        result = apply_space_tactics(notes, "hallway")
        assert "Limited flanking" in result
        assert "Reach weapons effective" in result
        assert "Single-file movement" in result
        assert "Enemy ahead." in result
    
    def test_large_room_tactics(self):
        """Test tactical notes for large room."""
        notes = "Enemy ahead."
        result = apply_space_tactics(notes, "large_room")
        assert "Flanking opportunities" in result
        assert "Use cover" in result
        assert "Multiple approach vectors" in result
    
    def test_vertical_space_tactics(self):
        """Test tactical notes for vertical space."""
        notes = "Enemy ahead."
        result = apply_space_tactics(notes, "vertical_space")
        assert "Height advantage" in result
        assert "Climbing required" in result
        assert "Fall hazards" in result
    
    def test_outside_tactics(self):
        """Test tactical notes for outside."""
        notes = "Enemy ahead."
        result = apply_space_tactics(notes, "outside")
        assert "Weather effects" in result
        assert "Long sight lines" in result
        assert "Open terrain" in result
    
    def test_water_tactics(self):
        """Test tactical notes for water."""
        notes = "Enemy ahead."
        result = apply_space_tactics(notes, "water")
        assert "Swimming required" in result
        assert "Drowning risk" in result
        assert "Aquatic advantage" in result
    
    def test_small_room_tactics(self):
        """Test tactical notes for small room."""
        notes = "Enemy ahead."
        result = apply_space_tactics(notes, "small_room")
        assert "Cramped quarters" in result
        assert "Limited movement" in result
        assert "Close combat" in result
    
    def test_unknown_space_no_addition(self):
        """Test that unknown space adds no tactical notes."""
        notes = "Enemy ahead."
        result = apply_space_tactics(notes, "unknown")
        assert result == "Enemy ahead."


class TestAddStatusFlavor:
    """Test suite for add_status_flavor function."""
    
    def test_healthy_no_flavor(self):
        """Test that healthy status adds no flavor."""
        description = "You proceed forward."
        result = add_status_flavor(description, "healthy")
        assert result == "You proceed forward."
    
    def test_injured_flavor(self):
        """Test injured status adds appropriate flavor."""
        description = "you proceed forward."
        result = add_status_flavor(description, "injured")
        assert result == "Despite your wounds, you proceed forward."
    
    def test_low_resources_flavor(self):
        """Test low_resources status adds appropriate flavor."""
        description = "you must decide."
        result = add_status_flavor(description, "low_resources")
        assert result == "With supplies running low, you must decide."


class TestApplyAllContext:
    """Test suite for apply_all_context function."""
    
    def test_apply_all_modifications(self):
        """Test that all context modifications are applied."""
        event = {
            "title": "Test Event",
            "description": "In {space}, you encounter enemies {combat_context}.",
            "tactical_notes": "Be careful."
        }
        context = EventContext(
            space_type="hallway",
            recent_combat=True,
            party_status="injured"
        )
        
        result = apply_all_context(event, context)
        
        # Check description has space and combat context
        assert "a narrow corridor" in result["description"]
        assert "from the recent skirmish" in result["description"]
        # Check status flavor
        assert "Despite your wounds" in result["description"]
        # Check tactical notes
        assert "Limited flanking" in result["tactical_notes"]
    
    def test_event_without_tactical_notes(self):
        """Test event without tactical_notes field."""
        event = {
            "title": "Test Event",
            "description": "Simple event."
        }
        context = EventContext(space_type="hallway")
        
        result = apply_all_context(event, context)
        assert result["description"] == "Simple event."
        assert "tactical_notes" not in result
    
    def test_original_event_not_modified(self):
        """Test that original event dictionary is not modified."""
        event = {
            "title": "Test Event",
            "description": "In {space}."
        }
        context = EventContext(space_type="hallway")
        
        original_desc = event["description"]
        result = apply_all_context(event, context)
        
        # Original should be unchanged
        assert event["description"] == original_desc
        # Result should be modified
        assert result["description"] != original_desc


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
