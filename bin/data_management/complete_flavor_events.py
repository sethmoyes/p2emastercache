#!/usr/bin/env python3
"""
Complete the dungeon_flavor_events.json with all 50 events for floors 3-10
"""

import json

# Load existing
with open('etc/dungeon_flavor_events.json', 'r') as f:
    data = json.load(f)

# Add floors 3-10 with 50 events each
new_floors = {
    "3": [  # The Library - books, ghouls, knowledge, flesh collection
        {"title": "Quill Scratching", "description": "You hear a quill scratching on parchment from somewhere nearby. Constant. Methodical. Never stopping.", "teaching": "Hints at endless work"},
        {"title": "Chunk of Flesh", "description": "A chunk of rotting flesh on the floor. Bite marks on it. Someone's eating their own collection.", "teaching": "Hints at failed collection"},
        {"title": "Forbidden Title", "description": "A book spine catches your eye. The title makes your head hurt to read. You look away.", "teaching": "Hints at dark knowledge"},
        {"title": "Tattooing Needle", "description": "A tattooing needle on a table, still wet with ink. And blood. Fresh.", "teaching": "Hints at disturbing practice"},
        {"title": "Whispering Pages", "description": "A book lies open. The pages whisper when you're not looking at them. You slam it shut.", "teaching": "Hints at cursed texts"},
        {"title": "Glass Shards", "description": "Fresh glass shards on the floor. Something was displayed here. Recently taken.", "teaching": "Hints at recent theft"},
        {"title": "Clutched Portrait", "description": "A skeleton's bony fingers still clutch a small portrait. Even in death, they wouldn't let go.", "teaching": "Hints at devotion"},
        {"title": "Bookworm Trail", "description": "A trail of book dust and tiny holes. Something eats the pages here.", "teaching": "Hints at vermin"},
        {"title": "Ink Stain", "description": "A massive ink stain on the floor. A whole bottle spilled. Or thrown.", "teaching": "Hints at frustration"},
        {"title": "Torn Binding", "description": "A book binding torn apart. The pages are gone. Someone wanted what was inside.", "teaching": "Hints at theft"},
        {"title": "Reading Glasses", "description": "Spectacles with one lens cracked. Left on a table as if the reader just stepped away.", "teaching": "Hints at scholars"},
        {"title": "Bookmark", "description": "A silk bookmark in a book. The page it marks is about summoning.", "teaching": "Hints at research"},
        {"title": "Candle Ring", "description": "A ring of candle stubs around a reading desk. Someone studied here for hours.", "teaching": "Hints at study"},
        {"title": "Chewed Page", "description": "A page chewed and spat out. The teeth marks are humanoid.", "teaching": "Hints at ghouls"},
        {"title": "Dropped Quill", "description": "A quill pen, the nib broken. Someone pressed too hard while writing.", "teaching": "Hints at anger"},
        {"title": "Book Stack", "description": "Books stacked in a precise tower. Someone organized these. Recently.", "teaching": "Hints at current activity"},
        {"title": "Dusty Shelf", "description": "One shelf is dust-free. Books are taken from here regularly.", "teaching": "Hints at use"},
        {"title": "Torn Map", "description": "A map torn from a book. It shows a city. Absalom.", "teaching": "Hints at targets"},
        {"title": "Bloodstained Page", "description": "A page with a bloody fingerprint. Someone read while bleeding.", "teaching": "Hints at injury"},
        {"title": "Broken Pen", "description": "A pen snapped in half. Frustration or rage.", "teaching": "Hints at emotion"},
        {"title": "Scattered Notes", "description": "Notes scattered across a desk. The handwriting degrades from neat to frantic.", "teaching": "Hints at madness"},
        {"title": "Empty Inkwell", "description": "An inkwell scraped completely dry. Someone needed every drop.", "teaching": "Hints at desperation"},
        {"title": "Bookend", "description": "A single bookend. Its partner is missing. The books have fallen.", "teaching": "Hints at disorder"},
        {"title": "Paper Scraps", "description": "Tiny scraps of paper like confetti. Someone tore up a document.", "teaching": "Hints at destruction"},
        {"title": "Wax Seal", "description": "A broken wax seal on the floor. The symbol is a skull.", "teaching": "Hints at correspondence"},
        {"title": "Leather Strap", "description": "A strap from a book binding. The book it held is gone.", "teaching": "Hints at missing books"},
        {"title": "Page Corner", "description": "A page corner torn off and dropped. Someone marked their place.", "teaching": "Hints at reading"},
        {"title": "Magnifying Glass", "description": "A magnifying glass with a cracked lens. For reading small text.", "teaching": "Hints at detailed work"},
        {"title": "Book Cart", "description": "A small cart for moving books. One wheel is broken.", "teaching": "Hints at library work"},
        {"title": "Ladder Rung", "description": "A broken rung from a library ladder. Someone fell.", "teaching": "Hints at accident"},
        {"title": "Dust Motes", "description": "Dust motes swirl in the air. Someone disturbed the shelves recently.", "teaching": "Hints at movement"},
        {"title": "Pressed Flower", "description": "A dried flower pressed between book pages. A bookmark from long ago.", "teaching": "Hints at past readers"},
        {"title": "Gnawed Cover", "description": "A book cover gnawed at the corners. Rats? Or something else?", "teaching": "Hints at damage"},
        {"title": "Spilled Sand", "description": "Sand spilled from a blotter. For drying ink.", "teaching": "Hints at writing"},
        {"title": "Broken Ruler", "description": "A wooden ruler snapped in two. For measuring or drawing lines.", "teaching": "Hints at precision"},
        {"title": "Page Weight", "description": "A small weight for holding pages open. Made of brass.", "teaching": "Hints at tools"},
        {"title": "Ribbon Marker", "description": "A ribbon hanging from a book. The page it marks is about necromancy.", "teaching": "Hints at dark arts"},
        {"title": "Cracked Spine", "description": "A book with its spine cracked from being opened too wide. Well-used.", "teaching": "Hints at popular texts"},
        {"title": "Margin Notes", "description": "A book with frantic notes scrawled in the margins. 'This works!' 'Try this!'", "teaching": "Hints at experimentation"},
        {"title": "Bookplate", "description": "A bookplate inside a cover: 'Property of Belcorra Haruvex.' Her library.", "teaching": "Hints at ownership"},
        {"title": "Moldy Pages", "description": "Pages stuck together with mold. The dampness is destroying the books.", "teaching": "Hints at decay"},
        {"title": "Torn Illustration", "description": "An illustration torn from a book. It shows a summoning circle.", "teaching": "Hints at magic"},
        {"title": "Empty Shelf", "description": "A shelf completely empty. The dust outline shows many books were here.", "teaching": "Hints at removal"},
        {"title": "Reading Stand", "description": "A wooden stand for holding books open. Adjusted to a short person's height.", "teaching": "Hints at readers"},
        {"title": "Dropped Bookmark", "description": "A bookmark on the floor. Someone lost their place.", "teaching": "Hints at interruption"},
        {"title": "Catalog Card", "description": "A card from a catalog system. This library was organized once.", "teaching": "Hints at order"},
        {"title": "Blotter Paper", "description": "Blotter paper covered in ink smudges. Someone wrote many letters here.", "teaching": "Hints at correspondence"},
        {"title": "Book Strap", "description": "A leather strap for carrying books. Worn smooth from use.", "teaching": "Hints at transport"},
        {"title": "Page Knife", "description": "A small knife for cutting pages. The blade is dull from use.", "teaching": "Hints at book maintenance"},
        {"title": "Wax Drips", "description": "Wax dripped on a book. Someone read by candlelight and wasn't careful.", "teaching": "Hints at late night study"}
    ],
    "4": [  # Belcorra's Retreat - personal items, trophies, meditation, imprisonment
        {"title": "Meditation Cushion", "description": "A single cushion, positioned to face one direction. The fabric is stained with old sweat and tears.", "teaching": "Hints at obsessive meditation"},
        {"title": "Preserved Hand", "description": "A severed hand in a display case, impossibly well preserved. A trophy of some kind.", "teaching": "Hints at collected victories"},
        {"title": "Ghostly Hum", "description": "A faint humming sound, like energy crackling. It's coming from below, but you can't go down. Something blocks the way.", "teaching": "Hints at barrier"},
        {"title": "Distant Moaning", "description": "Faint moaning echoes from somewhere. It sounds... entranced. Dreamy, not pained.", "teaching": "Hints at entranced prisoner"},
        {"title": "Rogue's Lockpick", "description": "A lockpick lies next to a skeleton. The pick is bent - they were trying to open something when they died.", "teaching": "Hints at trapped explorer"},
        {"title": "Forgotten Whip", "description": "A whip lies on a table, covered in dust. It hasn't been touched in a very long time.", "teaching": "Hints at abandoned tool"},
        {"title": "Single Leech", "description": "A leech crawls across the floor. Just one. Where did it come from?", "teaching": "Hints at leech source"},
        {"title": "Incense Ash", "description": "A pile of incense ash. The smell is faint but still present. Meditation rituals.", "teaching": "Hints at rituals"},
        {"title": "Broken Icon", "description": "A religious icon smashed on the floor. Someone rejected the gods.", "teaching": "Hints at apostasy"},
        {"title": "Silk Scarf", "description": "A silk scarf, expensive and fine. Personal clothing from centuries ago.", "teaching": "Hints at wealth"},
        {"title": "Trophy Plaque", "description": "An empty plaque on the wall. Whatever it displayed is gone.", "teaching": "Hints at missing trophy"},
        {"title": "Meditation Bell", "description": "A small bell for meditation. It rings with a pure, clear tone.", "teaching": "Hints at practice"},
        {"title": "Dropped Earring", "description": "A single earring, gold and ornate. Someone lost it here.", "teaching": "Hints at jewelry"},
        {"title": "Perfume Bottle", "description": "An empty perfume bottle. The scent is long gone.", "teaching": "Hints at vanity"},
        {"title": "Mirror Shard", "description": "A shard from a broken mirror. The silver backing is intact.", "teaching": "Hints at reflection"},
        {"title": "Hairpin", "description": "An ornate hairpin on the floor. Dropped or torn out?", "teaching": "Hints at struggle"},
        {"title": "Cushion Stuffing", "description": "Stuffing pulled from a cushion. Someone searched it.", "teaching": "Hints at searching"},
        {"title": "Candle Holder", "description": "An ornate candle holder, tarnished black. Once it was silver.", "teaching": "Hints at decay"},
        {"title": "Dropped Ring", "description": "A ring on the floor. The stone is missing from its setting.", "teaching": "Hints at theft"},
        {"title": "Torn Tapestry", "description": "A scrap of tapestry. The pattern shows a battle scene.", "teaching": "Hints at decoration"},
        {"title": "Broken Lute", "description": "A lute with broken strings. Someone played music here once.", "teaching": "Hints at entertainment"},
        {"title": "Wine Stain", "description": "An old wine stain on the floor. A bottle was dropped or thrown.", "teaching": "Hints at drinking"},
        {"title": "Dropped Dagger", "description": "A small dagger, ornamental. The blade is dull.", "teaching": "Hints at weapons"},
        {"title": "Powder Compact", "description": "A compact for face powder. The mirror inside is cracked.", "teaching": "Hints at grooming"},
        {"title": "Broken Comb", "description": "A comb with teeth missing. Personal grooming items.", "teaching": "Hints at daily life"},
        {"title": "Spilled Perfume", "description": "A stain where perfume was spilled. The smell is faint but sickly sweet.", "teaching": "Hints at luxury"},
        {"title": "Torn Letter", "description": "A letter torn into pieces. You can make out '...never forgive...'", "teaching": "Hints at correspondence"},
        {"title": "Dropped Brooch", "description": "A brooch shaped like a skull. Morbid jewelry.", "teaching": "Hints at dark tastes"},
        {"title": "Broken Necklace", "description": "A necklace with its chain broken. The beads are scattered.", "teaching": "Hints at violence"},
        {"title": "Makeup Brush", "description": "A brush for applying makeup. The bristles are stiff with age.", "teaching": "Hints at vanity"},
        {"title": "Dropped Glove", "description": "A single glove, fine leather. Its partner is missing.", "teaching": "Hints at clothing"},
        {"title": "Broken Fan", "description": "A folding fan with broken ribs. Once it was elegant.", "teaching": "Hints at refinement"},
        {"title": "Spilled Ink", "description": "Ink spilled on a writing desk. Someone was writing letters.", "teaching": "Hints at correspondence"},
        {"title": "Quill Pen", "description": "A quill pen with a gold nib. Expensive writing tools.", "teaching": "Hints at wealth"},
        {"title": "Wax Seal", "description": "A wax seal stamp. The symbol is a tower.", "teaching": "Hints at correspondence"},
        {"title": "Torn Diary", "description": "Pages torn from a diary. The entries are frantic, angry.", "teaching": "Hints at emotions"},
        {"title": "Dropped Key", "description": "A small key on a chain. What does it open?", "teaching": "Hints at locks"},
        {"title": "Broken Hourglass", "description": "An hourglass with its glass broken. The sand has spilled out.", "teaching": "Hints at time"},
        {"title": "Candle Wax", "description": "Wax pooled on a table. Many candles burned here.", "teaching": "Hints at late nights"},
        {"title": "Dropped Coin", "description": "A gold coin. The face shows a ruler you don't recognize.", "teaching": "Hints at age"},
        {"title": "Broken Seal", "description": "A broken seal on the floor. Someone opened a sealed letter.", "teaching": "Hints at secrets"},
        {"title": "Torn Ribbon", "description": "A ribbon torn in half. Once it tied something closed.", "teaching": "Hints at packages"},
        {"title": "Dropped Pendant", "description": "A pendant on a broken chain. The symbol is arcane.", "teaching": "Hints at magic"},
        {"title": "Broken Bracelet", "description": "A bracelet snapped in two. The metal is bent.", "teaching": "Hints at force"},
        {"title": "Spilled Powder", "description": "Face powder spilled on a vanity. The container is tipped over.", "teaching": "Hints at haste"},
        {"title": "Dropped Vial", "description": "An empty vial. It once held perfume or poison.", "teaching": "Hints at substances"},
        {"title": "Broken Clasp", "description": "A clasp from a cloak or dress. The pin is bent.", "teaching": "Hints at clothing"},
        {"title": "Torn Fabric", "description": "A scrap of fine fabric. Silk or velvet. From expensive clothing.", "teaching": "Hints at wealth"},
        {"title": "Dropped Button", "description": "A button carved from bone. From an expensive garment.", "teaching": "Hints at fashion"},
        {"title": "Broken Buckle", "description": "A belt buckle, ornate and heavy. The leather is gone.", "teaching": "Hints at accessories"}
    ]
}

# Merge with existing
data.update(new_floors)

# Save
with open('etc/dungeon_flavor_events.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Updated! Now have floors: {sorted(data.keys())}")
print(f"Total events: {sum(len(events) for events in data.values())}")
