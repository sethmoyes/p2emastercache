# Requirements Document: Event Filter Builder

## Introduction

This feature replaces the simple "Situation Context" section in the GM web interface with a comprehensive event filter builder. The current system provides only 4 basic context controls (space type, party status, recent combat, new area). The new system will allow the GM to filter dungeon turn events by ANY field in the event JSON structure, providing fine-grained control over which events can be generated.

The filter builder uses a "Lego-style" approach where the GM can combine multiple filter criteria to narrow down the event pool. The system will display how many events match the current filters and allow the GM to generate a random event from the filtered set.

## Glossary

- **Event**: A dungeon turn occurrence stored in etc/dungeon_turn_events.json with fields like title, description, skills, time_cost, etc.
- **Event_Category**: One of four types: OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT
- **Filter_Builder**: The UI component that allows GMs to select multiple filter criteria
- **Filter_Criteria**: A specific constraint on event selection (e.g., "skills includes Stealth")
- **Skill**: A Pathfinder 2e skill that an event tests (Perception, Stealth, Thievery, Athletics, Acrobatics, Arcana, Nature, Medicine, Diplomacy, Intimidation, Deception, Society, Religion, Crafting, Survival)
- **Time_Cost**: How long an event takes to resolve (Quick: 1-3 actions, Short: 5-10 min, Long: 20-30 min)
- **Matching_Event**: An event that satisfies all selected filter criteria
- **GM**: Game Master, the user of this interface

## Requirements

### Requirement 1: Multi-Select Event Category Filter

**User Story:** As a GM, I want to filter events by category, so that I can generate specific types of events (opportunities, complications, dilemmas, or threats).

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a multi-select control for Event_Category
2. WHEN the GM selects one or more categories, THE System SHALL include only events matching those categories in the filtered set
3. THE System SHALL support selecting OPPORTUNITY, COMPLICATION, DILEMMA, and ACTIVE_THREAT categories
4. WHEN no categories are selected, THE System SHALL include events from all categories

### Requirement 2: Multi-Select Skill Filter

**User Story:** As a GM, I want to filter events by required skills, so that I can generate events that test specific abilities.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a multi-select control for Skill
2. WHEN the GM selects one or more skills, THE System SHALL include only events where the skills array contains at least one selected skill
3. THE System SHALL support selecting Perception, Stealth, Thievery, Athletics, Acrobatics, Arcana, Nature, Medicine, Diplomacy, Intimidation, Deception, Society, Religion, Crafting, and Survival
4. WHEN no skills are selected, THE System SHALL include events with any skill

### Requirement 3: Multi-Select Time Cost Filter

**User Story:** As a GM, I want to filter events by time cost, so that I can control how much time events consume.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a multi-select control for Time_Cost with three options: Quick, Short, and Long
2. WHEN the GM selects Quick, THE System SHALL include events with time_cost containing "1 action", "2 actions", or "3 actions"
3. WHEN the GM selects Short, THE System SHALL include events with time_cost containing "5 min" or "10 min"
4. WHEN the GM selects Long, THE System SHALL include events with time_cost containing "20 min" or "30 min"
5. WHEN no time costs are selected, THE System SHALL include events with any time cost

### Requirement 3: Multi-Select Time Cost Filter

**User Story:** As a GM, I want to filter events by new area status, so that I can generate events appropriate for exploration or familiar territory.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a single-select control for new area with three options: Yes, No, Either
2. WHEN the GM selects Yes, THE System SHALL include only events that require a new or unfamiliar area
3. WHEN the GM selects No, THE System SHALL include only events that do not require a new area
4. WHEN the GM selects Either, THE System SHALL include events regardless of new area requirements
5. THE System SHALL default to Either

### Requirement 4: Text Search Filter for Reward Type

**User Story:** As a GM, I want to search for events by reward type, so that I can generate opportunities with specific rewards.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a text input field for reward type search
2. WHEN the GM enters text in the reward field, THE System SHALL include only OPPORTUNITY events where the reward field contains the entered text (case-insensitive)
3. WHEN the reward field is empty, THE System SHALL not filter by reward type
4. THE System SHALL perform partial matching on the reward field

### Requirement 5: Multi-Select Threat Level Filter

**User Story:** As a GM, I want to filter events by threat level, so that I can control the danger level of active threats.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a multi-select control for threat level
2. WHEN the GM selects one or more threat levels, THE System SHALL include only ACTIVE_THREAT events where the threat_level field contains at least one selected level
3. THE System SHALL support selecting Low, Moderate, High, and Extreme threat levels
4. WHEN no threat levels are selected, THE System SHALL include ACTIVE_THREAT events with any threat level

### Requirement 6: Additive Filter Logic

**User Story:** As a GM, I want filters to work together with AND logic, so that I can narrow down events to exactly what I need.

#### Acceptance Criteria

1. WHEN multiple filters are active, THE System SHALL include only events that satisfy ALL filter criteria
2. WHEN a multi-select filter has multiple values selected, THE System SHALL use OR logic within that filter
3. FOR ALL events in the filtered set, each event SHALL match every active filter criterion

### Requirement 7: Matching Event Count Display

**User Story:** As a GM, I want to see how many events match my current filters, so that I know if my filters are too restrictive or too broad.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display the count of Matching_Events
2. WHEN any filter changes, THE System SHALL update the count immediately
3. WHEN the count is zero, THE System SHALL display a warning message
4. THE System SHALL display the count in a prominent location near the Generate Event button

### Requirement 8: Clear All Filters Action

**User Story:** As a GM, I want to clear all filters at once, so that I can quickly reset to the default state.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a "Clear All Filters" button
2. WHEN the GM clicks Clear All Filters, THE System SHALL reset all filters to their default state
3. WHEN filters are cleared, THE System SHALL update the matching event count
4. THE System SHALL reset multi-select filters to empty, single-select filters to "Either", and text fields to empty

### Requirement 9: Generate Event from Filtered Set

**User Story:** As a GM, I want to generate a random event from the filtered set, so that I can get an appropriate event for the current situation.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a "Generate Event" button
2. WHEN the GM clicks Generate Event and matching events exist, THE System SHALL select one Matching_Event at random
3. WHEN the GM clicks Generate Event and no matching events exist, THE System SHALL display an error message
4. THE System SHALL display the generated event in the existing encounter display area
5. WHEN no filters are selected, THE System SHALL use the current random selection logic

### Requirement 10: Event Preview List

**User Story:** As a GM, I want to see a preview of available event titles, so that I can verify my filters are working correctly.

#### Acceptance Criteria

1. THE Filter_Builder SHALL display a list of Matching_Event titles
2. WHEN any filter changes, THE System SHALL update the preview list
3. THE System SHALL display only event titles, not full event details
4. THE System SHALL limit the preview list to 10 events maximum
5. WHEN more than 10 events match, THE System SHALL display "and X more..." at the end of the list

### Requirement 11: Backend Filter Parameter Support

**User Story:** As a developer, I want the backend to accept filter parameters, so that event generation can be filtered server-side.

#### Acceptance Criteria

1. THE Backend SHALL accept filter parameters in the /api/encounter endpoint
2. THE Backend SHALL support filtering by categories, skills, time_cost, new_area, reward, and threat_level
3. THE Backend SHALL return only events matching all provided filter criteria
4. THE Backend SHALL return the count of matching events
5. THE Backend SHALL return a list of matching event titles for preview

### Requirement 12: Backward Compatibility

**User Story:** As a developer, I want to maintain backward compatibility, so that existing functionality continues to work.

#### Acceptance Criteria

1. WHEN no filter parameters are provided, THE System SHALL use the current random selection logic
2. THE System SHALL not break existing API contracts
3. THE System SHALL preserve the current dice jar and floor selection functionality

### Requirement 13: UI Organization and Usability

**User Story:** As a GM, I want the filter builder to replace the current "Situation Context" section, so that I have a more powerful filtering interface in the same location.

#### Acceptance Criteria

1. THE Filter_Builder SHALL replace the existing "Situation Context" section in bin/web/templates/gm.html
2. THE Filter_Builder SHALL use the same visual style and layout as the current "Situation Context" section
3. THE Filter_Builder SHALL organize filters into logical groups
4. THE Filter_Builder SHALL use collapsible sections or tabs to reduce visual clutter
5. THE Filter_Builder SHALL display filter controls in a consistent style
6. THE Filter_Builder SHALL provide clear labels for all filter controls
7. THE Filter_Builder SHALL fit within the existing page layout without requiring excessive scrolling

### Requirement 14: Performance with Large Event Sets

**User Story:** As a GM, I want filtering to be fast, so that I can adjust filters without delays during gameplay.

#### Acceptance Criteria

1. WHEN the GM changes any filter, THE System SHALL update the matching count within 100 milliseconds
2. WHEN the GM changes any filter, THE System SHALL update the preview list within 100 milliseconds
3. THE System SHALL handle filtering of 100+ events without noticeable lag
4. THE System SHALL perform filtering client-side for immediate feedback
