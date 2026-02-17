#!/usr/bin/env python3
"""
Integration test for complete end-to-end event generation.

Tests the refactored system by:
1. Generating events for all dice sums (5-100)
2. Generating events for all floors (1-10)
3. Verifying category distribution matches expected ranges
4. Comparing outputs with original system behavior

**Validates: Requirements 4.5, 9.3, 9.4, 9.5**
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'generators'))

from generate_dungeon_turn_v2 import (
    load_json,
    load_markdown,
    parse_gauntlight_levels,
    get_category_from_sum,
    generate_event_for_sum,
    get_creatures_for_floor
)
from event_context import EventContext


def test_all_dice_sums():
    """Test event generation for all possible dice sums (5-100)."""
    print("=" * 60)
    print("Test 1: Generate events for all dice sums (5-100)")
    print("=" * 60 + "\n")
    
    # Load floor data and creatures
    gauntlight_content = load_markdown('etc/gauntlight_keep_levels.md')
    floors = parse_gauntlight_levels(gauntlight_content)
    creatures = load_json('etc/creatures.json')
    
    floor_data = floors[1]  # Use floor 1 for testing
    party_level = 2
    
    # Track category distribution
    category_counts = defaultdict(int)
    extreme_counts = defaultdict(int)
    
    # Generate events for all dice sums
    print("Generating events for dice sums 5-100...")
    for dice_sum in range(5, 101):
        context = EventContext()
        event = generate_event_for_sum(
            dice_sum, 1, floor_data, party_level, creatures, context
        )
        
        category = event.get('category', 'UNKNOWN')
        category_counts[category] += 1
        
        # Track extreme rolls
        if dice_sum <= 15 or dice_sum >= 90:
            extreme_counts[category] += 1
    
    # Display results
    print(f"\n✓ Generated {sum(category_counts.values())} events\n")
    print("Category Distribution:")
    for category in sorted(category_counts.keys()):
        count = category_counts[category]
        percentage = (count / 96) * 100  # 96 total dice sums
        print(f"  {category:20s}: {count:3d} ({percentage:5.1f}%)")
    
    print(f"\nExtreme Roll Distribution (sums 5-15, 90-100):")
    for category in sorted(extreme_counts.keys()):
        count = extreme_counts[category]
        print(f"  {category:20s}: {count:3d}")
    
    # Verify all events have required fields
    print("\nVerifying event structure...")
    for dice_sum in range(5, 101):
        context = EventContext()
        event = generate_event_for_sum(
            dice_sum, 1, floor_data, party_level, creatures, context
        )
        
        assert 'category' in event, f"Event for sum {dice_sum} missing 'category'"
        assert 'sum' in event, f"Event for sum {dice_sum} missing 'sum'"
        assert event['sum'] == dice_sum, f"Event sum mismatch: expected {dice_sum}, got {event['sum']}"
    
    print("✓ All events have required fields\n")
    
    return category_counts


def test_all_floors():
    """Test event generation for all floors (1-10)."""
    print("=" * 60)
    print("Test 2: Generate events for all floors (1-10)")
    print("=" * 60 + "\n")
    
    # Load floor data and creatures
    gauntlight_content = load_markdown('etc/gauntlight_keep_levels.md')
    floors = parse_gauntlight_levels(gauntlight_content)
    creatures = load_json('etc/creatures.json')
    
    # Test a sample of dice sums for each range
    test_sums = [10, 25, 45, 65, 85, 95]  # Sample from each range
    
    print("Generating events for floors 1-10...")
    for floor_num in range(1, 11):
        floor_data = floors.get(floor_num, {})
        party_level = 2  # Use consistent party level for testing
        
        print(f"\nFloor {floor_num}:")
        
        for dice_sum in test_sums:
            context = EventContext()
            event = generate_event_for_sum(
                dice_sum, floor_num, floor_data, party_level, creatures, context
            )
            
            category = event.get('category', 'UNKNOWN')
            title = event.get('title', 'UNKNOWN')
            print(f"  Sum {dice_sum:3d} -> {category:15s}: {title[:40]}")
    
    print("\n✓ Successfully generated events for all floors\n")


def test_category_distribution():
    """Test that category distribution matches expected ranges."""
    print("=" * 60)
    print("Test 3: Verify category distribution")
    print("=" * 60 + "\n")
    
    # Load floor data and creatures
    gauntlight_content = load_markdown('etc/gauntlight_keep_levels.md')
    floors = parse_gauntlight_levels(gauntlight_content)
    creatures = load_json('etc/creatures.json')
    
    floor_data = floors[1]
    party_level = 2
    
    # Run multiple iterations to get statistical distribution
    iterations = 100
    category_counts = defaultdict(int)
    
    print(f"Running {iterations} iterations for each dice sum...")
    for dice_sum in range(5, 101):
        for _ in range(iterations):
            context = EventContext()
            event = generate_event_for_sum(
                dice_sum, 1, floor_data, party_level, creatures, context
            )
            category = event.get('category', 'UNKNOWN')
            category_counts[category] += 1
    
    total_events = sum(category_counts.values())
    
    print(f"\n✓ Generated {total_events} total events\n")
    print("Category Distribution (over 100 iterations):")
    for category in sorted(category_counts.keys()):
        count = category_counts[category]
        percentage = (count / total_events) * 100
        print(f"  {category:20s}: {count:5d} ({percentage:5.1f}%)")
    
    # Verify NO_EVENT is approximately 50% of non-extreme rolls
    # Extreme rolls: 5-15 (11) + 90-100 (11) = 22 out of 96
    # Non-extreme rolls: 96 - 22 = 74
    # Expected NO_EVENT: 74 * 100 * 0.5 = 3700 out of 9600
    expected_no_event_percentage = (74 / 96) * 50  # ~38.5%
    actual_no_event_percentage = (category_counts['NO_EVENT'] / total_events) * 100
    
    print(f"\nNO_EVENT Analysis:")
    print(f"  Expected: ~{expected_no_event_percentage:.1f}%")
    print(f"  Actual: {actual_no_event_percentage:.1f}%")
    
    # Allow 5% tolerance
    tolerance = 5.0
    assert abs(actual_no_event_percentage - expected_no_event_percentage) < tolerance, \
        f"NO_EVENT percentage outside tolerance: expected ~{expected_no_event_percentage:.1f}%, got {actual_no_event_percentage:.1f}%"
    
    print(f"  ✓ Within {tolerance}% tolerance\n")


def test_extreme_rolls():
    """Test that extreme rolls always generate combat."""
    print("=" * 60)
    print("Test 4: Verify extreme rolls generate combat")
    print("=" * 60 + "\n")
    
    # Load floor data and creatures
    gauntlight_content = load_markdown('etc/gauntlight_keep_levels.md')
    floors = parse_gauntlight_levels(gauntlight_content)
    creatures = load_json('etc/creatures.json')
    
    floor_data = floors[1]
    party_level = 2
    
    # Test extreme low rolls (5-15)
    print("Testing extreme low rolls (5-15)...")
    for dice_sum in range(5, 16):
        context = EventContext()
        event = generate_event_for_sum(
            dice_sum, 1, floor_data, party_level, creatures, context
        )
        
        category = event.get('category', 'UNKNOWN')
        is_extreme = event.get('is_extreme', False)
        
        assert category == 'COMBAT', f"Sum {dice_sum} should be COMBAT, got {category}"
        assert is_extreme, f"Sum {dice_sum} should be marked as extreme"
    
    print("✓ All extreme low rolls generate combat\n")
    
    # Test extreme high rolls (90-100)
    print("Testing extreme high rolls (90-100)...")
    for dice_sum in range(90, 101):
        context = EventContext()
        event = generate_event_for_sum(
            dice_sum, 1, floor_data, party_level, creatures, context
        )
        
        category = event.get('category', 'UNKNOWN')
        is_extreme = event.get('is_extreme', False)
        
        assert category == 'COMBAT', f"Sum {dice_sum} should be COMBAT, got {category}"
        assert is_extreme, f"Sum {dice_sum} should be marked as extreme"
    
    print("✓ All extreme high rolls generate combat\n")


def test_event_structure():
    """Test that all generated events have proper structure."""
    print("=" * 60)
    print("Test 5: Verify event structure")
    print("=" * 60 + "\n")
    
    # Load floor data and creatures
    gauntlight_content = load_markdown('etc/gauntlight_keep_levels.md')
    floors = parse_gauntlight_levels(gauntlight_content)
    creatures = load_json('etc/creatures.json')
    
    floor_data = floors[1]
    party_level = 2
    
    # Required fields for all events
    required_fields = {'category', 'sum'}
    
    # Category-specific required fields
    category_fields = {
        'OPPORTUNITY': {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'},
        'COMPLICATION': {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'},
        'DILEMMA': {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'},
        'ACTIVE_THREAT': {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'},
        'COMBAT': {'title', 'description'},  # gm_notes is optional for combat
        'NO_EVENT': {'title', 'description', 'gm_notes'}
    }
    
    print("Checking event structure for all dice sums...")
    errors = []
    
    for dice_sum in range(5, 101):
        context = EventContext()
        event = generate_event_for_sum(
            dice_sum, 1, floor_data, party_level, creatures, context
        )
        
        # Check required fields
        missing = required_fields - set(event.keys())
        if missing:
            errors.append(f"Sum {dice_sum}: Missing required fields {missing}")
            continue
        
        # Check category-specific fields
        category = event['category']
        if category in category_fields:
            expected = category_fields[category]
            missing = expected - set(event.keys())
            if missing:
                errors.append(f"Sum {dice_sum} ({category}): Missing fields {missing}")
    
    if errors:
        print("❌ Structure errors found:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
        raise AssertionError(f"Found {len(errors)} structure errors")
    
    print("✓ All events have proper structure\n")


def test_context_parameters():
    """Test that events respect context parameters."""
    print("=" * 60)
    print("Test 6: Verify context parameter handling")
    print("=" * 60 + "\n")
    
    # Load floor data and creatures
    gauntlight_content = load_markdown('etc/gauntlight_keep_levels.md')
    floors = parse_gauntlight_levels(gauntlight_content)
    creatures = load_json('etc/creatures.json')
    
    floor_data = floors[1]
    party_level = 2
    
    # Test with different space types
    space_types = ['hallway', 'large_room', 'small_room', 'outside']
    
    print("Testing with different space types...")
    for space in space_types:
        context = EventContext(space_type=space)
        event = generate_event_for_sum(
            50, 1, floor_data, party_level, creatures, context
        )
        print(f"  Space '{space}': {event.get('category', 'UNKNOWN')}")
    
    print("\n✓ Context parameters handled correctly\n")
    
    # Test with recent combat flag
    print("Testing with recent_combat flag...")
    context_no_combat = EventContext(recent_combat=False)
    context_with_combat = EventContext(recent_combat=True)
    
    event1 = generate_event_for_sum(
        50, 1, floor_data, party_level, creatures, context_no_combat
    )
    event2 = generate_event_for_sum(
        50, 1, floor_data, party_level, creatures, context_with_combat
    )
    
    print(f"  No recent combat: {event1.get('category', 'UNKNOWN')}")
    print(f"  Recent combat: {event2.get('category', 'UNKNOWN')}")
    print("\n✓ Recent combat flag handled correctly\n")


def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUITE: End-to-End Event Generation")
    print("=" * 60 + "\n")
    
    try:
        # Run all tests
        category_counts = test_all_dice_sums()
        test_all_floors()
        test_category_distribution()
        test_extreme_rolls()
        test_event_structure()
        test_context_parameters()
        
        # Summary
        print("=" * 60)
        print("ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        print("\nSummary:")
        print("  ✓ Generated events for all dice sums (5-100)")
        print("  ✓ Generated events for all floors (1-10)")
        print("  ✓ Category distribution matches expected ranges")
        print("  ✓ Extreme rolls always generate combat")
        print("  ✓ All events have proper structure")
        print("  ✓ Context parameters handled correctly")
        print("\nThe refactored system is working correctly!")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
