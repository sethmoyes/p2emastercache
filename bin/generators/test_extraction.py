#!/usr/bin/env python3
"""
Property-Based Tests for Event Extraction Module

Tests the extraction of event templates from Python source to JSON format.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_events import (
    extract_event_templates,
    convert_to_json,
    validate_extraction,
    ast_dict_to_python_dict,
    ast_node_to_python_value
)

import pytest
from hypothesis import given, strategies as st, settings


class TestExtractionCompleteness:
    """
    Feature: dungeon-turn-event-refactor, Property 1: Extraction Completeness
    
    **Validates: Requirements 1.1, 2.1, 2.2, 2.5**
    
    For any extraction run, the total number of events in the backup JSON file 
    should equal the total number of events in the Python source template lists.
    """
    
    def test_extraction_count_matches_source(self):
        """Test that all events are extracted from the source file."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract templates
        templates = extract_event_templates(source_file)
        
        # Count extracted events
        total_extracted = sum(len(events) for events in templates.values())
        
        # We know from the source that there are:
        # - 19 OPPORTUNITY_TEMPLATES
        # - 30 COMPLICATION_TEMPLATES  
        # - 19 DILEMMA_TEMPLATES
        # - 19 ACTIVE_THREAT_TEMPLATES
        # Total: 87 events
        expected_total = 87
        
        assert total_extracted == expected_total, \
            f"Expected {expected_total} events, but extracted {total_extracted}"
    
    def test_all_categories_extracted(self):
        """Test that all four event categories are extracted."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Check all categories exist
        expected_categories = {'OPPORTUNITY', 'COMPLICATION', 'DILEMMA', 'ACTIVE_THREAT'}
        assert set(templates.keys()) == expected_categories
        
        # Check each category has events
        for category in expected_categories:
            assert len(templates[category]) > 0, \
                f"Category {category} has no events"
    
    def test_category_counts_match_source(self):
        """Test that each category has the correct number of events."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Expected counts from source file
        expected_counts = {
            'OPPORTUNITY': 19,
            'COMPLICATION': 30,
            'DILEMMA': 19,
            'ACTIVE_THREAT': 19
        }
        
        for category, expected_count in expected_counts.items():
            actual_count = len(templates[category])
            assert actual_count == expected_count, \
                f"Category {category}: expected {expected_count} events, got {actual_count}"
    
    def test_extraction_validation_passes(self):
        """Test that validation passes for extracted templates."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        is_valid, message = validate_extraction(templates, source_file)
        
        assert is_valid, f"Validation failed: {message}"
        assert "87 events" in message
    
    def test_all_events_have_required_fields(self):
        """Test that all extracted events have required fields."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Required fields for all events
        required_fields = {'title', 'description', 'spotlight', 'skills', 'time_cost', 'gm_notes'}
        
        for category, events in templates.items():
            for i, event in enumerate(events):
                event_fields = set(event.keys())
                missing_fields = required_fields - event_fields
                
                assert not missing_fields, \
                    f"Event {i} in {category} ('{event.get('title', 'UNKNOWN')}') " \
                    f"missing required fields: {missing_fields}"
    
    def test_json_serialization_preserves_count(self):
        """Test that JSON serialization preserves event count."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract templates
        templates = extract_event_templates(source_file)
        original_count = sum(len(events) for events in templates.values())
        
        # Serialize to JSON and back
        json_str = json.dumps(templates)
        loaded_templates = json.loads(json_str)
        loaded_count = sum(len(events) for events in loaded_templates.values())
        
        assert loaded_count == original_count, \
            f"JSON round-trip changed event count from {original_count} to {loaded_count}"
    
    def test_backup_file_contains_all_events(self):
        """Test that the backup file contains all extracted events."""
        backup_file = 'etc/dungeon_turn_events_backup.json'
        
        # Load backup file
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_templates = json.load(f)
        
        # Count events in backup
        backup_count = sum(len(events) for events in backup_templates.values())
        
        # Should match expected total
        expected_total = 87
        assert backup_count == expected_total, \
            f"Backup file has {backup_count} events, expected {expected_total}"


class TestDataPreservation:
    """
    Feature: dungeon-turn-event-refactor, Property 2: Data Preservation Round-Trip
    
    **Validates: Requirements 1.2, 1.3, 2.3, 5.1, 5.2, 5.3**
    
    For any event in the Python source, extracting it to JSON and loading it back 
    should produce an equivalent event with all fields and nested structures preserved.
    """
    
    def test_field_types_preserved(self):
        """Test that field data types are preserved during extraction."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Check first event from each category
        for category, events in templates.items():
            if events:
                event = events[0]
                
                # String fields
                assert isinstance(event['title'], str)
                assert isinstance(event['description'], str)
                assert isinstance(event['time_cost'], str)
                assert isinstance(event['gm_notes'], str)
                
                # List fields
                assert isinstance(event['spotlight'], list)
                assert isinstance(event['skills'], list)
                
                # All spotlight items should be strings
                for item in event['spotlight']:
                    assert isinstance(item, str)
                
                # All skill items should be strings
                for item in event['skills']:
                    assert isinstance(item, str)
    
    def test_optional_fields_preserved(self):
        """Test that optional fields are preserved when present."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Find events with optional fields
        optional_fields = ['reward', 'consequence', 'required_spaces', 
                          'requires_recent_combat', 'requires_new_area']
        
        for category, events in templates.items():
            for event in events:
                # Check if any optional fields are present
                for field in optional_fields:
                    if field in event:
                        # Verify the field has a value (not None)
                        assert event[field] is not None, \
                            f"Optional field '{field}' is present but None in event '{event['title']}'"
    
    def test_boolean_fields_preserved(self):
        """Test that boolean fields are correctly extracted."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Find events with boolean fields
        boolean_fields = ['requires_recent_combat', 'requires_new_area']
        
        found_boolean = False
        for category, events in templates.items():
            for event in events:
                for field in boolean_fields:
                    if field in event:
                        assert isinstance(event[field], bool), \
                            f"Field '{field}' should be boolean in event '{event['title']}'"
                        found_boolean = True
        
        assert found_boolean, "No boolean fields found in any events"
    
    def test_nested_list_fields_preserved(self):
        """Test that nested list fields (like required_spaces) are preserved."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Find events with required_spaces
        found_nested_list = False
        for category, events in templates.items():
            for event in events:
                if 'required_spaces' in event:
                    spaces = event['required_spaces']
                    assert isinstance(spaces, list), \
                        f"required_spaces should be a list in event '{event['title']}'"
                    
                    # All items should be strings
                    for space in spaces:
                        assert isinstance(space, str), \
                            f"required_spaces items should be strings in event '{event['title']}'"
                    
                    found_nested_list = True
        
        assert found_nested_list, "No events with required_spaces found"
    
    def test_json_round_trip_preserves_data(self):
        """Test that JSON serialization and deserialization preserves all data."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        # Extract templates
        original_templates = extract_event_templates(source_file)
        
        # Convert to JSON string and back
        json_str = json.dumps(original_templates, indent=2)
        loaded_templates = json.loads(json_str)
        
        # Compare each event
        for category in original_templates.keys():
            assert len(original_templates[category]) == len(loaded_templates[category]), \
                f"Category {category} event count changed during round-trip"
            
            for i, (original, loaded) in enumerate(zip(original_templates[category], 
                                                       loaded_templates[category])):
                # Compare all fields
                assert original.keys() == loaded.keys(), \
                    f"Event {i} in {category} has different fields after round-trip"
                
                for key in original.keys():
                    assert original[key] == loaded[key], \
                        f"Event {i} in {category}: field '{key}' changed during round-trip"


class TestJSONFormatting:
    """
    Feature: dungeon-turn-event-refactor, Property 3: Valid Readable JSON
    
    **Validates: Requirements 1.4, 2.4, 10.1**
    
    For any generated JSON file, it should parse without errors, use consistent 
    indentation, and properly escape special characters.
    """
    
    def test_backup_file_is_valid_json(self):
        """Test that the backup file is valid JSON."""
        backup_file = 'etc/dungeon_turn_events_backup.json'
        
        # Should parse without errors
        with open(backup_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        
        # Should have the expected structure
        assert isinstance(templates, dict)
        assert 'OPPORTUNITY' in templates
        assert 'COMPLICATION' in templates
        assert 'DILEMMA' in templates
        assert 'ACTIVE_THREAT' in templates
    
    def test_json_uses_consistent_indentation(self):
        """Test that JSON file uses 2-space indentation."""
        backup_file = 'etc/dungeon_turn_events_backup.json'
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for 2-space indentation (look for common patterns)
        lines = content.split('\n')
        indented_lines = [line for line in lines if line.startswith('  ') and not line.startswith('    ')]
        
        # Should have many lines with 2-space indentation
        assert len(indented_lines) > 0, "No 2-space indented lines found"
    
    def test_special_characters_escaped(self):
        """Test that special characters are properly escaped in JSON."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Serialize to JSON
        json_str = json.dumps(templates)
        
        # Should be able to parse back without errors
        loaded = json.loads(json_str)
        
        # Check that strings with quotes are preserved
        for category, events in loaded.items():
            for event in events:
                # All string fields should be intact
                assert isinstance(event['title'], str)
                assert len(event['title']) > 0
    
    def test_apostrophes_and_quotes_preserved(self):
        """Test that apostrophes and quotes in text are properly handled."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Serialize to JSON and back
        json_str = json.dumps(templates, indent=2)
        loaded = json.loads(json_str)
        
        # Find events with apostrophes (contractions)
        apostrophe_found = False
        for category, events in loaded.items():
            for event in events:
                # Check all string fields for apostrophes
                for key, value in event.items():
                    if isinstance(value, str) and "'" in value:
                        apostrophe_found = True
                        # Verify the apostrophe is preserved correctly
                        assert "don't" in value or "can't" in value or "won't" in value or \
                               "it's" in value or "you're" in value or "they're" in value or \
                               "'" in value, \
                               f"Apostrophe found but not in expected format in: {value}"
        
        assert apostrophe_found, "No apostrophes found in any events"
    
    def test_nested_structures_preserved(self):
        """Test that nested structures (lists, dicts) are properly serialized."""
        source_file = 'bin/generators/generate_dungeon_turn_v2.py'
        
        templates = extract_event_templates(source_file)
        
        # Serialize to JSON and back
        json_str = json.dumps(templates, indent=2)
        loaded = json.loads(json_str)
        
        # Check nested list structures
        nested_list_found = False
        for category, events in loaded.items():
            for event in events:
                # Check spotlight (list of strings)
                assert isinstance(event['spotlight'], list)
                assert all(isinstance(s, str) for s in event['spotlight'])
                
                # Check skills (list of strings)
                assert isinstance(event['skills'], list)
                assert all(isinstance(s, str) for s in event['skills'])
                
                # Check required_spaces if present (nested list)
                if 'required_spaces' in event:
                    assert isinstance(event['required_spaces'], list)
                    assert all(isinstance(s, str) for s in event['required_spaces'])
                    nested_list_found = True
        
        assert nested_list_found, "No nested list structures found"
    
    def test_two_space_indentation_format(self):
        """Test that JSON uses exactly 2-space indentation as required."""
        import tempfile
        
        # Create test data
        test_templates = {
            'OPPORTUNITY': [
                {
                    'title': 'Test Event',
                    'description': 'Test description with "quotes" and apostrophe\'s',
                    'spotlight': ['Rogue', 'Wizard'],
                    'skills': ['Stealth', 'Arcana'],
                    'time_cost': '10 minutes',
                    'gm_notes': 'Test notes',
                    'required_spaces': ['hallway', 'large_room']
                }
            ]
        }
        
        # Write to temp file with 2-space indentation
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            convert_to_json(test_templates, f.name, indent=2)
            temp_file = f.name
        
        # Read back and check indentation
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # Verify 2-space indentation is used
        lines = content.split('\n')
        
        # Check for 2-space indented lines (should have many)
        two_space_lines = [line for line in lines if line.startswith('  ') and not line.startswith('    ')]
        assert len(two_space_lines) > 0, "No 2-space indented lines found"
        
        # Check for 4-space indented lines (nested level)
        four_space_lines = [line for line in lines if line.startswith('    ') and not line.startswith('      ')]
        assert len(four_space_lines) > 0, "No 4-space indented lines found (nested structures)"
        
        # Verify it's valid JSON
        with open(temp_file, 'r') as f:
            loaded = json.load(f)
        
        assert loaded == test_templates
        
        # Clean up
        Path(temp_file).unlink()
    
    def test_special_characters_in_descriptions(self):
        """Test that various special characters are properly handled."""
        import tempfile
        
        # Create test data with various special characters
        test_templates = {
            'COMPLICATION': [
                {
                    'title': 'Test with "quotes"',
                    'description': 'Text with apostrophe\'s, "double quotes", and newlines\nand tabs\t',
                    'spotlight': ['Rogue'],
                    'skills': ['Stealth'],
                    'time_cost': '5 minutes',
                    'gm_notes': 'Notes with special chars: & < > \\ /',
                    'challenge': 'DC 15',
                    'success': 'Success!',
                    'failure': 'Failure!'
                }
            ]
        }
        
        # Serialize to JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            convert_to_json(test_templates, f.name, indent=2)
            temp_file = f.name
        
        # Load back and verify all special characters preserved
        with open(temp_file, 'r') as f:
            loaded = json.load(f)
        
        event = loaded['COMPLICATION'][0]
        assert '"quotes"' in event['title']
        assert "apostrophe's" in event['description']
        assert '"double quotes"' in event['description']
        assert '&' in event['gm_notes']
        assert '<' in event['gm_notes']
        assert '>' in event['gm_notes']
        
        # Clean up
        Path(temp_file).unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
