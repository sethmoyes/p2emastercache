# Implementation Plan: Context-Aware Event Generator

## Overview

This implementation plan enhances the existing dungeon turn event generator to accept context parameters. The approach is incremental: create the context data model, add context support to the generator, update templates, then integrate with web and CLI interfaces.

## Tasks

- [x] 1. Create EventContext data model
  - [x] 1.1 Create `event_context.py` module
    - Implement EventContext dataclass with fields: space_type, recent_combat, new_area, party_status
    - Implement validate() method to check parameter values
    - Add default values for all fields
    - Add docstrings explaining each parameter
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 1.2 Write unit tests for EventContext
    - Test validation with valid parameters
    - Test validation with invalid space_type
    - Test validation with invalid party_status
    - Test default values
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Implement template selection system
  - [x] 2.1 Create `template_selector.py` module
    - Implement select_template() function to choose templates based on context
    - Implement is_compatible() function to check template-context compatibility
    - Add logic to filter templates by required_spaces
    - Add logic to filter templates by requires_recent_combat
    - Add logic to filter templates by requires_new_area
    - _Requirements: 9.1, 9.2_
  
  - [x] 2.2 Write unit tests for template selection
    - Test template selection with various contexts
    - Test compatibility checking
    - Test fallback when no compatible templates exist
    - Test random selection from compatible templates
    - _Requirements: 9.1, 9.2_

- [x] 3. Implement context-aware description generation
  - [x] 3.1 Add description modification functions to generator
    - Implement apply_context_to_description() to replace placeholders
    - Implement apply_space_tactics() to add space-specific tactical notes
    - Implement add_status_flavor() to add party status flavor text
    - Implement get_space_description() helper function
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 9.3, 9.4_
  
  - [x] 3.2 Write unit tests for description generation
    - Test placeholder replacement with various contexts
    - Test space-specific tactical notes for each space type
    - Test party status flavor text
    - Test description generation with no context
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 9.3, 9.4_

- [x] 4. Enhance event templates with context metadata
  - [x] 4.1 Add context metadata to DILEMMA templates
    - Add requires_recent_combat flag to combat-related dilemmas
    - Add requires_new_area flag to discovery-related dilemmas
    - Add required_spaces list to space-specific dilemmas
    - Add context placeholders to descriptions ({space}, {combat_context})
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 4.2 Add context metadata to OPPORTUNITY templates
    - Add requires_new_area flag to discovery opportunities
    - Add required_spaces list to space-specific opportunities
    - Add context placeholders to descriptions
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 4.3 Add context metadata to COMPLICATION templates
    - Add required_spaces list to space-specific complications
    - Add context placeholders to descriptions
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 4.4 Add context metadata to ACTIVE_THREAT templates
    - Add required_spaces list to space-specific threats
    - Add context placeholders to descriptions
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 4.5 Add context metadata to COMBAT templates
    - Add required_spaces list to space-specific combat encounters
    - Add context placeholders to tactical descriptions
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 5. Modify core event generation function
  - [x] 5.1 Update generate_event_for_sum() function
    - Add optional context parameter (default: None)
    - Create default EventContext if none provided
    - Call context.validate()
    - Pass context to template selection
    - Pass context to description generation
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.4_
  
  - [x] 5.2 Update generate_from_template() function
    - Accept context parameter
    - Apply context to description
    - Apply space tactics to tactical notes
    - Apply party status flavor
    - _Requirements: 9.3, 9.4_
  
  - [x] 5.3 Write integration tests for event generation
    - Test event generation with various contexts
    - Test event generation without context (backward compatibility)
    - Test that combat-related events only appear with recent_combat=true
    - Test that discovery events only appear with new_area=true
    - Test space-specific tactical notes
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 8.1, 8.2, 8.3, 8.4_

- [x] 6. Update web interface backend
  - [x] 6.1 Modify /api/encounter endpoint in dungeon_turn_app.py
    - Extract context parameters from request JSON
    - Create EventContext from parameters
    - Pass context to generate_event_for_sum()
    - Handle validation errors gracefully
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 6.2 Write API tests for context parameters
    - Test API with all context parameters
    - Test API with missing context parameters (defaults)
    - Test API with invalid context parameters
    - Test API response format unchanged
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 7. Update web interface frontend
  - [x] 7.1 Add context controls to index.html
    - Add space_type dropdown with all options
    - Add recent_combat checkbox
    - Add new_area checkbox (default checked)
    - Add party_status dropdown
    - Add section heading "Situation Context"
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 7.2 Update JavaScript to handle context
    - Read context values from form inputs
    - Include context in API request
    - Store context in sessionStorage for persistence
    - Restore context values on page load
    - _Requirements: 6.2, 6.4, 6.5_
  
  - [x] 7.3 Style context controls in style.css
    - Style context controls section
    - Make controls visually distinct but not intrusive
    - Ensure mobile-friendly layout
    - Add tooltips/help text for parameters
    - _Requirements: 6.1, 6.3_

- [x] 8. Update CLI interface
  - [x] 8.1 Add context arguments to CLI
    - Add --space-type argument with choices
    - Add --recent-combat flag
    - Add --new-area flag (default true)
    - Add --party-status argument with choices
    - Update help text to explain context parameters
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 8.2 Pass context to generator in CLI
    - Create EventContext from CLI arguments
    - Pass context to generate_all_encounters()
    - Handle validation errors with clear messages
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 8.3 Write CLI tests
    - Test CLI with context arguments
    - Test CLI without context arguments (defaults)
    - Test CLI with invalid arguments
    - Test help text display
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9. Create documentation
  - [x] 9.1 Create CONTEXT_PARAMETERS.md
    - Document each context parameter and its effects
    - Provide examples of context usage
    - Include before/after examples showing context impact
    - Explain when to use each space type
    - Add quick reference guide
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 9.2 Update README with context information
    - Add section on context-aware generation
    - Link to CONTEXT_PARAMETERS.md
    - Add quick examples
    - _Requirements: 10.1, 10.2_
  
  - [x] 9.3 Add inline help to web interface
    - Add tooltips to context controls
    - Add "?" icons with explanations
    - Add examples in UI
    - _Requirements: 10.1, 10.2, 10.3_

- [x] 10. Testing and validation
  - [x] 10.1 Run all unit tests
    - Verify EventContext tests pass
    - Verify template selection tests pass
    - Verify description generation tests pass
    - _Requirements: All_
  
  - [x] 10.2 Run all integration tests
    - Verify event generation tests pass
    - Verify API tests pass
    - Verify CLI tests pass
    - _Requirements: All_
  
  - [x] 10.3 Manual testing
    - Test web interface with various context combinations
    - Test CLI with various context arguments
    - Verify descriptions feel natural
    - Verify tactical notes match space type
    - Verify combat events only appear with recent_combat=true
    - Verify discovery events only appear with new_area=true
    - _Requirements: All_
  
  - [x] 10.4 Backward compatibility testing
    - Test existing code without context parameters
    - Verify output format unchanged
    - Verify default behavior matches original
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

## Notes

- All changes are backward-compatible - existing code works without modification
- Context parameter is optional with sensible defaults
- Template enhancement can be done incrementally (start with DILEMMA, then others)
- Web interface changes are purely additive (no breaking changes)
- CLI changes are purely additive (no breaking changes)
- Focus on making descriptions feel natural and situationally appropriate
- Test thoroughly to ensure context filtering works correctly
