# Design Document

## Overview

This design describes the refactoring of the dungeon turn event generation system to externalize event templates from Python code into JSON configuration files. The refactoring separates data from logic, enabling easier maintenance and customization of events without modifying code.

The system will:
1. Extract all existing event templates from Python to JSON
2. Create a complete backup of all events
3. Generate and curate a collection of 500+ working events
4. Modify the generator script to load events from JSON
5. Maintain backward compatibility with existing event selection logic

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Generator Script                          │
│  (generate_dungeon_turn_v2.py)                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Event Loading Module                                 │  │
│  │  - load_events_from_json()                           │  │
│  │  - validate_event_structure()                        │  │
│  │  - organize_by_category()                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Event Selection Logic (unchanged)                    │  │
│  │  - generate_opportunity_event()                      │  │
│  │  - generate_complication_event()                     │  │
│  │  - generate_dilemma_event()                          │  │
│  │  - generate_active_threat_event()                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ reads from
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              JSON Event Files                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  dungeon_turn_events_backup.json                     │  │
│  │  - All original events (unfiltered)                  │  │
│  │  - Complete historical record                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  dungeon_turn_events.json                            │  │
│  │  - 500+ curated working events                       │  │
│  │  - Organized by category                             │  │
│  │  - Validated and tested                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Extraction Phase**: Python script extracts hardcoded templates → JSON backup file
2. **Curation Phase**: Filter and generate events → JSON curated file
3. **Runtime Phase**: Generator loads JSON → Validates structure → Uses in event generation

## Components and Interfaces

### 1. Event Extraction Module

**Purpose**: Extract hardcoded event templates from Python to JSON format.

**Functions**:
- `extract_event_templates()`: Parse Python source to extract event dictionaries
- `convert_to_json()`: Serialize Python dicts to JSON with proper formatting
- `validate_extraction()`: Verify all events were extracted correctly

**Interface**:
```python
def extract_event_templates(source_file: str) -> dict:
    """
    Extract all event templates from Python source file.
    
    Args:
        source_file: Path to generate_dungeon_turn_v2.py
        
    Returns:
        Dictionary with keys: OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT
        Each key maps to a list of event dictionaries
    """
    pass
```

### 2. Event Curation Module

**Purpose**: Filter events based on quality criteria and generate new events to reach 500+ total.

**Functions**:
- `validate_event(event: dict) -> tuple[bool, str]`: Check if event meets quality criteria
- `generate_new_events(category: str, count: int) -> list`: Create new events following patterns
- `curate_event_collection(all_events: dict) -> dict`: Filter and augment event collection

**Quality Validation Rules**:
```python
def validate_event(event: dict) -> tuple[bool, str]:
    """
    Validate event against quality criteria.
    
    Returns:
        (is_valid, reason)
        
    Rejection criteria:
    - Assumes NPCs present: "An NPC you trusted suddenly attacks!"
    - Assumes specific actions: "The magical ward you're examining explodes!"
    - Assumes enemies present: "An enemy breaks away and flees"
    - Overly specific prerequisites without context creation
    - Creates new dungeon features: "You find a secret passage that bypasses..."
    - Modifies fixed dungeon map: "A shortcut leads to..."
    - Creates passages that don't exist: "You discover a hidden tunnel to..."
    
    Acceptance criteria:
    - Works in any context with space parameters
    - Creates own context: "A dying enemy stumbles into the room..."
    - Clear choices and consequences
    - Rewards clever play
    - Works within the existing, fixed dungeon map
    """
    pass
```

**Event Generation Patterns**:

The system will generate new events following these proven patterns:

1. **Opportunity Events** (Target: 125 events)
   - Eavesdropping and intelligence gathering
   - Resource caches (healing, supplies, weapons)
   - Friendly NPCs with information
   - Environmental advantages for combat prep
   - Magical discoveries
   - Tactical positioning opportunities
   - Creature behavior observation
   - **EXCLUDE**: Secret passages, shortcuts, or any events that modify the fixed dungeon map

2. **Complication Events** (Target: 125 events)
   - Locked doors and barriers (that exist on the map)
   - Unstable structures
   - Magical wards and traps
   - Language barriers
   - Environmental hazards (poison, water, darkness)
   - Puzzle locks
   - Territorial creatures (non-hostile initially)
   - **EXCLUDE**: Events that create new passages or modify dungeon layout

3. **Dilemma Events** (Target: 125 events)
   - Speed vs stealth trade-offs
   - Resource vs time decisions
   - Moral choices with tactical implications
   - Risk vs reward scenarios
   - Party splitting decisions
   - Negotiation vs combat options
   - **EXCLUDE**: Events that assume unknown dungeon features

4. **Active Threat Events** (Target: 125 events)
   - Patrols approaching
   - Environmental collapses (within existing structures)
   - Alarms and alerts
   - Ambushes
   - Spreading hazards (fire, gas, water)
   - Reinforcements arriving
   - Immediate danger requiring quick decisions
   - **EXCLUDE**: Events that create new dungeon features

### 3. JSON Event Loader Module

**Purpose**: Load and validate events from JSON files at runtime.

**Functions**:
- `load_events_from_json(filepath: str) -> dict`: Load and parse JSON file
- `validate_event_structure(event: dict) -> bool`: Verify required fields present
- `organize_events_by_category(events: dict) -> dict`: Separate into category lists

**Interface**:
```python
def load_events_from_json(filepath: str) -> dict:
    """
    Load event templates from JSON file.
    
    Args:
        filepath: Path to dungeon_turn_events.json
        
    Returns:
        Dictionary with category keys mapping to event lists
        
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        JSONDecodeError: If JSON is malformed
        ValidationError: If events missing required fields
    """
    pass

def validate_event_structure(event: dict) -> bool:
    """
    Validate event has required fields.
    
    Required fields (all events):
    - title: str
    - description: str
    - spotlight: list[str]
    - skills: list[str]
    - time_cost: str
    - gm_notes: str
    
    Category-specific required fields:
    OPPORTUNITY/COMPLICATION:
    - challenge: str
    - success: str
    - failure: str
    
    DILEMMA:
    - choice_a: str
    - choice_b: str
    - consequence: str
    
    ACTIVE_THREAT:
    - immediate_action: str
    - success: str
    - failure: str
    - threat_level: str
    
    Optional fields (all):
    - required_spaces: list[str]
    - requires_recent_combat: bool
    - requires_new_area: bool
    - reward: str
    - consequence: str
    """
    pass
```

### 4. Generator Script Modifications

**Changes Required**:

1. **Remove hardcoded templates**: Delete OPPORTUNITY_TEMPLATES, COMPLICATION_TEMPLATES, DILEMMA_TEMPLATES, ACTIVE_THREAT_TEMPLATES lists

2. **Add JSON loading at startup** (reads ONLY from curated file):
```python
# At module level, after imports
# NOTE: Only reads from curated file, not backup
EVENTS_FILE = 'etc/dungeon_turn_events.json'  # Curated events only
LOADED_EVENTS = load_events_from_json(EVENTS_FILE)

OPPORTUNITY_TEMPLATES = LOADED_EVENTS['OPPORTUNITY']
COMPLICATION_TEMPLATES = LOADED_EVENTS['COMPLICATION']
DILEMMA_TEMPLATES = LOADED_EVENTS['DILEMMA']
ACTIVE_THREAT_TEMPLATES = LOADED_EVENTS['ACTIVE_THREAT']
```

3. **Add error handling**:
```python
try:
    LOADED_EVENTS = load_events_from_json(EVENTS_FILE)
except FileNotFoundError:
    print(f"ERROR: Event file not found: {EVENTS_FILE}")
    print("Please ensure dungeon_turn_events.json exists in etc/ directory")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in {EVENTS_FILE}: {e}")
    sys.exit(1)
except ValidationError as e:
    print(f"ERROR: Invalid event structure: {e}")
    sys.exit(1)
```

4. **Keep all existing functions unchanged**: The event generation functions (generate_opportunity_event, etc.) will work with the loaded templates without modification.

## Data Models

### Event Template Structure

```json
{
  "OPPORTUNITY": [
    {
      "title": "Secret Passage",
      "description": "You notice unusual wear patterns on the floor leading to a wall section.",
      "challenge": "DC 18 Perception to find hidden door",
      "success": "You discover a secret passage that bypasses the next 3 rooms. Saves 30 minutes of exploration.",
      "failure": "You don't find anything unusual. Continue the normal way.",
      "spotlight": ["Rogue", "Monk"],
      "skills": ["Perception"],
      "time_cost": "1 action to search",
      "gm_notes": "If found, skip next 3 dice jar rolls. Mark on map.",
      "reward": "Shortcut, time saved, avoid encounters",
      "requires_new_area": true,
      "required_spaces": ["hallway", "large_room", "small_room"]
    }
  ],
  "COMPLICATION": [
    {
      "title": "Locked Door",
      "description": "The door you need to pass through is locked. The mechanism is complex but functional.",
      "challenge": "DC 18 Thievery to pick lock OR DC 22 Athletics to force open",
      "success": "Door opens. Quietly if picked, loudly if forced.",
      "failure": "Lock jams (Thievery) or door holds (Athletics). Must find key or try different approach.",
      "spotlight": ["Rogue", "Monk"],
      "skills": ["Thievery", "Athletics"],
      "time_cost": "2 actions (Thievery) or 3 actions (Athletics)",
      "gm_notes": "If forced open, noise may attract attention.",
      "consequence": "Noise attracts attention"
    }
  ],
  "DILEMMA": [
    {
      "title": "Approach: Loud vs Quiet",
      "description": "You can hear activity ahead. You could move quickly and directly (fast but noisy) or take your time being stealthy (slow but hidden).",
      "choice_a": "Move quickly: 10 minutes, but next encounter is alerted to your presence",
      "choice_b": "Move stealthily: 30 minutes (add 2 dice to jar), but next encounter doesn't know you're coming",
      "spotlight": ["All"],
      "skills": ["Stealth", "Tactical thinking"],
      "time_cost": "10 min vs 30 min",
      "gm_notes": "Track choice. Quick approach = enemies get surprise round. Stealthy approach = party gets surprise round.",
      "consequence": "Time vs stealth trade-off",
      "required_spaces": ["hallway", "large_room", "small_room"]
    }
  ],
  "ACTIVE_THREAT": [
    {
      "title": "Patrol Approaching!",
      "description": "You hear heavy footsteps and voices. A patrol is coming this way. You have seconds to act!",
      "immediate_action": "Choose NOW: Hide (DC 17 Stealth), Prepare ambush (ready actions), or Flee (move away quickly)",
      "success": "Hide: They pass by. Ambush: Surprise round. Flee: Avoid encounter.",
      "failure": "Hide: They spot you (they get surprise). Flee: They chase you (running combat).",
      "spotlight": ["Rogue", "All"],
      "skills": ["Stealth", "Tactics"],
      "time_cost": "1 round to react",
      "gm_notes": "Immediate decision. No time to discuss. Tests party coordination.",
      "threat_level": "Moderate - can be avoided"
    }
  ]
}
```

### Field Definitions

**Common Fields** (all events):
- `title` (string): Short name for the event
- `description` (string): What the players encounter
- `spotlight` (array of strings): Which classes shine in this event
- `skills` (array of strings): Skills that can be used
- `time_cost` (string): How long the event takes
- `gm_notes` (string): GM guidance for running the event

**Category-Specific Fields**:

OPPORTUNITY/COMPLICATION:
- `challenge` (string): DC and skill check required
- `success` (string): What happens on success
- `failure` (string): What happens on failure
- `reward` (string, optional): Mechanical benefit for success
- `consequence` (string, optional): Mechanical penalty for failure

DILEMMA:
- `choice_a` (string): First option with outcome
- `choice_b` (string): Second option with outcome
- `choice_c` (string, optional): Third option with outcome
- `consequence` (string): Summary of stakes

ACTIVE_THREAT:
- `immediate_action` (string): What players must do NOW
- `success` (string): Outcome if they succeed
- `failure` (string): Outcome if they fail
- `threat_level` (string): Severity rating
- `urgency` (string, optional): Emphasis on time pressure

**Context Fields** (optional, all categories):
- `required_spaces` (array of strings): Valid location types ["hallway", "large_room", "small_room", "outside", "vertical_space", "water"]
- `requires_recent_combat` (boolean): Event only triggers after combat
- `requires_new_area` (boolean): Event only triggers in unexplored areas

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Extraction Completeness

*For any* extraction run, the total number of events in the backup JSON file should equal the total number of events in the Python source template lists.

**Validates: Requirements 1.1, 2.1, 2.2, 2.5**

### Property 2: Data Preservation Round-Trip

*For any* event in the Python source, extracting it to JSON and loading it back should produce an equivalent event with all fields and nested structures preserved.

**Validates: Requirements 1.2, 1.3, 2.3, 5.1, 5.2, 5.3**

### Property 3: Valid Readable JSON

*For any* generated JSON file, it should parse without errors, use consistent indentation, and properly escape special characters.

**Validates: Requirements 1.4, 2.4, 10.1**

### Property 4: Category Organization

*For any* event in the JSON file, it should appear under exactly one category key that matches its original Python template list name.

**Validates: Requirements 1.5, 5.5, 9.1**

### Property 5: Curated Event Count

*For any* curated event file generation, the resulting file should contain at least 500 events distributed proportionally across all categories.

**Validates: Requirements 3.1, 3.11**

### Property 6: Invalid Event Exclusion

*For any* event that assumes NPCs, specific actions, present enemies, or overly specific prerequisites without creating context, it should not appear in the curated events file.

**Validates: Requirements 3.2, 3.3, 3.4, 3.5**

### Property 7: Valid Event Inclusion

*For any* event that works in any context, creates its own context, has clear choices and consequences, or rewards clever play, it should appear in the curated events file.

**Validates: Requirements 3.6, 3.7, 3.8, 3.9**

### Property 8: Generated Event Quality

*For any* newly generated event, it should follow the same structure and pass the same validation criteria as existing validated events.

**Validates: Requirements 3.10, 3.12**

### Property 9: Successful JSON Loading

*For any* valid JSON event file, the generator script should successfully load it and organize events into category-specific lists matching the original Python structure.

**Validates: Requirements 4.1, 4.3, 9.2**

### Property 10: Error Handling

*For any* missing or malformed JSON file, the generator script should raise a clear error message indicating the specific issue and file path.

**Validates: Requirements 4.2, 10.4**

### Property 11: Behavioral Equivalence

*For any* dice sum and floor combination, the refactored system should select events from the same category as the original system.

**Validates: Requirements 4.5, 9.3, 9.4, 9.5**

### Property 12: Event Validation

*For any* loaded event, all required fields for its category should be present, and all choices should have defined outcomes.

**Validates: Requirements 4.6, 6.3, 6.5**

### Property 13: Creature Reference Validity

*For any* event that references creatures, the creatures should be appropriate for the specified Gauntlight level according to gauntlight_keep_levels.md.

**Validates: Requirements 6.1, 7.1, 7.3**

### Property 14: Skill-Class Consistency

*For any* event, the required skills should be appropriate for at least one of the spotlight classes.

**Validates: Requirements 6.4**

### Property 15: Reward Balance

*For any* event offering rewards, the rewards should include dice removal or time benefits, and should not allow reducing the dice jar below the 5-dice trigger threshold.

**Validates: Requirements 6.2, 8.1, 8.2, 8.3, 8.4, 8.5**

### Property 16: Context Parameter Support

*For any* event with context parameters (required_spaces, requires_recent_combat, requires_new_area), these parameters should be preserved during extraction and loading.

**Validates: Requirements 5.4**

### Property 17: Fresh Loading

*For any* execution of the generator script, events should be loaded fresh from the JSON file without caching from previous runs.

**Validates: Requirements 10.3**

## Error Handling

### Error Scenarios

1. **Missing JSON File**
   - Error: `FileNotFoundError`
   - Message: "ERROR: Event file not found: {filepath}. Please ensure dungeon_turn_events.json exists in etc/ directory"
   - Recovery: Exit with code 1

2. **Malformed JSON**
   - Error: `JSONDecodeError`
   - Message: "ERROR: Invalid JSON in {filepath}: {error_details}"
   - Recovery: Exit with code 1

3. **Missing Required Fields**
   - Error: `ValidationError`
   - Message: "ERROR: Event '{title}' missing required field '{field_name}' for category {category}"
   - Recovery: Exit with code 1

4. **Invalid Category**
   - Error: `ValidationError`
   - Message: "ERROR: Unknown event category '{category}'. Valid categories: OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT"
   - Recovery: Exit with code 1

5. **Empty Event List**
   - Error: `ValidationError`
   - Message: "ERROR: No events found in category '{category}'"
   - Recovery: Exit with code 1

### Error Handling Strategy

- **Fail Fast**: Validate all events at load time, not during generation
- **Clear Messages**: Include file paths, line numbers (if possible), and specific issues
- **No Fallbacks**: Don't fall back to hardcoded events - force fixing the JSON
- **Validation Logging**: Log validation results during curation phase

## Testing Strategy

### Dual Testing Approach

This system requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific example events that demonstrate correct behavior
- Edge cases like empty event lists, missing optional fields
- Error conditions with malformed JSON
- Integration between extraction, curation, and loading modules

**Property-Based Tests** focus on:
- Universal properties that hold for all events
- Round-trip consistency (extract → JSON → load → equivalent)
- Validation rules applied consistently
- Category distribution and organization

### Property-Based Testing Configuration

- **Library**: Use `hypothesis` for Python property-based testing
- **Iterations**: Minimum 100 iterations per property test
- **Test Tags**: Each property test must reference its design document property
- **Tag Format**: `# Feature: dungeon-turn-event-refactor, Property {number}: {property_text}`

### Test Coverage Requirements

1. **Extraction Module**
   - Unit: Test extraction of specific event examples
   - Property: Test that all events are extracted (count preservation)
   - Property: Test that field values are preserved (round-trip)

2. **Curation Module**
   - Unit: Test specific invalid events are excluded
   - Unit: Test specific valid events are included
   - Property: Test that all invalid patterns are excluded
   - Property: Test that generated events meet quality criteria
   - Property: Test that 500+ events are generated

3. **Loading Module**
   - Unit: Test loading specific JSON structures
   - Unit: Test error handling for missing/malformed files
   - Property: Test that all valid JSON files load successfully
   - Property: Test that loaded events match JSON structure

4. **Integration**
   - Unit: Test end-to-end flow with sample events
   - Property: Test behavioral equivalence with original system
   - Property: Test that event selection matches dice sum ranges

### Example Property Test

```python
from hypothesis import given, strategies as st
import json

@given(st.lists(st.dictionaries(
    keys=st.sampled_from(['title', 'description', 'spotlight', 'skills']),
    values=st.text()
), min_size=1))
def test_extraction_preserves_count(events):
    """
    Feature: dungeon-turn-event-refactor, Property 1: Extraction Completeness
    
    For any list of events, extracting to JSON and counting should preserve
    the original count.
    """
    # Extract to JSON
    json_data = extract_to_json(events)
    
    # Parse back
    loaded = json.loads(json_data)
    
    # Count should match
    assert len(loaded) == len(events)
```

## Implementation Notes

### Phase 1: Extraction (Non-Destructive)

1. Create extraction script that reads Python source
2. Generate backup JSON file
3. Validate backup completeness
4. **Do not modify Python file yet**

### Phase 2: Curation

1. Load backup JSON
2. Apply filtering rules
3. Generate new events to reach 500+
4. Validate all events
5. Write curated JSON file

### Phase 3: Refactoring

1. Add JSON loading code to generator
2. Test with curated JSON
3. Verify behavioral equivalence
4. Remove hardcoded templates
5. Update documentation

### Event Generation Guidelines

When generating new events to reach 500+, follow these patterns:

**Good Event Patterns**:
- "You find..." (creates context)
- "A creature appears..." (creates context)
- "The environment..." (uses existing context)
- "You hear/see/smell..." (sensory discovery)

**Bad Event Patterns**:
- "The NPC you're with..." (assumes NPC)
- "The enemy you're fighting..." (assumes combat)
- "The spell you're casting..." (assumes action)
- "Your ally..." (assumes specific party composition)
- "You find a secret passage that bypasses..." (creates new dungeon features)
- "A shortcut leads to..." (modifies fixed dungeon map)
- "You discover a hidden tunnel to..." (creates passages that don't exist)

**Event Variety**:
- Mix of skill checks (don't over-rely on Perception/Stealth)
- Different spotlight classes (ensure all classes get moments)
- Various time costs (1 action to 30 minutes)
- Different reward types (dice removal, time savings, tactical advantages)
- Multiple difficulty levels (DC 15-22 range)

### JSON File Organization

```
etc/
├── dungeon_turn_events_backup.json    # Complete backup (all events) - NOT READ BY GENERATOR
├── dungeon_turn_events.json           # Curated events (500+) - USED BY GENERATOR
└── dungeon_turn_events_schema.md      # Documentation of event structure
```

**Important**: The generator script reads ONLY from `dungeon_turn_events.json` (the curated file). The backup file `dungeon_turn_events_backup.json` exists solely as a historical record and is never loaded by the generator.

### Backward Compatibility

The refactored system maintains 100% backward compatibility:
- Event selection logic unchanged
- Event structure unchanged
- Dice sum ranges unchanged
- Category distribution unchanged
- Only the data source changes (Python → JSON)

This ensures existing game sessions can continue without disruption.
