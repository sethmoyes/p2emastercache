# Requirements Document: Context-Aware Event Generator

## Introduction

The Context-Aware Event Generator enhances the existing dungeon turn event generator to accept situational context parameters before generating events. This prevents immersion-breaking assumptions (like "You wounded an enemy and they're fleeing" when no combat occurred) by tailoring event descriptions to the actual game state.

Instead of generating generic events and fixing them afterward, the generator will use context parameters to create appropriate events from the start.

## Glossary

- **Context_Parameters**: Input values describing the current game state (space type, recent combat, area familiarity, etc.)
- **Space_Type**: The physical environment where the event occurs (hallway, large room, outside, vertical space, etc.)
- **Recent_Combat**: Boolean indicating whether the party just finished combat
- **New_Area**: Boolean indicating whether the party is exploring an unfamiliar area
- **Event_Generator**: The existing generate_dungeon_turn_v2.py system that creates random encounters
- **Context_Aware_Generation**: Event generation that considers situational context to create appropriate descriptions

## Requirements

### Requirement 1: Context Parameter Input

**User Story:** As a GM, I want to provide context about the current situation before rolling for an event, so that generated events fit naturally into the game state.

#### Acceptance Criteria

1. THE Event_Generator SHALL accept a `space_type` parameter with values: "hallway", "large_room", "small_room", "outside", "vertical_space", "water", "unknown"
2. THE Event_Generator SHALL accept a `recent_combat` boolean parameter (default: false)
3. THE Event_Generator SHALL accept a `new_area` boolean parameter (default: true)
4. THE Event_Generator SHALL accept a `party_status` parameter with values: "healthy", "injured", "low_resources" (default: "healthy")
5. WHEN no context parameters are provided, THE Event_Generator SHALL use sensible defaults

### Requirement 2: Space-Aware Event Generation

**User Story:** As a GM, I want events to match the physical space we're in, so that encounters feel believable and tactical.

#### Acceptance Criteria

1. WHEN `space_type` is "hallway", THE Event_Generator SHALL generate events emphasizing linear movement, chokepoints, and limited flanking
2. WHEN `space_type` is "large_room", THE Event_Generator SHALL generate events emphasizing open tactics, flanking, and cover
3. WHEN `space_type` is "vertical_space", THE Event_Generator SHALL generate events emphasizing climbing, height advantages, and falling hazards
4. WHEN `space_type` is "outside", THE Event_Generator SHALL generate events emphasizing weather, visibility, and open terrain
5. WHEN `space_type` is "water", THE Event_Generator SHALL generate events emphasizing swimming, drowning, and aquatic creatures
6. THE Event_Generator SHALL adapt enemy positioning descriptions to match the space type

### Requirement 3: Combat-Aware Event Generation

**User Story:** As a GM, I want events to acknowledge whether we just fought, so that descriptions don't assume combat that never happened.

#### Acceptance Criteria

1. WHEN `recent_combat` is true, THE Event_Generator SHALL generate events that can reference ongoing skirmishes or fleeing enemies
2. WHEN `recent_combat` is false, THE Event_Generator SHALL generate events that do not assume prior combat
3. WHEN `recent_combat` is true AND category is DILEMMA, THE Event_Generator SHALL prefer dilemmas related to combat aftermath (chase fleeing enemies, spare wounded foes, etc.)
4. WHEN `recent_combat` is false AND category is DILEMMA, THE Event_Generator SHALL prefer dilemmas unrelated to combat
5. THE Event_Generator SHALL never use phrases like "You wounded" or "You defeated" when `recent_combat` is false

### Requirement 4: Area Familiarity Awareness

**User Story:** As a GM, I want events to reflect whether the party knows this area, so that discovery events make sense.

#### Acceptance Criteria

1. WHEN `new_area` is true, THE Event_Generator SHALL favor OPPORTUNITY events involving discovery and exploration
2. WHEN `new_area` is false, THE Event_Generator SHALL reduce discovery-based OPPORTUNITY events
3. WHEN `new_area` is true, THE Event_Generator SHALL include more environmental clues and hints
4. WHEN `new_area` is false, THE Event_Generator SHALL assume the party has basic knowledge of the area layout

### Requirement 5: Party Status Awareness

**User Story:** As a GM, I want events to consider the party's condition, so that challenges feel appropriate to our current state.

#### Acceptance Criteria

1. WHEN `party_status` is "injured", THE Event_Generator SHALL include more references to wounds, exhaustion, and vulnerability
2. WHEN `party_status` is "low_resources", THE Event_Generator SHALL include more references to depleted supplies and limited options
3. WHEN `party_status` is "healthy", THE Event_Generator SHALL use neutral descriptions without status references
4. THE Event_Generator SHALL not alter mechanical difficulty based on party status (only narrative descriptions)

### Requirement 6: Web Interface Integration

**User Story:** As a GM, I want to set context parameters in the web interface before rolling, so that I can quickly generate appropriate events during play.

#### Acceptance Criteria

1. THE Web_Interface SHALL display context parameter inputs on the main page
2. THE Web_Interface SHALL remember context parameter selections between rolls (session persistence)
3. THE Web_Interface SHALL provide sensible defaults for all context parameters
4. THE Web_Interface SHALL send context parameters to the backend when generating events
5. THE Web_Interface SHALL allow quick toggling of boolean parameters (recent_combat, new_area)

### Requirement 7: CLI Interface Support

**User Story:** As a developer, I want to provide context parameters via command-line arguments, so that I can script event generation with specific contexts.

#### Acceptance Criteria

1. THE CLI SHALL accept `--space-type` argument with valid space type values
2. THE CLI SHALL accept `--recent-combat` flag (boolean)
3. THE CLI SHALL accept `--new-area` flag (boolean, default true)
4. THE CLI SHALL accept `--party-status` argument with valid status values
5. THE CLI SHALL display help text explaining all context parameters

### Requirement 8: Backward Compatibility

**User Story:** As a developer, I want the enhanced generator to work without context parameters, so that existing code doesn't break.

#### Acceptance Criteria

1. WHEN called without context parameters, THE Event_Generator SHALL function exactly as before
2. THE Event_Generator SHALL use sensible defaults for missing context parameters
3. THE Event_Generator SHALL not require code changes in existing integrations
4. THE Event_Generator SHALL maintain the same output format as before

### Requirement 9: Context-Appropriate Event Templates

**User Story:** As a GM, I want event descriptions to naturally incorporate context, so that events feel tailored to the situation.

#### Acceptance Criteria

1. THE Event_Generator SHALL have multiple description templates for each event type
2. THE Event_Generator SHALL select templates based on context parameters
3. THE Event_Generator SHALL adapt tactical descriptions to match space type
4. THE Event_Generator SHALL adapt narrative descriptions to match recent combat and party status
5. THE Event_Generator SHALL maintain mechanical consistency (DCs, rewards, enemies) across template variations

### Requirement 10: Documentation and Examples

**User Story:** As a GM, I want clear documentation on context parameters, so that I understand how to use them effectively.

#### Acceptance Criteria

1. THE Documentation SHALL explain each context parameter and its effects
2. THE Documentation SHALL provide examples of how context affects event generation
3. THE Documentation SHALL include a quick reference guide for the web interface
4. THE Documentation SHALL explain when to use each space type
5. THE Documentation SHALL include before/after examples showing context impact
