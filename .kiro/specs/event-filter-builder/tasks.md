# Implementation Plan: Event Filter Builder

## Overview

This implementation replaces the "Situation Context" section in the GM web interface with a comprehensive event filter builder. The approach is to:

1. Create backend filtering logic first (Python)
2. Update the frontend UI to replace the old section (HTML/JavaScript)
3. Implement client-side filtering for immediate feedback
4. Wire everything together with the existing event generation system
5. Add property-based tests to verify filtering correctness

## Tasks

- [ ] 1. Implement backend event filtering logic
  - [x] 1.1 Create filter application function in dungeon_turn_app.py
    - Write `apply_event_filters(events, filters)` function that takes event list and filter parameters
    - Implement category filtering (OR logic within filter)
    - Implement skills filtering (OR logic within filter)
    - Implement time cost pattern matching (quick/short/long)
    - Implement new area filtering (yes/no/either)
    - Implement reward text search (case-insensitive, OPPORTUNITY only)
    - Implement threat level filtering (OR logic within filter, ACTIVE_THREAT only)
    - Ensure AND logic across all filters
    - _Requirements: 1.2, 2.2, 3.2, 3.3, 3.4, 3.2, 3.3, 4.2, 5.2, 6.1, 6.2_
  
  - [ ]* 1.2 Write property test for category filtering
    - **Property 1: Category Filter Correctness**
    - **Validates: Requirements 1.2**
  
  - [ ]* 1.3 Write property test for skill filtering
    - **Property 2: Skill Filter Correctness**
    - **Validates: Requirements 2.2**
  
  - [ ]* 1.4 Write property test for time cost filtering
    - **Property 3: Time Cost Filter Correctness**
    - **Validates: Requirements 3.2, 3.3, 3.4**
  
  - [ ]* 1.5 Write property test for new area filtering
    - **Property 4 & 5: New Area Filter Correctness**
    - **Validates: Requirements 3.2, 3.3**
  
  - [ ]* 1.6 Write property test for reward text search
    - **Property 6: Reward Text Search Correctness**
    - **Validates: Requirements 4.2, 4.4**
  
  - [ ]* 1.7 Write property test for threat level filtering
    - **Property 7: Threat Level Filter Correctness**
    - **Validates: Requirements 5.2**
  
  - [ ]* 1.8 Write property test for AND logic across filters
    - **Property 8: AND Logic Across Filters**
    - **Validates: Requirements 6.1, 6.3**
  
  - [ ]* 1.9 Write property test for OR logic within multi-select filters
    - **Property 9: OR Logic Within Multi-Select Filters**
    - **Validates: Requirements 6.2**

- [x] 2. Create filtered event generation function
  - [x] 2.1 Implement generate_filtered_event function
    - Write `generate_filtered_event(filters, floor, floor_data, party_level, creatures)` function
    - Load and flatten all events from dungeon_turn_events.json
    - Apply filters using apply_event_filters function
    - Handle empty filtered set (return error event)
    - Select random event from filtered set
    - Return selected event
    - _Requirements: 9.2, 9.3, 11.3_
  
  - [ ]* 2.2 Write property test for random selection from filtered set
    - **Property 11: Random Selection from Filtered Set**
    - **Validates: Requirements 9.2**
  
  - [ ]* 2.3 Write unit tests for edge cases
    - Test empty filter set (all events available)
    - Test zero matching events (error event returned)
    - Test missing event fields (handled gracefully)
    - _Requirements: 1.4, 2.4, 3.5, 3.4, 4.3, 5.3, 6.4_

- [x] 3. Update /api/encounter endpoint to support filters
  - [x] 3.1 Modify get_encounter function to accept filter parameters
    - Extract filters from request JSON
    - Check if filters are provided and non-empty
    - If filters provided, call generate_filtered_event
    - If no filters, use existing event generation logic
    - Maintain backward compatibility
    - _Requirements: 11.1, 11.2, 12.1, 12.3_
  
  - [ ]* 3.2 Write unit tests for API endpoint
    - Test endpoint accepts filter parameters
    - Test endpoint returns filtered events
    - Test backward compatibility (no filters provided)
    - Test error handling (invalid floor, missing parameters)
    - _Requirements: 11.1, 11.2, 11.4, 11.5, 12.1, 12.2, 12.3_

- [x] 4. Checkpoint - Ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Create frontend Filter Builder UI
  - [x] 5.1 Replace "Situation Context" section in gm.html
    - Remove existing "Situation Context" HTML section
    - Add new "Event Filters" section with same styling
    - Create multi-select for Event Categories (OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT)
    - Create multi-select for Skills (15 skills)
    - Create multi-select for Time Cost (Quick, Short, Long)
    - Create single-select for New Area (Yes, No, Either)
    - Create text input for Reward Type search
    - Create multi-select for Threat Level (Low, Moderate, High, Extreme)
    - Add matching count display
    - Add "Clear All Filters" button
    - Add event preview list container
    - Add "Generate Filtered Event" button
    - _Requirements: 1.1, 1.3, 2.1, 2.3, 3.1, 3.1, 4.1, 5.1, 7.1, 8.1, 10.1, 13.1, 13.2, 13.5, 13.6, 13.7_
  
  - [ ]* 5.2 Write unit tests for UI rendering
    - Test all filter controls are present
    - Test all options are available in multi-selects
    - Test default values are correct
    - _Requirements: 1.1, 1.3, 2.1, 2.3, 3.1, 3.1, 4.1, 4.5, 5.1, 6.1, 6.3_

- [x] 6. Implement client-side filtering logic
  - [x] 6.1 Create EventFilterManager JavaScript object
    - Create EventFilterManager object with state (allEvents, filteredEvents)
    - Implement init function to load events and attach listeners
    - Implement getFilterValues function to extract current filter values
    - Implement filterEvents function with same logic as backend
    - Implement updateFilters function to apply filters and update UI
    - Implement updateMatchingCount function
    - Implement updatePreviewList function (max 10 events)
    - _Requirements: 1.2, 2.2, 3.2, 3.3, 3.4, 3.2, 3.3, 4.2, 5.2, 6.1, 6.2, 7.1, 7.2, 10.2, 10.4, 10.5_
  
  - [ ]* 6.2 Write property test for frontend-backend filter consistency
    - **Property 13: Backend Filter Consistency**
    - **Validates: Requirements 11.3**
  
  - [ ]* 6.3 Write unit tests for filter manager
    - Test filter values extraction
    - Test filter updates trigger UI updates
    - Test matching count updates
    - Test preview list updates
    - _Requirements: 7.2, 7.3, 10.2_

- [x] 7. Implement filter UI interactions
  - [x] 7.1 Create clearAllFilters function
    - Reset all multi-select filters to empty
    - Reset single-select to "Either"
    - Reset text input to empty
    - Call updateFilters to refresh UI
    - _Requirements: 8.2, 8.3, 8.4_
  
  - [ ]* 7.2 Write property test for clear filters reset
    - **Property 10: Clear Filters Reset**
    - **Validates: Requirements 8.2, 8.4**
  
  - [x] 7.3 Create generateFilteredEvent function
    - Get current filter values
    - Check if filtered events exist (show error if not)
    - Disable button and show loading state
    - Send AJAX request to /api/encounter with filters
    - Display returned event in encounter area
    - Re-enable button
    - Handle errors gracefully
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 7.4 Write unit tests for UI interactions
    - Test clear all filters resets controls
    - Test generate event sends correct API request
    - Test error handling for zero matches
    - Test error handling for network failures
    - _Requirements: 8.2, 8.3, 9.1, 9.2, 9.3_

- [x] 8. Load event data for client-side filtering
  - [x] 8.1 Add event data loading to page initialization
    - Load dungeon_turn_events.json on page load
    - Flatten events from all categories
    - Initialize EventFilterManager with event data
    - Attach event listeners to filter controls
    - _Requirements: 14.1, 14.2, 14.3, 14.4_
  
  - [ ]* 8.2 Write unit tests for initialization
    - Test events load correctly
    - Test EventFilterManager initializes
    - Test event listeners are attached
    - _Requirements: 14.1, 14.2_

- [x] 9. Implement preview list display
  - [x] 9.1 Create preview list update logic
    - Display up to 10 event titles
    - Show "and X more..." if more than 10 events
    - Show "No events match" if zero events
    - Update on every filter change
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 9.2 Write property test for preview list truncation
    - **Property 12: Preview List Truncation**
    - **Validates: Requirements 10.4**
  
  - [ ]* 9.3 Write unit tests for preview list
    - Test displays correct number of titles
    - Test shows "and X more" for large sets
    - Test shows error message for empty sets
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Integration and final wiring
  - [x] 11.1 Wire filter builder to existing event display
    - Ensure generated filtered events display in existing encounter area
    - Ensure history tracking works with filtered events
    - Ensure dice jar and floor selection still work
    - Test backward compatibility with dice-based generation
    - _Requirements: 9.4, 12.1, 12.2, 12.3_
  
  - [ ]* 11.2 Write integration tests
    - Test filter changes update UI immediately
    - Test generate event displays in encounter area
    - Test history includes filtered events
    - Test backward compatibility (dice-based generation still works)
    - _Requirements: 9.4, 12.1, 12.3_

- [x] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Backend filtering logic must match frontend filtering logic exactly
- The UI replaces the existing "Situation Context" section in the same location
- Backward compatibility is maintained - existing dice-based generation continues to work
