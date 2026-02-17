# Requirements Document

## Introduction

This specification defines the refactoring of the dungeon turn event generation system to externalize event templates from Python code into JSON configuration files. The system currently has all event templates hardcoded in the Python generator script, making them difficult to maintain, curate, and modify. This refactoring will separate data from logic, create a backup of all existing events, and establish a curated set of working events.

## Glossary

- **Event_Template**: A structured data object defining a dungeon turn encounter with description, choices, skills, and outcomes
- **Generator_Script**: The Python file `/Users/smoyes/Documents/p2emastercache/bin/generators/generate_dungeon_turn_v2.py` that creates dungeon turn encounters
- **Event_Category**: Classification of events (OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT, COMBAT)
- **JSON_Event_File**: External JSON file containing event template data structures
- **Backup_File**: Complete archive of all existing event templates at `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events_backup.json`
- **Curated_File**: Filtered collection of working events at `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events.json`
- **Space_Parameter**: Context variable indicating location type (hallway, large_room, small_room, outside)
- **Context_Prerequisite**: Required conditions for an event to trigger (requires_recent_combat, requires_new_area, required_spaces)

## Requirements

### Requirement 1: Extract Event Templates to JSON

**User Story:** As a game master, I want event templates stored in JSON files, so that I can easily view, edit, and manage events without modifying Python code.

#### Acceptance Criteria

1. THE System SHALL extract all event templates from OPPORTUNITY_TEMPLATES, COMPLICATION_TEMPLATES, DILEMMA_TEMPLATES, and ACTIVE_THREAT_TEMPLATES lists
2. THE System SHALL preserve all event fields including title, description, challenge, success, failure, spotlight, skills, time_cost, gm_notes, and optional fields
3. THE System SHALL maintain the original event structure with all nested data intact
4. THE System SHALL create valid JSON with proper escaping of special characters and quotes
5. THE System SHALL organize events by category in the JSON structure

### Requirement 2: Create Backup File

**User Story:** As a developer, I want a complete backup of all existing events, so that I can reference the original data if issues arise during refactoring.

#### Acceptance Criteria

1. THE System SHALL create `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events_backup.json` containing all extracted events
2. THE System SHALL include all events regardless of quality or functionality
3. THE System SHALL preserve exact field values and structure from the Python source
4. THE System SHALL format the JSON with indentation for human readability
5. THE System SHALL validate that the backup file contains the same number of events as the Python source

### Requirement 3: Create Curated Events File

**User Story:** As a game master, I want a curated file containing only working events, so that I can generate high-quality encounters without broken or contextually invalid events.

#### Acceptance Criteria

1. THE System SHALL create `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events.json` containing at least 500 validated events
2. WHEN an event assumes NPCs are present without creating them, THE System SHALL exclude it from the curated file
3. WHEN an event assumes specific actions are being taken without context, THE System SHALL exclude it from the curated file
4. WHEN an event assumes enemies are already present without creating them, THE System SHALL exclude it from the curated file
5. WHEN an event has overly specific prerequisites that may not be met, THE System SHALL exclude it from the curated file
6. WHEN an event works in any context with available space parameters, THE System SHALL include it in the curated file
7. WHEN an event creates its own context, THE System SHALL include it in the curated file
8. WHEN an event has clear choices and consequences, THE System SHALL include it in the curated file
9. WHEN an event rewards clever play with dice removal or time benefits, THE System SHALL include it in the curated file
10. THE System SHALL generate new events following the working event patterns to reach the minimum of 500 curated events
11. THE System SHALL distribute new events across all categories (OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT) proportionally
12. THE System SHALL ensure new events follow the same structure and quality criteria as validated existing events

### Requirement 4: Update Generator Script

**User Story:** As a developer, I want the generator script to load events from JSON files, so that event data is separated from application logic.

#### Acceptance Criteria

1. THE Generator_Script SHALL load event templates from `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events.json` at startup
2. WHEN the JSON file is missing or invalid, THE Generator_Script SHALL raise a clear error message indicating the file path and issue
3. THE Generator_Script SHALL parse JSON event data into the same data structures previously used by hardcoded templates
4. THE Generator_Script SHALL remove the hardcoded OPPORTUNITY_TEMPLATES, COMPLICATION_TEMPLATES, DILEMMA_TEMPLATES, and ACTIVE_THREAT_TEMPLATES lists
5. THE Generator_Script SHALL maintain all existing functionality for event selection and generation
6. THE Generator_Script SHALL validate that loaded events contain required fields before use

### Requirement 5: Maintain Event Structure Compatibility

**User Story:** As a developer, I want the JSON event structure to match the Python structure, so that no code changes are needed beyond loading the data.

#### Acceptance Criteria

1. THE JSON_Event_File SHALL use the same field names as the Python dictionaries
2. THE JSON_Event_File SHALL preserve data types (strings, lists, booleans, integers)
3. THE JSON_Event_File SHALL maintain optional fields as optional in the JSON structure
4. THE JSON_Event_File SHALL support all context parameters (required_spaces, requires_recent_combat, requires_new_area)
5. THE JSON_Event_File SHALL organize events by category with keys matching Python list names

### Requirement 6: Validate Event Quality Criteria

**User Story:** As a game master, I want events that work properly in gameplay, so that I don't encounter broken or nonsensical encounters.

#### Acceptance Criteria

1. WHEN an event references creatures, THE System SHALL verify creatures are appropriate for the Gauntlight level
2. WHEN an event offers rewards, THE System SHALL ensure rewards are balanced (dice removal, time benefits, or tactical advantages)
3. WHEN an event has multiple choices, THE System SHALL verify each choice has clear outcomes
4. WHEN an event requires skills, THE System SHALL ensure skills are appropriate for the spotlight classes
5. THE System SHALL validate that event descriptions are self-contained and don't assume unknown context

### Requirement 7: Support Creature References

**User Story:** As a game master, I want events involving creatures to reference appropriate Gauntlight level creatures, so that encounters are thematically consistent and level-appropriate.

#### Acceptance Criteria

1. WHEN an event involves creatures, THE System SHALL reference the NPCs & Creatures section from `/Users/smoyes/Documents/p2emastercache/etc/gauntlight_keep_levels.md`
2. WHEN generating events for Level 2, THE System SHALL only use undead creatures and morlocks
3. WHEN generating events for any level, THE System SHALL use creatures listed in that level's NPCs & Creatures section
4. THE System SHALL support alternative encounters with rival adventuring parties
5. THE System SHALL allow events to specify creature types generically for GM adaptation

### Requirement 8: Preserve Reward System

**User Story:** As a game master, I want events to frequently offer dice removal or time benefits, so that players are rewarded for clever solutions and creative problem-solving.

#### Acceptance Criteria

1. WHEN a player uses a clever solution, THE System SHALL offer dice removal as a reward option
2. WHEN a player successfully avoids combat through skills, THE System SHALL offer time benefits or dice removal
3. WHEN a player demonstrates creative problem-solving, THE System SHALL provide mechanical rewards
4. THE System SHALL ensure events still trigger at 5 dice regardless of rewards
5. THE System SHALL balance rewards so they don't trivialize the dice jar mechanic

### Requirement 9: Maintain Event Categories

**User Story:** As a developer, I want events organized by category, so that the generator can select appropriate events based on dice roll ranges.

#### Acceptance Criteria

1. THE JSON_Event_File SHALL organize events into OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT, and COMBAT categories
2. THE Generator_Script SHALL load events into separate lists by category
3. THE Generator_Script SHALL select events from the appropriate category based on dice sum ranges
4. THE System SHALL preserve the probability distribution (5-25 OPPORTUNITY, 26-45 COMPLICATION, 46-65 DILEMMA, 66-85 ACTIVE_THREAT, 86-100 COMBAT)
5. THE System SHALL maintain the existing event selection logic without modification

### Requirement 10: Enable Future Event Management

**User Story:** As a game master, I want to easily add, remove, or modify events, so that I can customize the dungeon experience without programming knowledge.

#### Acceptance Criteria

1. THE JSON_Event_File SHALL use human-readable formatting with consistent indentation
2. THE JSON_Event_File SHALL include comments or documentation about event structure (via separate documentation file)
3. THE Generator_Script SHALL reload events from JSON on each execution without caching
4. THE System SHALL validate JSON structure and provide clear error messages for malformed events
5. THE System SHALL allow adding new events by appending to the appropriate category array in JSON
