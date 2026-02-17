"""
Unit tests for event_loader module.
"""

import json
import os
import tempfile
import pytest
from event_loader import load_events_from_json


def test_load_valid_json():
    """Test loading a valid JSON file with all categories."""
    # Create temporary JSON file
    test_data = {
        "OPPORTUNITY": [
            {
                "title": "Test Opportunity",
                "description": "A test event",
                "spotlight": ["Rogue"],
                "skills": ["Perception"]
            }
        ],
        "COMPLICATION": [
            {
                "title": "Test Complication",
                "description": "Another test event",
                "spotlight": ["Fighter"],
                "skills": ["Athletics"]
            }
        ],
        "DILEMMA": [],
        "ACTIVE_THREAT": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name
    
    try:
        result = load_events_from_json(temp_path)
        
        assert 'OPPORTUNITY' in result
        assert 'COMPLICATION' in result
        assert 'DILEMMA' in result
        assert 'ACTIVE_THREAT' in result
        
        assert len(result['OPPORTUNITY']) == 1
        assert len(result['COMPLICATION']) == 1
        assert len(result['DILEMMA']) == 0
        assert len(result['ACTIVE_THREAT']) == 0
        
        assert result['OPPORTUNITY'][0]['title'] == "Test Opportunity"
        assert result['COMPLICATION'][0]['title'] == "Test Complication"
    finally:
        os.unlink(temp_path)


def test_load_missing_file():
    """Test that FileNotFoundError is raised with clear message."""
    with pytest.raises(FileNotFoundError) as exc_info:
        load_events_from_json('/nonexistent/path/events.json')
    
    error_msg = str(exc_info.value)
    assert "ERROR: Event file not found" in error_msg
    assert "/nonexistent/path/events.json" in error_msg
    assert "etc/ directory" in error_msg


def test_load_malformed_json():
    """Test that JSONDecodeError is raised for invalid JSON."""
    # Create temporary file with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{ "OPPORTUNITY": [ invalid json }')
        temp_path = f.name
    
    try:
        with pytest.raises(json.JSONDecodeError) as exc_info:
            load_events_from_json(temp_path)
        
        error_msg = str(exc_info.value)
        assert "ERROR: Invalid JSON" in error_msg
        assert temp_path in error_msg
    finally:
        os.unlink(temp_path)


def test_load_missing_categories():
    """Test that missing categories are handled gracefully."""
    # Create JSON with only some categories
    test_data = {
        "OPPORTUNITY": [{"title": "Test"}]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name
    
    try:
        result = load_events_from_json(temp_path)
        
        # All categories should be present
        assert 'OPPORTUNITY' in result
        assert 'COMPLICATION' in result
        assert 'DILEMMA' in result
        assert 'ACTIVE_THREAT' in result
        
        # Missing categories should be empty lists
        assert len(result['OPPORTUNITY']) == 1
        assert len(result['COMPLICATION']) == 0
        assert len(result['DILEMMA']) == 0
        assert len(result['ACTIVE_THREAT']) == 0
    finally:
        os.unlink(temp_path)


def test_load_empty_json():
    """Test loading an empty JSON object."""
    test_data = {}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name
    
    try:
        result = load_events_from_json(temp_path)
        
        # All categories should be present with empty lists
        assert result == {
            'OPPORTUNITY': [],
            'COMPLICATION': [],
            'DILEMMA': [],
            'ACTIVE_THREAT': []
        }
    finally:
        os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



def test_validate_opportunity_event_valid():
    """Test validation of a valid OPPORTUNITY event."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Opportunity",
        "description": "A test event",
        "challenge": "DC 18 Perception",
        "success": "You find something",
        "failure": "You don't find anything",
        "spotlight": ["Rogue"],
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes"
    }
    
    assert validate_event_structure(event, "OPPORTUNITY") is True


def test_validate_complication_event_valid():
    """Test validation of a valid COMPLICATION event."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Complication",
        "description": "A test event",
        "challenge": "DC 18 Athletics",
        "success": "You overcome it",
        "failure": "You fail",
        "spotlight": ["Fighter"],
        "skills": ["Athletics"],
        "time_cost": "2 actions",
        "gm_notes": "Test notes"
    }
    
    assert validate_event_structure(event, "COMPLICATION") is True


def test_validate_dilemma_event_valid():
    """Test validation of a valid DILEMMA event."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Dilemma",
        "description": "A test event",
        "choice_a": "Option A",
        "choice_b": "Option B",
        "consequence": "Something happens",
        "spotlight": ["All"],
        "skills": ["Tactics"],
        "time_cost": "10 minutes",
        "gm_notes": "Test notes"
    }
    
    assert validate_event_structure(event, "DILEMMA") is True


def test_validate_active_threat_event_valid():
    """Test validation of a valid ACTIVE_THREAT event."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Threat",
        "description": "A test event",
        "immediate_action": "Do something now!",
        "success": "You survive",
        "failure": "You don't",
        "threat_level": "High",
        "spotlight": ["All"],
        "skills": ["Stealth"],
        "time_cost": "1 round",
        "gm_notes": "Test notes"
    }
    
    assert validate_event_structure(event, "ACTIVE_THREAT") is True


def test_validate_missing_common_field():
    """Test that missing common required field raises ValidationError."""
    from event_loader import validate_event_structure, ValidationError
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        # Missing spotlight
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success",
        "failure": "Failure"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_event_structure(event, "OPPORTUNITY")
    
    assert "missing required field 'spotlight'" in str(exc_info.value)


def test_validate_missing_category_field():
    """Test that missing category-specific field raises ValidationError."""
    from event_loader import validate_event_structure, ValidationError
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["Rogue"],
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success"
        # Missing failure
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_event_structure(event, "OPPORTUNITY")
    
    assert "missing required field 'failure'" in str(exc_info.value)
    assert "OPPORTUNITY" in str(exc_info.value)


def test_validate_wrong_data_type():
    """Test that wrong data type raises ValidationError."""
    from event_loader import validate_event_structure, ValidationError
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": "Rogue",  # Should be list
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success",
        "failure": "Failure"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_event_structure(event, "OPPORTUNITY")
    
    assert "must be list" in str(exc_info.value)


def test_validate_list_contains_non_strings():
    """Test that list with non-string items raises ValidationError."""
    from event_loader import validate_event_structure, ValidationError
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["Rogue", 123],  # Contains non-string
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success",
        "failure": "Failure"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_event_structure(event, "OPPORTUNITY")
    
    assert "must contain only strings" in str(exc_info.value)


def test_validate_optional_fields():
    """Test that optional fields are validated when present."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["Rogue"],
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success",
        "failure": "Failure",
        "required_spaces": ["hallway", "large_room"],
        "requires_recent_combat": True,
        "requires_new_area": False,
        "reward": "Remove 1 die"
    }
    
    assert validate_event_structure(event, "OPPORTUNITY") is True


def test_validate_optional_field_wrong_type():
    """Test that optional field with wrong type raises ValidationError."""
    from event_loader import validate_event_structure, ValidationError
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["Rogue"],
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success",
        "failure": "Failure",
        "requires_recent_combat": "yes"  # Should be bool
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_event_structure(event, "OPPORTUNITY")
    
    assert "must be bool" in str(exc_info.value)


def test_validate_infer_category_opportunity():
    """Test category inference for OPPORTUNITY/COMPLICATION events."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["Rogue"],
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success",
        "failure": "Failure"
    }
    
    # Should infer OPPORTUNITY from challenge field
    assert validate_event_structure(event) is True


def test_validate_infer_category_dilemma():
    """Test category inference for DILEMMA events."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["All"],
        "skills": ["Tactics"],
        "time_cost": "10 minutes",
        "gm_notes": "Test notes",
        "choice_a": "Option A",
        "choice_b": "Option B",
        "consequence": "Something happens"
    }
    
    # Should infer DILEMMA from choice fields
    assert validate_event_structure(event) is True


def test_validate_infer_category_active_threat():
    """Test category inference for ACTIVE_THREAT events."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["All"],
        "skills": ["Stealth"],
        "time_cost": "1 round",
        "gm_notes": "Test notes",
        "immediate_action": "Do something!",
        "success": "You survive",
        "failure": "You don't",
        "threat_level": "High"
    }
    
    # Should infer ACTIVE_THREAT from immediate_action and threat_level
    assert validate_event_structure(event) is True


def test_validate_cannot_infer_category():
    """Test that ValidationError is raised when category cannot be inferred."""
    from event_loader import validate_event_structure, ValidationError
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["All"],
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes"
        # No category-specific fields
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_event_structure(event)
    
    assert "Cannot infer category" in str(exc_info.value)


def test_validate_invalid_category():
    """Test that ValidationError is raised for invalid category."""
    from event_loader import validate_event_structure, ValidationError
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["All"],
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success",
        "failure": "Failure"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_event_structure(event, "INVALID_CATEGORY")
    
    assert "Unknown event category" in str(exc_info.value)
    assert "INVALID_CATEGORY" in str(exc_info.value)


def test_validate_dilemma_with_optional_choice_c():
    """Test that DILEMMA events can have optional choice_c field."""
    from event_loader import validate_event_structure
    
    event = {
        "title": "Test Dilemma",
        "description": "A test event",
        "choice_a": "Option A",
        "choice_b": "Option B",
        "choice_c": "Option C",
        "consequence": "Something happens",
        "spotlight": ["All"],
        "skills": ["Tactics"],
        "time_cost": "10 minutes",
        "gm_notes": "Test notes"
    }
    
    assert validate_event_structure(event, "DILEMMA") is True


def test_validate_required_spaces_non_strings():
    """Test that required_spaces with non-string items raises ValidationError."""
    from event_loader import validate_event_structure, ValidationError
    
    event = {
        "title": "Test Event",
        "description": "A test event",
        "spotlight": ["Rogue"],
        "skills": ["Perception"],
        "time_cost": "1 action",
        "gm_notes": "Test notes",
        "challenge": "DC 18",
        "success": "Success",
        "failure": "Failure",
        "required_spaces": ["hallway", 123]  # Contains non-string
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_event_structure(event, "OPPORTUNITY")
    
    assert "required_spaces" in str(exc_info.value)
    assert "must contain only strings" in str(exc_info.value)


def test_organize_events_by_category_valid():
    """Test organizing events with all valid categories."""
    from event_loader import organize_events_by_category
    
    events = {
        "OPPORTUNITY": [{"title": "Opp1"}, {"title": "Opp2"}],
        "COMPLICATION": [{"title": "Comp1"}],
        "DILEMMA": [],
        "ACTIVE_THREAT": [{"title": "Threat1"}]
    }
    
    result = organize_events_by_category(events)
    
    assert len(result) == 4
    assert "OPPORTUNITY" in result
    assert "COMPLICATION" in result
    assert "DILEMMA" in result
    assert "ACTIVE_THREAT" in result
    
    assert len(result["OPPORTUNITY"]) == 2
    assert len(result["COMPLICATION"]) == 1
    assert len(result["DILEMMA"]) == 0
    assert len(result["ACTIVE_THREAT"]) == 1


def test_organize_events_by_category_missing_categories():
    """Test organizing events when some categories are missing."""
    from event_loader import organize_events_by_category
    
    events = {
        "OPPORTUNITY": [{"title": "Opp1"}],
        "COMPLICATION": [{"title": "Comp1"}]
    }
    
    result = organize_events_by_category(events)
    
    # All categories should be present
    assert len(result) == 4
    assert "OPPORTUNITY" in result
    assert "COMPLICATION" in result
    assert "DILEMMA" in result
    assert "ACTIVE_THREAT" in result
    
    # Missing categories should have empty lists
    assert len(result["OPPORTUNITY"]) == 1
    assert len(result["COMPLICATION"]) == 1
    assert len(result["DILEMMA"]) == 0
    assert len(result["ACTIVE_THREAT"]) == 0


def test_organize_events_by_category_empty():
    """Test organizing an empty events dictionary."""
    from event_loader import organize_events_by_category
    
    events = {}
    
    result = organize_events_by_category(events)
    
    # All categories should be present with empty lists
    assert result == {
        "OPPORTUNITY": [],
        "COMPLICATION": [],
        "DILEMMA": [],
        "ACTIVE_THREAT": []
    }


def test_organize_events_by_category_invalid_key():
    """Test that invalid category keys raise ValidationError."""
    from event_loader import organize_events_by_category, ValidationError
    
    events = {
        "OPPORTUNITY": [{"title": "Opp1"}],
        "INVALID_CATEGORY": [{"title": "Invalid"}],
        "ANOTHER_BAD_KEY": []
    }
    
    with pytest.raises(ValidationError) as exc_info:
        organize_events_by_category(events)
    
    error_msg = str(exc_info.value)
    assert "Invalid category keys found" in error_msg
    assert "INVALID_CATEGORY" in error_msg or "ANOTHER_BAD_KEY" in error_msg
    assert "Valid categories" in error_msg


def test_organize_events_by_category_preserves_data():
    """Test that organizing events preserves all event data."""
    from event_loader import organize_events_by_category
    
    events = {
        "OPPORTUNITY": [
            {
                "title": "Test Event",
                "description": "Test description",
                "spotlight": ["Rogue"],
                "skills": ["Perception"],
                "nested": {"key": "value"}
            }
        ]
    }
    
    result = organize_events_by_category(events)
    
    # Verify data is preserved
    assert result["OPPORTUNITY"][0]["title"] == "Test Event"
    assert result["OPPORTUNITY"][0]["description"] == "Test description"
    assert result["OPPORTUNITY"][0]["spotlight"] == ["Rogue"]
    assert result["OPPORTUNITY"][0]["nested"]["key"] == "value"
