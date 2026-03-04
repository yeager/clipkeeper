#!/usr/bin/env python3
"""
ClipKeeper - GTK4 clipboard manager for Linux.

Module entry point for `python -m clipkeeper`.
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())