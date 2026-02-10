# Dungeon Turn V2 - Quick Start Guide

## 🎲 What Is This?

A web-based random encounter generator for Pathfinder 2E's Abomination Vaults adventure path. Roll 5d20 at the table, enter the total, and get instant encounters with full creature stats!

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
source ~/boto3env/bin/activate
```

### 2. Start the Server
```bash
./bin/web/start.sh
```

### 3. Open Browser
Navigate to: **http://localhost:5000**

### 4. Play!
1. Select a floor (1-10)
2. Roll 5d20 in person
3. Enter the total (5-100)
4. Get your encounter with full stats!

## ✨ Features

### Manual Dice Rolling
- Roll physical dice at the table
- Enter the total in the web app
- More tactile and engaging than virtual rolls

### Extreme Roll Indicators
- Rolls 5-8 or 97-100 show **⚡ EXTREME ROLL! ⚡**
- Makes crazy rolls feel significant

### Complete Creature Stats
For key Gauntlight creatures:
- ⚔️ **Attacks** - Full attack bonuses and damage
- ✨ **Abilities** - Special powers and effects
- 🛡️ **Defenses** - Immunities, resistances, weaknesses
- 🎯 **Skills** - All skill bonuses
- 💬 **Languages** - What they speak

### Enhanced Creatures
Full stats available for:
- Mitflit
- Morlock
- Ghoul
- Skeleton Guard
- Zombie Shambler
- Giant Monitor Lizard
- Wight
- Shadow

Other creatures show basic stats with a link to Archives of Nethys.

### Dice Jar Tracker
- Track dice accumulation between encounters
- Visual display of 5d20 jar
- Auto-resets after rolling

### Roll History
- See your last 10 encounters
- Track what happened on each floor
- Clear history anytime

## 📁 Project Structure

```
p2emastercache/
├── bin/
│   ├── generators/          # Encounter generation logic
│   ├── scrapers/            # Data enhancement scripts
│   └── web/                 # Web application
│       ├── templates/       # HTML templates
│       ├── static/          # CSS, JS, images
│       ├── dungeon_turn_app.py
│       └── start.sh
├── etc/                     # Game data
│   ├── creatures.json       # 2,877 creatures (11 fully enhanced)
│   ├── gauntlight_keep_levels.md
│   └── ...
├── docs/                    # Documentation
├── players/                 # Player-facing guides
└── gm/                      # GM resources
```

## 🔧 Troubleshooting

### Port 5000 Already in Use
```bash
# Kill processes on port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
python3 bin/web/dungeon_turn_app.py --port 5001
```

### Flask Not Found
```bash
# Make sure you're in the virtual environment
source ~/boto3env/bin/activate

# Install Flask
pip3 install Flask
```

### Creatures Missing Attacks
Some creatures don't have full stats yet. To add more:
```bash
# Edit the enhancement script
nano bin/scrapers/add_gauntlight_creatures.py

# Add creature data to GAUNTLIGHT_CREATURES dict

# Run the script
python3 bin/scrapers/add_gauntlight_creatures.py
```

## 📚 Documentation

- **[Web Interface Guide](docs/WEB_INTERFACE.md)** - Detailed web app documentation
- **[Fixes Complete](docs/FIXES_COMPLETE.md)** - Recent improvements
- **[Dungeon Turn Redesign](docs/DUNGEON_TURN_REDESIGN.md)** - System design
- **[Player Guide](players/DUNGEON_EXPLORATION_GUIDE.md)** - For players

## 🎨 Adding Background Art

The app supports rotating Wayne Reynolds art:

1. Find 5 Pathfinder images by Wayne Reynolds
2. Save as JPG in `bin/web/static/art/`:
   - `wr_goblin.jpg`
   - `wr_dragon.jpg`
   - `wr_dungeon.jpg`
   - `wr_combat.jpg`
   - `wr_monster.jpg`
3. Restart the server
4. Art will rotate every 30 seconds at 10% opacity

See `bin/web/static/art/README.md` for details.

## 🎯 Tips for GMs

### Encounter Pacing
- **5-20:** Opportunities (treasure, shortcuts)
- **21-40:** Complications (skill challenges)
- **41-60:** Dilemmas (choices with consequences)
- **61-80:** Active Threats (time pressure)
- **81-100:** Combat (monsters!)

### Extreme Rolls
- **5-8:** Extremely beneficial or trivial
- **97-100:** Extremely dangerous or epic

### Dice Jar
- Add a die when players:
  - Fail a critical roll
  - Trigger a trap
  - Make excessive noise
  - Spend too much time
- When jar fills (5 dice), roll for encounter

### Creature Stats
- Click creature names to see full stats
- Use Archives of Nethys link for creatures without full data
- Print stat blocks for common encounters

## 🔥 Ready to Play!

Your dungeon is enhanced and ready to rock. Roll those dice and let the chaos begin! 🎲

---

**Questions?** Check the docs folder or the README files in each directory.
