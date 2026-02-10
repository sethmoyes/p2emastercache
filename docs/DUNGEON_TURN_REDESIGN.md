# Dungeon Turn System Redesign - Brainstorming Document

## THE PROBLEM
Players are exhausted, paranoid, and bored. They:
- Only use Detect Magic and Listen at doors
- Close doors on monsters and walk away
- Have no time pressure or urgency
- Don't engage with the dungeon creatively
- Find exploration tedious (detect, search, fight, repeat)

## THE GOAL
Make the dungeon **FUN** by:
1. **Creating tension** - Every 10 minutes matters
2. **Rewarding creativity** - Use ALL those Pathfinder 2e actions
3. **Forcing meaningful choices** - Trade-offs with real consequences
4. **Showing living dungeon** - Monsters have lives, not just waiting
5. **Draining resources** - Without TPK or bogging down gameplay

## PARTY COMPOSITION
- **Cleric** - Healing, Religion, Medicine, Diplomacy
- **Wizard** - Arcana, Recall Knowledge, utility spells
- **Rogue** - Thievery, Stealth, Acrobatics, Deception
- **Swashbuckler** - Acrobatics, Deception, Performance, Intimidation
- **Monk** - Athletics, Acrobatics, Perception, unarmed combat

## NEW PROBABILITY DISTRIBUTION (50/50 Combat vs Non-Combat)

### 5d20 Sum Distribution:
- **5-25 (21 sums):** OPPORTUNITIES - Reward creativity, shortcuts, intel
- **26-45 (20 sums):** COMPLICATIONS - Force skill use, environmental puzzles
- **46-65 (20 sums):** DILEMMAS - Meaningful choices with trade-offs
- **66-85 (20 sums):** ACTIVE THREATS - Immediate danger, patrols, alarms
- **86-100 (15 sums):** COMBAT ENCOUNTERS - Actual fights

**Total:** 96 possible sums per floor
**Combat:** 86-100 = 15 sums = ~16% pure combat
**Active Threats:** 66-85 = 20 sums = ~21% (can become combat)
**Combined Combat Potential:** ~37% (close to 50/50 with player choices)

## EVENT CATEGORIES

### 1. OPPORTUNITIES (5-25) - Reward Creativity
**Goal:** Make players feel smart for using skills besides Detect Magic

**Examples:**
- **Secret Passages** (Perception) - Shortcut saves 30 minutes
- **Eavesdropping** (Stealth + Society) - Learn enemy patrol schedule
- **Abandoned Supplies** (Medicine) - Quick heal but takes 10 min
- **Friendly NPC** (Diplomacy) - Information about upcoming dangers
- **Environmental Advantage** (Crafting) - Oil to spill, rope to rig trap
- **Magical Residue** (Arcana) - Identify recent spell, predict danger
- **Tracks** (Survival) - Know what's ahead, prepare accordingly
- **Architectural Weakness** (Crafting) - Collapse passage behind you
- **Ancient Inscription** (Society/Religion) - Reveals safe path
- **Distracted Guards** (Deception) - Sneak past without fighting

**Spotlight:**
- Rogue: Stealth, Thievery, Deception
- Wizard: Arcana, Recall Knowledge
- Cleric: Religion, Medicine, Diplomacy
- Swashbuckler: Deception, Performance
- Monk: Perception, Athletics

### 2. COMPLICATIONS (26-45) - Force Skill Use
**Goal:** Create problems that REQUIRE actions besides combat

**Examples:**
- **Locked Door** (Thievery or Athletics) - Can't progress without solving
- **Unstable Floor** (Acrobatics or Crafting) - Cross carefully or fall
- **Magical Ward** (Arcana or Thievery) - Disable or trigger alarm
- **Language Barrier** (Society) - NPC has info but doesn't speak Common
- **Tracking Challenge** (Survival) - Follow fleeing enemy or lose them
- **Poisoned Air** (Nature or Medicine) - Identify antidote or suffer
- **Collapsing Ceiling** (Athletics) - Hold it up while others escape
- **Puzzle Lock** (Crafting or Arcana) - Mechanical or magical solution
- **Intimidating Presence** (Diplomacy or Intimidation) - Talk down hostile
- **Performance Required** (Performance) - Convince guards you belong

**Spotlight:**
- Rogue: Thievery, Acrobatics
- Wizard: Arcana, Recall Knowledge
- Cleric: Medicine, Diplomacy
- Swashbuckler: Acrobatics, Performance, Intimidation
- Monk: Athletics, Acrobatics

### 3. DILEMMAS (46-65) - Meaningful Choices
**Goal:** Force trade-offs where every choice has consequences

**Examples:**
- **Loud vs Quiet Path** - Fast (10 min) but risky vs Slow (30 min) but safe
- **Help Prisoner** - Free now (loud, 10 min) vs Come back (might die)
- **Fight or Avoid** - Combat now (fresh) vs Sneak (they reinforce later)
- **Rest Here** - Recover (risky ambush) vs Push on (exhausted)
- **Loot Now** - Take time (10 min) vs Mark for later (might be gone)
- **Chase Fleeing Enemy** - Stop alarm (encounter now) vs Let go (harder later)
- **Ritual in Progress** - Interrupt (surprise) vs Wait (learn more, they complete)
- **Wounded Ally** - Treat Wounds (10 min, add die) vs Push on (bleeding)
- **Alarm Triggered** - Disable (Thievery, risky) vs Flee (reinforcements)
- **Treasure vs Time** - Investigate (10 min) vs Ignore (miss loot)

**Key:** Every choice costs TIME (adds dice to jar) or RESOURCES (HP, spells, items)

### 4. ACTIVE THREATS (66-85) - Immediate Danger
**Goal:** Create urgency and force immediate action

**Examples:**
- **Patrol Approaching** - "You hear guards. 1 round to hide/prepare/flee"
- **Trap Triggering** - "Floor collapsing! Athletics/Acrobatics NOW"
- **Alarm Going Off** - "Bell ringing! Disable or face reinforcements"
- **Fire Spreading** - "Smoke filling room. Con save each turn you stay"
- **Ambush** - "Enemies drop from ceiling! Roll initiative"
- **Magical Backlash** - "Ward exploding! Reflex save or take damage"
- **Falling Debris** - "Ceiling crumbling! Move or be crushed"
- **Poison Gas** - "Green mist seeping in! Nature to identify, Medicine to treat"
- **Flooding** - "Water rising! Athletics to swim or find exit"
- **Summoning Circle** - "Ritual completing! Stop it or face demon"

**Key:** These demand IMMEDIATE response, no time to deliberate

### 5. COMBAT ENCOUNTERS (86-100) - Actual Fights
**Goal:** Resource-draining fights, never bosses, show dungeon ecology

**Examples:**
- **Wandering Patrol** - 2-3 creatures below party level
- **Feeding Time** - Monsters eating, distracted (surprise round)
- **Territorial Dispute** - Two monster groups fighting each other
- **Scavengers** - Creatures picking over old battlefield
- **Nest Defense** - Protecting young (flee if hurt badly)
- **Hunting Party** - Tracking prey (players or other monsters)
- **Guard Post** - Stationed creatures, can be avoided with Stealth
- **Rival Adventurers** - Can negotiate, fight, or avoid
- **Escaped Experiment** - Wounded, dangerous, unpredictable
- **Undead Patrol** - Mindless, predictable patterns

**Key:** 
- Never bosses or mini-bosses
- 2 levels below party (resource drain, not deadly)
- Show monsters LIVING (eating, fighting, sleeping)
- Can often be avoided with creativity

## DUNGEON ECOLOGY EVENTS

**Goal:** Show monsters as living creatures with needs, not just combat encounters

### Monsters Eating
- Ghouls feasting on morlock corpse (distracted, surprise round)
- Mitflits arguing over shiny button
- Urdefhan roasting cave fish over fire
- Seugathi dissecting failed experiment

### Monsters Fighting Each Other
- Morlocks vs Ghouls territorial dispute
- Mitflits fleeing from web lurker
- Urdefhan hunting caligni
- Two monster groups you can pit against each other

### Monsters Sleeping/Resting
- Exhausted patrol sleeping (sneak past or ambush)
- Creatures in torpor (cold-blooded)
- Nocturnal monsters sleeping during "day"
- Wounded creature hiding and healing

### Monsters Communicating
- Ghouls discussing "Ghost Queen" return
- Mitflits planning Otari invasion
- Seugathi taking notes on experiments
- Urdefhan war chants

### Monsters Working
- Morlocks hauling supplies
- Ghouls copying books
- Seugathi conducting experiments
- Devils maintaining prison

## FLOOR-SPECIFIC THEMES

### Floor 1: Mitflit Chaos
- Mitflits everywhere, worshipping rusty helmet
- Boss Skrawng's giant maggot plans
- Crumbling surface level, fog, lighthouse pulse
- Basic undead shambling

### Floor 2: Morlock Territory
- King Graulgust's domain
- Recent occupation (2 years)
- Moldy, musty, echoing
- Evidence of Cult of Canker defeat

### Floor 3: Ghoul Library
- Cult of the Canker endless loop
- Collecting flesh, eating flesh
- Scholarly corruption
- Nhakazarin's necromancy

### Floor 4: Belcorra's Personal Space
- Volluk's leech-form
- Voidglutton (EXTREME - flee!)
- Lasda imprisoned
- Jaul Mezmin werewolf

### Floor 5: The Arena
- Blood-soaked sand
- Beast cages
- Cratonys (feral velstrac)
- Fleshwarped experiments

### Floor 6: Fleshwarping Labs
- Seugathi experiments
- Jafaki's living flesh golem
- Shadow Malice band prisoners
- Clinical horror

### Floor 7: Mini-Hell
- Urevian's devil prison
- Ysondkhelir (Denizen of Leng)
- Infernal heat, brimstone
- Rajani soul contract

### Floor 8: The Farm
- Bog mummies (Children of Belcorra)
- Urthagul with Crimson Lens
- Caligni cult
- Lazy naga

### Floor 9: Darklands Caverns
- Drow Yldaris settlement
- Urdefhan war camp (Khurfel)
- Caligni refugees
- Wild Darklands fauna

### Floor 10: Empty Vault
- Belcorra's ghost (EXTREME)
- Ancient serpentfolk temple
- Nhimbaloth's presence
- Reality warping

## SKILLS TO SPOTLIGHT

### Currently UNUSED (Priority to reward):
- **Acrobatics** - Balance, tumble, squeeze
- **Athletics** - Climb, force open, grapple, swim
- **Crafting** - Repair, create, identify
- **Deception** - Lie, create diversion, feint
- **Diplomacy** - Make impression, request, gather info
- **Intimidation** - Coerce, demoralize
- **Nature** - Identify plants, animals, weather
- **Performance** - Act, play instrument, impersonate
- **Society** - Recall knowledge (humanoids), decipher writing
- **Survival** - Track, subsist, sense direction

### Currently OVERUSED (Still include but balance):
- **Arcana** - Detect Magic (they spam this)
- **Perception** - Listen at doors (they spam this)

## RESOURCE DRAIN PHILOSOPHY

**Goal:** Drain resources WITHOUT TPK or bogging down gameplay

### What to Drain:
- **HP** - Minor damage (1d6-2d6), forces healing
- **Spell Slots** - Situations requiring magic solutions
- **Focus Points** - Frequent small challenges
- **Time** - Every 10 minutes = 1 die in jar
- **Consumables** - Potions, scrolls, tools
- **Action Economy** - Conditions (frightened, sickened, etc.)

### What NOT to Drain:
- **Lives** - No TPK encounters
- **Morale** - Keep it fun, not punishing
- **Patience** - Quick resolution, not bogged down

### Encounter Difficulty:
- **Combat:** 2 levels below party (Trivial to Low)
- **Hazards:** Party level -2 to -1
- **Skill DCs:** Standard for level (14-20 range for level 4)

## CASCADING CONSEQUENCES

**Simple System:** Track player choices, reference later

### Examples:
- **Scared off Mitflits** → They return with reinforcements (2 encounters later)
- **Freed prisoner** → They help in later fight OR betray you
- **Triggered alarm** → Next patrol is alert and prepared
- **Avoided combat** → Those enemies reinforce later encounter
- **Made noise** → Next encounter has surprise round against you
- **Helped NPC** → They provide info or assistance later
- **Stole from monsters** → They hunt you specifically
- **Destroyed nest** → Parents return and track you

### Implementation:
- **Simple flags in events:** "If players chose X, add Y to next encounter"
- **GM notes:** "Mark this if players [action]. Reference in event #X"
- **No complex coding:** Just narrative suggestions for GM

## CODING APPROACH

### New Script: `bin/generators/generate_dungeon_turn_v2.py`

**Features:**
1. Load gauntlight_keep_levels.md for floor themes
2. Load creatures.json for specific monsters
3. Load dungeon_flavor_events.json for atmospheric details
4. Generate 96 events per floor (sums 5-100)
5. Map to new probability distribution
6. Include GM notes for cascading consequences
7. Spotlight different party members
8. Show dungeon ecology

**Event Structure:**
```python
{
    "sum": 42,
    "category": "COMPLICATION",
    "title": "Locked Iron Door",
    "description": "A heavy iron door blocks the passage. You hear movement beyond.",
    "challenge": "DC 18 Thievery to pick lock OR DC 20 Athletics to force open",
    "success": "Door opens quietly (Thievery) or loudly (Athletics - add 'noise' flag)",
    "failure": "Lock jams (Thievery) or door holds (Athletics). Try different approach or find key.",
    "spotlight": ["Rogue", "Monk"],
    "skills": ["Thievery", "Athletics"],
    "time_cost": "1 action (Thievery) or 2 actions (Athletics)",
    "gm_notes": "If forced open loudly, next encounter has surprise round against party",
    "ecology": "Morlocks use this door frequently - fresh scratches on handle",
    "floor_specific": "King Graulgust's territory - his symbol carved above door"
}
```

### Generation Logic:
1. **Determine category** from sum (5-25 = Opportunity, etc.)
2. **Select floor theme** from gauntlight_keep_levels.md
3. **Choose appropriate creatures** from creatures.json (2 levels below party)
4. **Add atmospheric details** from dungeon_flavor_events.json
5. **Spotlight party member** (rotate through Cleric, Wizard, Rogue, Swashbuckler, Monk)
6. **Include skill challenges** (prioritize unused skills)
7. **Add GM notes** for consequences
8. **Show dungeon ecology** (monsters living, not waiting)

## NEXT STEPS

1. **Review this document** - Does this solve the problem?
2. **Adjust probabilities** - Is 50/50 combat right?
3. **Create event templates** - 20-30 templates per category
4. **Code the generator** - New script with new logic
5. **Test with party** - See if it creates tension and fun
6. **Iterate** - Adjust based on actual play

## QUESTIONS FOR YOU

1. **Probability distribution** - Happy with 5-25, 26-45, 46-65, 66-85, 86-100?
2. **Cascading consequences** - Simple GM notes or try to code it?
3. **Dungeon ecology** - How much detail? Every event or just some?
4. **Skill spotlight** - Rotate evenly or weight toward unused skills?
5. **Time pressure** - Should some events add MULTIPLE dice to jar?
6. **Deadly encounters** - Any situations where TPK is possible?
7. **Boss encounters** - Should dice jar ever trigger boss fights?
8. **Faction awareness** - Should monsters learn about party and adapt?

## SUCCESS METRICS

**How do we know this works?**
- Players use skills besides Detect Magic and Listen
- Players engage with encounters creatively
- Players feel time pressure (dice jar filling)
- Players make meaningful choices (not obvious best option)
- Dungeon feels alive (monsters have lives)
- Combat is 50% of encounters (not 90%)
- Players have FUN (not tedious or frustrating)

---

**Ready to code when you give the green light!**
