#!/bin/bash
# Startup script for Dungeon Turn V2 Web Interface

echo "=================================="
echo "Dungeon Turn V2 - Web Interface"
echo "=================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
elif [ -d "$HOME/boto3env" ]; then
    echo "🔧 Activating virtual environment..."
    source "$HOME/boto3env/bin/activate"
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask not installed!"
    echo ""
    echo "Installing Flask..."
    pip3 install Flask
    echo ""
fi

echo "✅ Flask is installed"
echo ""
echo "Starting server..."
echo "Open your browser to: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop"
echo "=================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory and start the app
cd "$SCRIPT_DIR"
python3 dungeon_turn_app.py
