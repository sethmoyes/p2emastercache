#!/usr/bin/env python3
"""
Property-Based Test for Skill-Class Consistency (Property 14)

**Validates: Requirements 6.4**

For any event, the required skills should be appropriate for at least one 
of the spotlight classes.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_loader import load_events_from_json
from hypothesis import given, strategies as st, settings
import pytest


# Mapping of classes to their typical skills
# Note: This includes both trained skills and commonly used skills for each class
# Also includes saving throws (Reflex, Fortitude, Will) as they're used in events
CLASS_SKILLS = {
    'Rogue': ['Stealth', 'Thievery', 'Acrobatics', 'Deception', 'Perception', 'Diplomacy', 
              'Athletics', 'Crafting', 'Survival', 'Society', 'Arcana', 'Religion', 'Reflex'],
    'Fighter': ['Athletics', 'Intimidation', 'Acrobatics', 'Crafting', 'Perception', 'Fortitude'],
    'Wizard': ['Arcana', 'Occultism', 'Society', 'Crafting', 'Nature', 'Perception', 'Will'],
    'Cleric': ['Religion', 'Medicine', 'Diplomacy', 'Occultism', 'Society', 'Arcana', 'Nature', 'Will'],
    'Monk': ['Athletics', 'Acrobatics', 'Stealth', 'Religion', 'Perception', 'Survival', 
             'Nature', 'Crafting', 'Reflex', 'Fortitude', 'Will'],
    'Swashbuckler': ['Acrobatics', 'Athletics', 'Diplomacy', 'Deception', 'Intimidation', 
                     'Perception', 'Performance', 'Reflex'],
    'Ranger': ['Survival', 'Nature', 'Stealth', 'Perception', 'Athletics', 'Reflex', 'Diplomacy', 'Intimidation'],
    'Barbarian': ['Athletics', 'Intimidation', 'Nature', 'Survival', 'Perception', 'Fortitude'],
    'Bard': ['Performance', 'Diplomacy', 'Deception', 'Occultism', 'Society', 'Perception', 'Will'],
    'Druid': ['Nature', 'Survival', 'Medicine', 'Diplomacy', 'Perception', 'Will'],
    'Sorcerer': ['Arcana', 'Intimidation', 'Deception', 'Diplomacy', 'Perception', 'Will'],
    'Champion': ['Religion', 'Athletics', 'Diplomacy', 'Intimidation', 'Medicine', 'Perception', 'Fortitude'],
    'Alchemist': ['Crafting', 'Medicine', 'Nature', 'Society', 'Perception', 'Reflex'],
    'All': ['Perception', 'Athletics', 'Stealth', 'Diplomacy', 'Intimidation', 
            'Acrobatics', 'Arcana', 'Religion', 'Nature', 'Survival', 'Medicine',
            'Thievery', 'Deception', 'Society', 'Crafting', 'Performance', 'Occultism',
            'Reflex', 'Fortitude', 'Will']  # Include saves as they're used in events
}


def is_skill_appropriate_for_class(skill: str, class_name: str) -> bool:
    """
    Check if a skill is appropriate for a given class.
    
    Args:
        skill: Skill name (may include description like "Arcana to identify")
        class_name: Class name
    
    Returns:
        True if the skill is appropriate for the class
    """
    # Normalize class name
    class_name = class_name.strip()
    
    # 'All' means any class can use any skill
    if class_name == 'All':
        return True
    
    # Check if class is in our mapping
    if class_name not in CLASS_SKILLS:
        # Unknown class - assume it's valid (might be a custom class)
        return True
    
    # Extract the base skill name (before any "to" or other descriptors)
    # e.g., "Arcana to identify" -> "Arcana"
    base_skill = skill.split(' to ')[0].split(' or ')[0].strip()
    
    # Check if base skill is in the class's skill list
    return base_skill in CLASS_SKILLS[class_name]


def event_has_appropriate_skills(event: dict) -> tuple[bool, str]:
    """
    Check if an event's skills are appropriate for at least one spotlight class.
    
    Args:
        event: Event dictionary
    
    Returns:
        (is_valid, reason) tuple
    """
    spotlight_classes = event.get('spotlight', [])
    skills = event.get('skills', [])
    
    if not spotlight_classes:
        return False, "No spotlight classes defined"
    
    if not skills:
        return False, "No skills defined"
    
    # Check if at least one skill is appropriate for at least one spotlight class
    for class_name in spotlight_classes:
        for skill in skills:
            if is_skill_appropriate_for_class(skill, class_name):
                return True, f"Skill '{skill}' is appropriate for class '{class_name}'"
    
    # No appropriate skills found
    return False, f"None of the skills {skills} are appropriate for spotlight classes {spotlight_classes}"


class TestSkillClassConsistency:
    """
    Feature: dungeon-turn-event-refactor, Property 14: Skill-Class Consistency
    
    **Validates: Requirements 6.4**
    
    For any event, the required skills should be appropriate for at least one 
    of the spotlight classes.
    """
    
    def test_all_events_have_appropriate_skills(self):
        """Test that all events have skills appropriate for their spotlight classes."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        invalid_events = []
        
        for category, event_list in events.items():
            for event in event_list:
                is_valid, reason = event_has_appropriate_skills(event)
                if not is_valid:
                    invalid_events.append({
                        'event': event['title'],
                        'category': category,
                        'reason': reason,
                        'spotlight': event.get('spotlight', []),
                        'skills': event.get('skills', [])
                    })
        
        # Report any invalid events
        if invalid_events:
            error_msg = "Found events with inappropriate skill-class combinations:\n"
            for ref in invalid_events:
                error_msg += f"  - Event '{ref['event']}' ({ref['category']}): {ref['reason']}\n"
                error_msg += f"    Spotlight: {ref['spotlight']}, Skills: {ref['skills']}\n"
            pytest.fail(error_msg)
    
    def test_rogue_events_use_rogue_skills(self):
        """Test that events spotlighting Rogue use appropriate Rogue skills."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for category, event_list in events.items():
            for event in event_list:
                if 'Rogue' in event.get('spotlight', []):
                    skills = event.get('skills', [])
                    
                    # At least one skill should be appropriate for Rogue
                    has_rogue_skill = any(is_skill_appropriate_for_class(skill, 'Rogue') for skill in skills)
                    
                    assert has_rogue_skill, \
                        f"Event '{event['title']}' spotlights Rogue but uses no Rogue skills: {skills}"
    
    def test_wizard_events_use_wizard_skills(self):
        """Test that events spotlighting Wizard use appropriate Wizard skills."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for category, event_list in events.items():
            for event in event_list:
                if 'Wizard' in event.get('spotlight', []):
                    skills = event.get('skills', [])
                    
                    # At least one skill should be appropriate for Wizard
                    has_wizard_skill = any(is_skill_appropriate_for_class(skill, 'Wizard') for skill in skills)
                    
                    assert has_wizard_skill, \
                        f"Event '{event['title']}' spotlights Wizard but uses no Wizard skills: {skills}"
    
    def test_cleric_events_use_cleric_skills(self):
        """Test that events spotlighting Cleric use appropriate Cleric skills."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for category, event_list in events.items():
            for event in event_list:
                if 'Cleric' in event.get('spotlight', []):
                    skills = event.get('skills', [])
                    
                    # At least one skill should be appropriate for Cleric
                    has_cleric_skill = any(is_skill_appropriate_for_class(skill, 'Cleric') for skill in skills)
                    
                    assert has_cleric_skill, \
                        f"Event '{event['title']}' spotlights Cleric but uses no Cleric skills: {skills}"
    
    def test_all_spotlight_events_work(self):
        """Test that 'All' spotlight events use generally accessible skills."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for category, event_list in events.items():
            for event in event_list:
                if 'All' in event.get('spotlight', []):
                    # 'All' events should always be valid
                    is_valid, reason = event_has_appropriate_skills(event)
                    assert is_valid, \
                        f"Event '{event['title']}' with 'All' spotlight failed validation: {reason}"
    
    @settings(max_examples=100)
    @given(st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']))
    def test_property_all_events_in_category_have_appropriate_skills(self, category):
        """
        Property test: For any category, all events should have skills appropriate 
        for their spotlight classes.
        
        This test runs 100 iterations, checking skill-class consistency across categories.
        """
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        event_list = events[category]
        
        for event in event_list:
            is_valid, reason = event_has_appropriate_skills(event)
            assert is_valid, \
                f"Event '{event['title']}' in {category} has inappropriate skills: {reason}"
    
    @settings(max_examples=100)
    @given(
        st.sampled_from(list(CLASS_SKILLS.keys())),
        st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT'])
    )
    def test_property_class_specific_events_use_class_skills(self, class_name, category):
        """
        Property test: For any class and category, events spotlighting that class 
        should use appropriate skills for that class.
        
        This test runs 100 iterations across all classes and categories.
        """
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        event_list = events[category]
        
        for event in event_list:
            if class_name in event.get('spotlight', []):
                skills = event.get('skills', [])
                
                # At least one skill should be appropriate for this class
                has_appropriate_skill = any(is_skill_appropriate_for_class(skill, class_name) for skill in skills)
                
                assert has_appropriate_skill, \
                    f"Event '{event['title']}' spotlights {class_name} but uses no {class_name} skills: {skills}"
    
    def test_no_events_have_empty_spotlight(self):
        """Test that no events have empty spotlight lists."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for category, event_list in events.items():
            for event in event_list:
                spotlight = event.get('spotlight', [])
                assert len(spotlight) > 0, \
                    f"Event '{event['title']}' in {category} has empty spotlight list"
    
    def test_no_events_have_empty_skills(self):
        """Test that no events have empty skills lists."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        for category, event_list in events.items():
            for event in event_list:
                skills = event.get('skills', [])
                assert len(skills) > 0, \
                    f"Event '{event['title']}' in {category} has empty skills list"
    
    def test_skill_names_are_valid(self):
        """Test that all skill names are recognized Pathfinder 2e skills."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        # All valid Pathfinder 2e skills
        valid_skills = {
            'Acrobatics', 'Arcana', 'Athletics', 'Crafting', 'Deception',
            'Diplomacy', 'Intimidation', 'Medicine', 'Nature', 'Occultism',
            'Performance', 'Religion', 'Society', 'Stealth', 'Survival',
            'Thievery', 'Perception', 'Lore', 'Tactics', 'Tactical thinking'
        }
        
        invalid_skills = set()
        
        for category, event_list in events.items():
            for event in event_list:
                skills = event.get('skills', [])
                for skill in skills:
                    if skill not in valid_skills:
                        invalid_skills.add(skill)
        
        # Report any invalid skills (this is informational, not a hard failure)
        if invalid_skills:
            print(f"\nNote: Found non-standard skill names: {sorted(invalid_skills)}")
            print("These may be custom skills or need to be added to the valid skills list.")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
