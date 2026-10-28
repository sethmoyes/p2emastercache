# Dungeon Turn Events: Format

`etc/dungeon_turn_events.json` holds the event templates the dungeon turn draws
from, in four lists: `OPPORTUNITY`, `COMPLICATION`, `DILEMMA` and
`ACTIVE_THREAT`. COMBAT events aren't templates; they come from
`etc/floor_ecology.json`, as do most ACTIVE_THREAT rolls (70%).

When a roll lands on a category, the generator picks a template for the
current floor: a floor's own templates three times in four, otherwise any
template from that floor or floor 0 (works anywhere). Templates with a
`retired` field never roll.

## Fields

Every event has:

| Field | What it holds |
|---|---|
| `title` | Short name shown on the card |
| `description` | What the party sees, read aloud |
| `skills` | List of the skills and saves the event calls for |
| `time_cost` | How much time it takes, with its effect on the jar ("ADD 1 DIE TO JAR", "NO DICE ADDED") |
| `gm_notes` | Floor, faction ties, tactics, consequences and lore |
| `floor` | 1-10, or 0 for an event that works on any floor |

Then, by category:

| Category | Fields |
|---|---|
| OPPORTUNITY | `challenge`, `success`, `failure`, `reward` |
| COMPLICATION | `challenge`, `success`, `failure`, `consequence`, optional `reward` |
| DILEMMA | `choice_a`, `choice_b`, optional `choice_c`, `consequence`, optional `reward` |
| ACTIVE_THREAT | `immediate_action`, `success`, `failure`, `threat_level`, optional `consequence` |

A `success` with several options separated by " OR " shows as a numbered list.

Optional on any event:

| Field | What it holds |
|---|---|
| `creatures` | How many of what, in prose: "1d3 Ghouls" |
| `creature_reference` | `{creature name: {source, aon_url, level, hp, ac}}`, copied from `creatures.json`; the GM page shows each one's full stat block |
| `retired` | Why the template was retired (it stays on file but never rolls) |

## Rules for writing them

See "Event Writing Philosophy" in `claude.md`. In short: specific creatures
with real stats, explicit DCs and jar costs, no named enemies as incidental
encounters, nothing that invents passages or teleports the party into a keyed
room, and ASCII only. `avtools/validation.py` checks the structural rules.
