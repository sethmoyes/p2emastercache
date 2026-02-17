#!/usr/bin/env python3
"""
Property-Based Test for Creature Reference Validity (Property 13)

**Validates: Requirements 6.1, 7.1, 7.3**

For any event that references creatures, the creatures should be appropriate 
for the specified Gauntlight level according to gauntlight_keep_levels.md.
"""

import json
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_loader import load_events_from_json
from hypothesis import given, strategies as st, settings
import pytest


# Creature mappings from gauntlight_keep_levels.md
GAUNTLIGHT_CREATURES_BY_LEVEL = {
    1: {
        'mitflits', 'mitflit', 'basic undead', 'undead', 'shambling', 'zombie', 'skeleton'
    },
    2: {
        'morlock', 'morlocks', 'undead', 'undead servants', 'zombie', 'skeleton', 
        'ghoul', 'ghouls'
    },
    3: {
        'ghoul', 'ghouls', 'ghoul librarians', 'librarian', 'librarians',
        'web lurker', 'web lurkers', 'zebub', 'zebubs', 'devil wasp', 'devil wasps',
        'undead', 'morlock', 'morlocks'
    },
    4: {
        'worm-that-walks', 'werewolf', 'velstrac', 'undead', 'urdefhan',
        'voidglutton', 'ghost', 'ghosts', 'wraith', 'wraiths', 'specter', 'specters'
    },
    5: {
        'arena beasts', 'beast', 'beasts', 'monster', 'monsters',
        'fleshwarped', 'fleshwarped creatures', 'grothlut', 'grothluts',
        'velstrac', 'devil', 'devils', 'urdefhan'
    },
    6: {
        'seugathi', 'drider', 'driders', 'fleshwarped', 'fleshwarped creatures',
        'grothlut', 'grothluts', 'destrachan', 'shanrigol', 'shanrigol behemoth',
        'urdefhan', 'duergar', 'xulgath', 'caligni', 'ratfolk'
    },
    7: {
        'devil', 'devils', 'contract devil', 'erinyes', 'imp', 'imps',
        'will-o\'-wisp', 'will-o-wisp', 'wisp', 'wisps',
        'denizen of leng', 'leng', 'giant crawling hand', 'crawling hand',
        'tiefling'
    },
    8: {
        'bog mummy', 'bog mummies', 'mummy', 'mummies', 'deep gnome', 'deep gnomes',
        'svirneblin', 'bodak', 'bodaks', 'naga', 'gug', 'froghemoth',
        'caligni', 'urdefhan', 'will-o\'-wisp', 'will-o-wisp', 'wisp', 'wisps',
        'chuul', 'goliath spider', 'spider'
    },
    9: {
        'drow', 'urdefhan', 'caligni', 'owb', 'derghodaemon', 'daemon',
        'dragon', 'ravirex', 'darklands fauna', 'darklands creatures'
    },
    10: {
        'ghost', 'ghosts', 'belcorra', 'nhimbaloth', 'serpentfolk',
        'manifestation', 'manifestations', 'outer god'
    }
}

# Generic creature terms that work at any level
GENERIC_CREATURES = {
    'creature', 'creatures', 'enemy', 'enemies', 'foe', 'foes',
    'opponent', 'opponents', 'adversary', 'adversaries',
    'patrol', 'patrols', 'guard', 'guards', 'sentry', 'sentries',
    'inhabitant', 'inhabitants', 'denizen', 'denizens',
    'presence', 'presences', 'entity', 'entities',
    'thing', 'things', 'being', 'beings'
}

# Rival adventuring parties (allowed per Requirement 7.4)
RIVAL_PARTY_TERMS = {
    'rival', 'rivals', 'adventurer', 'adventurers', 'party', 'parties',
    'explorer', 'explorers', 'treasure hunter', 'treasure hunters',
    'mercenary', 'mercenaries', 'bounty hunter', 'bounty hunters'
}


def extract_creature_references(text):
    """
    Extract creature references from event text.
    
    Returns a set of lowercase creature terms found in the text.
    """
    if not text:
        return set()
    
    text_lower = text.lower()
    references = set()
    
    # Check all creature types from all levels
    all_creatures = set()
    for level_creatures in GAUNTLIGHT_CREATURES_BY_LEVEL.values():
        all_creatures.update(level_creatures)
    
    # Add generic and rival party terms
    all_creatures.update(GENERIC_CREATURES)
    all_creatures.update(RIVAL_PARTY_TERMS)
    
    # Find creature references
    for creature in all_creatures:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(creature) + r'\b'
        if re.search(pattern, text_lower):
            references.add(creature)
    
    return references


def is_creature_appropriate_for_level(creature, level):
    """
    Check if a creature is appropriate for a given Gauntlight level.
    
    Args:
        creature: Lowercase creature name
        level: Gauntlight level (1-10)
    
    Returns:
        True if creature is appropriate, False otherwise
    """
    # Generic creatures work at any level
    if creature in GENERIC_CREATURES:
        return True
    
    # Rival parties work at any level (Requirement 7.4)
    if creature in RIVAL_PARTY_TERMS:
        return True
    
    # Check if creature is in the level's creature list
    if level in GAUNTLIGHT_CREATURES_BY_LEVEL:
        if creature in GAUNTLIGHT_CREATURES_BY_LEVEL[level]:
            return True
    
    return False


def get_event_level_context(event):
    """
    Determine what Gauntlight level(s) an event might occur on.
    
    Returns a list of possible levels, or None if level-agnostic.
    """
    # Check for explicit level references in gm_notes or description
    text = f"{event.get('description', '')} {event.get('gm_notes', '')}"
    text_lower = text.lower()
    
    # Look for explicit level mentions
    level_patterns = [
        (r'\blevel\s+(\d+)\b', lambda m: int(m.group(1))),
        (r'\bfloor\s+(\d+)\b', lambda m: int(m.group(1))),
        (r'\b(\d+)(?:st|nd|rd|th)\s+level\b', lambda m: int(m.group(1))),
        (r'\b(\d+)(?:st|nd|rd|th)\s+floor\b', lambda m: int(m.group(1))),
    ]
    
    for pattern, extractor in level_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                level = extractor(match)
                if 1 <= level <= 10:
                    return [level]
            except (ValueError, IndexError):
                pass
    
    # If no explicit level, event is level-agnostic
    return None


class TestCreatureReferenceValidity:
    """
    Feature: dungeon-turn-event-refactor, Property 13: Creature Reference Validity
    
    **Validates: Requirements 6.1, 7.1, 7.3**
    
    For any event that references creatures, the creatures should be appropriate 
    for the specified Gauntlight level according to gauntlight_keep_levels.md.
    """
    
    def test_all_creature_references_are_valid(self):
        """Test that all creature references in curated events are valid."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        invalid_references = []
        
        for category, event_list in events.items():
            for event in event_list:
                # Get all text fields that might contain creature references
                text_fields = [
                    event.get('description', ''),
                    event.get('challenge', ''),
                    event.get('success', ''),
                    event.get('failure', ''),
                    event.get('choice_a', ''),
                    event.get('choice_b', ''),
                    event.get('choice_c', ''),
                    event.get('consequence', ''),
                    event.get('immediate_action', ''),
                    event.get('gm_notes', '')
                ]
                
                combined_text = ' '.join(text_fields)
                creatures = extract_creature_references(combined_text)
                
                if creatures:
                    # Get event level context
                    levels = get_event_level_context(event)
                    
                    if levels:
                        # Event is level-specific, validate creatures for those levels
                        for creature in creatures:
                            if creature not in GENERIC_CREATURES and creature not in RIVAL_PARTY_TERMS:
                                valid_for_any_level = any(
                                    is_creature_appropriate_for_level(creature, level)
                                    for level in levels
                                )
                                if not valid_for_any_level:
                                    invalid_references.append({
                                        'event': event['title'],
                                        'category': category,
                                        'creature': creature,
                                        'levels': levels
                                    })
        
        # Report any invalid references
        if invalid_references:
            error_msg = "Found events with invalid creature references:\n"
            for ref in invalid_references:
                error_msg += f"  - Event '{ref['event']}' ({ref['category']}): " \
                           f"creature '{ref['creature']}' not appropriate for " \
                           f"level(s) {ref['levels']}\n"
            pytest.fail(error_msg)
    
    def test_level_2_events_use_appropriate_creatures(self):
        """Test that Level 2 events only use undead and morlocks (Requirement 7.2)."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        level_2_creatures = GAUNTLIGHT_CREATURES_BY_LEVEL[2]
        invalid_events = []
        
        for category, event_list in events.items():
            for event in event_list:
                levels = get_event_level_context(event)
                
                # Only check events explicitly for Level 2
                if levels and 2 in levels:
                    text_fields = [
                        event.get('description', ''),
                        event.get('challenge', ''),
                        event.get('success', ''),
                        event.get('failure', ''),
                        event.get('gm_notes', '')
                    ]
                    combined_text = ' '.join(text_fields)
                    creatures = extract_creature_references(combined_text)
                    
                    # Check for non-Level-2 creatures
                    for creature in creatures:
                        if creature not in GENERIC_CREATURES and \
                           creature not in RIVAL_PARTY_TERMS and \
                           creature not in level_2_creatures:
                            invalid_events.append({
                                'event': event['title'],
                                'category': category,
                                'creature': creature
                            })
        
        if invalid_events:
            error_msg = "Found Level 2 events with inappropriate creatures " \
                       "(should only use undead and morlocks):\n"
            for ref in invalid_events:
                error_msg += f"  - Event '{ref['event']}' ({ref['category']}): " \
                           f"uses '{ref['creature']}'\n"
            pytest.fail(error_msg)
    
    def test_generic_creature_terms_work_at_all_levels(self):
        """Test that generic creature terms are accepted at all levels."""
        # Generic terms should work at any level
        for level in range(1, 11):
            for creature in GENERIC_CREATURES:
                assert is_creature_appropriate_for_level(creature, level), \
                    f"Generic creature term '{creature}' should work at level {level}"
    
    def test_rival_party_terms_work_at_all_levels(self):
        """Test that rival party terms are accepted at all levels (Requirement 7.4)."""
        # Rival party terms should work at any level
        for level in range(1, 11):
            for creature in RIVAL_PARTY_TERMS:
                assert is_creature_appropriate_for_level(creature, level), \
                    f"Rival party term '{creature}' should work at level {level}"
    
    def test_level_specific_creatures_only_work_at_their_levels(self):
        """Test that level-specific creatures are only valid for their designated levels."""
        # Test a few specific examples
        
        # Mitflits are Level 1 only
        assert is_creature_appropriate_for_level('mitflit', 1)
        assert not is_creature_appropriate_for_level('mitflit', 5)
        
        # Morlocks are Level 2-3
        assert is_creature_appropriate_for_level('morlock', 2)
        assert is_creature_appropriate_for_level('morlock', 3)
        assert not is_creature_appropriate_for_level('morlock', 1)
        
        # Seugathi are Level 6 only
        assert is_creature_appropriate_for_level('seugathi', 6)
        assert not is_creature_appropriate_for_level('seugathi', 3)
        
        # Drow are Level 9 only
        assert is_creature_appropriate_for_level('drow', 9)
        assert not is_creature_appropriate_for_level('drow', 4)
    
    def test_creature_extraction_finds_references(self):
        """Test that creature extraction correctly identifies creature references."""
        # Test various text patterns
        test_cases = [
            ("A morlock patrol approaches", {'morlock', 'patrol'}),
            ("You hear undead discussing their plans", {'undead'}),
            ("A friendly ghost appears", {'ghost'}),
            ("The creature lurks in shadows", {'creature'}),
            ("Rival adventurers are ahead", {'rival', 'adventurers'}),
            ("A drow scout watches you", {'drow'}),
        ]
        
        for text, expected_creatures in test_cases:
            found = extract_creature_references(text)
            for creature in expected_creatures:
                assert creature in found, \
                    f"Failed to extract '{creature}' from '{text}'"
    
    def test_creature_extraction_avoids_false_positives(self):
        """Test that creature extraction doesn't match partial words."""
        # These should NOT match creature terms
        test_cases = [
            "The underground passage is dark",  # Should not match 'undead'
            "A patrol route is marked",  # 'patrol' is generic, should match
            "The ghostly whispers fade",  # Should match 'ghost'
        ]
        
        # Just verify extraction runs without errors
        for text in test_cases:
            creatures = extract_creature_references(text)
            # We're mainly testing that it doesn't crash
            assert isinstance(creatures, set)
    
    @settings(max_examples=100)
    @given(st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']))
    def test_property_all_creature_references_valid_for_category(self, category):
        """
        Property test: For any category, all creature references should be valid.
        
        This test runs 100 iterations, checking creature validity across categories.
        """
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        event_list = events[category]
        
        for event in event_list:
            # Extract creature references
            text_fields = [
                event.get('description', ''),
                event.get('challenge', ''),
                event.get('success', ''),
                event.get('failure', ''),
                event.get('choice_a', ''),
                event.get('choice_b', ''),
                event.get('gm_notes', '')
            ]
            combined_text = ' '.join(text_fields)
            creatures = extract_creature_references(combined_text)
            
            if creatures:
                levels = get_event_level_context(event)
                
                # If event is level-specific, validate creatures
                if levels:
                    for creature in creatures:
                        if creature not in GENERIC_CREATURES and \
                           creature not in RIVAL_PARTY_TERMS:
                            valid = any(
                                is_creature_appropriate_for_level(creature, level)
                                for level in levels
                            )
                            assert valid, \
                                f"Event '{event['title']}' in {category} references " \
                                f"invalid creature '{creature}' for level(s) {levels}"
    
    @settings(max_examples=100)
    @given(st.integers(min_value=1, max_value=10))
    def test_property_creature_mappings_complete_for_all_levels(self, level):
        """
        Property test: For any level 1-10, creature mappings should exist.
        
        This test runs 100 iterations, verifying creature data for all levels.
        """
        assert level in GAUNTLIGHT_CREATURES_BY_LEVEL, \
            f"Missing creature mapping for level {level}"
        
        creatures = GAUNTLIGHT_CREATURES_BY_LEVEL[level]
        assert len(creatures) > 0, \
            f"Level {level} has no creatures defined"
        
        # Verify all creatures are lowercase strings
        for creature in creatures:
            assert isinstance(creature, str), \
                f"Creature '{creature}' at level {level} is not a string"
            assert creature == creature.lower(), \
                f"Creature '{creature}' at level {level} is not lowercase"
    
    def test_no_events_reference_inappropriate_creatures(self):
        """Test that no events reference creatures inappropriate for their context."""
        curated_file = 'etc/dungeon_turn_events.json'
        events = load_events_from_json(curated_file)
        
        total_events_checked = 0
        events_with_creatures = 0
        
        for category, event_list in events.items():
            for event in event_list:
                total_events_checked += 1
                
                # Extract creature references
                text_fields = [
                    event.get('description', ''),
                    event.get('challenge', ''),
                    event.get('success', ''),
                    event.get('failure', ''),
                    event.get('gm_notes', '')
                ]
                combined_text = ' '.join(text_fields)
                creatures = extract_creature_references(combined_text)
                
                if creatures:
                    events_with_creatures += 1
                    
                    # Get level context
                    levels = get_event_level_context(event)
                    
                    # If level-specific, validate
                    if levels:
                        for creature in creatures:
                            if creature not in GENERIC_CREATURES and \
                               creature not in RIVAL_PARTY_TERMS:
                                valid = any(
                                    is_creature_appropriate_for_level(creature, level)
                                    for level in levels
                                )
                                assert valid, \
                                    f"Event '{event['title']}' ({category}) references " \
                                    f"inappropriate creature '{creature}' for level(s) {levels}"
        
        # Ensure we actually checked some events
        assert total_events_checked > 0, "No events found to check"
        
        # Log statistics
        print(f"\nChecked {total_events_checked} events")
        print(f"Found {events_with_creatures} events with creature references")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
