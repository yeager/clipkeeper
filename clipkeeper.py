#!/usr/bin/env python3
"""
ClipKeeper - GTK4 clipboard manager for Linux.

Main entry point script.
"""

import sys
from clipkeeper.cli import main

if __name__ == "__main__":
    sys.exit(main())