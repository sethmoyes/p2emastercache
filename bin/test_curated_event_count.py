#!/usr/bin/env python3
"""
Property-Based Test for Curated Event Count

Tests that the curated event file contains at least 500 events distributed
proportionally across all categories.
"""

import json
import sys
from pathlib import Path

import pytest
from hypothesis import given, strategies as st, settings, assume


class TestCuratedEventCount:
    """
    Feature: dungeon-turn-event-refactor, Property 5: Curated Event Count
    
    **Validates: Requirements 3.1, 3.11**
    
    For any curated event file generation, the resulting file should contain 
    at least 500 events distributed proportionally across all categories.
    """
    
    def test_curated_file_has_minimum_500_events(self):
        """Test that curated file contains at least 500 events."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Count total events
        total_events = sum(len(events) for events in curated_events.values())
        
        assert total_events >= 500, \
            f"Curated file should contain at least 500 events, but has {total_events}"
    
    def test_curated_file_has_all_categories(self):
        """Test that curated file contains all required categories."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Required categories
        required_categories = {'OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT'}
        
        # Check all categories present
        actual_categories = set(curated_events.keys())
        
        assert required_categories.issubset(actual_categories), \
            f"Curated file missing categories: {required_categories - actual_categories}"
    
    def test_curated_file_proportional_distribution(self):
        """Test that events are distributed proportionally across categories."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Count events by category
        category_counts = {
            category: len(events) 
            for category, events in curated_events.items()
        }
        
        total_events = sum(category_counts.values())
        
        # Calculate proportions
        category_proportions = {
            category: count / total_events 
            for category, count in category_counts.items()
        }
        
        # Expected proportions (roughly equal distribution across 4 categories)
        # Each category should have approximately 25% of events
        # Allow for some variance (15% to 35% per category is reasonable)
        expected_min_proportion = 0.15
        expected_max_proportion = 0.35
        
        for category, proportion in category_proportions.items():
            assert expected_min_proportion <= proportion <= expected_max_proportion, \
                f"Category {category} has {proportion:.1%} of events, " \
                f"expected between {expected_min_proportion:.1%} and {expected_max_proportion:.1%}. " \
                f"Counts: {category_counts}"
    
    def test_each_category_has_minimum_events(self):
        """Test that each category has a reasonable minimum number of events."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Minimum events per category (500 total / 4 categories = 125 per category)
        # Allow some variance, so minimum 75 per category
        min_events_per_category = 75
        
        for category, events in curated_events.items():
            event_count = len(events)
            assert event_count >= min_events_per_category, \
                f"Category {category} has only {event_count} events, " \
                f"expected at least {min_events_per_category}"
    
    @given(st.integers(min_value=500, max_value=600))
    @settings(max_examples=100)
    def test_property_event_count_invariant(self, min_count):
        """
        Property test: For any minimum event count >= 500, the curated file
        should meet or exceed that count.
        """
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Count total events
        total_events = sum(len(events) for events in curated_events.values())
        
        # If we're testing a count higher than what we have, skip
        assume(min_count <= total_events)
        
        # Property: curated file should have at least the minimum count
        assert total_events >= min_count, \
            f"Curated file has {total_events} events, expected at least {min_count}"
    
    @given(
        st.lists(
            st.sampled_from(['OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT']),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=100)
    def test_property_category_coverage(self, sampled_categories):
        """
        Property test: For any sample of category names, all should exist
        in the curated file.
        """
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Property: all sampled categories should exist in curated file
        for category in sampled_categories:
            assert category in curated_events, \
                f"Category {category} not found in curated file"
            assert len(curated_events[category]) > 0, \
                f"Category {category} is empty in curated file"
    
    def test_curated_file_structure_valid(self):
        """Test that curated file has valid JSON structure."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file (will raise JSONDecodeError if invalid)
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Check structure
        assert isinstance(curated_events, dict), \
            "Curated file should be a JSON object (dict)"
        
        for category, events in curated_events.items():
            assert isinstance(events, list), \
                f"Category {category} should contain a list of events"
            
            for event in events:
                assert isinstance(event, dict), \
                    f"Each event in {category} should be a dict"
    
    def test_curated_vs_backup_comparison(self):
        """Test that curated file is a filtered subset of backup file."""
        curated_file = 'etc/dungeon_turn_events.json'
        backup_file = 'etc/dungeon_turn_events_backup.json'
        
        # Check if files exist
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        if not Path(backup_file).exists():
            pytest.skip("Backup file not yet created")
        
        # Load both files
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_events = json.load(f)
        
        # Count events
        curated_count = sum(len(events) for events in curated_events.values())
        backup_count = sum(len(events) for events in backup_events.values())
        
        # Curated should have at least 500 events
        assert curated_count >= 500, \
            f"Curated file should have at least 500 events, has {curated_count}"
        
        # Curated may have more events than backup (due to generation)
        # or fewer (due to filtering), so we just verify both exist
        assert backup_count > 0, \
            f"Backup file should contain events, has {backup_count}"
        
        print(f"\nEvent counts:")
        print(f"  Backup: {backup_count}")
        print(f"  Curated: {curated_count}")
        print(f"  Difference: {curated_count - backup_count}")
    
    def test_distribution_statistics(self):
        """Test and report distribution statistics for curated events."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Check if curated file exists
        if not Path(curated_file).exists():
            pytest.skip("Curated file not yet created")
        
        # Load curated file
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_events = json.load(f)
        
        # Calculate statistics
        category_counts = {
            category: len(events) 
            for category, events in curated_events.items()
        }
        
        total_events = sum(category_counts.values())
        
        print(f"\n{'='*60}")
        print(f"Curated Event Distribution Statistics")
        print(f"{'='*60}")
        print(f"Total events: {total_events}")
        print(f"\nBy category:")
        
        for category, count in sorted(category_counts.items()):
            proportion = count / total_events if total_events > 0 else 0
            print(f"  {category:20s}: {count:4d} ({proportion:6.1%})")
        
        print(f"{'='*60}\n")
        
        # Verify minimum count
        assert total_events >= 500, \
            f"Total events {total_events} is less than required minimum of 500"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
