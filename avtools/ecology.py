"""
Floor ecology for dungeon turns.

Builds COMBAT and ACTIVE_THREAT events from etc/floor_ecology.json, so that what
the dice jar sends at the party is what actually lives on that floor of the
Gauntlight. Creature counts are scaled to the party with the PF2e encounter XP
budget instead of a fixed "2 levels below party" rule.
"""

import random

from avtools.data import AON_BASE, find_creature, floor_ecology

# XP per creature by its level relative to the party (Core Rulebook, Table 10-2)
CREATURE_XP = {-4: 10, -3: 15, -2: 20, -1: 30, 0: 40, 1: 60, 2: 80, 3: 120, 4: 160}

# Threat budgets for four PCs, plus the adjustment for each PC above or below four
THREAT_BUDGETS = {
    'Trivial': (40, 10),
    'Low': (60, 15),
    'Moderate': (80, 20),
    'Severe': (120, 30),
    'Extreme': (160, 40),
}

# How often an ACTIVE_THREAT roll uses a floor hazard/event instead of a template
ECOLOGY_THREAT_CHANCE = 0.7

DEFAULT_MAX_COUNT = 6


def encounter_budget(threat, party_size=4):
    base, per_pc = THREAT_BUDGETS[threat]
    return base + per_pc * (party_size - 4)


def creature_xp(level, party_level):
    """XP for one creature, 0 if it's too weak to count, None if it's off the chart."""
    diff = level - party_level
    if diff < -4:
        return 0
    if diff > 4:
        return None
    return CREATURE_XP[diff]


def rate_encounter(total_xp, party_size=4, off_chart=False):
    """Name the threat tier whose budget is closest to this total XP. A creature
    more than 4 levels above the party is past the XP table: beyond Extreme."""
    if off_chart:
        return 'Beyond Extreme'
    return min(THREAT_BUDGETS, key=lambda threat: abs(encounter_budget(threat, party_size) - total_xp))


THREAT_ORDER = ['Trivial', 'Low', 'Moderate', 'Severe', 'Extreme', 'Beyond Extreme']


def build_roster(entry, creatures, party_level, budget, strict=True, min_ratio=0.5, count_scale=1.0):
    """
    Turn an ecology entry into [(creature, count), ...] and its total XP.

    Fixed groups keep the book's numbers. Scaled entries fill the budget with
    the entry's creature, up to max_count (times count_scale, so a lone creature
    stays alone). With strict=True an entry that can't
    land between min_ratio and 125% of the budget returns None.
    """
    if 'group' in entry:
        roster = [(find_creature(creatures, g['creature']), g['count']) for g in entry['group']]
    else:
        roster = [(find_creature(creatures, c['creature']), c['count']) for c in entry.get('companions', [])]
        main = find_creature(creatures, entry['creature'])
        if main is None:
            return None
        companion_xp = sum((creature_xp(c['level'], party_level) or 0) * n for c, n in roster if c)
        main_xp = creature_xp(main['level'], party_level)
        max_count = int(entry.get('max_count', DEFAULT_MAX_COUNT) * count_scale)
        if main_xp is None:
            if strict:
                return None
            count = 1
        elif main_xp == 0:
            if strict:
                return None
            count = max_count
        else:
            count = min(max_count, (budget - companion_xp) // main_xp)
            if count < 1:
                if strict:
                    return None
                count = 1
        roster.insert(0, (main, count))

    if any(c is None for c, _ in roster):
        return None
    xps = [creature_xp(c['level'], party_level) for c, _ in roster]
    if strict and any(xp is None for xp in xps):
        return None
    total = sum((xp or 0) * n for xp, (_, n) in zip(xps, roster))
    if strict and not (budget * min_ratio <= total <= budget * 1.25):
        return None
    return roster, total


def _weighted_choice(options):
    return random.choices(options, weights=[o[0].get('weight', 1) for o in options])[0]


def choose_creature_encounter(floor_num, creatures, party_level, threat, party_size=4):
    """Pick a creature entry for this floor that fits the budget, or None if the floor has none."""
    floor = floor_ecology().get(floor_num)
    if not floor:
        return None
    entries = [e for e in floor['entries'] if e['kind'] == 'creature']
    if not entries:
        return None
    budget = encounter_budget(threat, party_size)
    # Extreme rolls shouldn't land on a group that's merely Low, and may bring
    # more of a floor's residents than usual; bigger parties meet bigger groups
    extreme = threat != 'Low'
    min_ratio = 0.65 if extreme else 0.5
    count_scale = (1.5 if extreme else 1.0) * max(1.0, party_size / 4)

    fits = []
    for entry in entries:
        built = build_roster(entry, creatures, party_level, budget,
                             min_ratio=min_ratio, count_scale=count_scale)
        if built:
            fits.append((entry, built))
    if fits:
        return _weighted_choice(fits) + (budget,)

    # Nothing on this floor fits the budget (the party is far above or below the
    # floor's level). Still send the floor's own creatures, just rated honestly.
    loose = []
    for entry in entries:
        built = build_roster(entry, creatures, party_level, budget, strict=False, count_scale=count_scale)
        if built:
            loose.append((entry, built))
    if not loose:
        return None
    return min(loose, key=lambda o: abs(o[1][1] - budget)) + (budget,)


def build_ecology_combat_event(floor_num, floor_data, party_level, creatures, dice_sum,
                               threat='Low', party_size=4, extreme=False):
    """A COMBAT event from the floor's ecology, or None to fall back to the old generator."""
    choice = choose_creature_encounter(floor_num, creatures, party_level, threat, party_size)
    if not choice:
        return None
    entry, (roster, total_xp), budget = choice
    floor = floor_ecology()[floor_num]

    main = roster[0][0]
    perception_dc = max(c.get('perception') or 0 for c, _ in roster) + 10
    off_chart = any(creature_xp(c['level'], party_level) is None for c, _ in roster)
    rating = rate_encounter(total_xp, party_size, off_chart)
    summary = ', '.join(f"{n}x {c['name']} (Level {c['level']}, HP {c['hp']}, AC {c['ac']})" for c, n in roster)

    if extreme:
        difficulty_note = f"EXTREME ROLL ({dice_sum})! The floor's deadliest residents. Consider letting them retreat or negotiate."
        if dice_sum <= 15:
            difficulty_note += " Low extreme roll: the party can get the surprise round."
    else:
        difficulty_note = "Standard dungeon-turn encounter."

    # Say so when the floor and the party are badly matched, either way
    gap = THREAT_ORDER.index(rating) - THREAT_ORDER.index(threat)
    if gap >= 2:
        difficulty_note += f" Rated {rating}: this floor's residents outclass the party. Give them a way out."
    elif gap <= -2:
        difficulty_note += f" Rated {rating}: the party outclasses this floor; consider letting it pass in a sentence."

    return {
        'title': entry['title'],
        'description': entry['description'],
        'ecology': entry['why_here'],
        'tactical_option': f"{entry['tactics']} To slip past: DC {perception_dc} Stealth (their Perception DC).",
        'avoidable': not extreme,
        'surprise_available': dice_sum <= 15 if extreme else True,
        'creatures': [c['name'] for c, _ in roster],
        'num_creatures': sum(n for _, n in roster),
        'creature_level': main['level'],
        'creature_summary': summary,
        'creature_reference': {
            c['name']: {
                'source': 'creatures.json',
                'aon_url': AON_BASE + c['url'] if c.get('url') else '',
                'level': c['level'],
                'hp': c['hp'],
                'ac': c['ac'],
                'perception': c.get('perception'),
            }
            for c, _ in roster
        },
        'difficulty': (f"{rating} ({'creatures more than 4 levels above the party' if off_chart else f'{total_xp} XP'}; "
                       f"{threat} budget is {budget} XP for {party_size} PCs at level {party_level})"),
        'difficulty_note': difficulty_note,
        'floor_ecology': floor['ecology'],
        'lore_hook': entry['lore_hook'],
        'gm_notes': f"Floor {floor_num}. Book: {entry['book_source']}. {entry['lore_hook']}",
        'ecology_id': entry['id'],
        'floor': floor_num,
        'floor_name': floor_data.get('name', floor['name']),
        'dice_sum': dice_sum,
    }


def build_ecology_threat_event(floor_num, floor_data):
    """An ACTIVE_THREAT event from the floor's hazards and events, or None."""
    floor = floor_ecology().get(floor_num)
    if not floor:
        return None
    entries = [e for e in floor['entries'] if e['kind'] in ('hazard', 'event')]
    if not entries:
        return None
    entry = random.choices(entries, weights=[e.get('weight', 1) for e in entries])[0]

    if entry['kind'] == 'hazard':
        threat_level = f"Hazard (level {entry['level']})" if 'level' in entry else 'Hazard'
    else:
        threat_level = 'Floor event'
    gm_notes = f"Floor {floor_num}. Book: {entry['book_source']}. {entry['why_here']}"
    if entry.get('consequence'):
        gm_notes += f" {entry['consequence']}"

    return {
        'title': entry['title'],
        'description': entry['description'],
        'urgency': "IMMEDIATE ACTION REQUIRED! No time to discuss!",
        'immediate_action': entry['immediate_action'],
        'success': entry['success'],
        'failure': entry['failure'],
        'skills': entry['skills'],
        'threat_level': threat_level,
        'gm_notes': gm_notes,
        'ecology_id': entry['id'],
        'floor': floor_num,
        'floor_name': floor_data.get('name', floor['name']),
    }
