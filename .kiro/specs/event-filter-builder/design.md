# Design Document: Event Filter Builder

## Overview

The Event Filter Builder replaces the simple "Situation Context" section with a comprehensive filtering system that allows GMs to filter dungeon turn events by multiple criteria. The system uses client-side filtering for immediate feedback and sends filter parameters to the backend for event generation.

The architecture follows a clean separation between:
- Frontend UI (HTML/JavaScript in gm.html)
- Client-side filtering logic (JavaScript)
- Backend filtering and event selection (Python)
- Event data storage (JSON)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (gm.html)                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │  Filter Builder  │  │  Event Preview   │  │  Generate │ │
│  │  UI Components   │──│  List Display    │  │  Button   │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
│           │                      │                   │       │
│           └──────────────────────┴───────────────────┘       │
│                              │                               │
│                    ┌─────────▼─────────┐                     │
│                    │  Filter Manager   │                     │
│                    │  (JavaScript)     │                     │
│                    └─────────┬─────────┘                     │
└──────────────────────────────┼───────────────────────────────┘
                               │ AJAX Request
                               │ (filter params)
┌──────────────────────────────▼───────────────────────────────┐
│                    Backend (dungeon_turn_app.py)             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │  /api/encounter  │──│  Event Filter    │──│  Event    │ │
│  │  Endpoint        │  │  Logic           │  │  Selector │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
│                                │                             │
└────────────────────────────────┼─────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  dungeon_turn_events    │
                    │  .json                  │
                    └─────────────────────────┘
```

### Data Flow

1. User adjusts filter controls in UI
2. JavaScript Filter Manager updates immediately:
   - Filters events client-side
   - Updates matching count display
   - Updates preview list
3. User clicks "Generate Event"
4. JavaScript sends AJAX request with filter parameters
5. Backend filters events and selects one randomly
6. Backend returns selected event
7. Frontend displays event in encounter display area

## Components and Interfaces

### Frontend Components

#### 1. Filter Builder UI Component

**Location**: bin/web/templates/gm.html (replaces "Situation Context" section)

**HTML Structure**:
```html
<div class="bg-gray-800 rounded-lg p-6 shadow-2xl border border-purple-500 mb-6">
    <h2 class="text-2xl font-bold mb-4">Event Filters</h2>
    
    <!-- Filter Controls -->
    <div class="grid md:grid-cols-2 gap-4 mb-4">
        <!-- Event Category Multi-Select -->
        <div>
            <label class="block text-sm font-bold mb-2">Event Categories</label>
            <select id="filter-categories" multiple class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-purple-500">
                <option value="OPPORTUNITY">Opportunity</option>
                <option value="COMPLICATION">Complication</option>
                <option value="DILEMMA">Dilemma</option>
                <option value="ACTIVE_THREAT">Active Threat</option>
            </select>
        </div>
        
        <!-- Skills Multi-Select -->
        <div>
            <label class="block text-sm font-bold mb-2">Skills</label>
            <select id="filter-skills" multiple class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-purple-500">
                <option value="Perception">Perception</option>
                <option value="Stealth">Stealth</option>
                <option value="Thievery">Thievery</option>
                <option value="Athletics">Athletics</option>
                <option value="Acrobatics">Acrobatics</option>
                <option value="Arcana">Arcana</option>
                <option value="Nature">Nature</option>
                <option value="Medicine">Medicine</option>
                <option value="Diplomacy">Diplomacy</option>
                <option value="Intimidation">Intimidation</option>
                <option value="Deception">Deception</option>
                <option value="Society">Society</option>
                <option value="Religion">Religion</option>
                <option value="Crafting">Crafting</option>
                <option value="Survival">Survival</option>
            </select>
        </div>
        
        <!-- Time Cost Multi-Select -->
        <div>
            <label class="block text-sm font-bold mb-2">Time Cost</label>
            <select id="filter-time-cost" multiple class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-purple-500">
                <option value="quick">Quick (1-3 actions)</option>
                <option value="short">Short (5-10 min)</option>
                <option value="long">Long (20-30 min)</option>
            </select>
        </div>
        
        <!-- New Area Single-Select -->
        <div>
            <label class="block text-sm font-bold mb-2">New/Unfamiliar Area</label>
            <select id="filter-new-area" class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-purple-500">
                <option value="either">Either</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
            </select>
        </div>
        
        <!-- Reward Type Text Search (for OPPORTUNITY events) -->
        <div>
            <label class="block text-sm font-bold mb-2">Reward Type (Opportunities)</label>
            <input type="text" id="filter-reward" placeholder="e.g., healing, gold, tactical" 
                class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-purple-500">
        </div>
        
        <!-- Threat Level Multi-Select (for ACTIVE_THREAT events) -->
        <div>
            <label class="block text-sm font-bold mb-2">Threat Level (Active Threats)</label>
            <select id="filter-threat-level" multiple class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-purple-500">
                <option value="Low">Low</option>
                <option value="Moderate">Moderate</option>
                <option value="High">High</option>
                <option value="Extreme">Extreme</option>
            </select>
        </div>
    </div>
    
    <!-- Matching Count and Actions -->
    <div class="flex justify-between items-center mb-4">
        <div>
            <span class="text-lg font-bold">Matching Events: </span>
            <span id="matching-count" class="text-2xl text-green-400">0</span>
        </div>
        <button onclick="clearAllFilters()" class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition">
            Clear All Filters
        </button>
    </div>
    
    <!-- Event Preview List -->
    <div class="bg-gray-700 rounded-lg p-4 mb-4 max-h-48 overflow-y-auto">
        <h3 class="text-sm font-bold mb-2">Available Events:</h3>
        <ul id="event-preview-list" class="text-sm text-gray-300 space-y-1">
            <!-- Preview items populated by JavaScript -->
        </ul>
    </div>
    
    <!-- Generate Event Button -->
    <button onclick="generateFilteredEvent()" id="generate-filtered-event-btn" 
        class="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-4 rounded-lg text-xl transition transform hover:scale-105 shadow-lg">
        🎲 GENERATE FILTERED EVENT
    </button>
</div>
```

**JavaScript Interface**:
```javascript
// Filter Manager Object
const EventFilterManager = {
    // State
    allEvents: [],
    filteredEvents: [],
    
    // Initialize with event data
    init: function(events) {
        this.allEvents = events;
        this.attachEventListeners();
        this.updateFilters();
    },
    
    // Attach change listeners to all filter controls
    attachEventListeners: function() {
        document.getElementById('filter-categories').addEventListener('change', () => this.updateFilters());
        document.getElementById('filter-skills').addEventListener('change', () => this.updateFilters());
        document.getElementById('filter-time-cost').addEventListener('change', () => this.updateFilters());
        document.getElementById('filter-new-area').addEventListener('change', () => this.updateFilters());
        document.getElementById('filter-reward').addEventListener('input', () => this.updateFilters());
        document.getElementById('filter-threat-level').addEventListener('change', () => this.updateFilters());
    },
    
    // Get current filter values
    getFilterValues: function() {
        return {
            categories: Array.from(document.getElementById('filter-categories').selectedOptions).map(o => o.value),
            skills: Array.from(document.getElementById('filter-skills').selectedOptions).map(o => o.value),
            timeCost: Array.from(document.getElementById('filter-time-cost').selectedOptions).map(o => o.value),
            newArea: document.getElementById('filter-new-area').value,
            reward: document.getElementById('filter-reward').value.toLowerCase(),
            threatLevel: Array.from(document.getElementById('filter-threat-level').selectedOptions).map(o => o.value)
        };
    },
    
    // Apply filters to events
    filterEvents: function(events, filters) {
        return events.filter(event => {
            // Category filter (OR logic within filter)
            if (filters.categories.length > 0 && !filters.categories.includes(event.category)) {
                return false;
            }
            
            // Skills filter (OR logic within filter)
            if (filters.skills.length > 0) {
                const hasMatchingSkill = event.skills && event.skills.some(skill => filters.skills.includes(skill));
                if (!hasMatchingSkill) return false;
            }
            
            // Time cost filter (OR logic within filter)
            if (filters.timeCost.length > 0) {
                const timeCostStr = event.time_cost || '';
                const matchesTimeCost = filters.timeCost.some(tc => {
                    if (tc === 'quick') return /\d+ action/i.test(timeCostStr);
                    if (tc === 'short') return /(5|10) min/i.test(timeCostStr);
                    if (tc === 'long') return /(20|30) min/i.test(timeCostStr);
                    return false;
                });
                if (!matchesTimeCost) return false;
            }
            
            // New area filter
            if (filters.newArea !== 'either') {
                const requiresNewArea = event.requires_new_area === true;
                if (filters.newArea === 'yes' && !requiresNewArea) return false;
                if (filters.newArea === 'no' && requiresNewArea) return false;
            }
            
            // Reward filter (text search, only for OPPORTUNITY events)
            if (filters.reward && event.category === 'OPPORTUNITY') {
                const reward = (event.reward || '').toLowerCase();
                if (!reward.includes(filters.reward)) return false;
            }
            
            // Threat level filter (OR logic within filter, only for ACTIVE_THREAT events)
            if (filters.threatLevel.length > 0 && event.category === 'ACTIVE_THREAT') {
                const threatLevel = event.threat_level || '';
                const matchesThreatLevel = filters.threatLevel.some(tl => 
                    threatLevel.toLowerCase().includes(tl.toLowerCase())
                );
                if (!matchesThreatLevel) return false;
            }
            
            return true;
        });
    },
    
    // Update filtered events and UI
    updateFilters: function() {
        const filters = this.getFilterValues();
        this.filteredEvents = this.filterEvents(this.allEvents, filters);
        this.updateMatchingCount();
        this.updatePreviewList();
    },
    
    // Update matching count display
    updateMatchingCount: function() {
        const countElement = document.getElementById('matching-count');
        countElement.textContent = this.filteredEvents.length;
        countElement.className = this.filteredEvents.length === 0 ? 'text-2xl text-red-400' : 'text-2xl text-green-400';
    },
    
    // Update preview list
    updatePreviewList: function() {
        const listElement = document.getElementById('event-preview-list');
        listElement.innerHTML = '';
        
        if (this.filteredEvents.length === 0) {
            listElement.innerHTML = '<li class="text-red-400">No events match current filters</li>';
            return;
        }
        
        const previewCount = Math.min(10, this.filteredEvents.length);
        for (let i = 0; i < previewCount; i++) {
            const li = document.createElement('li');
            li.textContent = `• ${this.filteredEvents[i].title}`;
            listElement.appendChild(li);
        }
        
        if (this.filteredEvents.length > 10) {
            const li = document.createElement('li');
            li.textContent = `... and ${this.filteredEvents.length - 10} more`;
            li.className = 'text-gray-500 italic';
            listElement.appendChild(li);
        }
    }
};

// Clear all filters
function clearAllFilters() {
    document.getElementById('filter-categories').selectedIndex = -1;
    document.getElementById('filter-skills').selectedIndex = -1;
    document.getElementById('filter-time-cost').selectedIndex = -1;
    document.getElementById('filter-new-area').value = 'either';
    document.getElementById('filter-reward').value = '';
    document.getElementById('filter-threat-level').selectedIndex = -1;
    EventFilterManager.updateFilters();
}

// Generate filtered event
async function generateFilteredEvent() {
    const filters = EventFilterManager.getFilterValues();
    
    if (EventFilterManager.filteredEvents.length === 0) {
        alert('No events match your current filters. Please adjust your filters.');
        return;
    }
    
    const btn = document.getElementById('generate-filtered-event-btn');
    btn.disabled = true;
    btn.textContent = '⏳ Generating...';
    
    try {
        const response = await fetch('/api/encounter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                floor: currentFloor,
                sum: 50, // Dummy value since we're using filters
                party_level: partyLevel,
                filters: filters
            })
        });
        
        const event = await response.json();
        displayEncounter(event, 50);
        updateHistory();
    } catch (error) {
        console.error('Error generating filtered event:', error);
        alert('Error generating event. Please try again.');
    } finally {
        btn.disabled = false;
        btn.textContent = '🎲 GENERATE FILTERED EVENT';
    }
}
```

#### 2. Backend Filter Logic

**Location**: bin/web/dungeon_turn_app.py

**Modified /api/encounter Endpoint**:
```python
@app.route('/api/encounter', methods=['POST'])
def get_encounter():
    """Generate random encounter for given floor and sum with optional filters"""
    data = request.json
    floor = data.get('floor', 1)
    dice_sum = data.get('sum')
    party_level = data.get('party_level', 4)
    filters = data.get('filters', {})
    
    if not dice_sum:
        return jsonify({'error': 'Sum required'}), 400
    
    # Get floor data
    floor_data = levels_data.get(floor)
    if not floor_data:
        return jsonify({'error': f'Floor {floor} not found'}), 404
    
    # If filters are provided, use filtered event selection
    if filters and any(filters.values()):
        event = generate_filtered_event(filters, floor, floor_data, party_level, creatures)
    else:
        # Use existing logic for non-filtered generation
        context = EventContext(
            space_type=data.get('space_type', 'unknown'),
            recent_combat=data.get('recent_combat', False),
            new_area=data.get('new_area', True),
            party_status=data.get('party_status', 'healthy')
        )
        event = generate_event_for_sum(dice_sum, floor, floor_data, party_level, creatures, context)
    
    # Add creature stats if combat encounter
    if event.get('category') == 'COMBAT' and event.get('creatures'):
        # ... existing creature stats logic ...
    
    # Add to history
    roll_history.append({
        'floor': floor,
        'sum': dice_sum,
        'category': event['category'],
        'title': event['title']
    })
    
    return jsonify(event)
```

**New Filter Function**:
```python
def generate_filtered_event(filters, floor, floor_data, party_level, creatures):
    """Generate event based on filter criteria"""
    # Load all events
    events_file = os.path.join(PROJECT_ROOT, 'etc', 'dungeon_turn_events.json')
    with open(events_file, 'r') as f:
        all_events = json.load(f)
    
    # Flatten events from all categories
    flat_events = []
    for category, events_list in all_events.items():
        for event in events_list:
            event['category'] = category
            flat_events.append(event)
    
    # Apply filters
    filtered_events = apply_event_filters(flat_events, filters)
    
    if not filtered_events:
        return {
            'category': 'ERROR',
            'title': 'No Matching Events',
            'description': 'No events match your current filter criteria. Please adjust your filters.',
            'error': True
        }
    
    # Select random event from filtered set
    selected_event = random.choice(filtered_events)
    
    return selected_event

def apply_event_filters(events, filters):
    """Apply filter criteria to event list"""
    filtered = events
    
    # Category filter
    if filters.get('categories'):
        filtered = [e for e in filtered if e['category'] in filters['categories']]
    
    # Skills filter (OR logic)
    if filters.get('skills'):
        filtered = [e for e in filtered 
                   if e.get('skills') and any(skill in e['skills'] for skill in filters['skills'])]
    
    # Time cost filter
    if filters.get('timeCost'):
        def matches_time_cost(event, time_costs):
            time_str = event.get('time_cost', '').lower()
            for tc in time_costs:
                if tc == 'quick' and 'action' in time_str:
                    return True
                if tc == 'short' and ('5 min' in time_str or '10 min' in time_str):
                    return True
                if tc == 'long' and ('20 min' in time_str or '30 min' in time_str):
                    return True
            return False
        
        filtered = [e for e in filtered if matches_time_cost(e, filters['timeCost'])]
    
    # New area filter
    if filters.get('newArea') and filters['newArea'] != 'either':
        requires_new = filters['newArea'] == 'yes'
        filtered = [e for e in filtered if e.get('requires_new_area', False) == requires_new]
    
    # Reward filter (text search, OPPORTUNITY only)
    if filters.get('reward'):
        reward_text = filters['reward'].lower()
        filtered = [e for e in filtered 
                   if e['category'] == 'OPPORTUNITY' and 
                   reward_text in e.get('reward', '').lower()]
    
    # Threat level filter (ACTIVE_THREAT only)
    if filters.get('threatLevel'):
        filtered = [e for e in filtered 
                   if e['category'] == 'ACTIVE_THREAT' and 
                   any(tl.lower() in e.get('threat_level', '').lower() for tl in filters['threatLevel'])]
    
    return filtered
```

## Data Models

### Event Data Structure

Events are stored in `etc/dungeon_turn_events.json` with the following structure:

```json
{
  "OPPORTUNITY": [
    {
      "title": "Event Title",
      "description": "Event description",
      "challenge": "DC and skill requirements",
      "success": "Success outcome",
      "failure": "Failure outcome",
      "skills": ["Skill1", "Skill2"],
      "time_cost": "Time description",
      "gm_notes": "GM guidance",
      "reward": "Reward type",
      "requires_new_area": true/false
    }
  ],
  "COMPLICATION": [...],
  "DILEMMA": [...],
  "ACTIVE_THREAT": [
    {
      "title": "Threat Title",
      "description": "Threat description",
      "immediate_action": "Required action",
      "success": "Success outcome",
      "failure": "Failure outcome",
      "skills": ["Skill1"],
      "time_cost": "Time description",
      "gm_notes": "GM guidance",
      "threat_level": "Low/Moderate/High/Extreme"
    }
  ]
}
```

### Filter Parameters Object

```javascript
{
  categories: ["OPPORTUNITY", "COMPLICATION"],  // Array of selected categories
  skills: ["Stealth", "Perception"],            // Array of selected skills
  timeCost: ["quick", "short"],                 // Array of time cost ranges
  newArea: "either" | "yes" | "no",             // Single selection
  reward: "healing",                             // Text search string
  threatLevel: ["Moderate", "High"]             // Array of threat levels
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Category Filter Correctness

*For any* set of selected event categories and any event pool, all events in the filtered result set must have a category that matches at least one selected category.

**Validates: Requirements 1.2**

### Property 2: Skill Filter Correctness

*For any* set of selected skills and any event pool, all events in the filtered result set must have at least one skill in their skills array that matches a selected skill.

**Validates: Requirements 2.2**

### Property 3: Time Cost Filter Correctness

*For any* set of selected time cost ranges (quick, short, long) and any event pool, all events in the filtered result set must have a time_cost field that matches at least one selected range pattern.

**Validates: Requirements 3.2, 3.3, 3.4**

### Property 4: New Area Filter Correctness (Yes)

*For any* event pool, when the new area filter is set to "Yes", all events in the filtered result set must have requires_new_area set to true.

**Validates: Requirements 3.2**

### Property 5: New Area Filter Correctness (No)

*For any* event pool, when the new area filter is set to "No", all events in the filtered result set must have requires_new_area set to false or undefined.

**Validates: Requirements 3.3**

### Property 6: Reward Text Search Correctness

*For any* search string and any event pool, all OPPORTUNITY events in the filtered result set must have a reward field that contains the search string (case-insensitive substring match).

**Validates: Requirements 4.2, 4.4**

### Property 7: Threat Level Filter Correctness

*For any* set of selected threat levels and any event pool, all ACTIVE_THREAT events in the filtered result set must have a threat_level field that contains at least one selected threat level.

**Validates: Requirements 5.2**

### Property 8: AND Logic Across Filters

*For any* combination of active filters and any event pool, every event in the filtered result set must satisfy ALL active filter criteria simultaneously.

**Validates: Requirements 6.1, 6.3**

### Property 9: OR Logic Within Multi-Select Filters

*For any* multi-select filter with multiple values selected and any event pool, an event passes the filter if it matches ANY of the selected values within that filter.

**Validates: Requirements 6.2**

### Property 10: Clear Filters Reset

*For any* filter state, when clear all filters is invoked, all filter controls must return to their default state (multi-selects empty, single-selects to "Either", text fields empty).

**Validates: Requirements 8.2, 8.4**

### Property 11: Random Selection from Filtered Set

*For any* non-empty filtered event set, when generate event is invoked, the selected event must be a member of the filtered set.

**Validates: Requirements 9.2**

### Property 12: Preview List Truncation

*For any* filtered event set with more than 10 events, the preview list must display exactly 10 event titles.

**Validates: Requirements 10.4**

### Property 13: Backend Filter Consistency

*For any* set of filter parameters, the backend filtering logic must produce the same filtered event set as the frontend filtering logic when applied to the same event pool.

**Validates: Requirements 11.3**

## Error Handling

### Frontend Error Handling

1. **No Matching Events**: When filters result in zero matching events, display a warning message and disable the Generate Event button
2. **Network Errors**: When AJAX request fails, display error message and re-enable the Generate Event button
3. **Invalid Filter Combinations**: No validation needed - any filter combination is valid, even if it results in zero matches

### Backend Error Handling

1. **Missing Required Parameters**: Return 400 error if required parameters (floor, sum) are missing
2. **Invalid Floor**: Return 404 error if floor doesn't exist
3. **No Matching Events**: Return a special error event object with category "ERROR" and appropriate message
4. **File Read Errors**: Log error and return 500 error if events JSON file cannot be read

### Edge Cases

1. **Empty Filters**: When no filters are selected, all events should be available (no filtering applied)
2. **Contradictory Filters**: Some filter combinations may result in zero matches (e.g., OPPORTUNITY + threat_level filter) - this is valid and should show zero matches
3. **Partial Event Data**: Events may not have all fields (e.g., some events don't have requires_new_area) - treat missing fields as "doesn't match" for positive filters
4. **Case Sensitivity**: Text search should be case-insensitive
5. **Whitespace**: Text search should trim whitespace from search string

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure correctness:

- **Unit tests**: Verify specific examples, edge cases, UI interactions, and API contracts
- **Property tests**: Verify universal filtering properties across all possible inputs

### Unit Testing

Unit tests should focus on:

1. **UI Component Rendering**: Verify all filter controls are present with correct options
2. **Event Listeners**: Verify filter changes trigger updates
3. **API Integration**: Verify AJAX requests send correct parameters
4. **Edge Cases**: 
   - Empty filter state (all events available)
   - Zero matching events (warning displayed)
   - Clear all filters (resets to default)
   - Missing event fields (handled gracefully)
5. **Backend API**: 
   - Endpoint accepts filter parameters
   - Returns correct response structure
   - Handles missing parameters
   - Backward compatibility with existing calls

### Property-Based Testing

Property tests should verify filtering logic with randomized inputs. Each property test should run a minimum of 100 iterations.

**Test Configuration**:
- Use a property-based testing library appropriate for JavaScript (fast-check) and Python (Hypothesis)
- Each test should run 100+ iterations with randomized inputs
- Each test must reference its design document property using the tag format below

**Property Test Tags**:
Each property test must include a comment tag:
```javascript
// Feature: event-filter-builder, Property 1: Category Filter Correctness
```

**Property Tests to Implement**:

1. **Property 1 Test**: Generate random event pools and random category selections, verify all filtered events have matching categories
2. **Property 2 Test**: Generate random event pools and random skill selections, verify all filtered events have at least one matching skill
3. **Property 3 Test**: Generate random event pools and random time cost selections, verify all filtered events match time cost patterns
4. **Property 4 & 5 Tests**: Generate random event pools, test new area filter with "Yes" and "No" settings
5. **Property 6 Test**: Generate random event pools and random search strings, verify OPPORTUNITY events match search text
6. **Property 7 Test**: Generate random event pools and random threat level selections, verify ACTIVE_THREAT events match threat levels
7. **Property 8 Test**: Generate random event pools and random combinations of multiple filters, verify all filtered events satisfy ALL filters
8. **Property 9 Test**: Generate random event pools and random multi-select filter values, verify OR logic within filters
9. **Property 10 Test**: Generate random filter states, verify clear all resets to defaults
10. **Property 11 Test**: Generate random filtered event sets, verify selected event is always from the filtered set
11. **Property 12 Test**: Generate random filtered event sets of varying sizes, verify preview list truncation
12. **Property 13 Test**: Generate random filter parameters, verify frontend and backend produce identical filtered sets

### Test Data Generation

For property-based tests, generate random events with:
- Random categories (OPPORTUNITY, COMPLICATION, DILEMMA, ACTIVE_THREAT)
- Random skills arrays (0-5 skills from the valid skill list)
- Random time_cost strings (various formats: "X actions", "X min", "X-Y min")
- Random requires_new_area boolean (including undefined)
- Random reward strings (for OPPORTUNITY events)
- Random threat_level strings (for ACTIVE_THREAT events)

### Integration Testing

Integration tests should verify:
1. Filter changes update UI immediately
2. Generate event button triggers correct API call
3. Generated event displays in encounter area
4. Filter state persists during session
5. Backward compatibility with existing dice-based generation

## Performance Considerations

### Client-Side Filtering

- Filter operations run on every filter change
- Event pool size: ~100-200 events
- Expected performance: <10ms for filtering operations
- Use efficient array filtering methods
- Avoid unnecessary DOM updates

### Backend Filtering

- Load events JSON once at startup, cache in memory
- Filter operations on cached data
- Expected performance: <50ms for filtering and selection
- No database queries needed

### UI Responsiveness

- Use debouncing for text input filters (300ms delay)
- Update count and preview list synchronously
- Disable generate button during API call
- Show loading state during event generation

## Deployment Considerations

### File Changes

1. **bin/web/templates/gm.html**: Replace "Situation Context" section with Filter Builder UI
2. **bin/web/dungeon_turn_app.py**: Add filter logic to /api/encounter endpoint
3. **etc/dungeon_turn_events.json**: No changes needed (existing data structure supports filtering)

### Backward Compatibility

- Existing API calls without filters continue to work
- Existing dice jar and floor selection unchanged
- Existing event generation logic preserved for non-filtered calls

### Testing Before Deployment

1. Verify all filter controls render correctly
2. Test filtering with various combinations
3. Verify generate event works with filters
4. Test backward compatibility (dice-based generation still works)
5. Test with production event data
6. Verify performance with full event pool

### Rollback Plan

If issues arise:
1. Revert gm.html to restore "Situation Context" section
2. Revert dungeon_turn_app.py to remove filter logic
3. Existing functionality will be fully restored
