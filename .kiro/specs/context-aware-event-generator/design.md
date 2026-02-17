# Design Document: Context-Aware Event Generator

## Overview

The Context-Aware Event Generator enhances the existing `generate_dungeon_turn_v2.py` system to accept situational context parameters. Instead of generating generic events that may not fit the current game state, the generator uses context to create appropriate events from the start.

This is a focused enhancement to the existing generator, not a separate "tweaker" tool. The changes are minimal and backward-compatible.

## Architecture

The enhancement follows a simple pattern:

1. **Context Input**: Accept optional context parameters
2. **Template Selection**: Choose appropriate event templates based on context
3. **Description Generation**: Generate context-aware descriptions
4. **Output**: Return events in the existing format

```
┌─────────────────┐
│ Context Params  │
│ - space_type    │
│ - recent_combat │
│ - new_area      │
│ - party_status  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Event Generator │
│ (existing)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Template        │
│ Selector        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context-Aware   │
│ Event           │
└─────────────────┘
```

## Data Models

### EventContext

```python
@dataclass
class EventContext:
    """Context parameters for event generation."""
    space_type: str = "unknown"  # hallway, large_room, small_room, outside, vertical_space, water, unknown
    recent_combat: bool = False
    new_area: bool = True
    party_status: str = "healthy"  # healthy, injured, low_resources
    
    def validate(self):
        """Validate context parameters."""
        valid_spaces = ["hallway", "large_room", "small_room", "outside", "vertical_space", "water", "unknown"]
        valid_statuses = ["healthy", "injured", "low_resources"]
        
        if self.space_type not in valid_spaces:
            raise ValueError(f"Invalid space_type: {self.space_type}")
        if self.party_status not in valid_statuses:
            raise ValueError(f"Invalid party_status: {self.party_status}")
```

## Component Changes

### 1. Enhanced Event Generation Function

Modify the existing `generate_event_for_sum()` function to accept context:

```python
def generate_event_for_sum(
    dice_sum: int,
    floor: int,
    floor_data: dict,
    party_level: int,
    creatures: list,
    context: EventContext = None  # NEW PARAMETER
) -> dict:
    """
    Generate event for given dice sum with optional context.
    
    Args:
        dice_sum: Sum of 5d20 roll
        floor: Current dungeon floor
        floor_data: Floor information from gauntlight_keep_levels.md
        party_level: Party level
        creatures: Creature database
        context: Optional context parameters (NEW)
    
    Returns:
        Event dictionary
    """
    if context is None:
        context = EventContext()  # Use defaults
    
    context.validate()
    
    # Existing category determination logic...
    category = get_category_from_sum(dice_sum, is_extreme)
    
    # NEW: Select template based on context
    event_template = select_template(category, context)
    
    # Generate event using context-aware template
    event = generate_from_template(event_template, floor_data, party_level, creatures, context)
    
    return event
```

### 2. Template Selection System

```python
def select_template(category: str, context: EventContext) -> dict:
    """
    Select appropriate event template based on category and context.
    
    Args:
        category: Event category (COMBAT, DILEMMA, etc.)
        context: Context parameters
    
    Returns:
        Event template dictionary
    """
    # Get base templates for category
    templates = EVENT_TEMPLATES[category]
    
    # Filter templates by context compatibility
    compatible = [t for t in templates if is_compatible(t, context)]
    
    # Select random compatible template
    return random.choice(compatible) if compatible else random.choice(templates)

def is_compatible(template: dict, context: EventContext) -> bool:
    """
    Check if template is compatible with context.
    
    Args:
        template: Event template
        context: Context parameters
    
    Returns:
        True if compatible
    """
    # Check space type compatibility
    if 'required_spaces' in template:
        if context.space_type not in template['required_spaces']:
            return False
    
    # Check combat requirement
    if template.get('requires_recent_combat', False) and not context.recent_combat:
        return False
    
    # Check discovery requirement
    if template.get('requires_new_area', False) and not context.new_area:
        return False
    
    return True
```

### 3. Context-Aware Description Generation

```python
def generate_from_template(
    template: dict,
    floor_data: dict,
    party_level: int,
    creatures: list,
    context: EventContext
) -> dict:
    """
    Generate event from template with context-aware descriptions.
    
    Args:
        template: Event template
        floor_data: Floor information
        party_level: Party level
        creatures: Creature database
        context: Context parameters
    
    Returns:
        Complete event dictionary
    """
    event = template.copy()
    
    # Apply context-specific description modifiers
    event['description'] = apply_context_to_description(
        event['description'],
        context
    )
    
    # Apply space-specific tactical notes
    if 'tactical_notes' in event:
        event['tactical_notes'] = apply_space_tactics(
            event['tactical_notes'],
            context.space_type
        )
    
    # Apply party status modifiers
    if context.party_status != "healthy":
        event['description'] = add_status_flavor(
            event['description'],
            context.party_status
        )
    
    return event

def apply_context_to_description(description: str, context: EventContext) -> str:
    """Apply context-specific modifications to description."""
    # Replace space placeholders
    description = description.replace("{space}", get_space_description(context.space_type))
    
    # Add combat context if relevant
    if context.recent_combat and "{combat_context}" in description:
        description = description.replace("{combat_context}", "from the recent skirmish")
    else:
        description = description.replace("{combat_context}", "")
    
    return description

def apply_space_tactics(tactical_notes: str, space_type: str) -> str:
    """Apply space-specific tactical modifications."""
    space_tactics = {
        "hallway": "Limited flanking. Reach weapons effective. Single-file movement.",
        "large_room": "Flanking opportunities. Use cover. Multiple approach vectors.",
        "vertical_space": "Height advantage matters. Climbing required. Fall hazards.",
        "outside": "Weather effects. Long sight lines. Open terrain.",
        "water": "Swimming required. Drowning risk. Aquatic advantage.",
        "small_room": "Cramped quarters. Limited movement. Close combat.",
        "unknown": ""
    }
    
    space_note = space_tactics.get(space_type, "")
    return f"{tactical_notes} {space_note}".strip()

def add_status_flavor(description: str, party_status: str) -> str:
    """Add party status flavor to description."""
    status_prefixes = {
        "injured": "Despite your wounds, ",
        "low_resources": "With supplies running low, "
    }
    
    prefix = status_prefixes.get(party_status, "")
    return f"{prefix}{description}" if prefix else description
```

## Event Template Structure

Event templates will be enhanced with context metadata:

```python
EVENT_TEMPLATES = {
    "DILEMMA": [
        {
            "title": "Chase Fleeing Enemy",
            "description": "An enemy breaks away {combat_context} and flees toward their allies.",
            "requires_recent_combat": True,  # NEW: Only show if recent combat
            "required_spaces": ["hallway", "large_room", "outside"],  # NEW: Space compatibility
            "choice_a": "Chase them: Pursue and fight now (1 enemy, but you're split from party)",
            "choice_b": "Let them go: They alert others. Next encounter has +2 enemies and they're prepared.",
            "gm_notes": "If chase: solo combat for fastest PC. If let go: next encounter is significantly harder."
        },
        {
            "title": "Suspicious Discovery",
            "description": "You discover {space} that seems too convenient. A trap? Or genuine opportunity?",
            "requires_new_area": True,  # NEW: Only show in new areas
            "required_spaces": ["hallway", "large_room", "small_room"],
            "choice_a": "Investigate carefully: DC 18 Perception to spot danger. Success reveals truth.",
            "choice_b": "Proceed cautiously: Avoid the area entirely. Miss potential reward.",
            "gm_notes": "50% chance it's a trap, 50% chance it's a genuine treasure."
        },
        # More templates...
    ],
    # Other categories...
}
```

## Web Interface Changes

### Frontend (templates/index.html)

Add context parameter controls:

```html
<div class="context-controls">
    <h3>Situation Context</h3>
    
    <div class="control-group">
        <label for="space-type">Space Type:</label>
        <select id="space-type">
            <option value="unknown">Unknown</option>
            <option value="hallway">Hallway</option>
            <option value="large_room">Large Room</option>
            <option value="small_room">Small Room</option>
            <option value="outside">Outside</option>
            <option value="vertical_space">Vertical Space</option>
            <option value="water">Water/Underwater</option>
        </select>
    </div>
    
    <div class="control-group">
        <label>
            <input type="checkbox" id="recent-combat">
            Recent Combat
        </label>
    </div>
    
    <div class="control-group">
        <label>
            <input type="checkbox" id="new-area" checked>
            New/Unfamiliar Area
        </label>
    </div>
    
    <div class="control-group">
        <label for="party-status">Party Status:</label>
        <select id="party-status">
            <option value="healthy">Healthy</option>
            <option value="injured">Injured</option>
            <option value="low_resources">Low Resources</option>
        </select>
    </div>
</div>
```

### Backend (dungeon_turn_app.py)

Modify the `/api/encounter` endpoint:

```python
@app.route('/api/encounter', methods=['POST'])
def get_encounter():
    """Generate random encounter with context"""
    data = request.json
    floor = data.get('floor', 1)
    dice_sum = data.get('sum')
    party_level = data.get('party_level', 4)
    
    # NEW: Extract context parameters
    context = EventContext(
        space_type=data.get('space_type', 'unknown'),
        recent_combat=data.get('recent_combat', False),
        new_area=data.get('new_area', True),
        party_status=data.get('party_status', 'healthy')
    )
    
    if not dice_sum:
        return jsonify({'error': 'Sum required'}), 400
    
    floor_data = levels_data.get(floor)
    if not floor_data:
        return jsonify({'error': f'Floor {floor} not found'}), 404
    
    # Generate event with context
    event = generate_event_for_sum(
        dice_sum, 
        floor, 
        floor_data, 
        party_level, 
        creatures,
        context  # NEW: Pass context
    )
    
    # Rest of the function remains the same...
    return jsonify(event)
```

## CLI Changes

Add context parameter arguments:

```python
def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Dungeon Turn Encounters V2')
    parser.add_argument('--level', type=int, default=4, help='Party level (default: 4)')
    parser.add_argument('--floors', type=int, default=3, help='Number of floors to generate (1 to X)')
    parser.add_argument('--output', type=str, default='gm/dungeon_turn_encounters_v2.md', help='Output file path')
    
    # NEW: Context parameters
    parser.add_argument('--space-type', type=str, default='unknown', 
                       choices=['hallway', 'large_room', 'small_room', 'outside', 'vertical_space', 'water', 'unknown'],
                       help='Type of space for event generation')
    parser.add_argument('--recent-combat', action='store_true', help='Party just finished combat')
    parser.add_argument('--new-area', action='store_true', default=True, help='Party is in unfamiliar area')
    parser.add_argument('--party-status', type=str, default='healthy',
                       choices=['healthy', 'injured', 'low_resources'],
                       help='Current party condition')
    
    args = parser.parse_args()
    
    # Create context from args
    context = EventContext(
        space_type=args.space_type,
        recent_combat=args.recent_combat,
        new_area=args.new_area,
        party_status=args.party_status
    )
    
    generate_all_encounters(
        party_level=args.level,
        max_floor=args.floors,
        output_file=args.output,
        context=context  # NEW: Pass context
    )
```

## Example Context Effects

### Example 1: Chase Fleeing Enemy

**Without Context (Current):**
```
Title: Chase Fleeing Enemy
Description: You wounded an enemy and they're fleeing. They're heading toward their allies to raise the alarm.
```
❌ Problem: Assumes combat that may not have happened

**With Context (recent_combat=false):**
```
This event is filtered out and not shown
```
✅ Solution: Event only appears when recent_combat=true

**With Context (recent_combat=true, space_type="hallway"):**
```
Title: Chase Fleeing Enemy
Description: An enemy breaks away from the skirmish and flees down the narrow corridor toward their allies.
Tactical Notes: Limited flanking. Reach weapons effective. Single-file movement. Chase requires single-file pursuit.
```
✅ Solution: Natural description that acknowledges combat and adapts to space

### Example 2: Discovery Event

**Without Context (Current):**
```
Title: Hidden Cache
Description: You discover a hidden cache of supplies.
```
⚠️ Problem: Makes sense in new areas, but odd if you've been here before

**With Context (new_area=false):**
```
This event is filtered out or replaced with a different discovery type
```
✅ Solution: Discovery events only appear in new areas

**With Context (new_area=true, space_type="vertical_space"):**
```
Title: Hidden Cache
Description: You discover a hidden cache of supplies on a high ledge.
Tactical Notes: Height advantage matters. Climbing required. Fall hazards. DC 15 Athletics to reach cache safely.
```
✅ Solution: Discovery adapted to vertical space

## Testing Strategy

### Unit Tests

- Test EventContext validation
- Test template selection with various contexts
- Test description generation with context
- Test space-specific tactical notes
- Test party status flavor text
- Test backward compatibility (no context provided)

### Integration Tests

- Test web API with context parameters
- Test CLI with context arguments
- Test event generation across all space types
- Test event filtering based on context
- Test template compatibility checking

### Manual Testing

- Generate events with different context combinations
- Verify descriptions feel natural
- Verify tactical notes match space type
- Verify combat-related events only appear with recent_combat=true
- Verify discovery events only appear with new_area=true

## Implementation Notes

### Backward Compatibility

All changes are backward-compatible:
- Context parameter is optional (defaults to EventContext())
- Existing code works without modification
- Output format unchanged
- Existing templates work without context metadata

### Template Migration

Existing event templates can be gradually enhanced:
1. Phase 1: Add context parameter support (no template changes)
2. Phase 2: Add context metadata to templates (requires_recent_combat, etc.)
3. Phase 3: Add context placeholders to descriptions ({space}, {combat_context})
4. Phase 4: Create space-specific template variants

### Performance

Context-aware generation has minimal performance impact:
- Template selection: O(n) where n = templates per category (~10-20)
- Description modification: O(1) string replacements
- No additional API calls or database queries

## File Changes Summary

Files to modify:
- `bin/generators/generate_dungeon_turn_v2.py` - Add context support
- `bin/web/dungeon_turn_app.py` - Add context parameter handling
- `bin/web/templates/index.html` - Add context controls
- `bin/web/static/style.css` - Style context controls
- `bin/web/static/script.js` - Handle context in frontend

Files to create:
- `bin/generators/event_context.py` - EventContext dataclass
- `bin/generators/template_selector.py` - Template selection logic
- `docs/CONTEXT_PARAMETERS.md` - Documentation

## Future Enhancements

Potential improvements:
1. **Smart Defaults**: Infer context from recent rolls (auto-set recent_combat if last event was COMBAT)
2. **Context Presets**: Save common context combinations ("Exploring new floor", "After big fight", etc.)
3. **Context History**: Track context changes to maintain continuity
4. **More Parameters**: Time of day, party composition, resource levels
5. **AI-Generated Variants**: Use LLM to generate context-specific description variants
