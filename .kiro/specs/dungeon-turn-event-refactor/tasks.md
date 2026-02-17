# Implementation Plan: Dungeon Turn Event Refactor

## Overview

This plan refactors the dungeon turn event generation system to externalize event templates from Python code into JSON configuration files. The implementation follows three phases: extraction, curation, and integration.

## Tasks

- [x] 1. Create event extraction module
  - Create `bin/extract_events.py` script to parse Python source and extract event templates
  - Implement AST parsing to locate OPPORTUNITY_TEMPLATES, COMPLICATION_TEMPLATES, DILEMMA_TEMPLATES, and ACTIVE_THREAT_TEMPLATES
  - Convert Python dictionaries to JSON-serializable format
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 1.1 Write property test for extraction completeness
  - **Property 1: Extraction Completeness**
  - **Validates: Requirements 1.1, 2.1, 2.2, 2.5**

- [ ] 2. Generate backup JSON file
  - [x] 2.1 Implement JSON serialization with proper escaping and formatting
    - Handle special characters, quotes, and nested structures
    - Use 2-space indentation for readability
    - _Requirements: 1.4, 2.4_
  
  - [x] 2.2 Create `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events_backup.json`
    - Extract all events from Python source
    - Organize by category (OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT)
    - Validate count matches source
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  
  - [x] 2.3 Write property test for data preservation round-trip
    - **Property 2: Data Preservation Round-Trip**
    - **Validates: Requirements 1.2, 1.3, 2.3, 5.1, 5.2, 5.3**

- [x] 3. Checkpoint - Verify backup file
  - Ensure backup file exists and contains all original events
  - Manually review a sample of events for correctness
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Create event curation module
  - [x] 4.1 Implement event validation function
    - Check for invalid patterns (assumes NPCs, enemies, actions, dungeon modifications)
    - Check for valid patterns (self-contained, creates context, clear choices)
    - Return validation result with reason
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_
  
  - [x] 4.2 Write property test for invalid event exclusion
    - **Property 6: Invalid Event Exclusion**
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
  
  - [x] 4.3 Write property test for valid event inclusion
    - **Property 7: Valid Event Inclusion**
    - **Validates: Requirements 3.6, 3.7, 3.8, 3.9**

- [ ] 5. Generate new events to reach 500+ total
  - [x] 5.1 Create event generation templates for each category
    - Opportunity events: eavesdropping, resource caches, tactical advantages
    - Complication events: locked doors, hazards, territorial creatures
    - Dilemma events: trade-offs, moral choices, risk/reward
    - Active threat events: patrols, collapses, alarms, ambushes
    - _Requirements: 3.10, 3.11_
  
  - [x] 5.2 Generate 125 opportunity events
    - Follow proven patterns from existing events
    - Ensure variety in skills, spotlight classes, and rewards
    - Exclude any events that create dungeon features
    - _Requirements: 3.10, 3.12_
  
  - [x] 5.3 Generate 125 complication events
    - Focus on environmental challenges and skill checks
    - Ensure clear success/failure outcomes
    - Work within existing dungeon structure
    - _Requirements: 3.10, 3.12_
  
  - [x] 5.4 Generate 125 dilemma events
    - Create meaningful choices with trade-offs
    - Ensure all choices have clear consequences
    - Balance tactical and moral decisions
    - _Requirements: 3.10, 3.12_
  
  - [x] 5.5 Generate 125 active threat events
    - Focus on immediate danger and quick decisions
    - Vary threat levels and urgency
    - Ensure threats work in any dungeon context
    - _Requirements: 3.10, 3.12_
  
  - [x] 5.6 Write property test for generated event quality
    - **Property 8: Generated Event Quality**
    - **Validates: Requirements 3.10, 3.12**

- [ ] 6. Create curated events file
  - [x] 6.1 Filter backup events through validation
    - Load backup JSON
    - Apply validation rules to each event
    - Collect valid events
    - _Requirements: 3.1, 3.2-3.9_
  
  - [x] 6.2 Combine filtered and generated events
    - Merge valid existing events with newly generated events
    - Organize by category
    - Ensure proportional distribution
    - _Requirements: 3.11_
  
  - [x] 6.3 Write `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events.json`
    - Format with 2-space indentation
    - Validate JSON structure
    - Verify count >= 500
    - _Requirements: 3.1_
  
  - [x] 6.4 Write property test for curated event count
    - **Property 5: Curated Event Count**
    - **Validates: Requirements 3.1, 3.11**

- [x] 7. Checkpoint - Verify curated file
  - Ensure curated file has 500+ events
  - Manually review sample events from each category
  - Verify no invalid patterns present
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Create JSON loading module
  - [x] 8.1 Implement load_events_from_json function
    - Load and parse JSON file
    - Handle FileNotFoundError with clear message
    - Handle JSONDecodeError with clear message
    - Return organized event dictionary
    - _Requirements: 4.1, 4.2_
  
  - [x] 8.2 Implement validate_event_structure function
    - Check required fields for each category
    - Validate data types (strings, lists, booleans)
    - Check optional fields are properly optional
    - Return validation result
    - _Requirements: 4.6, 5.1, 5.2, 5.3_
  
  - [x] 8.3 Implement organize_events_by_category function
    - Separate events into category-specific lists
    - Validate category keys match expected names
    - Return dictionary with OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT keys
    - _Requirements: 1.5, 5.5, 9.1, 9.2_
  
  - [x] 8.4 Write property test for successful JSON loading
    - **Property 9: Successful JSON Loading**
    - **Validates: Requirements 4.1, 4.3, 9.2**
  
  - [x] 8.5 Write unit tests for error handling
    - Test missing file error
    - Test malformed JSON error
    - Test missing required fields error
    - Test invalid category error
    - _Requirements: 4.2, 10.4_

- [ ] 9. Integrate JSON loading into generator script
  - [x] 9.1 Add JSON loading at module level
    - Import load_events_from_json function
    - Load events from `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events.json`
    - Assign to OPPORTUNITY_TEMPLATES, COMPLICATION_TEMPLATES, DILEMMA_TEMPLATES, ACTIVE_THREAT_TEMPLATES
    - Add error handling with clear messages
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 9.2 Remove hardcoded event template lists
    - Delete OPPORTUNITY_TEMPLATES list definition
    - Delete COMPLICATION_TEMPLATES list definition
    - Delete DILEMMA_TEMPLATES list definition
    - Delete ACTIVE_THREAT_TEMPLATES list definition
    - _Requirements: 4.4_
  
  - [x] 9.3 Verify existing event generation functions work unchanged
    - Test generate_opportunity_event with loaded templates
    - Test generate_complication_event with loaded templates
    - Test generate_dilemma_event with loaded templates
    - Test generate_active_threat_event with loaded templates
    - _Requirements: 4.5_

- [ ] 10. Validate behavioral equivalence
  - [x] 10.1 Write property test for behavioral equivalence
    - **Property 11: Behavioral Equivalence**
    - **Validates: Requirements 4.5, 9.3, 9.4, 9.5**
  
  - [x] 10.2 Write property test for event validation
    - **Property 12: Event Validation**
    - **Validates: Requirements 4.6, 6.3, 6.5**
  
  - [x] 10.3 Run integration tests
    - Generate events for all dice sums (5-100)
    - Generate events for all floors (1-10)
    - Verify category distribution matches expected ranges
    - Compare outputs with original system
    - _Requirements: 4.5, 9.3, 9.4, 9.5_

- [ ] 11. Create event structure documentation
  - [x] 11.1 Write `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events_schema.md`
    - Document required fields for each category
    - Document optional fields and their meanings
    - Provide examples of valid events
    - Explain context parameters
    - Include guidelines for adding new events
    - _Requirements: 10.2_

- [ ] 12. Final validation and testing
  - [x] 12.1 Write property test for creature reference validity
    - **Property 13: Creature Reference Validity**
    - **Validates: Requirements 6.1, 7.1, 7.3**
  
  - [x] 12.2 Write property test for skill-class consistency
    - **Property 14: Skill-Class Consistency**
    - **Validates: Requirements 6.4**
  
  - [x] 12.3 Write property test for reward balance
    - **Property 15: Reward Balance**
    - **Validates: Requirements 6.2, 8.1, 8.2, 8.3, 8.4, 8.5**
  
  - [x] 12.4 Write property test for context parameter support
    - **Property 16: Context Parameter Support**
    - **Validates: Requirements 5.4**
  
  - [x] 12.5 Write property test for fresh loading
    - **Property 17: Fresh Loading**
    - **Validates: Requirements 10.3**
  
  - [x] 12.6 Run full test suite
    - Execute all unit tests
    - Execute all property tests (100+ iterations each)
    - Verify all tests pass
    - _Requirements: All_

- [x] 13. Final checkpoint - Complete refactoring
  - Verify generator script loads from JSON successfully
  - Verify no hardcoded templates remain in Python
  - Verify backup file exists and is complete
  - Verify curated file has 500+ events
  - Verify all tests pass
  - Generate sample dungeon turn encounters to validate functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Clean up temporary scripts
  - [x] 14.1 Remove extraction script
    - Delete `bin/extract_events.py` (no longer needed after extraction)
    - _Requirements: 10.5_
  
  - [x] 14.2 Remove curation script if created as standalone
    - Delete any temporary curation scripts used during event generation
    - Keep only the final JSON files
    - _Requirements: 10.5_
  
  - [x] 14.3 Remove test scripts if temporary
    - Archive or remove any one-off test scripts created during development
    - Keep only permanent test files in test directory
    - _Requirements: 10.5_
  
  - [x] 14.4 Verify final file structure
    - Confirm only production files remain: `etc/dungeon_turn_events.json`, `etc/dungeon_turn_events_backup.json`, `etc/dungeon_turn_events_schema.md`
    - Confirm generator script is updated and working
    - Document any scripts that should be kept for future maintenance
    - _Requirements: 10.5_

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The refactoring maintains 100% backward compatibility with existing event selection logic
