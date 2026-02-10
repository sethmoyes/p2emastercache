#!/usr/bin/env python3
"""
Dungeon Turn Encounter Generator V2 - The Fun Version!

Creates tension, rewards creativity, and makes the dungeon feel ALIVE.
50/50 combat vs non-combat split with meaningful choices.

New probability distribution:
- 5-25: OPPORTUNITIES (reward creativity)
- 26-45: COMPLICATIONS (force skill use)
- 46-65: DILEMMAS (meaningful choices)
- 66-85: ACTIVE THREATS (immediate danger)
- 86-100: COMBAT (actual fights)
"""

import random
import sys
import json
import re

def load_json(filename):
    """Load JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_markdown(filename):
    """Load markdown file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def parse_gauntlight_levels(content):
    """Parse gauntlight_keep_levels.md to extract floor information"""
    levels = {}
    
    # Extract each level section
    level_pattern = r'### Level (\d+): (.+?)\n(.*?)(?=### Level|\n---|\Z)'
    matches = re.finditer(level_pattern, content, re.DOTALL)
    
    for match in matches:
        level_num = int(match.group(1))
        level_name = match.group(2).strip()
        level_content = match.group(3).strip()
        
        # Extract theme
        theme_match = re.search(r'\*\*Theme:\*\* (.+)', level_content)
        theme = theme_match.group(1) if theme_match else ""
        
        # Extract threats
        threats = []
        threats_section = re.search(r'\*\*Threats:\*\* (.+)', level_content)
        if threats_section:
            threats = [t.strip() for t in threats_section.group(1).split(',')]
        
        levels[level_num] = {
            'name': level_name,
            'theme': theme,
            'threats': threats,
            'content': level_content
        }
    
    return levels

def get_category_from_sum(total):
    """Determine event category based on 5d20 sum"""
    if total <= 25:
        return "OPPORTUNITY"
    elif total <= 45:
        return "COMPLICATION"
    elif total <= 65:
        return "DILEMMA"
    elif total <= 85:
        return "ACTIVE_THREAT"
    else:
        return "COMBAT"


def get_party_member_spotlight():
    """Rotate through party members to spotlight"""
    return random.choice([
        {"class": "Cleric", "skills": ["Religion", "Medicine", "Diplomacy"]},
        {"class": "Wizard", "skills": ["Arcana", "Recall Knowledge", "Society"]},
        {"class": "Rogue", "skills": ["Thievery", "Stealth", "Acrobatics", "Deception"]},
        {"class": "Swashbuckler", "skills": ["Acrobatics", "Deception", "Performance", "Intimidation"]},
        {"class": "Monk", "skills": ["Athletics", "Acrobatics", "Perception"]}
    ])

def get_creatures_for_floor(creatures, floor_num, party_level):
    """Get appropriate creatures for this floor (2 levels below party)"""
    target_level = max(1, party_level - 2)
    
    # Filter creatures by level
    appropriate = [c for c in creatures if c['level'] == target_level]
    
    return appropriate if appropriate else creatures

# OPPORTUNITY EVENT TEMPLATES (5-25)
OPPORTUNITY_TEMPLATES = [
    {
        "title": "Secret Passage",
        "description": "You notice unusual wear patterns on the floor leading to a wall section.",
        "challenge": "DC 18 Perception to find hidden door",
        "success": "You discover a secret passage that bypasses the next 3 rooms. Saves 30 minutes of exploration.",
        "failure": "You don't find anything unusual. Continue the normal way.",
        "spotlight": ["Rogue", "Monk"],
        "skills": ["Perception"],
        "time_cost": "1 action to search",
        "gm_notes": "If found, skip next 3 dice jar rolls. Mark on map.",
        "reward": "Shortcut, time saved, avoid encounters"
    },
    {
        "title": "Eavesdropping Opportunity",
        "description": "You hear voices ahead - creatures discussing their patrol route.",
        "challenge": "DC 16 Stealth to get close, DC 18 Society to understand their language",
        "success": "You learn the patrol schedule: they pass through here every 2 hours. You know when it's safe.",
        "failure": "You make noise and alert them, or can't understand their language.",
        "spotlight": ["Rogue", "Wizard"],
        "skills": ["Stealth", "Society"],
        "time_cost": "10 minutes to listen carefully",
        "gm_notes": "If successful, next 2 encounters can be avoided with timing. Add 1 die to jar for time spent.",
        "reward": "Intelligence, tactical advantage"
    },

    {
        "title": "Abandoned Supplies",
        "description": "You find a cache of supplies left by previous explorers - bandages, healing herbs, and rations.",
        "challenge": "DC 16 Medicine to use supplies effectively",
        "success": "Each party member can heal 2d8 HP. Takes 10 minutes.",
        "failure": "Supplies are too old or damaged. Heal only 1d8 HP.",
        "spotlight": ["Cleric"],
        "skills": ["Medicine"],
        "time_cost": "10 minutes to treat wounds",
        "gm_notes": "Add 1 die to jar for time spent. Good reward for exploration.",
        "reward": "Healing without spell slots"
    },
    {
        "title": "Friendly Ghost",
        "description": "A translucent figure appears - a former servant who died here centuries ago. They seem willing to talk.",
        "challenge": "DC 15 Diplomacy to gain trust, DC 18 Religion to understand their nature",
        "success": "The ghost warns you about a trap ahead and tells you how to disarm it safely.",
        "failure": "The ghost fades away, frightened or offended.",
        "spotlight": ["Cleric", "Swashbuckler"],
        "skills": ["Diplomacy", "Religion"],
        "time_cost": "5 minutes of conversation",
        "gm_notes": "If successful, next trap is automatically disarmed or avoided.",
        "reward": "Information, trap avoidance"
    },
    {
        "title": "Environmental Advantage",
        "description": "You spot a chandelier above a narrow passage, and barrels of oil nearby.",
        "challenge": "DC 16 Crafting to rig a trap, DC 18 Athletics to position it correctly",
        "success": "You create a trap. Next enemy encounter triggers it for 3d6 fire damage to all enemies.",
        "failure": "Trap is poorly made and won't trigger reliably.",
        "spotlight": ["Rogue", "Monk"],
        "skills": ["Crafting", "Athletics"],
        "time_cost": "10 minutes to set up",
        "gm_notes": "Add 1 die to jar. Mark trap on map. Triggers on next combat encounter.",
        "reward": "Tactical advantage in combat"
    },

    {
        "title": "Magical Residue",
        "description": "The air shimmers with recent magical energy. Someone cast powerful magic here recently.",
        "challenge": "DC 18 Arcana to identify the spell and its purpose",
        "success": "You identify a teleportation spell. Someone left in a hurry. You know danger is ahead.",
        "failure": "The magical signature is too complex to decipher.",
        "spotlight": ["Wizard"],
        "skills": ["Arcana"],
        "time_cost": "1 action to analyze",
        "gm_notes": "If successful, players know next encounter is dangerous. Can prepare accordingly.",
        "reward": "Forewarning, preparation time"
    },
    {
        "title": "Fresh Tracks",
        "description": "You find fresh tracks in the dust - multiple creatures passed through here recently.",
        "challenge": "DC 17 Survival to identify creatures and direction",
        "success": "You identify the creatures and know they went ahead. You can avoid or ambush them.",
        "failure": "Tracks are too muddled to read clearly.",
        "spotlight": ["Rogue", "Monk"],
        "skills": ["Survival"],
        "time_cost": "1 action to examine",
        "gm_notes": "If successful, next encounter can be avoided or players get surprise round.",
        "reward": "Tactical choice, surprise advantage"
    },
    {
        "title": "Architectural Weakness",
        "description": "You notice the ceiling here is unstable - old damage from past battles.",
        "challenge": "DC 18 Crafting to identify weak points, DC 16 Athletics to trigger collapse safely",
        "success": "You can collapse this passage behind you, blocking pursuit. Or save for later.",
        "failure": "The structure is more stable than it looks.",
        "spotlight": ["Rogue", "Monk"],
        "skills": ["Crafting", "Athletics"],
        "time_cost": "2 actions to trigger if used",
        "gm_notes": "If used, blocks passage. Pursuing enemies must find another route (buys time).",
        "reward": "Escape option, tactical control"
    },
    {
        "title": "Ancient Inscription",
        "description": "Carved into the wall is text in an ancient language, partially worn away.",
        "challenge": "DC 19 Society to translate, DC 17 Religion if it's religious text",
        "success": "The inscription warns: 'The left path leads to the arena. The right to the laboratories.' You know where you're going.",
        "failure": "The text is too damaged to read fully.",
        "spotlight": ["Wizard", "Cleric"],
        "skills": ["Society", "Religion"],
        "time_cost": "5 minutes to study and translate",
        "gm_notes": "Provides map knowledge. Players can choose their path wisely.",
        "reward": "Navigation, informed choices"
    },

    {
        "title": "Distracted Guards",
        "description": "Two guards ahead are arguing loudly about something. They're completely focused on each other.",
        "challenge": "DC 15 Stealth to sneak past, or DC 17 Deception to join their argument and distract them further",
        "success": "You slip past unnoticed or convince them to leave their post to 'check something'.",
        "failure": "They notice you. Roll initiative.",
        "spotlight": ["Rogue", "Swashbuckler"],
        "skills": ["Stealth", "Deception"],
        "time_cost": "1 action to sneak, 5 minutes to deceive",
        "gm_notes": "Avoids combat encounter. If deception used, guards leave post for 30 minutes.",
        "reward": "Avoid combat, save resources"
    }
]

# COMPLICATION EVENT TEMPLATES (26-45)
COMPLICATION_TEMPLATES = [
    {
        "title": "Locked Iron Door",
        "description": "A heavy iron door blocks the passage. The lock is complex but functional.",
        "challenge": "DC 18 Thievery to pick lock OR DC 22 Athletics to force open",
        "success": "Door opens. Quietly if picked, loudly if forced.",
        "failure": "Lock jams (Thievery) or door holds (Athletics). Must find key or try different approach.",
        "spotlight": ["Rogue", "Monk"],
        "skills": ["Thievery", "Athletics"],
        "time_cost": "2 actions (Thievery) or 3 actions (Athletics)",
        "gm_notes": "If forced open, next encounter has surprise round against party (noise alert).",
        "consequence": "Noise attracts attention"
    },
    {
        "title": "Unstable Floor",
        "description": "The floor ahead is cracked and unstable. You hear creaking with each step.",
        "challenge": "DC 17 Acrobatics to cross carefully OR DC 19 Crafting to brace the floor",
        "success": "Everyone crosses safely. Crafting solution is permanent.",
        "failure": "Floor collapses. Everyone makes DC 18 Reflex save or falls 10 feet (2d6 damage).",
        "spotlight": ["Swashbuckler", "Rogue"],
        "skills": ["Acrobatics", "Crafting"],
        "time_cost": "1 action per person (Acrobatics) or 10 minutes (Crafting)",
        "gm_notes": "Crafting takes time but helps on return trip. Acrobatics is faster but risky.",
        "consequence": "Falling damage, noise"
    },

    {
        "title": "Magical Ward",
        "description": "A glowing sigil blocks the doorway. Touching it would trigger an alarm.",
        "challenge": "DC 19 Arcana to dispel OR DC 20 Thievery to disable the physical trigger",
        "success": "Ward is disabled. You can pass safely.",
        "failure": "Ward triggers! Alarm sounds throughout this floor. All encounters are now alert.",
        "spotlight": ["Wizard", "Rogue"],
        "skills": ["Arcana", "Thievery"],
        "time_cost": "3 actions to attempt",
        "gm_notes": "If failed, all remaining encounters on this floor get surprise round against party.",
        "consequence": "Dungeon-wide alert"
    },
    {
        "title": "Language Barrier",
        "description": "A wounded creature begs for help in a language you don't recognize. They seem to have important information.",
        "challenge": "DC 18 Society to identify language and communicate OR DC 16 Diplomacy with gestures",
        "success": "They warn you about an ambush ahead and tell you the safe route.",
        "failure": "You can't communicate. They flee in fear or frustration.",
        "spotlight": ["Wizard", "Cleric"],
        "skills": ["Society", "Diplomacy"],
        "time_cost": "5 minutes to communicate",
        "gm_notes": "If successful, next encounter can be avoided entirely. Creature may become ally.",
        "consequence": "Missed information"
    },
    {
        "title": "Tracking Challenge",
        "description": "An enemy fled this way, leaving a blood trail. They're wounded and know you're coming.",
        "challenge": "DC 17 Survival to track quickly and quietly",
        "success": "You find them before they can alert others. Surprise round.",
        "failure": "You lose the trail, or they hear you coming and prepare an ambush.",
        "spotlight": ["Rogue", "Monk"],
        "skills": ["Survival"],
        "time_cost": "10 minutes to track carefully",
        "gm_notes": "Success = surprise round for party. Failure = surprise round for enemy. Add 1 die to jar.",
        "consequence": "Enemy reinforcements"
    },

    {
        "title": "Poisoned Air",
        "description": "Green mist seeps from cracks in the walls. The smell is acrid and burning.",
        "challenge": "DC 18 Nature to identify poison and find antidote plants nearby OR DC 19 Medicine to treat symptoms",
        "success": "You neutralize the poison or treat everyone. Can pass safely.",
        "failure": "Everyone makes DC 17 Fortitude save or become sickened 1 for 1 hour.",
        "spotlight": ["Cleric", "Wizard"],
        "skills": ["Nature", "Medicine"],
        "time_cost": "10 minutes to treat everyone",
        "gm_notes": "Sickened 1 = -1 to all checks. Significantly weakens party. Add 1 die to jar for treatment time.",
        "consequence": "Condition penalty"
    },
    {
        "title": "Collapsing Ceiling",
        "description": "Cracks spread across the ceiling. Debris falls. It's going to collapse!",
        "challenge": "DC 19 Athletics to brace ceiling while others escape OR DC 18 Acrobatics to dodge falling debris",
        "success": "Everyone escapes safely. If braced, passage remains open.",
        "failure": "Everyone makes DC 18 Reflex save or takes 3d6 bludgeoning damage. Passage collapses.",
        "spotlight": ["Monk", "Swashbuckler"],
        "skills": ["Athletics", "Acrobatics"],
        "time_cost": "1 round of actions",
        "gm_notes": "If passage collapses, must find alternate route (adds 30 minutes = 3 dice to jar).",
        "consequence": "Damage, blocked passage"
    },
    {
        "title": "Puzzle Lock",
        "description": "The door has a complex mechanical puzzle lock - gears, levers, and symbols.",
        "challenge": "DC 19 Crafting to solve mechanically OR DC 20 Arcana if it has magical components",
        "success": "Lock opens. You can pass through.",
        "failure": "Lock remains sealed. Must find another way or the key.",
        "spotlight": ["Rogue", "Wizard"],
        "skills": ["Crafting", "Arcana"],
        "time_cost": "10 minutes to solve",
        "gm_notes": "Add 1 die to jar for time spent. Alternative: find key elsewhere in dungeon.",
        "consequence": "Time spent, alternate route needed"
    },
    {
        "title": "Intimidating Presence",
        "description": "A powerful creature blocks the path. They're not immediately hostile, but wary and aggressive.",
        "challenge": "DC 18 Diplomacy to negotiate passage OR DC 19 Intimidation to make them back down",
        "success": "They let you pass. May even provide information if Diplomacy used.",
        "failure": "They attack. Roll initiative.",
        "spotlight": ["Cleric", "Swashbuckler"],
        "skills": ["Diplomacy", "Intimidation"],
        "time_cost": "5 minutes of negotiation",
        "gm_notes": "Avoids combat if successful. Diplomacy may turn them into ally. Intimidation makes them hostile later.",
        "consequence": "Combat or future hostility"
    },

    {
        "title": "Performance Required",
        "description": "Guards ahead are bored and looking for entertainment. They challenge you to prove you're 'worthy' to pass.",
        "challenge": "DC 17 Performance to entertain them OR DC 18 Deception to pretend you're expected guests",
        "success": "They let you pass, laughing or convinced. May even give you information.",
        "failure": "They're offended or suspicious. Roll initiative.",
        "spotlight": ["Swashbuckler", "Rogue"],
        "skills": ["Performance", "Deception"],
        "time_cost": "5 minutes of performance/deception",
        "gm_notes": "Creative solution to avoid combat. Rewards social skills in dungeon.",
        "consequence": "Combat if failed"
    }
]

# DILEMMA EVENT TEMPLATES (46-65)
DILEMMA_TEMPLATES = [
    {
        "title": "Two Paths: Loud vs Quiet",
        "description": "The passage splits. Left: a wide, clear corridor (fast but exposed). Right: narrow maintenance tunnels (slow but hidden).",
        "choice_a": "Take the loud path: 10 minutes, but next encounter is alerted to your presence",
        "choice_b": "Take the quiet path: 30 minutes (add 2 dice to jar), but next encounter doesn't know you're coming",
        "spotlight": ["All"],
        "skills": ["Tactical thinking"],
        "time_cost": "10 min vs 30 min",
        "gm_notes": "Track choice. Loud path = enemies get surprise round. Quiet path = party gets surprise round.",
        "consequence": "Time vs stealth trade-off"
    },
    {
        "title": "Imprisoned Creature",
        "description": "A creature is locked in a cage, begging for freedom. They claim they were captured unjustly and will help you.",
        "choice_a": "Free them now: Takes 10 minutes (add 1 die), makes noise, but gain potential ally",
        "choice_b": "Come back later: Mark location, but they might be dead or moved when you return",
        "choice_c": "Leave them: No time cost, no risk, but no ally and they might alert enemies",
        "spotlight": ["Cleric", "Rogue"],
        "skills": ["Thievery", "Diplomacy"],
        "time_cost": "10 min to free, or none",
        "gm_notes": "If freed: 50% chance they help in next combat, 50% they flee. If left: they alert enemies.",
        "consequence": "Moral choice with tactical implications"
    },

    {
        "title": "Fight Now or Avoid",
        "description": "You spot a patrol ahead. They haven't seen you yet. You're at full strength.",
        "choice_a": "Fight now: Combat while you're fresh and they're unprepared (surprise round)",
        "choice_b": "Sneak past: DC 17 Stealth. Success = avoid combat. Failure = they join next encounter as reinforcements",
        "spotlight": ["Rogue", "All"],
        "skills": ["Stealth", "Tactics"],
        "time_cost": "Combat time vs 1 action",
        "gm_notes": "If avoided and Stealth fails, add these enemies to next combat encounter (harder fight).",
        "consequence": "Fight now vs potentially harder fight later"
    },
    {
        "title": "Rest Here or Push On",
        "description": "You find a defensible room. You're wounded and low on resources. But resting here is risky.",
        "choice_a": "Rest here: 10 minutes to Treat Wounds (add 1 die to jar). DC 15 Perception to avoid ambush during rest.",
        "choice_b": "Push on: No healing, but no risk of ambush. Continue while wounded.",
        "spotlight": ["Cleric", "All"],
        "skills": ["Medicine", "Perception"],
        "time_cost": "10 min to rest",
        "gm_notes": "If rest and fail Perception: ambush during rest (party is flat-footed). If push on: next combat is harder.",
        "consequence": "Risk vs reward for healing"
    },
    {
        "title": "Loot Now or Later",
        "description": "You find a treasure room, but it will take time to search thoroughly. You hear movement nearby.",
        "choice_a": "Loot now: 10 minutes (add 1 die to jar). Roll on treasure table. But enemies might arrive.",
        "choice_b": "Mark for later: No time cost now, but treasure might be gone when you return (50% chance).",
        "spotlight": ["Rogue", "All"],
        "skills": ["Perception", "Thievery"],
        "time_cost": "10 min to loot",
        "gm_notes": "If loot now: roll dice jar immediately after. If mark for later: 50% chance treasure is gone.",
        "consequence": "Greed vs caution"
    },
    {
        "title": "Chase Fleeing Enemy",
        "description": "You wounded an enemy and they're fleeing. They're heading toward their allies to raise the alarm.",
        "choice_a": "Chase them: Pursue and fight now (1 enemy, but you're split from party)",
        "choice_b": "Let them go: They alert others. Next encounter has +2 enemies and they're prepared.",
        "spotlight": ["Monk", "Rogue"],
        "skills": ["Athletics", "Tactics"],
        "time_cost": "Immediate decision",
        "gm_notes": "If chase: solo combat for fastest PC. If let go: next encounter is significantly harder.",
        "consequence": "Risk one PC vs harder group fight"
    },

    {
        "title": "Ritual in Progress",
        "description": "Through a doorway, you see creatures performing a ritual. It's almost complete.",
        "choice_a": "Interrupt now: Surprise round, but you don't know what the ritual does",
        "choice_b": "Watch and learn: DC 19 Arcana to understand ritual. Takes 5 minutes. They complete it but you know what to expect.",
        "spotlight": ["Wizard", "All"],
        "skills": ["Arcana", "Tactics"],
        "time_cost": "Immediate vs 5 min",
        "gm_notes": "If watch: ritual completes (enemy gets buff/summon). But party knows and can counter. If interrupt: surprise but unknown effect.",
        "consequence": "Knowledge vs tactical advantage"
    },
    {
        "title": "Wounded Ally",
        "description": "One party member is bleeding badly (persistent bleed damage). You can stop to treat them or push forward.",
        "choice_a": "Treat Wounds now: 10 minutes (add 1 die to jar). Heal 2d8 HP and stop bleeding.",
        "choice_b": "Push on: Ally takes 1d6 damage each turn until treated. But no time cost.",
        "spotlight": ["Cleric"],
        "skills": ["Medicine"],
        "time_cost": "10 min to treat",
        "gm_notes": "If push on: track bleed damage. Ally might go down before next rest. Add 1 die to jar when finally treated.",
        "consequence": "Time vs ally's health"
    },
    {
        "title": "Alarm Triggered",
        "description": "You accidentally triggered a magical alarm. A bell is ringing loudly. You have seconds to act.",
        "choice_a": "Disable alarm: DC 20 Thievery or Arcana. Takes 3 actions. If failed, alarm continues.",
        "choice_b": "Flee immediately: Run to next room and barricade. Enemies will search but might not find you (DC 17 Stealth).",
        "spotlight": ["Rogue", "Wizard"],
        "skills": ["Thievery", "Arcana", "Stealth"],
        "time_cost": "3 actions vs 1 round",
        "gm_notes": "If alarm continues: all encounters on this floor are alerted and prepared. If flee successfully: only nearby enemies respond.",
        "consequence": "Risk vs escape"
    },
    {
        "title": "Treasure vs Time",
        "description": "You find a locked chest. It looks valuable but the lock is complex. You hear footsteps approaching.",
        "choice_a": "Pick lock now: DC 19 Thievery, takes 10 minutes (add 1 die). Enemies will arrive during attempt.",
        "choice_b": "Ignore it: No time cost, but lose potential treasure and it might be gone later.",
        "choice_c": "Take whole chest: Athletics DC 18 to carry (Bulk 4). Slows movement but can open later.",
        "spotlight": ["Rogue", "Monk"],
        "skills": ["Thievery", "Athletics"],
        "time_cost": "10 min vs none vs encumbrance",
        "gm_notes": "If pick now: roll dice jar during attempt. If take chest: -5 ft speed until dropped. If ignore: treasure is gone.",
        "consequence": "Multiple trade-offs"
    }
]


# ACTIVE THREAT EVENT TEMPLATES (66-85)
ACTIVE_THREAT_TEMPLATES = [
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
    },
    {
        "title": "Floor Collapsing!",
        "description": "The floor beneath you cracks and gives way! Everyone make a Reflex save!",
        "immediate_action": "DC 18 Reflex save to grab edge. DC 19 Athletics to pull yourself up.",
        "success": "You catch yourself and climb up. No damage.",
        "failure": "You fall 15 feet into the room below. 3d6 damage. Separated from party.",
        "spotlight": ["Monk", "Swashbuckler"],
        "skills": ["Reflex", "Athletics"],
        "time_cost": "1 round",
        "gm_notes": "If anyone falls: they're in different room. Party must reunite. Adds tension.",
        "threat_level": "High - damage and separation"
    },
    {
        "title": "Alarm Bell Ringing!",
        "description": "A loud bell starts ringing throughout this floor. You triggered a magical alarm!",
        "immediate_action": "DC 20 Arcana or Thievery to disable in 3 actions, or flee immediately",
        "success": "Alarm stops. Only nearby enemies alerted.",
        "failure": "Alarm continues. All enemies on this floor are alerted and searching for you.",
        "spotlight": ["Wizard", "Rogue"],
        "skills": ["Arcana", "Thievery"],
        "time_cost": "3 actions to disable",
        "gm_notes": "If alarm continues: all remaining encounters get surprise round against party. Major consequence.",
        "threat_level": "High - affects entire floor"
    },

    {
        "title": "Fire Spreading!",
        "description": "A torch fell and ignited oil on the floor. Fire is spreading rapidly toward you!",
        "immediate_action": "DC 17 Acrobatics to jump through flames (2d6 fire damage on failure) or DC 18 Athletics to break through wall",
        "success": "You escape the fire safely.",
        "failure": "Take fire damage and must try again next round. Smoke inhalation (DC 16 Fort or sickened 1).",
        "spotlight": ["Monk", "Swashbuckler"],
        "skills": ["Acrobatics", "Athletics"],
        "time_cost": "1 round per attempt",
        "gm_notes": "Escalating danger. Each round fire spreads. Eventually blocks passage entirely.",
        "threat_level": "High - damage and time pressure"
    },
    {
        "title": "Ambush from Above!",
        "description": "Creatures drop from the ceiling onto the party! They were waiting in ambush!",
        "immediate_action": "Everyone makes DC 18 Perception check. Success = act in surprise round. Failure = flat-footed.",
        "success": "You noticed them falling. You can act in surprise round.",
        "failure": "You're caught off-guard. Enemies get surprise round against you.",
        "spotlight": ["Monk", "Rogue"],
        "skills": ["Perception"],
        "time_cost": "Immediate combat",
        "gm_notes": "Surprise round is critical. Rewards high Perception. Punishes low Perception.",
        "threat_level": "High - combat with disadvantage"
    },
    {
        "title": "Magical Backlash!",
        "description": "The magical ward you're examining suddenly explodes with energy!",
        "immediate_action": "DC 19 Reflex save or take 3d6 force damage. DC 20 Arcana to counter the effect.",
        "success": "You dodge or counter the blast. No damage.",
        "failure": "Take full damage and are pushed 10 feet back.",
        "spotlight": ["Wizard", "Swashbuckler"],
        "skills": ["Reflex", "Arcana"],
        "time_cost": "Immediate",
        "gm_notes": "Punishes careless interaction with magic. Rewards Arcana knowledge.",
        "threat_level": "Moderate - damage"
    },
    {
        "title": "Falling Debris!",
        "description": "The ceiling cracks and chunks of stone rain down on the party!",
        "immediate_action": "DC 18 Reflex save to dodge. Take 2d6 bludgeoning damage on failure.",
        "success": "You dodge the falling stones.",
        "failure": "Take damage and must make DC 16 Fort save or be stunned 1.",
        "spotlight": ["Monk", "Swashbuckler"],
        "skills": ["Reflex"],
        "time_cost": "Immediate",
        "gm_notes": "Environmental hazard. Can happen anywhere. Keeps party alert.",
        "threat_level": "Moderate - damage and condition"
    },

    {
        "title": "Poison Gas Seeping!",
        "description": "Green mist pours from cracks in the walls. It smells toxic!",
        "immediate_action": "DC 17 Nature to identify and find safe air, or DC 18 Fort save each round you stay",
        "success": "You identify safe breathing technique or find clean air pocket.",
        "failure": "Take 1d6 poison damage and become sickened 1. Worsens each round.",
        "spotlight": ["Cleric", "Wizard"],
        "skills": ["Nature", "Fortitude"],
        "time_cost": "1 round per save",
        "gm_notes": "Forces movement. Can't stay in this area. Escalating danger.",
        "threat_level": "High - ongoing damage"
    },
    {
        "title": "Flooding Chamber!",
        "description": "Water rushes in from broken pipes. The room is flooding rapidly!",
        "immediate_action": "DC 18 Athletics to swim to exit before water fills room. DC 16 Perception to spot air pocket.",
        "success": "You reach the exit or find air pocket to breathe.",
        "failure": "You're underwater. Hold breath or start drowning (DC 15 Fort each round).",
        "spotlight": ["Monk", "Rogue"],
        "skills": ["Athletics", "Perception"],
        "time_cost": "1 round per attempt",
        "gm_notes": "Escalating danger. Eventually room is completely flooded. Must escape or drown.",
        "threat_level": "High - potential death"
    },
    {
        "title": "Summoning Circle Activating!",
        "description": "A summoning circle on the floor glows brightly. Something is being summoned!",
        "immediate_action": "DC 20 Arcana to disrupt ritual (3 actions) or prepare for combat",
        "success": "Ritual disrupted. Nothing is summoned.",
        "failure": "A creature appears! Roll initiative. It's hostile.",
        "spotlight": ["Wizard"],
        "skills": ["Arcana"],
        "time_cost": "3 actions to disrupt",
        "gm_notes": "If disrupted: avoid combat. If not: combat encounter with summoned creature.",
        "threat_level": "High - combat or quick thinking"
    }
]

# COMBAT ENCOUNTER TEMPLATES (86-100)
# These will be generated dynamically based on floor and creatures
COMBAT_ECOLOGY_TYPES = [
    "feeding",      # Monsters eating, distracted
    "fighting",     # Two groups fighting each other
    "sleeping",     # Resting, can be avoided or ambushed
    "patrolling",   # Moving through area
    "working",      # Performing tasks
    "guarding",     # Stationed at post
    "hunting",      # Tracking prey
    "scavenging",   # Picking over remains
    "ritual",       # Performing ceremony
    "arguing"       # Internal conflict
]


def generate_opportunity_event(floor_num, floor_data, party_level):
    """Generate an OPPORTUNITY event (5-25)"""
    template = random.choice(OPPORTUNITY_TEMPLATES)
    
    # Customize for floor
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Add floor-specific flavor
    if floor_num == 1:
        event['flavor'] = "Mitflit trinkets scattered nearby suggest they pass through here often."
    elif floor_num == 2:
        event['flavor'] = "The musty smell of morlock occupation is strong here."
    elif floor_num == 3:
        event['flavor'] = "Dusty books and the smell of old parchment fill the air."
    elif floor_num == 4:
        event['flavor'] = "This area feels personal, intimate - Belcorra's private space."
    elif floor_num == 5:
        event['flavor'] = "Blood-soaked sand and the echo of past battles."
    elif floor_num == 6:
        event['flavor'] = "The clinical smell of alchemical preservatives mixed with rot."
    elif floor_num == 7:
        event['flavor'] = "Oppressive heat and the smell of brimstone."
    elif floor_num == 8:
        event['flavor'] = "Damp fungal smell and bioluminescent glow."
    elif floor_num == 9:
        event['flavor'] = "Wild Darklands cavern, untamed and dangerous."
    elif floor_num == 10:
        event['flavor'] = "Reality feels thin here. Ancient and alien."
    
    return event

def generate_complication_event(floor_num, floor_data, party_level):
    """Generate a COMPLICATION event (26-45)"""
    template = random.choice(COMPLICATION_TEMPLATES)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Add floor-specific complications
    if floor_num == 1:
        event['flavor'] = "Mitflit graffiti covers the walls - crude drawings of their 'Sky King'."
    elif floor_num == 2:
        event['flavor'] = "Morlock claw marks score the surfaces."
    elif floor_num == 3:
        event['flavor'] = "Ghoulish scribes have been through here - books disturbed."
    elif floor_num == 4:
        event['flavor'] = "Volluk's influence is evident - leech trails on the floor."
    elif floor_num == 5:
        event['flavor'] = "Arena sand has drifted into this area."
    elif floor_num == 6:
        event['flavor'] = "Seugathi slime trails glisten on the walls."
    elif floor_num == 7:
        event['flavor'] = "Infernal runes glow faintly in the darkness."
    elif floor_num == 8:
        event['flavor'] = "Bog mummy moans echo distantly."
    elif floor_num == 9:
        event['flavor'] = "Multiple faction territories overlap here - dangerous."
    elif floor_num == 10:
        event['flavor'] = "Nhimbaloth's presence is palpable."
    
    return event

def generate_dilemma_event(floor_num, floor_data, party_level):
    """Generate a DILEMMA event (46-65)"""
    template = random.choice(DILEMMA_TEMPLATES)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Add floor-specific context
    if floor_num <= 3:
        event['context'] = "You're still in the upper levels. Escape is possible if things go wrong."
    elif floor_num <= 6:
        event['context'] = "You're deep enough that retreat is costly. Choose wisely."
    else:
        event['context'] = "You're in the deep dungeon. Every choice matters. No easy escape."
    
    return event


def generate_active_threat_event(floor_num, floor_data, party_level):
    """Generate an ACTIVE THREAT event (66-85)"""
    template = random.choice(ACTIVE_THREAT_TEMPLATES)
    
    event = template.copy()
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    
    # Add urgency
    event['urgency'] = "IMMEDIATE ACTION REQUIRED! No time to discuss!"
    
    return event

def generate_combat_event(floor_num, floor_data, party_level, creatures, dice_sum=86):
    """Generate a COMBAT encounter (86-100) with dungeon ecology
    
    Dice sum ranges:
    - 86-94: Standard combat (2 levels below party) - "Low threat"
    - 95-99: Dangerous combat (at party level) - "Moderate threat"  
    - 100: EXTREME combat (at floor level) - "DEADLY threat"
    """
    
    # Determine target level and difficulty based on dice sum
    if dice_sum == 100:
        # EXTREME: Creatures at floor level (deadly)
        target_level = floor_num
        difficulty = "DEADLY (Floor Level)"
        difficulty_note = "⚠️ EXTREME ENCOUNTER - Creatures at floor level!"
    elif dice_sum >= 95:
        # High roll: Creatures at party level (moderate)
        target_level = party_level
        difficulty = "Moderate (Party Level)"
        difficulty_note = "Dangerous encounter - creatures at your level"
    else:
        # Normal combat: 2 levels below party (low)
        target_level = max(1, party_level - 2)
        difficulty = "Low (2 levels below party)"
        difficulty_note = "Standard encounter"
    
    # Get creatures at target level - be strict about it for extreme encounters
    floor_creatures = [c for c in creatures if c['level'] == target_level]
    
    # Only fall back if we have NO creatures at target level
    if not floor_creatures:
        # Try within 1 level
        floor_creatures = [c for c in creatures if abs(c['level'] - target_level) <= 1]
    
    if not floor_creatures:
        # Last resort: any creatures up to target level
        floor_creatures = [c for c in creatures if c['level'] <= target_level and c['level'] > 0]
    
    # For extreme encounters, prefer higher level creatures
    if dice_sum >= 95 and floor_creatures:
        # Sort by level descending and take top half
        floor_creatures.sort(key=lambda x: x['level'], reverse=True)
        cutoff = max(1, len(floor_creatures) // 2)
        floor_creatures = floor_creatures[:cutoff]
    
    # Select ecology type
    ecology_type = random.choice(COMBAT_ECOLOGY_TYPES)
    
    # Select 1-3 creatures
    num_creatures = random.randint(1, 3)
    selected_creatures = random.sample(floor_creatures, min(num_creatures, len(floor_creatures)))
    
    # Build encounter based on ecology
    if ecology_type == "feeding":
        event = {
            "title": f"{selected_creatures[0]['name']} Feeding",
            "description": f"You come upon {num_creatures} {selected_creatures[0]['name']}(s) feasting on a fresh corpse. They're completely focused on their meal.",
            "ecology": "The creatures are distracted by food. Blood and gore everywhere.",
            "tactical_option": "DC 15 Stealth to sneak past OR surprise round if you attack",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "fighting":
        creature_a = selected_creatures[0]
        creature_b = selected_creatures[1] if len(selected_creatures) > 1 else random.choice(floor_creatures)
        event = {
            "title": f"Territorial Dispute",
            "description": f"Two groups are fighting: {creature_a['name']} vs {creature_b['name']}. They're so focused on each other they haven't noticed you.",
            "ecology": "Monsters fighting each other over territory or resources.",
            "tactical_option": "Wait for them to weaken each other, join one side, or sneak past (DC 16 Stealth)",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "sleeping":
        event = {
            "title": f"Sleeping {selected_creatures[0]['name']}",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are sleeping in a pile. They're exhausted from a recent patrol.",
            "ecology": "Creatures need rest too. They're vulnerable but will wake if you're loud.",
            "tactical_option": "DC 17 Stealth to sneak past OR automatic surprise round if you attack",
            "avoidable": True,
            "surprise_available": True
        }

    
    elif ecology_type == "patrolling":
        event = {
            "title": f"{selected_creatures[0]['name']} Patrol",
            "description": f"A patrol of {num_creatures} {selected_creatures[0]['name']}(s) is making rounds. They're alert and armed.",
            "ecology": "Regular patrol route. They'll return this way in 1 hour.",
            "tactical_option": "DC 18 Stealth to hide OR prepare ambush for surprise round",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "working":
        event = {
            "title": f"{selected_creatures[0]['name']} Working",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are hauling supplies, repairing walls, or performing maintenance. They're distracted by their task.",
            "ecology": "Monsters have jobs and responsibilities. Not just waiting to fight.",
            "tactical_option": "DC 16 Stealth to sneak past OR surprise round if you attack",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "guarding":
        event = {
            "title": f"{selected_creatures[0]['name']} Guard Post",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are stationed at a guard post. They're bored but watchful.",
            "ecology": "Stationed guards. Can be distracted or negotiated with.",
            "tactical_option": "DC 19 Stealth to sneak past OR DC 18 Deception to distract them",
            "avoidable": True,
            "surprise_available": False
        }
    
    elif ecology_type == "hunting":
        event = {
            "title": f"{selected_creatures[0]['name']} Hunting Party",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are tracking prey. They're focused on the trail ahead.",
            "ecology": "Hunting other creatures (or maybe hunting YOU if you've been loud).",
            "tactical_option": "DC 17 Stealth to avoid OR follow them to their prey",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "scavenging":
        event = {
            "title": f"{selected_creatures[0]['name']} Scavenging",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are picking through an old battlefield, looking for valuables.",
            "ecology": "Scavengers cleaning up after past battles. Opportunistic.",
            "tactical_option": "DC 16 Stealth to sneak past OR they might flee if you're intimidating",
            "avoidable": True,
            "surprise_available": True
        }
    
    elif ecology_type == "ritual":
        event = {
            "title": f"{selected_creatures[0]['name']} Ritual",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are performing some kind of ceremony. Chanting, candles, offerings.",
            "ecology": "Religious or magical ritual. They're deeply focused.",
            "tactical_option": "DC 15 Stealth to sneak past OR surprise round if you interrupt",
            "avoidable": True,
            "surprise_available": True
        }
    
    else:  # arguing
        event = {
            "title": f"{selected_creatures[0]['name']} Argument",
            "description": f"{num_creatures} {selected_creatures[0]['name']}(s) are arguing loudly about something. Voices raised, gestures wild.",
            "ecology": "Internal conflict. They have disagreements and politics.",
            "tactical_option": "DC 14 Stealth to sneak past (they're very distracted) OR surprise round",
            "avoidable": True,
            "surprise_available": True
        }
    
    # Add combat stats
    event['creatures'] = [c['name'] for c in selected_creatures]
    event['num_creatures'] = num_creatures
    event['creature_level'] = target_level
    event['floor'] = floor_num
    event['floor_name'] = floor_data['name']
    event['difficulty'] = difficulty
    event['difficulty_note'] = difficulty_note
    event['dice_sum'] = dice_sum
    
    # Add floor-specific ecology notes
    if floor_num == 1:
        event['floor_ecology'] = "Mitflits are chaotic and disorganized. They worship a rusty helmet as their 'Sky King'."
    elif floor_num == 2:
        event['floor_ecology'] = "Morlocks worship Belcorra as the 'Ghost Queen'. They're territorial and aggressive."
    elif floor_num == 3:
        event['floor_ecology'] = "Ghouls are stuck in an endless loop: collect flesh, eat flesh, need more flesh."
    elif floor_num == 4:
        event['floor_ecology'] = "This is Belcorra's personal floor. Creatures here serve her directly."
    elif floor_num == 5:
        event['floor_ecology'] = "Arena creatures are trained for combat. Aggressive and dangerous."
    elif floor_num == 6:
        event['floor_ecology'] = "Seugathi are curious researchers. They observe and experiment."
    elif floor_num == 7:
        event['floor_ecology'] = "Devils are lawful and organized. They follow strict hierarchies."
    elif floor_num == 8:
        event['floor_ecology'] = "Bog mummies are the 'Children of Belcorra' - enthralled deep gnomes."
    elif floor_num == 9:
        event['floor_ecology'] = "Multiple factions compete: drow, urdefhan, caligni. Dangerous politics."
    elif floor_num == 10:
        event['floor_ecology'] = "Ancient serpentfolk temple. Reality is thin here."
    
    return event


def generate_event_for_sum(dice_sum, floor_num, floor_data, party_level, creatures):
    """Generate appropriate event based on dice sum"""
    category = get_category_from_sum(dice_sum)
    
    if category == "OPPORTUNITY":
        event = generate_opportunity_event(floor_num, floor_data, party_level)
    elif category == "COMPLICATION":
        event = generate_complication_event(floor_num, floor_data, party_level)
    elif category == "DILEMMA":
        event = generate_dilemma_event(floor_num, floor_data, party_level)
    elif category == "ACTIVE_THREAT":
        event = generate_active_threat_event(floor_num, floor_data, party_level)
    else:  # COMBAT
        event = generate_combat_event(floor_num, floor_data, party_level, creatures, dice_sum)
    
    event['sum'] = dice_sum
    event['category'] = category
    
    return event

def format_event_markdown(event):
    """Format event as markdown for output"""
    lines = []
    
    lines.append(f"## Sum: {event['sum']} - {event['category']}")
    lines.append("")
    lines.append(f"### {event['title']}")
    lines.append("")
    lines.append(f"**Description:** {event['description']}")
    lines.append("")
    
    # Category-specific formatting
    if event['category'] == "OPPORTUNITY":
        lines.append(f"**Challenge:** {event['challenge']}")
        lines.append(f"**Success:** {event['success']}")
        lines.append(f"**Failure:** {event['failure']}")
        lines.append(f"**Spotlight:** {', '.join(event['spotlight'])}")
        lines.append(f"**Skills:** {', '.join(event['skills'])}")
        lines.append(f"**Time Cost:** {event['time_cost']}")
        lines.append(f"**Reward:** {event['reward']}")
        if 'flavor' in event:
            lines.append(f"**Floor Flavor:** {event['flavor']}")
    
    elif event['category'] == "COMPLICATION":
        lines.append(f"**Challenge:** {event['challenge']}")
        lines.append(f"**Success:** {event['success']}")
        lines.append(f"**Failure:** {event['failure']}")
        lines.append(f"**Spotlight:** {', '.join(event['spotlight'])}")
        lines.append(f"**Skills:** {', '.join(event['skills'])}")
        lines.append(f"**Time Cost:** {event['time_cost']}")
        lines.append(f"**Consequence:** {event['consequence']}")
        if 'flavor' in event:
            lines.append(f"**Floor Flavor:** {event['flavor']}")
    
    elif event['category'] == "DILEMMA":
        lines.append(f"**Choice A:** {event['choice_a']}")
        if 'choice_b' in event:
            lines.append(f"**Choice B:** {event['choice_b']}")
        if 'choice_c' in event:
            lines.append(f"**Choice C:** {event['choice_c']}")
        lines.append(f"**Spotlight:** {', '.join(event['spotlight'])}")
        lines.append(f"**Skills:** {', '.join(event['skills'])}")
        lines.append(f"**Time Cost:** {event['time_cost']}")
        lines.append(f"**Consequence:** {event['consequence']}")
        if 'context' in event:
            lines.append(f"**Context:** {event['context']}")
    
    elif event['category'] == "ACTIVE_THREAT":
        lines.append(f"**{event['urgency']}**")
        lines.append("")
        lines.append(f"**Immediate Action:** {event['immediate_action']}")
        lines.append(f"**Success:** {event['success']}")
        lines.append(f"**Failure:** {event['failure']}")
        lines.append(f"**Spotlight:** {', '.join(event['spotlight'])}")
        lines.append(f"**Skills:** {', '.join(event['skills'])}")
        lines.append(f"**Threat Level:** {event['threat_level']}")
    
    else:  # COMBAT
        lines.append(f"**Ecology:** {event['ecology']}")
        lines.append(f"**Creatures:** {event['num_creatures']}x {', '.join(event['creatures'])} (Level {event['creature_level']})")
        lines.append(f"**Difficulty:** {event['difficulty']}")
        lines.append(f"**Tactical Option:** {event['tactical_option']}")
        lines.append(f"**Avoidable:** {'Yes' if event['avoidable'] else 'No'}")
        lines.append(f"**Surprise Available:** {'Yes' if event['surprise_available'] else 'No'}")
        lines.append(f"**Floor Ecology:** {event['floor_ecology']}")
    
    # GM notes for all events
    if 'gm_notes' in event:
        lines.append("")
        lines.append(f"**GM Notes:** {event['gm_notes']}")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def generate_all_encounters(party_level, max_floor, output_file):
    """Generate comprehensive encounter table for all floors"""
    
    print(f"=" * 80)
    print(f"DUNGEON TURN GENERATOR V2 - THE FUN VERSION")
    print(f"=" * 80)
    print(f"Party Level: {party_level}")
    print(f"Floors: 1-{max_floor}")
    print(f"Total Events: {96 * max_floor} (96 sums per floor)")
    print(f"")
    print(f"New Probability Distribution:")
    print(f"  5-25:  OPPORTUNITIES (21 sums, ~22%)")
    print(f"  26-45: COMPLICATIONS (20 sums, ~21%)")
    print(f"  46-65: DILEMMAS (20 sums, ~21%)")
    print(f"  66-85: ACTIVE THREATS (20 sums, ~21%)")
    print(f"  86-100: COMBAT (15 sums, ~16%)")
    print(f"")
    print(f"Combat potential: ~37% (ACTIVE THREATS can become combat)")
    print(f"=" * 80)
    print(f"")
    
    # Load data
    print("Loading data files...")
    gauntlight_content = load_markdown('etc/gauntlight_keep_levels.md')
    levels_data = parse_gauntlight_levels(gauntlight_content)
    creatures = load_json('etc/creatures.json')
    print(f"  Loaded {len(levels_data)} floor definitions")
    print(f"  Loaded {len(creatures)} creatures")
    print("")
    
    # Start building output
    lines = []
    lines.append("# Dungeon Turn Encounters V2 - Gauntlight Keep")
    lines.append("")
    lines.append(f"**Party Level:** {party_level}")
    lines.append(f"**Floors Covered:** 1-{max_floor}")
    lines.append(f"**Generated:** {96 * max_floor} events (sums 5-100 for each floor)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## How to Use")
    lines.append("")
    lines.append("1. When the dice jar reaches 5 dice, roll all 5d20")
    lines.append("2. Sum the total")
    lines.append("3. Find your current floor level below")
    lines.append("4. Look up the sum in that floor's table")
    lines.append("5. Read the encounter to your players")
    lines.append("")
    lines.append("## New Probability Distribution")
    lines.append("")
    lines.append("- **5-25:** OPPORTUNITIES (~22%) - Reward creativity, shortcuts, intel")
    lines.append("- **26-45:** COMPLICATIONS (~21%) - Force skill use, environmental puzzles")
    lines.append("- **46-65:** DILEMMAS (~21%) - Meaningful choices with trade-offs")
    lines.append("- **66-85:** ACTIVE THREATS (~21%) - Immediate danger, patrols, alarms")
    lines.append("- **86-100:** COMBAT (~16%) - Actual fights with dungeon ecology")
    lines.append("")
    lines.append("**Combat Potential:** ~37% (ACTIVE THREATS can escalate to combat)")
    lines.append("")
    lines.append("## Design Philosophy")
    lines.append("")
    lines.append("This system creates **tension** and rewards **creativity**:")
    lines.append("")
    lines.append("- **Every 10 minutes matters** - Dice jar fills, pressure builds")
    lines.append("- **Use ALL your skills** - Not just Detect Magic and Listen")
    lines.append("- **Meaningful choices** - Trade-offs with real consequences")
    lines.append("- **Living dungeon** - Monsters eat, sleep, fight each other")
    lines.append("- **Resource drain** - Without TPK or bogging down gameplay")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Generate events for each floor
    for floor in range(1, max_floor + 1):
        level_data = levels_data.get(floor)
        if not level_data:
            print(f"Warning: No data for floor {floor}, skipping...")
            continue
        
        level_name = level_data['name']
        print(f"Generating Floor {floor}: {level_name}...")
        
        lines.append(f"# Floor {floor}: {level_name}")
        lines.append("")
        
        if level_data.get('theme'):
            lines.append(f"**Theme:** {level_data['theme']}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Generate all 96 possible sums (5-100)
        for dice_sum in range(5, 101):
            event = generate_event_for_sum(dice_sum, floor, level_data, party_level, creatures)
            lines.append(format_event_markdown(event))
        
        print(f"  [OK] Generated 96 events for Floor {floor}")
        lines.append("")
    
    # Write to file
    print(f"")
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"")
    print(f"=" * 80)
    print(f"GENERATION COMPLETE!")
    print(f"=" * 80)
    print(f"Total events generated: {96 * max_floor}")
    print(f"Output file: {output_file}")
    print(f"")
    print(f"The dungeon is now ALIVE and FUN!")
    print(f"=" * 80)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Dungeon Turn Encounters V2')
    parser.add_argument('--level', type=int, default=4, help='Party level (default: 4)')
    parser.add_argument('--floors', type=int, default=3, help='Number of floors to generate (1 to X)')
    parser.add_argument('--output', type=str, default='gm/dungeon_turn_encounters_v2.md', help='Output file path')
    
    args = parser.parse_args()
    
    generate_all_encounters(
        party_level=args.level,
        max_floor=args.floors,
        output_file=args.output
    )

if __name__ == "__main__":
    main()
