#!/usr/bin/env python3
"""
Test script for event validation module.
Tests the validation function with example events.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_validation import validate_event, filter_events, get_validation_stats


def test_invalid_event_npc_assumption():
    """Test that events assuming NPCs are rejected."""
    event = {
        'title': 'NPC Betrayal',
        'description': 'The NPC you trusted suddenly attacks!',
        'spotlight': ['All'],
        'skills': ['Combat'],
        'time_cost': '1 round',
        'gm_notes': 'Test event',
        'challenge': 'DC 15',
        'success': 'You defend yourself',
        'failure': 'You take damage'
    }
    
    is_valid, reason = validate_event(event)
    print(f"Test NPC assumption: {'PASS' if not is_valid else 'FAIL'}")
    print(f"  Valid: {is_valid}, Reason: {reason}\n")
    assert not is_valid, "Should reject events assuming NPCs"


def test_invalid_event_action_assumption():
    """Test that events assuming specific actions are rejected."""
    event = {
        'title': 'Spell Backfire',
        'description': 'The spell you\'re casting suddenly backfires!',
        'spotlight': ['Wizard'],
        'skills': ['Arcana'],
        'time_cost': '1 action',
        'gm_notes': 'Test event',
        'challenge': 'DC 18',
        'success': 'You control it',
        'failure': 'It explodes'
    }
    
    is_valid, reason = validate_event(event)
    print(f"Test action assumption: {'PASS' if not is_valid else 'FAIL'}")
    print(f"  Valid: {is_valid}, Reason: {reason}\n")
    assert not is_valid, "Should reject events assuming specific actions"


def test_invalid_event_enemy_assumption():
    """Test that events assuming enemies are rejected."""
    event = {
        'title': 'Enemy Flees',
        'description': 'An enemy breaks away and flees down the corridor!',
        'spotlight': ['All'],
        'skills': ['Athletics'],
        'time_cost': '1 round',
        'gm_notes': 'Test event',
        'challenge': 'DC 15',
        'success': 'You catch them',
        'failure': 'They escape'
    }
    
    is_valid, reason = validate_event(event)
    print(f"Test enemy assumption: {'PASS' if not is_valid else 'FAIL'}")
    print(f"  Valid: {is_valid}, Reason: {reason}\n")
    assert not is_valid, "Should reject events assuming enemies"


def test_invalid_event_dungeon_modification():
    """Test that events creating dungeon features are rejected."""
    event = {
        'title': 'Secret Passage',
        'description': 'You find a secret passage that bypasses the next 3 rooms!',
        'spotlight': ['Rogue'],
        'skills': ['Perception'],
        'time_cost': '1 action',
        'gm_notes': 'Test event',
        'challenge': 'DC 18',
        'success': 'You find the shortcut',
        'failure': 'You don\'t find it'
    }
    
    is_valid, reason = validate_event(event)
    print(f"Test dungeon modification: {'PASS' if not is_valid else 'FAIL'}")
    print(f"  Valid: {is_valid}, Reason: {reason}\n")
    assert not is_valid, "Should reject events creating dungeon features"


def test_valid_event_creates_context():
    """Test that events creating their own context are accepted."""
    event = {
        'title': 'Dying Enemy',
        'description': 'A dying enemy stumbles into the room, clutching a warning note.',
        'spotlight': ['All'],
        'skills': ['Medicine', 'Diplomacy'],
        'time_cost': '2 actions',
        'gm_notes': 'Creates its own context',
        'challenge': 'DC 15 Medicine to stabilize',
        'success': 'You learn valuable information',
        'failure': 'They die before speaking'
    }
    
    is_valid, reason = validate_event(event)
    print(f"Test creates context: {'PASS' if is_valid else 'FAIL'}")
    print(f"  Valid: {is_valid}, Reason: {reason}\n")
    assert is_valid, "Should accept events creating their own context"


def test_valid_event_space_parameters():
    """Test that events using space parameters are accepted."""
    event = {
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
    }
    
    is_valid, reason = validate_event(event)
    print(f"Test space parameters: {'PASS' if is_valid else 'FAIL'}")
    print(f"  Valid: {is_valid}, Reason: {reason}\n")
    assert is_valid, "Should accept events with space parameters"


def test_valid_event_clear_choices():
    """Test that events with clear choices are accepted."""
    event = {
        'title': 'Speed vs Stealth',
        'description': 'You can move quickly (10 min) or stealthily (30 min).',
        'spotlight': ['All'],
        'skills': ['Stealth', 'Tactics'],
        'time_cost': '10 min vs 30 min',
        'gm_notes': 'Clear trade-off',
        'choice_a': 'Move quickly: 10 minutes, enemies alerted',
        'choice_b': 'Move stealthily: 30 minutes, surprise advantage',
        'consequence': 'Time vs stealth trade-off'
    }
    
    is_valid, reason = validate_event(event)
    print(f"Test clear choices: {'PASS' if is_valid else 'FAIL'}")
    print(f"  Valid: {is_valid}, Reason: {reason}\n")
    assert is_valid, "Should accept events with clear choices"


def test_valid_event_rewards_clever_play():
    """Test that events rewarding clever play are accepted."""
    event = {
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
    }
    
    is_valid, reason = validate_event(event)
    print(f"Test rewards clever play: {'PASS' if is_valid else 'FAIL'}")
    print(f"  Valid: {is_valid}, Reason: {reason}\n")
    assert is_valid, "Should accept events rewarding clever play"


def test_filter_events():
    """Test filtering a collection of events."""
    events = {
        'OPPORTUNITY': [
            {
                'title': 'Valid Event',
                'description': 'You find a healing potion.',
                'spotlight': ['All'],
                'skills': ['Perception'],
                'time_cost': '1 action',
                'gm_notes': 'Valid',
                'challenge': 'DC 12',
                'success': 'You get the potion',
                'failure': 'You miss it'
            },
            {
                'title': 'Invalid Event',
                'description': 'The NPC you\'re with gives you a potion.',
                'spotlight': ['All'],
                'skills': ['Diplomacy'],
                'time_cost': '1 action',
                'gm_notes': 'Invalid',
                'challenge': 'DC 10',
                'success': 'You get it',
                'failure': 'They refuse'
            }
        ],
        'COMPLICATION': [],
        'DILEMMA': [],
        'ACTIVE_THREAT': []
    }
    
    valid, invalid = filter_events(events)
    
    print(f"Test filter events: {'PASS' if len(valid['OPPORTUNITY']) == 1 and len(invalid['OPPORTUNITY']) == 1 else 'FAIL'}")
    print(f"  Valid: {len(valid['OPPORTUNITY'])}, Invalid: {len(invalid['OPPORTUNITY'])}\n")
    
    assert len(valid['OPPORTUNITY']) == 1, "Should have 1 valid event"
    assert len(invalid['OPPORTUNITY']) == 1, "Should have 1 invalid event"
    
    # Test stats
    stats = get_validation_stats(valid, invalid)
    print(f"Validation stats:")
    print(f"  Total valid: {stats['total_valid']}")
    print(f"  Total invalid: {stats['total_invalid']}")
    print(f"  Rejection reasons: {stats['rejection_reasons']}\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Event Validation Tests")
    print("=" * 60 + "\n")
    
    try:
        test_invalid_event_npc_assumption()
        test_invalid_event_action_assumption()
        test_invalid_event_enemy_assumption()
        test_invalid_event_dungeon_modification()
        test_valid_event_creates_context()
        test_valid_event_space_parameters()
        test_valid_event_clear_choices()
        test_valid_event_rewards_clever_play()
        test_filter_events()
        
        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
