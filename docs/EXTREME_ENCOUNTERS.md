# Extreme Encounter System

## Overview

The Dungeon Turn V2 system now scales combat difficulty based on dice rolls, making extreme rolls truly dangerous!

## Dice Sum Ranges

### Standard Combat (86-94)
- **Creature Level:** 2 levels below party
- **Difficulty:** Low threat
- **Description:** Standard encounters that are manageable for the party
- **Example:** Party level 4 faces level 2 creatures

### Dangerous Combat (95-99)
- **Creature Level:** At party level
- **Difficulty:** Moderate threat
- **Description:** Challenging encounters with creatures at the party's level
- **Example:** Party level 4 faces level 4 creatures
- **Warning:** ⚠️ Dangerous encounter - creatures at your level

### EXTREME Combat (100)
- **Creature Level:** At floor level
- **Difficulty:** DEADLY threat
- **Description:** Maximum danger! Creatures at the dungeon floor level
- **Example:** On Floor 7, party faces level 7 creatures regardless of party level
- **Warning:** 💀 EXTREME ENCOUNTER - Creatures at floor level!

## Floor Levels

Each floor of Gauntlight Keep has an associated danger level:

- **Floor 1:** Level 1 (Mitflits)
- **Floor 2:** Level 2 (Morlocks)
- **Floor 3:** Level 3 (Ghouls)
- **Floor 4:** Level 4 (Belcorra's servants)
- **Floor 5:** Level 5 (Arena creatures)
- **Floor 6:** Level 6 (Seugathi)
- **Floor 7:** Level 7 (Devils)
- **Floor 8:** Level 8 (Bog mummies)
- **Floor 9:** Level 9 (Drow/Urdefhan)
- **Floor 10:** Level 10 (Serpentfolk)

## Strategy Tips

### For Players
- **Low rolls (5-25):** Opportunities! Take advantage of them
- **Mid rolls (26-85):** Complications, dilemmas, and threats - stay alert
- **High rolls (86-94):** Standard combat - manageable
- **Very high rolls (95-99):** Dangerous combat - use tactics and resources
- **Maximum roll (100):** EXTREME - consider retreat, use all resources, or find creative solutions

### For GMs
- Extreme encounters (95-100) should feel genuinely dangerous
- A roll of 100 on Floor 7+ can be deadly for unprepared parties
- Use the tactical options and avoidable flags to give players choices
- Remember: not every encounter needs to be fought!

## Examples

### Example 1: Floor 1, Roll 88
- Category: COMBAT
- Creature Level: 2 (party level 4 - 2)
- Difficulty: Low threat
- Result: 2 Mitflits (level 2)

### Example 2: Floor 5, Roll 97
- Category: COMBAT
- Creature Level: 4 (party level)
- Difficulty: Moderate threat
- Result: 1 Arena creature at party level
- Warning: ⚠️ Dangerous encounter

### Example 3: Floor 7, Roll 100
- Category: COMBAT
- Creature Level: 7 (floor level!)
- Difficulty: DEADLY
- Result: 1-3 Devils at level 7
- Warning: 💀 EXTREME ENCOUNTER - Creatures at floor level!

## Design Philosophy

The extreme encounter system creates:
- **Tension:** High rolls mean real danger
- **Choices:** Players can often avoid or prepare for encounters
- **Scaling:** Deeper floors become progressively more dangerous
- **Excitement:** Rolling 100 is memorable and dramatic
- **Balance:** Most encounters (86-94) remain manageable

## Technical Details

The system is implemented in `bin/generators/generate_dungeon_turn_v2.py`:

```python
if dice_sum == 100:
    target_level = floor_num  # Floor level
    difficulty = "DEADLY (Floor Level)"
elif dice_sum >= 95:
    target_level = party_level  # Party level
    difficulty = "Moderate (Party Level)"
else:
    target_level = max(1, party_level - 2)  # 2 below party
    difficulty = "Low (2 levels below party)"
```

The web interface displays difficulty warnings prominently with color coding:
- Red background + 💀 for roll of 100
- Orange background + ⚠️ for rolls 95-99
- Gray background + ⚔️ for rolls 86-94
