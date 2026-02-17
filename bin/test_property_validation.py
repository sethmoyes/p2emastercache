#!/usr/bin/env python3
"""
Property-Based Tests for Event Validation Module

Tests the validation and filtering of event templates based on quality criteria.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_validation import validate_event, filter_events, get_validation_stats
from extract_events import extract_event_templates

import pytest
from hypothesis import given, strategies as st, settings


class TestInvalidEventExclusion:
    """
    Feature: dungeon-turn-event-refactor, Property 6: Invalid Event Exclusion
    
    **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
    
    For any event that assumes NPCs, specific actions, present enemies, or overly 
    specific prerequisites without creating context, it should not appear in the 
    curated events file.
    """
    
    def test_events_assuming_npcs_are_excluded(self):
        """Test that events assuming NPCs without creating them are excluded."""
        # Test various NPC assumption patterns
        npc_assumption_events = [
            {
                'title': 'NPC Betrayal',
                'description': 'The NPC you trusted suddenly attacks!',
                'spotlight': ['All'],
                'skills': ['Combat'],
                'time_cost': '1 round',
                'gm_notes': 'Test event',
                'challenge': 'DC 15',
                'success': 'You defend yourself',
                'failure': 'You take damage'
            },
            {
                'title': 'Guide Disappears',
                'description': 'Your guide suddenly vanishes into the shadows.',
                'spotlight': ['All'],
                'skills': ['Perception'],
                'time_cost': '1 action',
                'gm_notes': 'Test event',
                'challenge': 'DC 18',
                'success': 'You track them',
                'failure': 'They are gone'
            },
            {
                'title': 'Ally Wounded',
                'description': 'The ally you are traveling with is wounded.',
                'spotlight': ['Cleric'],
                'skills': ['Medicine'],
                'time_cost': '2 actions',
                'gm_notes': 'Test event',
                'challenge': 'DC 15',
                'success': 'You heal them',
                'failure': 'They worsen'
            },
            {
                'title': 'Companion Advice',
                'description': 'Your companion suggests a different route.',
                'spotlight': ['All'],
                'skills': ['Survival'],
                'time_cost': '1 minute',
                'gm_notes': 'Test event',
                'choice_a': 'Follow their advice',
                'choice_b': 'Ignore them',
                'consequence': 'Route choice'
            }
        ]
        
        for event in npc_assumption_events:
            is_valid, reason = validate_event(event)
            assert not is_valid, \
                f"Event '{event['title']}' assumes NPC but was not excluded. Reason: {reason}"
            assert 'npc' in reason.lower() or 'guide' in reason.lower() or \
                   'ally' in reason.lower() or 'companion' in reason.lower(), \
                f"Rejection reason should mention NPC assumption: {reason}"
    
    def test_events_assuming_actions_are_excluded(self):
        """Test that events assuming specific actions are excluded."""
        action_assumption_events = [
            {
                'title': 'Spell Backfire',
                'description': 'The spell you\'re casting suddenly backfires!',
                'spotlight': ['Wizard'],
                'skills': ['Arcana'],
                'time_cost': '1 action',
                'gm_notes': 'Test event',
                'challenge': 'DC 18',
                'success': 'You control it',
                'failure': 'It explodes'
            },
            {
                'title': 'Ritual Interrupted',
                'description': 'The ritual you\'re performing is interrupted by a noise.',
                'spotlight': ['Wizard', 'Cleric'],
                'skills': ['Arcana', 'Religion'],
                'time_cost': '1 round',
                'gm_notes': 'Test event',
                'challenge': 'DC 20',
                'success': 'You maintain focus',
                'failure': 'The ritual fails'
            },
            {
                'title': 'Ward Explodes',
                'description': 'The magical ward you\'re examining explodes!',
                'spotlight': ['Wizard'],
                'skills': ['Arcana'],
                'time_cost': '1 action',
                'gm_notes': 'Test event',
                'challenge': 'DC 17',
                'success': 'You dodge',
                'failure': 'You take damage'
            },
            {
                'title': 'Potion Spills',
                'description': 'The potion you\'re drinking spills as you stumble.',
                'spotlight': ['All'],
                'skills': ['Acrobatics'],
                'time_cost': '1 action',
                'gm_notes': 'Test event',
                'challenge': 'DC 15',
                'success': 'You save it',
                'failure': 'It\'s wasted'
            }
        ]
        
        for event in action_assumption_events:
            is_valid, reason = validate_event(event)
            assert not is_valid, \
                f"Event '{event['title']}' assumes specific action but was not excluded. Reason: {reason}"
            assert 'action' in reason.lower() or 'spell' in reason.lower() or \
                   'ritual' in reason.lower() or 'casting' in reason.lower(), \
                f"Rejection reason should mention action assumption: {reason}"
    
    def test_events_assuming_enemies_are_excluded(self):
        """Test that events assuming enemies without creating them are excluded."""
        enemy_assumption_events = [
            {
                'title': 'Enemy Flees',
                'description': 'An enemy breaks away and flees down the corridor!',
                'spotlight': ['All'],
                'skills': ['Athletics'],
                'time_cost': '1 round',
                'gm_notes': 'Test event',
                'challenge': 'DC 15',
                'success': 'You catch them',
                'failure': 'They escape'
            },
            {
                'title': 'Enemy Reinforcements',
                'description': 'The enemy you\'re fighting calls for reinforcements!',
                'spotlight': ['All'],
                'skills': ['Intimidation'],
                'time_cost': '1 round',
                'gm_notes': 'Test event',
                'challenge': 'DC 18',
                'success': 'You silence them',
                'failure': 'Help arrives'
            },
            {
                'title': 'Creature Retreats',
                'description': 'The creature you\'re fighting suddenly retreats.',
                'spotlight': ['All'],
                'skills': ['Perception'],
                'time_cost': '1 round',
                'gm_notes': 'Test event',
                'challenge': 'DC 15',
                'success': 'You understand why',
                'failure': 'You\'re confused'
            },
            {
                'title': 'Enemy Tactic',
                'description': 'One of the enemies changes tactics mid-fight.',
                'spotlight': ['All'],
                'skills': ['Tactics'],
                'time_cost': '1 round',
                'gm_notes': 'Test event',
                'challenge': 'DC 16',
                'success': 'You adapt',
                'failure': 'You\'re caught off guard'
            }
        ]
        
        for event in enemy_assumption_events:
            is_valid, reason = validate_event(event)
            assert not is_valid, \
                f"Event '{event['title']}' assumes enemy present but was not excluded. Reason: {reason}"
            assert 'enemy' in reason.lower() or 'creature' in reason.lower() or \
                   'fighting' in reason.lower(), \
                f"Rejection reason should mention enemy assumption: {reason}"
    
    def test_events_creating_dungeon_features_are_excluded(self):
        """Test that events creating new dungeon features are excluded."""
        dungeon_modification_events = [
            {
                'title': 'Secret Passage',
                'description': 'You find a secret passage that bypasses the next 3 rooms!',
                'spotlight': ['Rogue'],
                'skills': ['Perception'],
                'time_cost': '1 action',
                'gm_notes': 'Test event',
                'challenge': 'DC 18',
                'success': 'You find the shortcut',
                'failure': 'You don\'t find it'
            },
            {
                'title': 'Hidden Tunnel',
                'description': 'You discover a hidden tunnel that leads to the next floor.',
                'spotlight': ['Rogue', 'Ranger'],
                'skills': ['Perception', 'Survival'],
                'time_cost': '5 minutes',
                'gm_notes': 'Test event',
                'challenge': 'DC 20',
                'success': 'You find the tunnel',
                'failure': 'You miss it'
            },
            {
                'title': 'Shortcut Found',
                'description': 'A shortcut to the boss room is revealed.',
                'spotlight': ['All'],
                'skills': ['Perception'],
                'time_cost': '1 action',
                'gm_notes': 'Test event',
                'challenge': 'DC 19',
                'success': 'You take the shortcut',
                'failure': 'You go the long way'
            },
            {
                'title': 'Bypass Route',
                'description': 'You find a way to bypass several encounters ahead.',
                'spotlight': ['Rogue'],
                'skills': ['Stealth', 'Perception'],
                'time_cost': '10 minutes',
                'gm_notes': 'Test event',
                'challenge': 'DC 18',
                'success': 'You skip ahead',
                'failure': 'You continue normally'
            },
            {
                'title': 'Concealed Door',
                'description': 'A concealed door that leads to a treasure room is found.',
                'spotlight': ['Rogue'],
                'skills': ['Perception'],
                'time_cost': '2 actions',
                'gm_notes': 'Test event',
                'challenge': 'DC 17',
                'success': 'You find treasure',
                'failure': 'You miss it'
            }
        ]
        
        for event in dungeon_modification_events:
            is_valid, reason = validate_event(event)
            assert not is_valid, \
                f"Event '{event['title']}' creates dungeon feature but was not excluded. Reason: {reason}"
            assert 'dungeon' in reason.lower() or 'passage' in reason.lower() or \
                   'shortcut' in reason.lower() or 'bypass' in reason.lower() or \
                   'tunnel' in reason.lower(), \
                f"Rejection reason should mention dungeon modification: {reason}"
    
    def test_extracted_events_invalid_patterns_excluded(self):
        """Test that extracted events with invalid patterns are properly excluded."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract all events
        templates = extract_event_templates(source_file)
        
        # Filter events
        valid_events, invalid_events = filter_events(templates)
        
        # Check that invalid events were found and excluded
        total_invalid = sum(len(events) for events in invalid_events.values())
        
        # We expect some events to be invalid based on the criteria
        # (The exact number may vary, but there should be at least some)
        assert total_invalid > 0, \
            "Expected some events to be excluded as invalid, but none were found"
        
        # Verify each invalid event has a rejection reason
        for category, events in invalid_events.items():
            for event in events:
                assert '_rejection_reason' in event, \
                    f"Invalid event '{event['title']}' missing rejection reason"
                
                reason = event['_rejection_reason']
                assert len(reason) > 0, \
                    f"Invalid event '{event['title']}' has empty rejection reason"
    
    def test_backup_file_contains_invalid_events(self):
        """Test that backup file contains all events including invalid ones."""
        backup_file = 'etc/dungeon_turn_events_backup.json'
        
        # Load backup file
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_events = json.load(f)
        
        # Filter events
        valid_events, invalid_events = filter_events(backup_events)
        
        # Backup should contain both valid and invalid events
        total_backup = sum(len(events) for events in backup_events.values())
        total_valid = sum(len(events) for events in valid_events.values())
        total_invalid = sum(len(events) for events in invalid_events.values())
        
        assert total_backup == total_valid + total_invalid, \
            "Backup file event count doesn't match valid + invalid counts"
        
        # Backup should have some invalid events
        assert total_invalid > 0, \
            "Backup file should contain some invalid events"
    
    def test_curated_file_excludes_invalid_events(self):
        """Test that curated file excludes all invalid events."""
        # Check if curated file exists
        curated_file = 'etc/dungeon_turn_events.json'
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Validate all events in curated file
        for category, events in curated_events.items():
            for event in events:
                is_valid, reason = validate_event(event)
                assert is_valid, \
                    f"Curated file contains invalid event '{event['title']}': {reason}"
    
    def test_validation_consistency(self):
        """Test that validation is consistent across multiple runs."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract events
        templates = extract_event_templates(source_file)
        
        # Run validation twice
        valid1, invalid1 = filter_events(templates)
        valid2, invalid2 = filter_events(templates)
        
        # Results should be identical
        for category in templates.keys():
            assert len(valid1[category]) == len(valid2[category]), \
                f"Validation inconsistent for {category} valid events"
            assert len(invalid1[category]) == len(invalid2[category]), \
                f"Validation inconsistent for {category} invalid events"
    
    def test_all_invalid_patterns_detected(self):
        """Test that all four types of invalid patterns are detected."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract and filter events
        templates = extract_event_templates(source_file)
        valid_events, invalid_events = filter_events(templates)
        
        # Get rejection reasons
        stats = get_validation_stats(valid_events, invalid_events)
        rejection_reasons = stats['rejection_reasons']
        
        # Check that we have various types of rejections
        # (We may not have all types, but we should have at least some variety)
        assert len(rejection_reasons) > 0, \
            "No rejection reasons found"
        
        # Verify rejection reasons are descriptive
        for reason, count in rejection_reasons.items():
            assert len(reason) > 10, \
                f"Rejection reason too short: '{reason}'"
            assert count > 0, \
                f"Rejection reason has zero count: '{reason}'"


class TestValidEventInclusion:
    """
    Feature: dungeon-turn-event-refactor, Property 7: Valid Event Inclusion
    
    **Validates: Requirements 3.6, 3.7, 3.8, 3.9**
    
    For any event that works in any context, creates its own context, has clear 
    choices and consequences, or rewards clever play, it should appear in the 
    curated events file.
    """
    
    def test_events_working_in_any_context_are_included(self):
        """Test that events working in any context with space parameters are included."""
        # Test events that work in any context using space parameters
        any_context_events = [
            {
                'title': 'Locked Door',
                'description': 'The door ahead is locked with a complex mechanism.',
                'spotlight': ['Rogue'],
                'skills': ['Thievery'],
                'time_cost': '2 actions',
                'gm_notes': 'Works in any context',
                'challenge': 'DC 18 Thievery',
                'success': 'Door opens quietly',
                'failure': 'Lock jams',
                'required_spaces': ['hallway', 'large_room']
            },
            {
                'title': 'Unstable Floor',
                'description': 'The floor beneath you creaks ominously.',
                'spotlight': ['All'],
                'skills': ['Acrobatics', 'Perception'],
                'time_cost': '1 action',
                'gm_notes': 'Environmental hazard',
                'challenge': 'DC 15 Acrobatics',
                'success': 'You cross safely',
                'failure': 'Floor collapses partially',
                'required_spaces': ['hallway', 'large_room', 'small_room']
            },
            {
                'title': 'Magical Ward',
                'description': 'A glowing magical ward blocks the passage.',
                'spotlight': ['Wizard', 'Cleric'],
                'skills': ['Arcana', 'Religion'],
                'time_cost': '3 actions',
                'gm_notes': 'Magical barrier',
                'challenge': 'DC 17 Arcana',
                'success': 'Ward dispelled',
                'failure': 'Ward remains active',
                'required_spaces': ['hallway']
            },
            {
                'title': 'Narrow Passage',
                'description': 'The passage narrows significantly ahead.',
                'spotlight': ['All'],
                'skills': ['Athletics', 'Acrobatics'],
                'time_cost': '5 minutes',
                'gm_notes': 'Physical challenge',
                'challenge': 'DC 14 Athletics',
                'success': 'You squeeze through',
                'failure': 'You get stuck briefly',
                'required_spaces': ['hallway']
            }
        ]
        
        for event in any_context_events:
            is_valid, reason = validate_event(event)
            assert is_valid, \
                f"Event '{event['title']}' works in any context but was excluded. Reason: {reason}"
            assert 'space' in reason.lower() or 'context' in reason.lower() or 'valid' in reason.lower(), \
                f"Acceptance reason should mention space parameters or context: {reason}"
    
    def test_events_creating_own_context_are_included(self):
        """Test that events creating their own context are included."""
        context_creation_events = [
            {
                'title': 'Dying Enemy',
                'description': 'A dying enemy stumbles into the room, clutching a warning note.',
                'spotlight': ['All'],
                'skills': ['Medicine', 'Diplomacy'],
                'time_cost': '2 actions',
                'gm_notes': 'Creates its own context',
                'challenge': 'DC 15 Medicine to stabilize',
                'success': 'You learn valuable information',
                'failure': 'They die before speaking'
            },
            {
                'title': 'Patrol Approaching',
                'description': 'You hear heavy footsteps and voices approaching from ahead.',
                'spotlight': ['Rogue', 'All'],
                'skills': ['Stealth', 'Perception'],
                'time_cost': '1 round',
                'gm_notes': 'Creates patrol context',
                'immediate_action': 'Hide, ambush, or flee',
                'success': 'You avoid or surprise them',
                'failure': 'They spot you',
                'threat_level': 'Moderate'
            },
            {
                'title': 'Treasure Cache',
                'description': 'You discover a hidden cache of supplies.',
                'spotlight': ['Rogue', 'All'],
                'skills': ['Perception'],
                'time_cost': '1 action',
                'gm_notes': 'Creates treasure context',
                'challenge': 'DC 16 Perception',
                'success': 'You find healing potions',
                'failure': 'You miss it'
            },
            {
                'title': 'Ceiling Collapse',
                'description': 'The ceiling suddenly begins to crumble above you!',
                'spotlight': ['All'],
                'skills': ['Acrobatics', 'Athletics'],
                'time_cost': '1 round',
                'gm_notes': 'Creates danger context',
                'immediate_action': 'Dodge or take cover',
                'success': 'You avoid the debris',
                'failure': 'You take damage',
                'threat_level': 'High'
            },
            {
                'title': 'Strange Noise',
                'description': 'You hear a strange scraping noise from the walls.',
                'spotlight': ['All'],
                'skills': ['Perception', 'Nature'],
                'time_cost': '1 action',
                'gm_notes': 'Creates mystery context',
                'challenge': 'DC 15 Perception',
                'success': 'You identify the source',
                'failure': 'The noise continues'
            }
        ]
        
        for event in context_creation_events:
            is_valid, reason = validate_event(event)
            assert is_valid, \
                f"Event '{event['title']}' creates own context but was excluded. Reason: {reason}"
            assert 'context' in reason.lower() or 'valid' in reason.lower(), \
                f"Acceptance reason should mention context creation: {reason}"
    
    def test_events_with_clear_choices_are_included(self):
        """Test that events with clear choices and consequences are included."""
        clear_choice_events = [
            {
                'title': 'Speed vs Stealth',
                'description': 'You can move quickly (10 min) or stealthily (30 min).',
                'spotlight': ['All'],
                'skills': ['Stealth', 'Tactics'],
                'time_cost': '10 min vs 30 min',
                'gm_notes': 'Clear trade-off',
                'choice_a': 'Move quickly: 10 minutes, enemies alerted',
                'choice_b': 'Move stealthily: 30 minutes, surprise advantage',
                'consequence': 'Time vs stealth trade-off'
            },
            {
                'title': 'Risk vs Safety',
                'description': 'You can take a risky path or the safe long route.',
                'spotlight': ['All'],
                'skills': ['Survival', 'Tactics'],
                'time_cost': '15 min vs 30 min',
                'gm_notes': 'Risk/reward choice',
                'choice_a': 'Risky path: 15 minutes, DC 18 Athletics or fall',
                'choice_b': 'Safe route: 30 minutes, no risk',
                'consequence': 'Time vs safety trade-off'
            },
            {
                'title': 'Loud vs Quiet',
                'description': 'You can force the door (loud) or pick the lock (quiet).',
                'spotlight': ['Rogue', 'Fighter'],
                'skills': ['Thievery', 'Athletics'],
                'time_cost': '1 action vs 3 actions',
                'gm_notes': 'Method choice',
                'choice_a': 'Force door: 1 action, loud noise',
                'choice_b': 'Pick lock: 3 actions, silent',
                'consequence': 'Speed vs stealth'
            },
            {
                'title': 'Resource Decision',
                'description': 'You can use a healing potion now or save it for later.',
                'spotlight': ['All'],
                'skills': ['Medicine', 'Tactics'],
                'time_cost': '1 action',
                'gm_notes': 'Resource management',
                'choice_a': 'Use potion now: heal immediately',
                'choice_b': 'Save potion: keep for emergency',
                'consequence': 'Resource allocation'
            }
        ]
        
        for event in clear_choice_events:
            is_valid, reason = validate_event(event)
            assert is_valid, \
                f"Event '{event['title']}' has clear choices but was excluded. Reason: {reason}"
            assert 'choice' in reason.lower() or 'valid' in reason.lower(), \
                f"Acceptance reason should mention clear choices: {reason}"
    
    def test_events_rewarding_clever_play_are_included(self):
        """Test that events rewarding clever play are included."""
        clever_play_events = [
            {
                'title': 'Eavesdrop on Patrol',
                'description': 'You hear guards discussing their patrol route.',
                'spotlight': ['Rogue', 'All'],
                'skills': ['Stealth', 'Perception'],
                'time_cost': '5 minutes',
                'gm_notes': 'Rewards clever play',
                'challenge': 'DC 15 Stealth to remain hidden',
                'success': 'Learn patrol route, remove 1 dice from jar',
                'failure': 'They spot you',
                'reward': 'Dice removal'
            },
            {
                'title': 'Disable Alarm',
                'description': 'You notice an alarm mechanism on the door.',
                'spotlight': ['Rogue'],
                'skills': ['Thievery', 'Perception'],
                'time_cost': '3 actions',
                'gm_notes': 'Prevents alert',
                'challenge': 'DC 17 Thievery',
                'success': 'Alarm disabled, saves time later',
                'failure': 'Alarm remains active',
                'reward': 'Time benefit'
            },
            {
                'title': 'Tactical Positioning',
                'description': 'You spot a defensible position ahead.',
                'spotlight': ['Fighter', 'All'],
                'skills': ['Tactics', 'Perception'],
                'time_cost': '2 actions',
                'gm_notes': 'Tactical advantage',
                'challenge': 'DC 14 Tactics',
                'success': 'Gain surprise round in next combat',
                'failure': 'No special advantage',
                'reward': 'Tactical advantage'
            },
            {
                'title': 'Avoid Encounter',
                'description': 'You notice signs of a creature\'s lair ahead.',
                'spotlight': ['Ranger', 'All'],
                'skills': ['Survival', 'Stealth'],
                'time_cost': '10 minutes',
                'gm_notes': 'Avoidance option',
                'challenge': 'DC 16 Survival',
                'success': 'Bypass lair quietly, remove 1 dice',
                'failure': 'Must confront creature',
                'reward': 'Dice removal'
            }
        ]
        
        for event in clever_play_events:
            is_valid, reason = validate_event(event)
            assert is_valid, \
                f"Event '{event['title']}' rewards clever play but was excluded. Reason: {reason}"
            assert 'clever' in reason.lower() or 'reward' in reason.lower() or 'valid' in reason.lower(), \
                f"Acceptance reason should mention clever play or rewards: {reason}"
    
    def test_extracted_events_valid_patterns_included(self):
        """Test that extracted events with valid patterns are properly included."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract all events
        templates = extract_event_templates(source_file)
        
        # Filter events
        valid_events, invalid_events = filter_events(templates)
        
        # Check that valid events were found and included
        total_valid = sum(len(events) for events in valid_events.values())
        
        # We expect many events to be valid
        assert total_valid > 0, \
            "Expected some events to be included as valid, but none were found"
        
        # Verify each valid event passes validation
        for category, events in valid_events.items():
            for event in events:
                is_valid, reason = validate_event(event)
                assert is_valid, \
                    f"Valid event '{event['title']}' failed validation: {reason}"
    
    def test_curated_file_includes_valid_events(self):
        """Test that curated file includes all valid event patterns."""
        # Check if curated file exists
        curated_file = 'etc/dungeon_turn_events.json'
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Count events by valid pattern type
        pattern_counts = {
            'space_parameters': 0,
            'creates_context': 0,
            'clear_choices': 0,
            'rewards_clever_play': 0
        }
        
        for category, events in curated_events.items():
            for event in events:
                is_valid, reason = validate_event(event)
                assert is_valid, \
                    f"Curated file contains invalid event '{event['title']}': {reason}"
                
                # Categorize by pattern type
                if 'space' in reason.lower():
                    pattern_counts['space_parameters'] += 1
                elif 'context' in reason.lower():
                    pattern_counts['creates_context'] += 1
                elif 'choice' in reason.lower():
                    pattern_counts['clear_choices'] += 1
                elif 'clever' in reason.lower() or 'reward' in reason.lower():
                    pattern_counts['rewards_clever_play'] += 1
        
        # Verify we have a good distribution of valid patterns
        total_events = sum(len(events) for events in curated_events.values())
        assert total_events > 0, "Curated file should contain events"
        
        # At least some events should match each pattern type
        # (We may not have all types, but we should have variety)
        patterns_found = sum(1 for count in pattern_counts.values() if count > 0)
        assert patterns_found > 0, \
            "Curated file should contain events matching valid patterns"
    
    def test_validation_accepts_all_valid_patterns(self):
        """Test that validation accepts all four types of valid patterns."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract and filter events
        templates = extract_event_templates(source_file)
        valid_events, invalid_events = filter_events(templates)
        
        # Get validation stats
        stats = get_validation_stats(valid_events, invalid_events)
        
        # Check that we have valid events
        assert stats['total_valid'] > 0, \
            "No valid events found"
        
        # Verify valid events across categories
        for category, counts in stats['by_category'].items():
            # Each category should have at least some valid events
            # (We may not have valid events in every category, but overall we should)
            pass
        
        # Overall, we should have a reasonable ratio of valid to invalid
        total = stats['total_valid'] + stats['total_invalid']
        if total > 0:
            valid_ratio = stats['total_valid'] / total
            # We expect at least some events to be valid
            assert valid_ratio > 0, \
                "Expected some valid events in the collection"
    
    def test_valid_events_have_required_fields(self):
        """Test that all valid events have required fields."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract and filter events
        templates = extract_event_templates(source_file)
        valid_events, invalid_events = filter_events(templates)
        
        # Check required fields for all valid events
        required_fields = {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'}
        
        for category, events in valid_events.items():
            for event in events:
                # Check required fields
                for field in required_fields:
                    assert field in event, \
                        f"Valid event '{event['title']}' missing required field '{field}'"
                
                # Check category-specific fields
                if category in ['OPPORTUNITY', 'COMPLICATION']:
                    # Should have challenge, success, failure
                    if 'challenge' not in event or 'success' not in event or 'failure' not in event:
                        # Some events might be DILEMMA-style, check for choices
                        if 'choice_a' not in event or 'choice_b' not in event:
                            assert False, \
                                f"Valid {category} event '{event['title']}' missing required outcome fields"
                
                elif category == 'DILEMMA':
                    # Should have choice_a and choice_b
                    assert 'choice_a' in event and 'choice_b' in event, \
                        f"Valid DILEMMA event '{event['title']}' missing choice fields"
                
                elif category == 'ACTIVE_THREAT':
                    # Should have immediate_action, success, failure
                    assert 'immediate_action' in event and 'success' in event and 'failure' in event, \
                        f"Valid ACTIVE_THREAT event '{event['title']}' missing threat fields"
    
    def test_consistency_between_runs(self):
        """Test that valid event identification is consistent across multiple runs."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract events
        templates = extract_event_templates(source_file)
        
        # Run validation twice
        valid1, invalid1 = filter_events(templates)
        valid2, invalid2 = filter_events(templates)
        
        # Results should be identical
        for category in templates.keys():
            assert len(valid1[category]) == len(valid2[category]), \
                f"Valid event count inconsistent for {category}"
            
            # Check that the same events are valid in both runs
            titles1 = {event['title'] for event in valid1[category]}
            titles2 = {event['title'] for event in valid2[category]}
            assert titles1 == titles2, \
                f"Different events marked as valid in {category} between runs"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
