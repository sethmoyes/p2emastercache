#!/usr/bin/env python3
"""
Integration test for event extraction and validation.
Tests the complete workflow from extraction to validation.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extract_events import extract_event_templates
from event_validation import validate_event, filter_events, get_validation_stats


def test_extraction_and_validation():
    """Test that extracted events can be validated."""
    source_file = 'bin/generators/generate_dungeon_turn_v2.py'
    
    print("=" * 60)
    print("Integration Test: Extraction + Validation")
    print("=" * 60 + "\n")
    
    # Extract events
    print("Step 1: Extracting events from source...")
    templates = extract_event_templates(source_file)
    total_extracted = sum(len(events) for events in templates.values())
    print(f"✓ Extracted {total_extracted} events\n")
    
    # Validate events
    print("Step 2: Validating extracted events...")
    valid_events, invalid_events = filter_events(templates)
    stats = get_validation_stats(valid_events, invalid_events)
    
    print(f"✓ Valid: {stats['total_valid']}")
    print(f"✓ Invalid: {stats['total_invalid']}")
    print(f"✓ Pass rate: {stats['total_valid'] / total_extracted * 100:.1f}%\n")
    
    # Test specific validation cases
    print("Step 3: Testing specific validation patterns...\n")
    
    # Find an event that should be valid
    valid_found = False
    for category, events in valid_events.items():
        if events:
            event = events[0]
            is_valid, reason = validate_event(event)
            print(f"✓ Valid event test: {event['title']}")
            print(f"  Category: {category}")
            print(f"  Valid: {is_valid}, Reason: {reason}\n")
            assert is_valid, "Valid event should pass validation"
            valid_found = True
            break
    
    assert valid_found, "Should have at least one valid event"
    
    # Find an event that should be invalid
    invalid_found = False
    for category, events in invalid_events.items():
        if events:
            event = events[0]
            is_valid, reason = validate_event(event)
            print(f"✓ Invalid event test: {event['title']}")
            print(f"  Category: {category}")
            print(f"  Valid: {is_valid}, Reason: {reason}\n")
            assert not is_valid, "Invalid event should fail validation"
            invalid_found = True
            break
    
    if not invalid_found:
        print("⚠ No invalid events found (all events passed validation)\n")
    
    # Test that validation is consistent
    print("Step 4: Testing validation consistency...")
    for category, events in templates.items():
        for event in events:
            result1 = validate_event(event)
            result2 = validate_event(event)
            assert result1 == result2, f"Validation should be consistent for {event['title']}"
    print("✓ Validation is consistent\n")
    
    # Test that all required fields are present
    print("Step 5: Testing required fields...")
    required_fields = {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'}
    
    for category, events in templates.items():
        for event in events:
            missing = required_fields - set(event.keys())
            assert not missing, f"Event {event.get('title', 'UNKNOWN')} missing fields: {missing}"
    print("✓ All events have required fields\n")
    
    print("=" * 60)
    print("Integration Test: PASSED")
    print("=" * 60)
    
    return stats


def test_backup_file_validation():
    """Test validation against the backup file."""
    backup_file = 'etc/dungeon_turn_events_backup.json'
    
    print("\n" + "=" * 60)
    print("Backup File Validation Test")
    print("=" * 60 + "\n")
    
    # Load backup
    print(f"Loading {backup_file}...")
    with open(backup_file, 'r', encoding='utf-8') as f:
        events = json.load(f)
    
    total = sum(len(event_list) for event_list in events.values())
    print(f"✓ Loaded {total} events\n")
    
    # Validate
    print("Validating events...")
    valid_events, invalid_events = filter_events(events)
    stats = get_validation_stats(valid_events, invalid_events)
    
    print(f"✓ Valid: {stats['total_valid']}")
    print(f"✓ Invalid: {stats['total_invalid']}")
    print(f"✓ Pass rate: {stats['total_valid'] / total * 100:.1f}%\n")
    
    # Check that we have enough valid events to start with
    print(f"Valid events by category:")
    for category, cat_stats in stats['by_category'].items():
        print(f"  {category}: {cat_stats['valid']} valid")
    
    print(f"\nNeed to generate {max(0, 500 - stats['total_valid'])} more events to reach 500 target\n")
    
    print("=" * 60)
    print("Backup File Validation: PASSED")
    print("=" * 60)
    
    return stats


def main():
    """Run all integration tests."""
    try:
        stats1 = test_extraction_and_validation()
        stats2 = test_backup_file_validation()
        
        print("\n" + "=" * 60)
        print("ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  Extracted and validated: {stats1['total_valid']} valid events")
        print(f"  Backup file validated: {stats2['total_valid']} valid events")
        print(f"  Ready to proceed with event generation phase")
        
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
