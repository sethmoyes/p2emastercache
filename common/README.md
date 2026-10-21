# Common / Shared Reference Material

Shared Abomination Vaults reference material, copied from the GM's
Pathfinder Second Edition Remastered repo. Party-specific material (PCs,
backstories, session history) was left out on purpose.

## `compendium/`

The hub layer of the Obsidian web: one note per recurring NPC, faction,
deity and item (plus hubs for the [[Gauntlight]] and the [[Arcanamirium]]). Each note holds what the thing *is* in the book and every
spelling the tables have used (as `aliases`).
[[Compendium]] is the index, with sortable tables from
[[Compendium.base]].

## `campaign-reference/`

Actual game content, originally copied from the `p2emastercache` tool repo
(markdown only — the large data files backing these stayed behind as JSON
in that repo, and aren't duplicated here). This has since been trimmed: the
old tool's own dev docs and its bulk-generated encounter dumps were moved to
`../archive/` (see below), keeping only what's actually reusable at the
table:

- `gm/` — random merchant NPC writeups, plus a compact 2d20 wilderness
  encounter table
- `players/` — [[00-campaign-overview-and-otari#The Town of Otari|Otari]] location writeups (shops, taverns, library, fishery, etc.)
- `docs/` — [[DUNGEON_EXPLORATION_GUIDE|DUNGEON_EXPLORATION_GUIDE.md]], the consolidated "dice jar"
  exploration/pacing house rule (player-facing rule + a GM-notes section
  with the operational tips, troubleshooting, and success metrics worth
  keeping from the old design docs)
- `etc/` — [[Gauntlight|Gauntlight Keep]] dungeon levels, Inner Sea region gazetteer,
  players' guide
- `floors/` — GM-only, every-detail reference for each Abomination Vaults
  level (rooms, DCs, creatures, treasure, cross-floor connections), encoded
  from the Your Pocket GM chapter videos by the `/video-encoder` skill. See
  [[floors/README|floors/README.md]] for the status table.
- `locations/` — deep-dive reference for specific locations beyond Otari
  itself (currently: [[locations/absalom|absalom.md]], the full Absalom gazetteer, road
  encounters, and arrival sequence; [[absalom-immersion|absalom-immersion.md]], curated
  ambience/music/art for running it at the table)

## `archive/`

Non-deleted, non-live material from the old `p2emastercache` tool: its own
software dev docs, plus bulk-generated encounter tables and design docs for
a dice-sum encounter system that needed the app to run well. Kept for
reference, not meant to be used at the table — see [[archive/README|archive/README.md]] for
what's there and why, and [[CLAUDE|CLAUDE.md]]'s "GM philosophy" section for the
durable lessons that were pulled out of it before archiving.

## `onenote-import/`

Raw, unreviewed conversion of the user's old OneNote notebook — in progress
as of this writing, not yet reconciled with the curated docs above. Don't
restructure or re-run this import; it's an active in-progress task.
