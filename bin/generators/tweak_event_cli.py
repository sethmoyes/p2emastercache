#!/usr/bin/env python3
"""
CLI interface for the Dungeon Event Tweaker.

Usage:
    python tweak_event_cli.py event.json
    python tweak_event_cli.py event.json --format markdown
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dungeon_event_tweaker import EventTweaker, InvalidEventError, TweakerError


def main():
    parser = argparse.ArgumentParser(
        description="Adapt dungeon turn events to different spatial contexts"
    )
    parser.add_argument(
        'event_file',
        help='Path to JSON file containing event data'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    
    args = parser.parse_args()
    
    # Load event data
    try:
        with open(args.event_file, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.event_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate variations
    tweaker = EventTweaker()
    try:
        if args.format == 'json':
            result = tweaker.tweak_event(event_data, output_format='dict')
            print(json.dumps(result, indent=2))
        else:
            result = tweaker.tweak_event(event_data, output_format='markdown')
            print(result)
    except InvalidEventError as e:
        print(f"Error: Invalid event data: {e}", file=sys.stderr)
        sys.exit(1)
    except TweakerError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
