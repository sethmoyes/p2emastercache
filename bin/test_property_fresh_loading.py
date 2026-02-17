#!/usr/bin/env python3
"""
Property-Based Test for Fresh Loading (Property 17)

**Validates: Requirements 10.3**

For any execution of the generator script, events should be loaded fresh from 
the JSON file without caching from previous runs.
"""

import json
import tempfile
import os
import sys
import importlib
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from event_loader import load_events_from_json
from hypothesis import given, strategies as st, settings
import pytest


def create_test_event(title: str, category: str = 'OPPORTUNITY') -> dict:
    """Create a minimal valid test event."""
    base_event = {
        'title': title,
        'description': f'Test description for {title}',
        'spotlight': ['Rogue'],
        'skills': ['Stealth'],
        'time_cost': '1 action',
        'gm_notes': 'Test notes'
    }
    
    if category in ['OPPORTUNITY', 'COMPLICATION']:
        base_event.update({
            'challenge': 'DC 15 Test',
            'success': 'Success outcome',
            'failure': 'Failure outcome'
        })
    elif category == 'DILEMMA':
        base_event.update({
            'choice_a': 'Choice A',
            'choice_b': 'Choice B',
            'consequence': 'Consequence'
        })
    elif category == 'ACTIVE_THREAT':
        base_event.update({
            'immediate_action': 'Act now',
            'success': 'Success outcome',
            'failure': 'Failure outcome',
            'threat_level': 'Moderate'
        })
    
    return base_event


class TestFreshLoading:
    """
    Feature: dungeon-turn-event-refactor, Property 17: Fresh Loading
    
    **Validates: Requirements 10.3**
    
    For any execution of the generator script, events should be loaded fresh from 
    the JSON file without caching from previous runs.
    """
    
    def test_loading_same_file_twice_gives_same_results(self):
        """Test that loading the same file twice gives identical results."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Load twice
        events1 = load_events_from_json(curated_file)
        events2 = load_events_from_json(curated_file)
        
        # Should be identical
        assert events1.keys() == events2.keys(), "Categories differ between loads"
        
        for category in events1.keys():
            assert len(events1[category]) == len(events2[category]), \
                f"Event count differs for {category} between loads"
            
            for i, (event1, event2) in enumerate(zip(events1[category], events2[category])):
                assert event1 == event2, \
                    f"Event {i} in {category} differs between loads"
    
    def test_modifying_file_reflects_in_next_load(self):
        """Test that modifying the JSON file is reflected in the next load."""
        # Create a temporary file with initial events
        initial_events = {
            'OPPORTUNITY': [create_test_event('Initial Event', 'OPPORTUNITY')],
            'COMPLICATION': [],
            'DILEMMA': [],
            'ACTIVE_THREAT': []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(initial_events, f)
            temp_path = f.name
        
        try:
            # Load initial events
            loaded1 = load_events_from_json(temp_path)
            assert len(loaded1['OPPORTUNITY']) == 1
            assert loaded1['OPPORTUNITY'][0]['title'] == 'Initial Event'
            
            # Modify the file
            modified_events = {
                'OPPORTUNITY': [create_test_event('Modified Event', 'OPPORTUNITY')],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }
            
            with open(temp_path, 'w') as f:
                json.dump(modified_events, f)
            
            # Load again - should see the modification
            loaded2 = load_events_from_json(temp_path)
            assert len(loaded2['OPPORTUNITY']) == 1
            assert loaded2['OPPORTUNITY'][0]['title'] == 'Modified Event'
            
            # Verify it's actually different
            assert loaded1['OPPORTUNITY'][0]['title'] != loaded2['OPPORTUNITY'][0]['title']
        
        finally:
            os.unlink(temp_path)
    
    def test_adding_events_reflects_in_next_load(self):
        """Test that adding events to the file is reflected in the next load."""
        # Create a temporary file with one event
        initial_events = {
            'OPPORTUNITY': [create_test_event('Event 1', 'OPPORTUNITY')],
            'COMPLICATION': [],
            'DILEMMA': [],
            'ACTIVE_THREAT': []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(initial_events, f)
            temp_path = f.name
        
        try:
            # Load initial events
            loaded1 = load_events_from_json(temp_path)
            assert len(loaded1['OPPORTUNITY']) == 1
            
            # Add more events
            expanded_events = {
                'OPPORTUNITY': [
                    create_test_event('Event 1', 'OPPORTUNITY'),
                    create_test_event('Event 2', 'OPPORTUNITY'),
                    create_test_event('Event 3', 'OPPORTUNITY')
                ],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }
            
            with open(temp_path, 'w') as f:
                json.dump(expanded_events, f)
            
            # Load again - should see all events
            loaded2 = load_events_from_json(temp_path)
            assert len(loaded2['OPPORTUNITY']) == 3
            assert loaded2['OPPORTUNITY'][0]['title'] == 'Event 1'
            assert loaded2['OPPORTUNITY'][1]['title'] == 'Event 2'
            assert loaded2['OPPORTUNITY'][2]['title'] == 'Event 3'
        
        finally:
            os.unlink(temp_path)
    
    def test_removing_events_reflects_in_next_load(self):
        """Test that removing events from the file is reflected in the next load."""
        # Create a temporary file with multiple events
        initial_events = {
            'OPPORTUNITY': [
                create_test_event('Event 1', 'OPPORTUNITY'),
                create_test_event('Event 2', 'OPPORTUNITY'),
                create_test_event('Event 3', 'OPPORTUNITY')
            ],
            'COMPLICATION': [],
            'DILEMMA': [],
            'ACTIVE_THREAT': []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(initial_events, f)
            temp_path = f.name
        
        try:
            # Load initial events
            loaded1 = load_events_from_json(temp_path)
            assert len(loaded1['OPPORTUNITY']) == 3
            
            # Remove some events
            reduced_events = {
                'OPPORTUNITY': [create_test_event('Event 1', 'OPPORTUNITY')],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }
            
            with open(temp_path, 'w') as f:
                json.dump(reduced_events, f)
            
            # Load again - should see fewer events
            loaded2 = load_events_from_json(temp_path)
            assert len(loaded2['OPPORTUNITY']) == 1
            assert loaded2['OPPORTUNITY'][0]['title'] == 'Event 1'
        
        finally:
            os.unlink(temp_path)
    
    def test_changing_event_fields_reflects_in_next_load(self):
        """Test that changing event fields is reflected in the next load."""
        # Create a temporary file with an event
        initial_events = {
            'OPPORTUNITY': [create_test_event('Test Event', 'OPPORTUNITY')],
            'COMPLICATION': [],
            'DILEMMA': [],
            'ACTIVE_THREAT': []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(initial_events, f)
            temp_path = f.name
        
        try:
            # Load initial events
            loaded1 = load_events_from_json(temp_path)
            assert loaded1['OPPORTUNITY'][0]['description'] == 'Test description for Test Event'
            
            # Modify event fields
            modified_events = {
                'OPPORTUNITY': [create_test_event('Test Event', 'OPPORTUNITY')],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }
            modified_events['OPPORTUNITY'][0]['description'] = 'MODIFIED DESCRIPTION'
            
            with open(temp_path, 'w') as f:
                json.dump(modified_events, f)
            
            # Load again - should see the modification
            loaded2 = load_events_from_json(temp_path)
            assert loaded2['OPPORTUNITY'][0]['description'] == 'MODIFIED DESCRIPTION'
            
            # Verify it's different from first load
            assert loaded1['OPPORTUNITY'][0]['description'] != loaded2['OPPORTUNITY'][0]['description']
        
        finally:
            os.unlink(temp_path)
    
    def test_no_caching_between_loads(self):
        """Test that there's no caching between successive loads."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Perform multiple load-modify-load cycles
            for i in range(5):
                # Write events with iteration number
                events = {
                    'OPPORTUNITY': [create_test_event(f'Event {i}', 'OPPORTUNITY')],
                    'COMPLICATION': [],
                    'DILEMMA': [],
                    'ACTIVE_THREAT': []
                }
                
                with open(temp_path, 'w') as f:
                    json.dump(events, f)
                
                # Load and verify
                loaded = load_events_from_json(temp_path)
                assert loaded['OPPORTUNITY'][0]['title'] == f'Event {i}', \
                    f"Iteration {i}: Expected 'Event {i}', got '{loaded['OPPORTUNITY'][0]['title']}' (possible caching)"
        
        finally:
            os.unlink(temp_path)
    
    @settings(max_examples=50)
    @given(st.integers(min_value=1, max_value=10))
    def test_property_multiple_loads_are_independent(self, num_events):
        """
        Property test: For any number of events, multiple loads should be independent.
        
        This test runs 50 iterations with different event counts.
        """
        # Create a temporary file with events
        events = {
            'OPPORTUNITY': [create_test_event(f'Event {i}', 'OPPORTUNITY') for i in range(num_events)],
            'COMPLICATION': [],
            'DILEMMA': [],
            'ACTIVE_THREAT': []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(events, f)
            temp_path = f.name
        
        try:
            # Load multiple times
            loads = [load_events_from_json(temp_path) for _ in range(3)]
            
            # All loads should be identical
            for i in range(1, len(loads)):
                assert loads[0] == loads[i], \
                    f"Load {i} differs from load 0 (possible caching or state issue)"
        
        finally:
            os.unlink(temp_path)
    
    @settings(max_examples=50)
    @given(st.text(min_size=1, max_size=50))
    def test_property_modifications_always_reflected(self, event_title):
        """
        Property test: For any event title, modifications should be reflected in next load.
        
        This test runs 50 iterations with different event titles.
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Write initial event
            initial_events = {
                'OPPORTUNITY': [create_test_event('Initial', 'OPPORTUNITY')],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }
            
            with open(temp_path, 'w') as f:
                json.dump(initial_events, f)
            
            # Load initial
            loaded1 = load_events_from_json(temp_path)
            assert loaded1['OPPORTUNITY'][0]['title'] == 'Initial'
            
            # Modify with generated title
            modified_events = {
                'OPPORTUNITY': [create_test_event(event_title, 'OPPORTUNITY')],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }
            
            with open(temp_path, 'w') as f:
                json.dump(modified_events, f)
            
            # Load modified
            loaded2 = load_events_from_json(temp_path)
            assert loaded2['OPPORTUNITY'][0]['title'] == event_title, \
                f"Modification not reflected: expected '{event_title}', got '{loaded2['OPPORTUNITY'][0]['title']}'"
        
        finally:
            os.unlink(temp_path)
    
    def test_concurrent_loads_from_same_file(self):
        """Test that concurrent loads from the same file work correctly."""
        curated_file = 'etc/dungeon_turn_events.json'
        
        # Load the same file multiple times "concurrently" (sequentially in this test)
        loads = [load_events_from_json(curated_file) for _ in range(5)]
        
        # All loads should be identical
        for i in range(1, len(loads)):
            assert loads[0] == loads[i], \
                f"Load {i} differs from load 0"
    
    def test_load_after_file_corruption_and_fix(self):
        """Test that loading works correctly after file corruption and fix."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Write valid events
            valid_events = {
                'OPPORTUNITY': [create_test_event('Valid Event', 'OPPORTUNITY')],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }
            
            with open(temp_path, 'w') as f:
                json.dump(valid_events, f)
            
            # Load successfully
            loaded1 = load_events_from_json(temp_path)
            assert loaded1['OPPORTUNITY'][0]['title'] == 'Valid Event'
            
            # Corrupt the file
            with open(temp_path, 'w') as f:
                f.write('{ invalid json }')
            
            # Loading should fail
            with pytest.raises(json.JSONDecodeError):
                load_events_from_json(temp_path)
            
            # Fix the file
            with open(temp_path, 'w') as f:
                json.dump(valid_events, f)
            
            # Loading should work again
            loaded2 = load_events_from_json(temp_path)
            assert loaded2['OPPORTUNITY'][0]['title'] == 'Valid Event'
        
        finally:
            os.unlink(temp_path)
    
    def test_no_module_level_caching(self):
        """Test that there's no module-level caching of loaded events."""
        # This test verifies that the event_loader module doesn't cache results
        
        # Create two different temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1:
            json.dump({
                'OPPORTUNITY': [create_test_event('File 1 Event', 'OPPORTUNITY')],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }, f1)
            temp_path1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
            json.dump({
                'OPPORTUNITY': [create_test_event('File 2 Event', 'OPPORTUNITY')],
                'COMPLICATION': [],
                'DILEMMA': [],
                'ACTIVE_THREAT': []
            }, f2)
            temp_path2 = f2.name
        
        try:
            # Load from both files
            loaded1 = load_events_from_json(temp_path1)
            loaded2 = load_events_from_json(temp_path2)
            
            # Should be different
            assert loaded1['OPPORTUNITY'][0]['title'] == 'File 1 Event'
            assert loaded2['OPPORTUNITY'][0]['title'] == 'File 2 Event'
            assert loaded1['OPPORTUNITY'][0]['title'] != loaded2['OPPORTUNITY'][0]['title']
        
        finally:
            os.unlink(temp_path1)
            os.unlink(temp_path2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
