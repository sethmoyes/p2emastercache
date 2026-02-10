# Installation Instructions

## Install Flask

You need Flask to run the web interface. Choose one method:

### Option 1: User Install (Recommended)
```bash
pip3 install --user Flask
```

### Option 2: Homebrew (if you prefer)
```bash
brew install pipx
pipx install flask
```

### Option 3: Virtual Environment (cleanest)
```bash
python3 -m venv venv
source venv/bin/activate
pip install Flask
```

## Run the App

### If you used Option 1 or 2:
```bash
./bin/web/start.sh
```

### If you used Option 3 (venv):
```bash
source venv/bin/activate
python3 bin/web/dungeon_turn_app.py
```

## Open Browser

Navigate to: **http://localhost:5000**

---

## Quick One-Liner

```bash
pip3 install --user Flask && ./bin/web/start.sh
```
