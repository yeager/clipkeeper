"""
ClipKeeper - Main application class.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import gettext
import locale

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, Gdk, GLib, Gio

from . import __version__, __app_id__, __author__, __email__
from .clipboard_monitor import ClipboardMonitor
from .clipboard_entry import ClipboardEntry, ClipboardType
from .preferences_window import PreferencesWindow
from .shortcuts_window import ShortcutsWindow


# Set up gettext
locale.bindtextdomain('clipkeeper', '/usr/share/locale')
gettext.bindtextdomain('clipkeeper', '/usr/share/locale')
gettext.textdomain('clipkeeper')
_ = gettext.gettext


class ClipKeeperApplication(Adw.Application):
    """Main application class."""
    
    def __init__(self):
        super().__init__(application_id=__app_id__, 
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        
        self.main_window = None
        self.clipboard_monitor = None
        self.entries: List[ClipboardEntry] = []
        self.pinned_entries: List[ClipboardEntry] = []
        self.data_dir = Path.home() / '.local' / 'share' / 'clipkeeper'
        self.config_file = self.data_dir / 'config.json'
        self.history_file = self.data_dir / 'history.json'
        
        # Default settings
        self.settings = {
            'max_history_size': 500,
            'show_tray_indicator': True,
            'auto_start': False,
            'theme': 'auto'  # auto, light, dark
        }
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up actions
        self.setup_actions()
        
        # Load settings and history
        self.load_settings()
        self.load_history()
        
    def setup_actions(self):
        """Set up application actions."""
        # Quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])
        
        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)
        
        # Preferences action
        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences)
        self.add_action(preferences_action)
        
        # Show shortcuts action
        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self.on_shortcuts)
        self.add_action(shortcuts_action)
        self.set_accels_for_action("app.shortcuts", ["<Ctrl>question"])
        
        # Toggle window action
        toggle_action = Gio.SimpleAction.new("toggle-window", None)
        toggle_action.connect("activate", self.on_toggle_window)
        self.add_action(toggle_action)
        self.set_accels_for_action("app.toggle-window", ["<Ctrl><Shift>V"])
        
        # Clear history action
        clear_action = Gio.SimpleAction.new("clear-history", None)
        clear_action.connect("activate", self.on_clear_history)
        self.add_action(clear_action)
        
    def do_activate(self):
        """Called when the application is activated."""
        if not self.main_window:
            from .main_window import MainWindow
            self.main_window = MainWindow(application=self)
            
            # Start clipboard monitoring
            self.clipboard_monitor = ClipboardMonitor()
            self.clipboard_monitor.connect("clipboard-changed", self.on_clipboard_changed)
            self.clipboard_monitor.start_monitoring()
            
            # Show welcome dialog on first run
            if self.is_first_run():
                self.show_welcome_dialog()
                
        self.main_window.present()
        
    def do_startup(self):
        """Called when the application starts up."""
        Adw.Application.do_startup(self)
        
    def is_first_run(self) -> bool:
        """Check if this is the first run."""
        return not self.config_file.exists()
        
    def show_welcome_dialog(self):
        """Show welcome dialog on first run."""
        dialog = Adw.StatusPage()
        dialog.set_title(_("Welcome to ClipKeeper"))
        dialog.set_description(_("ClipKeeper will monitor your clipboard and save your clipboard history for easy access. Use Ctrl+Shift+V to quickly access your clipboard history."))
        dialog.set_icon_name("dialog-information-symbolic")
        
        welcome_window = Adw.Window()
        welcome_window.set_title(_("Welcome"))
        welcome_window.set_default_size(500, 400)
        welcome_window.set_content(dialog)
        welcome_window.set_transient_for(self.main_window)
        welcome_window.set_modal(True)
        welcome_window.present()
        
    def on_clipboard_changed(self, monitor, content, content_type):
        """Handle clipboard changes."""
        if not content:
            return
            
        # Create new clipboard entry
        entry = ClipboardEntry(content, content_type)
        
        # Don't add duplicates at the top
        if self.entries and self.entries[0].equals(entry):
            return
            
        # Remove any existing duplicate
        self.entries = [e for e in self.entries if not e.equals(entry)]
        
        # Add to beginning
        self.entries.insert(0, entry)
        
        # Trim to max size (don't trim pinned entries)
        max_size = self.settings['max_history_size']
        unpinned = [e for e in self.entries if not e.pinned]
        if len(unpinned) > max_size:
            # Keep pinned entries and trim unpinned
            self.entries = self.pinned_entries + unpinned[:max_size]
            
        # Update UI
        if self.main_window:
            self.main_window.update_history_view()
            
        # Save history
        self.save_history()
        
    def add_pinned_entry(self, entry: ClipboardEntry):
        """Add entry to pinned list."""
        entry.pinned = True
        if entry not in self.pinned_entries:
            self.pinned_entries.append(entry)
            
    def remove_pinned_entry(self, entry: ClipboardEntry):
        """Remove entry from pinned list."""
        entry.pinned = False
        if entry in self.pinned_entries:
            self.pinned_entries.remove(entry)
            
    def get_entries(self) -> List[ClipboardEntry]:
        """Get all entries (pinned first, then recent)."""
        pinned = [e for e in self.entries if e.pinned]
        unpinned = [e for e in self.entries if not e.pinned]
        return pinned + unpinned
        
    def search_entries(self, query: str) -> List[ClipboardEntry]:
        """Search entries by content."""
        if not query:
            return self.get_entries()
            
        query = query.lower()
        matches = []
        for entry in self.get_entries():
            if query in entry.content.lower():
                matches.append(entry)
        return matches
        
    def copy_entry_to_clipboard(self, entry: ClipboardEntry):
        """Copy an entry back to the clipboard."""
        if self.clipboard_monitor:
            self.clipboard_monitor.set_clipboard_content(entry.content, entry.content_type)
            
    def load_settings(self):
        """Load settings from config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
                
    def save_settings(self):
        """Save settings to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def load_history(self):
        """Load clipboard history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    
                for item_data in data.get('entries', []):
                    entry = ClipboardEntry.from_dict(item_data)
                    self.entries.append(entry)
                    if entry.pinned:
                        self.pinned_entries.append(entry)
                        
            except Exception as e:
                print(f"Error loading history: {e}")
                
    def save_history(self):
        """Save clipboard history to file."""
        try:
            data = {
                'entries': [entry.to_dict() for entry in self.entries[:self.settings['max_history_size']]]
            }
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
            
    def clear_history(self):
        """Clear all clipboard history."""
        self.entries = [e for e in self.entries if e.pinned]
        if self.main_window:
            self.main_window.update_history_view()
        self.save_history()
        
    def on_toggle_window(self, action, param):
        """Toggle main window visibility."""
        if self.main_window:
            if self.main_window.is_visible():
                self.main_window.set_visible(False)
            else:
                self.main_window.present()
                
    def on_about(self, action, param):
        """Show about dialog."""
        about_dialog = Adw.AboutDialog()
        about_dialog.set_application_name("ClipKeeper")
        about_dialog.set_application_icon(__app_id__)
        about_dialog.set_version(__version__)
        about_dialog.set_developer_name(__author__)
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_website("https://github.com/yeager/clipkeeper")
        about_dialog.set_issue_url("https://github.com/yeager/clipkeeper/issues")
        about_dialog.set_copyright("© 2024 Daniel Nylander")
        about_dialog.set_developers([f"{__author__} <{__email__}>"])
        
        # Add debug info action
        copy_debug_action = Gio.SimpleAction.new("copy-debug-info", None)
        copy_debug_action.connect("activate", self.copy_debug_info)
        about_dialog.add_action(copy_debug_action)
        
        about_dialog.present(self.main_window)
        
    def copy_debug_info(self, action, param):
        """Copy debug information to clipboard."""
        import platform
        debug_info = f"""ClipKeeper Debug Information
Version: {__version__}
Python: {platform.python_version()}
GTK: {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}
Platform: {platform.platform()}
Entries: {len(self.entries)}
Pinned: {len(self.pinned_entries)}
"""
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(debug_info)
        
    def on_preferences(self, action, param):
        """Show preferences window."""
        prefs_window = PreferencesWindow(self)
        prefs_window.set_transient_for(self.main_window)
        prefs_window.present()
        
    def on_shortcuts(self, action, param):
        """Show keyboard shortcuts window."""
        shortcuts_window = ShortcutsWindow()
        shortcuts_window.set_transient_for(self.main_window)
        shortcuts_window.present()
        
    def on_clear_history(self, action, param):
        """Show confirmation dialog and clear history."""
        dialog = Adw.MessageDialog()
        dialog.set_heading(_("Clear Clipboard History"))
        dialog.set_body(_("Are you sure you want to clear all clipboard history? Pinned entries will be kept."))
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("clear", _("Clear"))
        dialog.set_response_appearance("clear", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        
        dialog.connect("response", self.on_clear_history_response)
        dialog.present(self.main_window)
        
    def on_clear_history_response(self, dialog, response):
        """Handle clear history dialog response."""
        if response == "clear":
            self.clear_history()


def main():
    """Main application entry point."""
    app = ClipKeeperApplication()
    return app.run(sys.argv)