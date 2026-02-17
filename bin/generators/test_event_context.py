"""
Unit tests for EventContext data model.
"""

import pytest
from event_context import EventContext


class TestEventContext:
    """Test suite for EventContext dataclass."""
    
    def test_default_values(self):
        """Test that EventContext has correct default values."""
        context = EventContext()
        assert context.space_type == "unknown"
        assert context.recent_combat is False
        assert context.new_area is True
        assert context.party_status == "healthy"
    
    def test_validation_with_valid_parameters(self):
        """Test validation passes with all valid parameters."""
        # Test all valid space types
        for space in ["hallway", "large_room", "small_room", "outside", 
                      "vertical_space", "water", "unknown"]:
            context = EventContext(space_type=space)
            context.validate()  # Should not raise
        
        # Test all valid party statuses
        for status in ["healthy", "injured", "low_resources"]:
            context = EventContext(party_status=status)
            context.validate()  # Should not raise
        
        # Test boolean parameters
        context = EventContext(recent_combat=True, new_area=False)
        context.validate()  # Should not raise
    
    def test_validation_with_invalid_space_type(self):
        """Test validation fails with invalid space_type."""
        context = EventContext(space_type="invalid_space")
        with pytest.raises(ValueError) as exc_info:
            context.validate()
        assert "Invalid space_type" in str(exc_info.value)
        assert "invalid_space" in str(exc_info.value)
    
    def test_validation_with_invalid_party_status(self):
        """Test validation fails with invalid party_status."""
        context = EventContext(party_status="invalid_status")
        with pytest.raises(ValueError) as exc_info:
            context.validate()
        assert "Invalid party_status" in str(exc_info.value)
        assert "invalid_status" in str(exc_info.value)
    
    def test_custom_values(self):
        """Test EventContext with custom values."""
        context = EventContext(
            space_type="hallway",
            recent_combat=True,
            new_area=False,
            party_status="injured"
        )
        assert context.space_type == "hallway"
        assert context.recent_combat is True
        assert context.new_area is False
        assert context.party_status == "injured"
        context.validate()  # Should not raise
    
    def test_partial_custom_values(self):
        """Test EventContext with some custom values and some defaults."""
        context = EventContext(space_type="large_room", recent_combat=True)
        assert context.space_type == "large_room"
        assert context.recent_combat is True
        assert context.new_area is True  # Default
        assert context.party_status == "healthy"  # Default
        context.validate()  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
