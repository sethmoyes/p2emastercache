# Dungeon Turn V2 - Web Interface

A beautiful web interface for generating random dungeon encounters at the table!

## Features

- 🎲 **Dice Roller** - Click to roll 5d20 with animations
- 🏰 **Floor Selector** - Easy buttons for floors 1-10
- 📊 **Dice Jar Tracker** - Visual counter for exploration time
- 🎨 **Beautiful UI** - Tailwind CSS with dark theme
- 📜 **Roll History** - Track your last 10 encounters
- ⚡ **Instant Results** - Random encounters generated on-demand
- 🎯 **True Randomness** - Different every time!

## Installation

```bash
# Install Flask
pip install -r requirements.txt

# Or just:
pip install Flask
```

## Usage

```bash
# From the bin/web directory
python3 dungeon_turn_app.py

# Or from project root
python3 bin/web/dungeon_turn_app.py
```

Then open your browser to: **http://localhost:5000**

## How It Works

1. **Track Time** - Click "+ Add Die" every 10 minutes of exploration
2. **Roll When Full** - At 5 dice, click "ROLL THE DICE JAR"
3. **Get Random Encounter** - Instantly generates a unique event
4. **Run the Encounter** - All details displayed beautifully
5. **Repeat** - Jar resets, keep exploring!

## Features Explained

### Dice Jar Tracker
- Visual display of current dice count (0-5)
- Add dice as players explore
- Automatic reset after rolling
- Warning when jar is full

### Floor Selector
- Buttons for all 10 floors
- Shows current floor name
- Easy to switch between floors

### Dice Roller
- Animated roll button
- Shows individual d20 results
- Displays total sum
- Generates encounter instantly

### Encounter Display
- Color-coded by category:
  - 🟢 Green = Opportunities
  - 🟡 Yellow = Complications
  - 🔵 Blue = Dilemmas
  - 🔴 Red = Active Threats
  - 🟣 Purple = Combat
- All relevant details shown
- GM notes highlighted
- Scrolls into view automatically

### Roll History
- Last 10 rolls displayed
- Shows floor, title, category, sum
- Clear button to reset
- Helps track session flow

## Technical Details

### Stack
- **Backend:** Flask (Python)
- **Frontend:** HTML + Tailwind CSS + Vanilla JS
- **Data:** Uses same generator as CLI version

### API Endpoints
- `POST /api/roll` - Roll 5d20
- `POST /api/encounter` - Generate encounter
- `GET/POST /api/dice-jar` - Manage dice jar
- `GET /api/history` - Get roll history
- `POST /api/clear-history` - Clear history

### True Randomness
Unlike the static markdown file, this generates encounters **on-demand**:
- Same sum can give different events
- Infinite variety
- Never the same game twice
- Can't be memorized by players

## Customization

### Change Party Level
Edit line 16 in `dungeon_turn_app.py`:
```python
partyLevel = 4;  // Change to your party level
```

### Change Port
Edit line 73 in `dungeon_turn_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

### Styling
The UI uses Tailwind CSS via CDN. To customize:
- Edit colors in `templates/index.html`
- Modify the gradient backgrounds
- Change button styles
- Adjust spacing and sizing

## Tips for Use

### At the Table
1. Keep browser open on laptop/tablet
2. Click "+ Add Die" as players explore
3. When jar fills, let a player click "ROLL"
4. Read the encounter dramatically
5. Track consequences in notes

### For Online Games
1. Share screen with players
2. Let them see the dice roll
3. Build tension as jar fills
4. Everyone sees results together

### For Prep
1. Generate a few encounters ahead
2. Take screenshots for reference
3. Adapt on the fly
4. Trust the randomness!

## Troubleshooting

### Port Already in Use
```bash
# Use different port
python3 dungeon_turn_app.py --port 5001
```

### Can't Access from Other Devices
- Make sure firewall allows port 5000
- Use your computer's IP address: `http://192.168.1.X:5000`

### Slow Loading
- First load takes 2-3 seconds (loading data)
- Subsequent rolls are instant
- Keep browser tab open

## Comparison to Static File

### Web Interface Pros
✅ True randomness every roll
✅ Beautiful, interactive UI
✅ Dice jar tracker built-in
✅ Roll history automatic
✅ Can't be memorized
✅ Fun to use at table

### Web Interface Cons
❌ Requires Python + Flask
❌ Need laptop/tablet at table
❌ Can't review ahead
❌ Depends on tech working

### When to Use Each
- **Web Interface:** For dynamic, tech-friendly tables
- **Static File:** For low-tech, prep-heavy games

## Future Enhancements

Possible additions:
- [ ] Save/load sessions
- [ ] Export encounters to PDF
- [ ] Sound effects for rolls
- [ ] Mobile-optimized layout
- [ ] Dark/light theme toggle
- [ ] Custom party level selector
- [ ] Encounter notes/tags
- [ ] Statistics tracking

---

**Enjoy your living dungeon!** 🎲
