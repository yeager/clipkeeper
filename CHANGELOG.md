# Changelog

All notable changes to ClipKeeper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-03-04

### Added

**Core Features:**
- Clipboard history monitoring with GLib
- Support for text, URL, code, image, and color content types
- Configurable history size (50-2000 entries, default 500)
- Pin/unpin important clipboard entries
- Instant search through clipboard history

**User Interface:**
- Modern GTK4/Adwaita interface following GNOME HIG
- Dark/light theme support with system integration
- Welcome dialog on first run
- Status bar showing entry count and timestamps
- Empty state pages with helpful messages

**Keyboard Shortcuts:**
- Ctrl+Shift+V to show/hide main window
- Ctrl+F for search
- Ctrl+? to show keyboard shortcuts help
- Ctrl+Q to quit application

**System Integration:**
- .desktop file for application launcher
- Proper app ID and window class
- SVG application icon
- XDG data directory storage (~/.local/share/clipkeeper/)

**Configuration:**
- Preferences window with all settings
- JSON-based configuration storage
- Auto-start option
- System tray indicator option

**Command Line Interface:**
- `clipkeeper --version` to show version
- `clipkeeper --list` to list clipboard history
- `clipkeeper --clear` to clear history (keeps pinned)

**Internationalization:**
- gettext support for translations
- English source strings
- .pot file generation ready

**About Dialog:**
- Adw.AboutDialog with proper credits
- Copy Debug Info action
- License and contact information

**Build System:**
- Complete pyproject.toml configuration
- Debian packaging files (debian/)
- RPM spec file (rpm/)
- Man page (man/clipkeeper.1)

### Technical Details

**Architecture:**
- Modular Python codebase with clear separation
- Application class with proper GTK4/Adwaita patterns  
- Clipboard monitoring with change detection
- JSON storage for history and configuration
- Type detection for clipboard content

**Dependencies:**
- Python 3.9+
- PyGObject
- GTK 4.0
- libadwaita 1.0

**Data Storage:**
- History: ~/.local/share/clipkeeper/history.json
- Config: ~/.local/share/clipkeeper/config.json
- Follows XDG Base Directory specification