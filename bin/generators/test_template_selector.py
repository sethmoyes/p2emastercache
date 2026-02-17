"""
Unit tests for template selection system.
"""

import pytest
from event_context import EventContext
from template_selector import is_compatible, select_template


class TestIsCompatible:
    """Test suite for is_compatible function."""
    
    def test_template_without_requirements(self):
        """Test that templates without requirements are always compatible."""
        template = {"title": "Generic Event"}
        context = EventContext(space_type="hallway", recent_combat=True)
        assert is_compatible(template, context) is True
    
    def test_required_spaces_compatible(self):
        """Test template with matching required_spaces."""
        template = {
            "title": "Hallway Event",
            "required_spaces": ["hallway", "small_room"]
        }
        context = EventContext(space_type="hallway")
        assert is_compatible(template, context) is True
    
    def test_required_spaces_incompatible(self):
        """Test template with non-matching required_spaces."""
        template = {
            "title": "Hallway Event",
            "required_spaces": ["hallway", "small_room"]
        }
        context = EventContext(space_type="outside")
        assert is_compatible(template, context) is False
    
    def test_requires_recent_combat_true(self):
        """Test template requiring recent combat with combat context."""
        template = {
            "title": "Combat Aftermath",
            "requires_recent_combat": True
        }
        context = EventContext(recent_combat=True)
        assert is_compatible(template, context) is True
    
    def test_requires_recent_combat_false(self):
        """Test template requiring recent combat without combat context."""
        template = {
            "title": "Combat Aftermath",
            "requires_recent_combat": True
        }
        context = EventContext(recent_combat=False)
        assert is_compatible(template, context) is False
    
    def test_requires_new_area_true(self):
        """Test template requiring new area with new area context."""
        template = {
            "title": "Discovery",
            "requires_new_area": True
        }
        context = EventContext(new_area=True)
        assert is_compatible(template, context) is True
    
    def test_requires_new_area_false(self):
        """Test template requiring new area without new area context."""
        template = {
            "title": "Discovery",
            "requires_new_area": True
        }
        context = EventContext(new_area=False)
        assert is_compatible(template, context) is False
    
    def test_multiple_requirements_all_met(self):
        """Test template with multiple requirements all satisfied."""
        template = {
            "title": "Combat in Hallway",
            "required_spaces": ["hallway"],
            "requires_recent_combat": True
        }
        context = EventContext(space_type="hallway", recent_combat=True)
        assert is_compatible(template, context) is True
    
    def test_multiple_requirements_one_not_met(self):
        """Test template with multiple requirements, one not satisfied."""
        template = {
            "title": "Combat in Hallway",
            "required_spaces": ["hallway"],
            "requires_recent_combat": True
        }
        context = EventContext(space_type="hallway", recent_combat=False)
        assert is_compatible(template, context) is False


class TestSelectTemplate:
    """Test suite for select_template function."""
    
    def test_select_from_compatible_templates(self):
        """Test selection from multiple compatible templates."""
        templates = [
            {"title": "Event 1", "required_spaces": ["hallway"]},
            {"title": "Event 2", "required_spaces": ["hallway"]},
            {"title": "Event 3", "required_spaces": ["outside"]}
        ]
        context = EventContext(space_type="hallway")
        
        # Run multiple times to check randomness
        results = set()
        for _ in range(20):
            selected = select_template(templates, context)
            results.add(selected["title"])
        
        # Should only select from compatible templates
        assert "Event 1" in results or "Event 2" in results
        assert "Event 3" not in results
    
    def test_fallback_when_no_compatible(self):
        """Test fallback to any template when none are compatible."""
        templates = [
            {"title": "Event 1", "required_spaces": ["outside"]},
            {"title": "Event 2", "required_spaces": ["water"]}
        ]
        context = EventContext(space_type="hallway")
        
        # Should still return a template (fallback behavior)
        selected = select_template(templates, context)
        assert selected in templates
    
    def test_select_without_requirements(self):
        """Test selection from templates without requirements."""
        templates = [
            {"title": "Event 1"},
            {"title": "Event 2"},
            {"title": "Event 3"}
        ]
        context = EventContext(space_type="hallway")
        
        # All templates should be compatible
        selected = select_template(templates, context)
        assert selected in templates
    
    def test_empty_template_list_raises_error(self):
        """Test that empty template list raises ValueError."""
        templates = []
        context = EventContext()
        
        with pytest.raises(ValueError) as exc_info:
            select_template(templates, context)
        assert "empty template list" in str(exc_info.value)
    
    def test_single_compatible_template(self):
        """Test selection with only one compatible template."""
        templates = [
            {"title": "Event 1", "required_spaces": ["hallway"]},
            {"title": "Event 2", "required_spaces": ["outside"]}
        ]
        context = EventContext(space_type="hallway")
        
        selected = select_template(templates, context)
        assert selected["title"] == "Event 1"
    
    def test_complex_context_filtering(self):
        """Test selection with complex context requirements."""
        templates = [
            {
                "title": "Combat Aftermath in Hallway",
                "required_spaces": ["hallway"],
                "requires_recent_combat": True
            },
            {
                "title": "Discovery in New Area",
                "requires_new_area": True
            },
            {
                "title": "Generic Event"
            }
        ]
        
        # Context matching first template
        context1 = EventContext(space_type="hallway", recent_combat=True)
        selected1 = select_template(templates, context1)
        # Should select from compatible templates (first or third)
        assert selected1["title"] in ["Combat Aftermath in Hallway", "Discovery in New Area", "Generic Event"]
        
        # Context matching second template
        context2 = EventContext(new_area=True)
        selected2 = select_template(templates, context2)
        assert selected2["title"] in ["Discovery in New Area", "Generic Event"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
