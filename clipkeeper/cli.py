"""
ClipKeeper - Command line interface.
"""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .clipboard_entry import ClipboardEntry


def load_history():
    """Load clipboard history from file."""
    data_dir = Path.home() / '.local' / 'share' / 'clipkeeper'
    history_file = data_dir / 'history.json'
    
    if not history_file.exists():
        return []
        
    try:
        with open(history_file, 'r') as f:
            data = json.load(f)
            return [ClipboardEntry.from_dict(item) for item in data.get('entries', [])]
    except Exception as e:
        print(f"Error loading history: {e}")
        return []


def clear_history():
    """Clear clipboard history."""
    data_dir = Path.home() / '.local' / 'share' / 'clipkeeper'
    history_file = data_dir / 'history.json'
    
    try:
        # Keep only pinned entries
        entries = load_history()
        pinned_entries = [e for e in entries if e.pinned]
        
        data = {
            'entries': [entry.to_dict() for entry in pinned_entries]
        }
        
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Cleared history, kept {len(pinned_entries)} pinned entries")
        
    except Exception as e:
        print(f"Error clearing history: {e}")
        return 1
        
    return 0


def list_history():
    """List clipboard history."""
    entries = load_history()
    
    if not entries:
        print("No clipboard history found")
        return 0
        
    print(f"Clipboard History ({len(entries)} entries):")
    print("-" * 50)
    
    for i, entry in enumerate(entries, 1):
        pin_marker = "📌 " if entry.pinned else "   "
        type_name = entry.get_type_name()
        timestamp = entry.get_timestamp_display()
        content_preview = entry.get_display_content(60)
        
        print(f"{pin_marker}{i:3d}. [{type_name:5s}] {content_preview}")
        print(f"       {timestamp}")
        print()
        
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ClipKeeper - GTK4 clipboard manager for Linux",
        prog="clipkeeper"
    )
    
    parser.add_argument(
        "--version",
        action="version", 
        version=f"ClipKeeper {__version__}"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear clipboard history (keeps pinned entries)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true", 
        help="List current clipboard history"
    )
    
    args = parser.parse_args()
    
    if args.clear:
        return clear_history()
    elif args.list:
        return list_history()
    else:
        # Launch GUI application
        from .application import main as gui_main
        return gui_main()


if __name__ == "__main__":
    sys.exit(main())