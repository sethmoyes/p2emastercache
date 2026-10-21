#!/bin/bash
# Run the web app locally on http://localhost:5001

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
cd "$ROOT"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

if ! python3 -c "import flask, requests, bs4" 2>/dev/null; then
    echo "Installing requirements..."
    pip3 install -r requirements.txt
fi

python3 bin/web/dungeon_turn_app.py
