# Dungeon Turn Events Schema Documentation

## Overview

This document describes the JSON structure for dungeon turn events used by the Gauntlight Keep dungeon generator. Events are organized into four categories based on their nature and the dice roll that triggers them. This documentation is designed for game masters who want to understand, modify, or create new events without programming knowledge.

## File Structure

Events are stored in `/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events.json` as a JSON object with four top-level category keys:

```json
{
  "OPPORTUNITY": [ /* array of opportunity events */ ],
  "COMPLICATION": [ /* array of complication events */ ],
  "DILEMMA": [ /* array of dilemma events */ ],
  "ACTIVE_THREAT": [ /* array of active threat events */ ]
}
```

## Event Categories

### OPPORTUNITY (Dice Sum: 5-25)
Positive encounters that reward clever play, provide resources, or offer tactical advantages. These events should feel like lucky breaks or rewards for exploration.

**Examples**: Finding supplies, eavesdropping on enemies, discovering tactical advantages, meeting friendly NPCs, magical discoveries.

### COMPLICATION (Dice Sum: 26-45)
Obstacles that require skill checks to overcome. These events slow progress but can be resolved with the right approach. They test player skills and creativity.

**Examples**: Locked doors, unstable structures, magical wards, language barriers, environmental hazards, puzzle locks.

### DILEMMA (Dice Sum: 46-65)
Meaningful choices with trade-offs. Players must decide between competing priorities, with each choice having clear consequences. No "right" answer.

**Examples**: Speed vs stealth, risk vs reward, moral choices with tactical implications, resource management decisions.

### ACTIVE_THREAT (Dice Sum: 66-85)
Immediate dangers requiring quick decisions. These events create urgency and tension, forcing players to react under pressure.

**Examples**: Approaching patrols, collapsing structures, alarms, ambushes, spreading hazards, environmental dangers.

## Common Fields (All Event Types)

Every event, regardless of category, must include these fields:

### Required Fields

#### `title` (string)
A short, descriptive name for the event. Should be clear and evocative.

**Examples**:
- "Eavesdropping Opportunity"
- "Locked Door"
- "Approach: Loud vs Quiet"
- "Patrol Approaching!"

#### `description` (string)
What the players encounter. This is what the GM reads to set the scene. Should be vivid but concise, creating context without assuming unknown information.

**Good Examples**:
- "You hear voices nearby - creatures discussing their patrol route."
- "The door you need to pass through is locked. The mechanism is complex but functional."
- "You hear heavy footsteps and voices. A patrol is coming this way. You have seconds to act!"

**Bad Examples** (avoid these patterns):
- "The NPC you're with suddenly attacks!" (assumes NPC presence)
- "The spell you're casting backfires!" (assumes specific action)
- "You find a secret passage that bypasses the next 3 rooms" (creates new dungeon features)

#### `spotlight` (array of strings)
Which character classes shine in this event. Use class names from the party composition.

**Valid Classes**: "Rogue", "Monk", "Wizard", "Cleric", "Swashbuckler", "Fighter", "Druid", "Ranger", "All"

**Examples**:
```json
"spotlight": ["Rogue", "Monk"]
"spotlight": ["Wizard"]
"spotlight": ["All"]
```

#### `skills` (array of strings)
Skills that can be used to resolve or interact with this event. Use Pathfinder 2e skill names.

**Common Skills**: "Perception", "Stealth", "Thievery", "Athletics", "Acrobatics", "Arcana", "Nature", "Medicine", "Diplomacy", "Intimidation", "Deception", "Society", "Religion", "Crafting", "Survival"

**Examples**:
```json
"skills": ["Stealth", "Society"]
"skills": ["Thievery", "Athletics"]
"skills": ["Perception"]
```

#### `time_cost` (string)
How long the event takes to resolve. This affects the dice jar mechanic (10 minutes = 1 die added).

**Examples**:
- "1 action to search"
- "10 minutes to listen carefully"
- "2 actions (Thievery) or 3 actions (Athletics)"
- "1 round to react"
- "10 min vs 30 min"

#### `gm_notes` (string)
Guidance for the GM on how to run this event, including mechanical effects, consequences, and adaptation notes.

**Examples**:
- "If successful, next 2 encounters can be avoided with timing. Add 1 die to jar for time spent."
- "If forced open, noise may attract attention."
- "Track choice. Quick approach = enemies get surprise round. Stealthy approach = party gets surprise round."
- "Immediate decision. No time to discuss. Tests party coordination."

## Category-Specific Fields

### OPPORTUNITY and COMPLICATION Events

These categories use a challenge-success-failure structure:

#### `challenge` (string, required)
The DC and skill check(s) required. Can offer multiple approaches.

**Examples**:
```json
"challenge": "DC 16 Stealth to get close, DC 18 Society to understand their language"
"challenge": "DC 18 Thievery to pick lock OR DC 22 Athletics to force open"
"challenge": "DC 17 Survival to identify creatures and direction"
```

#### `success` (string, required)
What happens when the skill check succeeds. Should provide clear mechanical benefits or narrative outcomes.

**Examples**:
```json
"success": "You learn the patrol schedule: they pass through here every 2 hours. You know when it's safe."
"success": "Door opens. Quietly if picked, loudly if forced."
"success": "You identify the creatures and know they went ahead. You can avoid or ambush them."
```

#### `failure` (string, required)
What happens when the skill check fails. Should have meaningful consequences without being punitive.

**Examples**:
```json
"failure": "You make noise and alert them, or can't understand their language."
"failure": "Lock jams (Thievery) or door holds (Athletics). Must find key or try different approach."
"failure": "Tracks are too muddled to read clearly."
```

#### `reward` (string, optional)
For OPPORTUNITY events, describes the mechanical benefit gained.

**Examples**:
```json
"reward": "Intelligence, tactical advantage"
"reward": "Healing without spell slots"
"reward": "Avoid combat, save resources"
```

#### `consequence` (string, optional)
For COMPLICATION events, describes the mechanical penalty or ongoing effect.

**Examples**:
```json
"consequence": "Noise attracts attention"
"consequence": "Dungeon-wide alert"
"consequence": "Damage, blocked passage"
```

### DILEMMA Events

These events present choices rather than skill checks:

#### `choice_a` (string, required)
The first option with its outcome clearly stated.

**Format**: "Action description: outcome and consequences"

**Examples**:
```json
"choice_a": "Move quickly: 10 minutes, but next encounter is alerted to your presence"
"choice_a": "Free them now: Takes 10 minutes (add 1 die), makes noise, but gain potential ally"
"choice_a": "Fight now: Combat while you're fresh and they're unprepared (surprise round)"
```

#### `choice_b` (string, required)
The second option with its outcome clearly stated.

**Examples**:
```json
"choice_b": "Move stealthily: 30 minutes (add 2 dice to jar), but next encounter doesn't know you're coming"
"choice_b": "Come back later: Mark location, but they might be dead or moved when you return"
"choice_b": "Sneak past: DC 17 Stealth. Success = avoid combat. Failure = they join next encounter as reinforcements"
```

#### `choice_c` (string, optional)
A third option if the dilemma warrants it. Not all dilemmas need three choices.

**Examples**:
```json
"choice_c": "Leave them: No time cost, no risk, but no ally and they might alert enemies"
```

#### `consequence` (string, required)
A summary of what's at stake in this dilemma. Helps the GM frame the decision.

**Examples**:
```json
"consequence": "Time vs stealth trade-off"
"consequence": "Moral choice with tactical implications"
"consequence": "Fight now vs potentially harder fight later"
```

### ACTIVE_THREAT Events

These events require immediate action:

#### `immediate_action` (string, required)
What players must do RIGHT NOW. Should convey urgency and present clear options.

**Examples**:
```json
"immediate_action": "Choose NOW: Hide (DC 17 Stealth), Prepare ambush (ready actions), or Flee (move away quickly)"
"immediate_action": "DC 18 Reflex save to grab edge. DC 19 Athletics to pull yourself up."
"immediate_action": "DC 20 Arcana or Thievery to disable in 3 actions, or flee immediately"
```

#### `success` (string, required)
What happens if the immediate action succeeds. Should resolve the threat or mitigate danger.

**Examples**:
```json
"success": "Hide: They pass by. Ambush: Surprise round. Flee: Avoid encounter."
"success": "You catch yourself and climb up. No damage."
"success": "Alarm stops. Only nearby enemies alerted."
```

#### `failure` (string, required)
What happens if the immediate action fails. Should have serious consequences that justify the urgency.

**Examples**:
```json
"failure": "Hide: They spot you (they get surprise). Flee: They chase you (running combat)."
"failure": "You fall 15 feet into the room below. 3d6 damage. Separated from party."
"failure": "Alarm continues. All enemies on this floor are alerted and searching for you."
```

#### `threat_level` (string, required)
Indicates the severity of the threat. Helps the GM convey appropriate urgency.

**Valid Values**:
- "Low - minor inconvenience"
- "Moderate - can be avoided"
- "High - damage and separation"
- "High - affects entire floor"
- "High - combat with disadvantage"
- "High - potential death"

**Examples**:
```json
"threat_level": "Moderate - can be avoided"
"threat_level": "High - damage and separation"
"threat_level": "High - potential death"
```

## Optional Context Fields (All Categories)

These fields control when and where an event can trigger:

### `required_spaces` (array of strings, optional)
Limits the event to specific location types. If omitted, the event can trigger anywhere.

**Valid Space Types**:
- "hallway"
- "large_room"
- "small_room"
- "outside"
- "vertical_space"
- "water"

**Examples**:
```json
"required_spaces": ["hallway", "large_room", "small_room"]
"required_spaces": ["water"]
"required_spaces": ["vertical_space"]
```

### `requires_recent_combat` (boolean, optional)
If `true`, this event only triggers after the party has been in combat recently. Use for events that reference wounds, exhaustion, or pursuit.

**Example**:
```json
"requires_recent_combat": true
```

### `requires_new_area` (boolean, optional)
If `true`, this event only triggers when the party enters an unexplored area. Use for discovery-based events.

**Example**:
```json
"requires_new_area": true
```

## Complete Event Examples

### OPPORTUNITY Event Example

```json
{
  "title": "Eavesdropping Opportunity",
  "description": "You hear voices nearby - creatures discussing their patrol route.",
  "challenge": "DC 16 Stealth to get close, DC 18 Society to understand their language",
  "success": "You learn the patrol schedule: they pass through here every 2 hours. You know when it's safe.",
  "failure": "You make noise and alert them, or can't understand their language.",
  "spotlight": ["Rogue", "Wizard"],
  "skills": ["Stealth", "Society"],
  "time_cost": "10 minutes to listen carefully",
  "gm_notes": "If successful, next 2 encounters can be avoided with timing. Add 1 die to jar for time spent.",
  "reward": "Intelligence, tactical advantage"
}
```

### COMPLICATION Event Example

```json
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
```

### DILEMMA Event Example

```json
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
```

### ACTIVE_THREAT Event Example

```json
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
```

## Guidelines for Adding New Events

### Quality Criteria

When creating new events, ensure they meet these criteria:

#### ✅ DO Create Events That:
- Work in any context with the available space parameters
- Create their own context (e.g., "A dying enemy stumbles into the room...")
- Have clear choices and consequences
- Reward clever play with dice removal or time benefits
- Work within the existing, fixed dungeon map
- Are self-contained and don't assume unknown information
- Offer meaningful decisions or skill challenges
- Have balanced risk/reward ratios

#### ❌ DON'T Create Events That:
- Assume NPCs are present without creating them
- Assume specific actions are being taken without context
- Assume enemies are already present without creating them
- Have overly specific prerequisites that may not be met
- Create new dungeon features (secret passages, shortcuts)
- Modify the fixed dungeon map
- Create passages or rooms that don't exist
- Reference "the NPC you're with" or "your ally"
- Reference "the spell you're casting" or similar assumed actions

### Event Variety Guidelines

Maintain variety across these dimensions:

**Skills**: Don't over-rely on Perception and Stealth. Include:
- Physical: Athletics, Acrobatics
- Mental: Arcana, Nature, Religion, Society
- Social: Diplomacy, Intimidation, Deception
- Technical: Thievery, Crafting, Medicine, Survival

**Spotlight Classes**: Ensure all classes get moments to shine:
- Rogue: Stealth, Thievery, trap-finding
- Wizard: Arcana, magical knowledge
- Cleric: Religion, Medicine, healing
- Monk: Athletics, Acrobatics, awareness
- Swashbuckler: Diplomacy, Deception, panache
- Fighter: Athletics, combat tactics
- Druid: Nature, animal handling
- Ranger: Survival, tracking

**Time Costs**: Vary the time investment:
- Quick: 1-3 actions (seconds)
- Short: 5-10 minutes (1 die to jar)
- Long: 20-30 minutes (2-3 dice to jar)

**Difficulty Levels**: Mix DC ranges:
- Easy: DC 15-16
- Moderate: DC 17-18
- Hard: DC 19-20
- Very Hard: DC 21-22

**Reward Types**: Offer different benefits:
- Dice removal from jar
- Time savings (avoid adding dice)
- Tactical advantages (surprise rounds, positioning)
- Resources (healing, equipment, information)
- Encounter avoidance

### Step-by-Step: Adding a New Event

1. **Choose a Category**: Decide if your event is an OPPORTUNITY, COMPLICATION, DILEMMA, or ACTIVE_THREAT

2. **Write the Description**: Create a vivid, self-contained scenario that doesn't assume unknown context

3. **Define the Mechanics**: Based on category:
   - OPPORTUNITY/COMPLICATION: Write challenge, success, and failure
   - DILEMMA: Write choice_a, choice_b, and optionally choice_c
   - ACTIVE_THREAT: Write immediate_action, success, and failure

4. **Set Spotlight and Skills**: Choose which classes shine and which skills apply

5. **Determine Time Cost**: How long does this take? Remember: 10 minutes = 1 die

6. **Write GM Notes**: Provide clear guidance on running the event and tracking consequences

7. **Add Optional Fields**: Include reward/consequence, threat_level, or context fields as appropriate

8. **Validate Your Event**: Check against the quality criteria above

9. **Add to JSON File**: Insert your event into the appropriate category array in `dungeon_turn_events.json`

10. **Test**: Run the generator and verify your event appears and works as intended

### Example: Creating a New OPPORTUNITY Event

Let's create a new event step-by-step:

**Step 1**: Category = OPPORTUNITY (positive encounter)

**Step 2**: Description = "You find a small alcove with ancient carvings. One carving glows faintly when you approach."

**Step 3**: Mechanics:
- Challenge: "DC 17 Arcana to understand the magic, DC 18 Religion to interpret the symbols"
- Success: "The carving grants a blessing: +1 to all saves for 1 hour."
- Failure: "The glow fades. You don't understand its purpose."

**Step 4**: Spotlight = ["Wizard", "Cleric"], Skills = ["Arcana", "Religion"]

**Step 5**: Time Cost = "5 minutes to study the carvings"

**Step 6**: GM Notes = "Blessing lasts 1 hour or until next rest. Stacks with other bonuses."

**Step 7**: Reward = "Temporary magical blessing"

**Step 8**: Validation:
- ✅ Works in any context
- ✅ Creates its own context (the alcove)
- ✅ Clear success/failure
- ✅ Rewards clever investigation
- ✅ Doesn't modify dungeon map

**Step 9**: Add to JSON:

```json
{
  "title": "Blessed Alcove",
  "description": "You find a small alcove with ancient carvings. One carving glows faintly when you approach.",
  "challenge": "DC 17 Arcana to understand the magic, DC 18 Religion to interpret the symbols",
  "success": "The carving grants a blessing: +1 to all saves for 1 hour.",
  "failure": "The glow fades. You don't understand its purpose.",
  "spotlight": ["Wizard", "Cleric"],
  "skills": ["Arcana", "Religion"],
  "time_cost": "5 minutes to study the carvings",
  "gm_notes": "Blessing lasts 1 hour or until next rest. Stacks with other bonuses.",
  "reward": "Temporary magical blessing"
}
```

**Step 10**: Test by running the generator and checking that the event can be selected.

## Technical Notes

### JSON Formatting
- Use 2-space indentation for readability
- Ensure all strings are properly quoted
- Escape special characters: `\"` for quotes, `\\` for backslashes
- Arrays use square brackets: `["item1", "item2"]`
- Objects use curly braces: `{"key": "value"}`

### File Location
The generator loads events from:
```
/Users/smoyes/Documents/p2emastercache/etc/dungeon_turn_events.json
```

### Validation
The generator validates that each event has:
- All required fields for its category
- Valid data types (strings, arrays, booleans)
- At least one spotlight class
- At least one skill
- Non-empty description and title

### Error Handling
If the JSON file is malformed or missing required fields, the generator will:
1. Display a clear error message
2. Indicate which event or field is problematic
3. Exit without generating encounters

Always validate your JSON after making changes!

## Troubleshooting

### Common Issues

**Issue**: Event never appears in game
- **Check**: Does it have overly restrictive context fields?
- **Solution**: Remove or broaden `required_spaces`, `requires_recent_combat`, or `requires_new_area`

**Issue**: Generator shows "Invalid JSON" error
- **Check**: Did you forget a comma, quote, or bracket?
- **Solution**: Use a JSON validator tool to find syntax errors

**Issue**: Generator shows "Missing required field" error
- **Check**: Does your event have all required fields for its category?
- **Solution**: Refer to the category-specific fields section above

**Issue**: Event appears but doesn't make sense in context
- **Check**: Does the description assume information not present?
- **Solution**: Rewrite to create its own context or use `required_spaces` to limit where it appears

**Issue**: Event feels too easy or too hard
- **Check**: Are your DCs appropriate for the party level?
- **Solution**: Use DC 15-18 for most events, DC 19-22 for challenging events

## Conclusion

This schema provides a flexible framework for creating engaging dungeon encounters. By following these guidelines, you can create events that:
- Integrate seamlessly with the existing system
- Provide meaningful choices and challenges
- Reward player creativity and skill
- Maintain narrative consistency
- Work reliably in any dungeon context

For questions or issues, refer to the design document at `.kiro/specs/dungeon-turn-event-refactor/design.md` or consult the requirements document at `.kiro/specs/dungeon-turn-event-refactor/requirements.md`.

Happy event crafting!
