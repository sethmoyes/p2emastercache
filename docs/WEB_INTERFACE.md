# Dungeon Turn V2 - Web Interface 🎲

## What Is This?

A **beautiful web app** that generates random dungeon encounters at your table!

Instead of looking up pre-generated events in a markdown file, you get:
- 🎲 **Click to roll** 5d20 with animations
- ⚡ **Instant random encounters** - different every time
- 🎨 **Gorgeous UI** with Tailwind CSS
- 📊 **Dice jar tracker** - visual counter
- 📜 **Roll history** - see your last 10 encounters

## Quick Start

```bash
# 1. Install Flask (one time)
pip3 install Flask

# 2. Start the server
./bin/web/start.sh

# 3. Open browser
http://localhost:5000
```

That's it! 🎉

## Screenshots

### Main Interface
```
┌─────────────────────────────────────────────┐
│         🎲 Dungeon Turn V2 🎲               │
│   Roll the dice jar and discover what      │
│            happens!                         │
├─────────────────────────────────────────────┤
│  Dice Jar: 🎲 🎲 🎲 ⚫ ⚫  [+ Add] [Reset] │
│  3/5 dice in jar. 2 more until roll.       │
├─────────────────────────────────────────────┤
│  Current Floor:                             │
│  [1] [2] [3] [4] [5] [6] [7] [8] [9] [10] │
│  The Library                                │
├─────────────────────────────────────────────┤
│         🎲 ROLL THE DICE JAR 🎲            │
│                                             │
│  Results: [18] [12] [7] [15] [3]          │
│  Total: 55                                  │
└─────────────────────────────────────────────┘
```

### Encounter Display
```
┌─────────────────────────────────────────────┐
│  Sum: 55 | DILEMMA                         │
│                                             │
│  🔵 Two Paths: Loud vs Quiet               │
│                                             │
│  The passage splits. Left: wide corridor   │
│  (fast but exposed). Right: narrow tunnels │
│  (slow but hidden).                        │
│                                             │
│  Choice A: Take loud path (10 min, but    │
│  next encounter is alerted)                │
│                                             │
│  Choice B: Take quiet path (30 min, add   │
│  2 dice, but surprise round)               │
│                                             │
│  ⚠️ GM Notes: Track choice. Loud = enemies│
│  get surprise. Quiet = party gets surprise │
└─────────────────────────────────────────────┘
```

## How to Use at the Table

### Step 1: Track Time
As players explore, click **"+ Add Die"** every 10 minutes:
- Searching a room thoroughly → Add die
- Treating wounds → Add die
- Picking locks → Add die
- Any 10-minute activity → Add die

### Step 2: Roll When Full
When jar reaches **5 dice**:
1. Select current floor (1-10)
2. Click **"ROLL THE DICE JAR"**
3. Watch the dice roll!

### Step 3: Get Random Encounter
The app instantly generates:
- Random event from appropriate category
- All details you need
- GM notes and consequences
- Tactical options

### Step 4: Run the Encounter
Read it to your players and play it out!

### Step 5: Repeat
Jar resets automatically. Keep exploring!

## Features

### Dice Jar Tracker
- Visual display (🎲 = filled, ⚫ = empty)
- Add dice with one click
- Reset button
- Warning when full

### Floor Selector
- Buttons for all 10 floors
- Shows floor name
- Easy to switch
- Correctly filters events by floor

### Event Filters (Collapsible)
- Filter by event type (Opportunity, Complication, Dilemma, Active Threat, Combat)
- Collapsible section to save screen space
- Starts collapsed by default
- Click header to expand/collapse
- Rotating arrow icon indicates state

### Dice Roller
- Animated button
- Shows individual d20 results
- Displays total
- Generates encounter instantly

### Encounter Display
Color-coded by category:
- 🟢 **Green** = Opportunities (rewards creativity)
- 🟡 **Yellow** = Complications (force skill use)
- 🔵 **Blue** = Dilemmas (meaningful choices)
- 🔴 **Red** = Active Threats (immediate danger)
- 🟣 **Purple** = Combat (living dungeon)

Shows all event fields:
- **OPPORTUNITY/COMPLICATION:** reward, spotlight, consequence
- **DILEMMA:** skills, time_cost, consequence, spotlight, context
- **ACTIVE_THREAT:** skills, threat_level, spotlight, creatures
- **Prepared tokens:** Visible in reward field when applicable

### Roll History
- Last 10 rolls shown
- Floor, title, category, sum
- Clear button
- Helps track session

## Why Use This Instead of Static File?

### Web Interface Advantages
✅ **True randomness** - Different every time
✅ **Can't be memorized** - Players can't learn patterns
✅ **Beautiful UI** - More engaging than markdown
✅ **Dice jar built-in** - Visual tracker
✅ **Roll history** - Automatic tracking
✅ **Fun to use** - Players love clicking the button

### Static File Advantages
✅ **No tech needed** - Works anywhere
✅ **Can review ahead** - See all events
✅ **Instant lookup** - No loading time
✅ **Printable** - Take to table on paper

### When to Use Each

**Use Web Interface if:**
- You have laptop/tablet at table
- You want true randomness
- Players enjoy tech at table
- You like visual trackers

**Use Static File if:**
- Low-tech table
- Want to prep/review ahead
- Prefer paper/PDF
- Tech makes you nervous

## Technical Details

### Stack
- **Backend:** Flask (Python web framework)
- **Frontend:** HTML + Tailwind CSS + JavaScript
- **Data:** Same generator as CLI version

### How It Works
1. Flask server loads dungeon data at startup
2. Browser connects to http://localhost:5000
3. Click "Roll" → JavaScript calls `/api/roll`
4. Server generates random encounter
5. JavaScript displays it beautifully
6. All in ~1 second!

### True Randomness
- Each roll picks random template
- Same sum can give different events
- Infinite variety
- Uses same logic as CLI generator

## Installation

### Requirements
- Python 3
- Flask

### Install Flask
```bash
pip3 install Flask
```

### Start Server
```bash
# Easy way (auto-installs Flask)
./bin/web/start.sh

# Manual way
python3 bin/web/dungeon_turn_app.py
```

### Access
Open browser to: **http://localhost:5000**

## Customization

### Change Party Level
Edit `templates/index.html` line 16:
```javascript
let partyLevel = 4;  // Change this
```

### Change Port
Edit `dungeon_turn_app.py` line 73:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port
```

### Change Colors
Edit `templates/index.html` - search for color classes:
- `bg-purple-600` → Change purple theme
- `from-gray-900` → Change background
- `text-white` → Change text color

## Troubleshooting

### "Module 'flask' not found"
```bash
pip3 install Flask
```

### "Port 5000 already in use"
Change port in `dungeon_turn_app.py` or kill other process:
```bash
lsof -ti:5000 | xargs kill
```

### Can't access from other devices
1. Find your IP: `ifconfig` or `ipconfig`
2. Open firewall port 5000
3. Access via: `http://YOUR_IP:5000`

### Slow loading
- First load takes 2-3 seconds (loading data)
- Keep browser tab open
- Subsequent rolls are instant

---

## Players Page - Interactive Otari Map

The players page (`/players`) features an interactive, high-resolution map of Otari that players can explore on any device.

### Features
- **High-resolution map:** 18MB ultra-high-res image for crystal-clear detail
- **Touch gestures:** Pinch to zoom, drag to pan (perfect for phones/tablets)
- **Mouse controls:** Scroll to zoom, drag to pan, double-click to reset
- **Zoom controls:** +, -, and reset buttons for easy navigation
- **Smooth animations:** Fluid zooming and panning experience
- **Zoom range:** 1x (full view) to 5x (extreme detail)

### How to Use

**On Mobile/Tablet:**
- Pinch with two fingers to zoom in/out
- Drag with one finger to pan around
- Tap zoom buttons (+/-) for precise control
- Double-tap to reset to full view

**On Desktop:**
- Scroll mouse wheel to zoom in/out
- Click and drag to pan around
- Click zoom buttons (+/-) for precise control
- Double-click to reset to full view

### Why This Rocks
- Players can explore Otari in detail during downtime
- Perfect for planning shopping trips or finding locations
- Works great on phones at the table
- No need to pass around a physical map
- Everyone can zoom in on their own device

### Technical Details
- **Library:** Panzoom v4.5.1
- **Image:** `/static/otari.big.webp` (18MB)
- **Container:** Overflow hidden with grab cursor
- **Controls:** Positioned bottom-right, always visible
- **Instructions:** Displayed below map

---

## Troubleshooting

### "Module 'flask' not found"
```bash
pip3 install Flask
```

### "Port 5000 already in use"
Change port in `dungeon_turn_app.py` or kill other process:
```bash
lsof -ti:5000 | xargs kill
```

### Can't access from other devices
1. Find your IP: `ifconfig` or `ipconfig`
2. Open firewall port 5000
3. Access via: `http://YOUR_IP:5000`

### Slow loading
- First load takes 2-3 seconds (loading data)
- Keep browser tab open
- Subsequent rolls are instant

## Tips

### For In-Person Games
- Keep laptop open at table
- Let players click "Roll" button
- Build tension as jar fills
- Everyone sees results together

### For Online Games
- Share screen with players
- They see dice roll live
- More engaging than reading markdown
- Visual dice jar creates urgency

### For Solo Prep
- Generate encounters ahead
- Take screenshots
- Test different floors
- Get feel for variety

## Future Ideas

Possible enhancements:
- ✅ Collapsible event filters (DONE - Feb 2026)
- ✅ Enhanced event display with all fields (DONE - Feb 2026)
- ✅ Interactive Otari map for players (DONE - Feb 2026)
- Sound effects for rolls
- Save/load sessions
- Export to PDF
- Mobile app version
- Encounter notes
- Statistics tracking
- Custom templates
- Prepared token tracker widget
- Multiple party support

## Comparison

| Feature | Web Interface | Static File |
|---------|--------------|-------------|
| Randomness | ✅ True | ❌ Pre-generated |
| Tech Required | ❌ Yes | ✅ No |
| Visual Appeal | ✅ Beautiful | ⚫ Plain text |
| Dice Jar Tracker | ✅ Built-in | ❌ Manual |
| Roll History | ✅ Automatic | ❌ Manual |
| Event Filters | ✅ Collapsible | ❌ None |
| Floor Filtering | ✅ Accurate | ✅ Yes |
| Prepared Tokens | ✅ Displayed | ✅ Documented |
| Interactive Map | ✅ Players page | ❌ No |
| Can Review Ahead | ❌ No | ✅ Yes |
| Printable | ❌ No | ✅ Yes |
| Fun Factor | ✅ High | ⚫ Medium |

## The Bottom Line

**Web Interface = Dynamic, engaging, tech-friendly**

Perfect for tables that:
- Have laptop/tablet available
- Enjoy tech integration
- Want true randomness
- Like visual trackers

**Try it!** It takes 2 minutes to set up and makes dungeons way more fun! 🎲

---

**Questions?** See `bin/web/README.md` for full technical docs.
