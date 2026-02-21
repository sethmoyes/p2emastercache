# Quick Start Guide - Pathfinder 2e Dungeon Tools

Get up and running in 5 minutes!

---

## 🚀 For GMs

### 1. Generate Encounters
```bash
python3 bin/generators/generate_dungeon_turn_v2.py --level 4 --floors 3
```

### 2. Start Web Interface (Optional)
```bash
source ~/boto3env/bin/activate  # or your venv
./bin/web/start.sh
# Open http://localhost:5000
```

### 3. Read This (10 minutes)
- `gm/DUNGEON_TURN_V2_QUICK_REFERENCE.md` - How to run the system

### 4. Give Players This
- `players/DUNGEON_EXPLORATION_GUIDE.md` - Player-facing guide

### 5. Play!
- Track time (10 min = 1 die)
- Roll at 5 dice
- Look up sum in generated file
- Run the encounter

---

## 🎲 The System in 30 Seconds

### The Dice Jar
- Every 10 minutes = add 1 die
- At 5 dice = roll all 5d20
- Sum (5-100) determines what happens

### What Happens
| Sum | Category | Effect |
|-----|----------|--------|
| 5-25 | OPPORTUNITY | Rewards creativity |
| 26-45 | COMPLICATION | Skill challenge |
| 46-65 | DILEMMA | Meaningful choice |
| 66-85 | ACTIVE THREAT | Immediate danger |
| 86-100 | COMBAT | Monster encounter |

### Example
```
GM: "You search thoroughly. 30 minutes. Add 3 dice."
Players: "We're at 5 dice!"
GM: "Roll them!"
Players: *rolls* "67!"
GM: "You hear footsteps approaching fast..."
```

---

## 🎮 Web Interface Quick Start

### Start Server
```bash
source ~/boto3env/bin/activate
./bin/web/start.sh
```

### Use It
1. Select floor (1-10)
2. Roll 5d20 physically
3. Enter total in web app
4. Get encounter with full stats

### Features
- ⚔️ Complete creature stats for key monsters
- 🎲 Dice jar tracker
- 📜 Roll history
- ⚡ Extreme roll indicators (5-8, 97-100)
- 💀 Extreme encounter scaling (100 = floor level = deadly!)

---

## 📚 Common Commands

### Generate Content
```bash
# Dungeon encounters
python3 bin/generators/generate_dungeon_turn_v2.py --level 4 --floors 3

# Merchant inventories
python3 bin/generators/generate_merchants.py --level 4

# Overland encounters
python3 bin/generators/generate_4d20_encounters.py --level 4
```

### Check Data
```bash
# Verify data integrity
python3 bin/data_management/check_data_integrity.py 10 equipment
```

---

## 🔧 Troubleshooting

### Port 5000 in Use
```bash
lsof -ti:5000 | xargs kill -9
```

### Flask Not Found
```bash
source ~/boto3env/bin/activate
pip install Flask
```

### Missing Data Files
Ensure these exist in `etc/`:
- `creatures.json`
- `equipment.json`
- `spells.json`
- `gauntlight_keep_levels.md`
- `dungeon_turn_events.json`

---

## 📖 Documentation

- **[README.md](README.md)** - Complete overview
- **[kiro.md](kiro.md)** - Project guidelines
- **[docs/](docs/)** - Full documentation
- **[gm/](gm/)** - GM resources
- **[players/](players/)** - Player guides

---

## 🎯 Key Features

### 630 Floor-Specific Events
Every event tied to actual dungeon lore:
- Floor 1: Mitflit chaos
- Floor 2: Morlock darkness
- Floor 3: Ghoul library
- Floor 4: Belcorra's quarters
- Floor 5: The Arena
- Floor 6: Fleshwarp labs
- Floor 7: Infernal prison
- Floor 8: Bog mummy crypts
- Floor 9: Darklands factions
- Floor 10: Serpentfolk temple

### Explicit Dice Mechanics
Every choice clearly states:
- "ADD 3 DICE TO JAR" (30 minutes)
- "ADD 1 DIE TO JAR" (10 minutes)
- "NO DICE" (instant)

### Meaningful Choices
- Risk vs reward
- Greed vs speed
- Knowledge vs time
- Honor vs pragmatism

---

## ✨ Tips for Success

### For GMs
- Reward creativity generously
- Track consequences visibly
- Make time pressure real
- Let players avoid combat through cleverness

### For Players
- Use ALL your skills
- Make meaningful choices
- Be creative
- Time matters - balance thoroughness vs speed

---

## 🎉 Ready to Play!

Your dungeon is enhanced and ready. Roll those dice! 🎲

**Questions?** Check [README.md](README.md) or the docs folder.

---

**The dungeon is alive. The choices matter. Have fun!**
