"""
ClipKeeper - Keyboard shortcuts window.
"""

import gettext
import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk

_ = gettext.gettext


class ShortcutsWindow(Gtk.ShortcutsWindow):
    """Keyboard shortcuts help window."""
    
    def __init__(self):
        super().__init__()
        
        self.set_modal(True)
        
        # Create shortcuts section
        section = Gtk.ShortcutsSection()
        section.set_title(_("ClipKeeper"))
        section.set_visible(True)
        
        # Application group
        app_group = Gtk.ShortcutsGroup()
        app_group.set_title(_("Application"))
        app_group.set_visible(True)
        
        # Show/Hide ClipKeeper
        show_shortcut = Gtk.ShortcutsShortcut()
        show_shortcut.set_title(_("Show/Hide ClipKeeper"))
        show_shortcut.set_accelerator("&lt;Ctrl&gt;&lt;Shift&gt;V")
        show_shortcut.set_visible(True)
        app_group.add(show_shortcut)
        
        # Quit
        quit_shortcut = Gtk.ShortcutsShortcut()
        quit_shortcut.set_title(_("Quit"))
        quit_shortcut.set_accelerator("&lt;Ctrl&gt;Q")
        quit_shortcut.set_visible(True)
        app_group.add(quit_shortcut)
        
        section.add(app_group)
        
        # Navigation group
        nav_group = Gtk.ShortcutsGroup()
        nav_group.set_title(_("Navigation"))
        nav_group.set_visible(True)
        
        # Search
        search_shortcut = Gtk.ShortcutsShortcut()
        search_shortcut.set_title(_("Search History"))
        search_shortcut.set_accelerator("&lt;Ctrl&gt;F")
        search_shortcut.set_visible(True)
        nav_group.add(search_shortcut)
        
        # Show shortcuts
        shortcuts_shortcut = Gtk.ShortcutsShortcut()
        shortcuts_shortcut.set_title(_("Show Keyboard Shortcuts"))
        shortcuts_shortcut.set_accelerator("&lt;Ctrl&gt;question")
        shortcuts_shortcut.set_visible(True)
        nav_group.add(shortcuts_shortcut)
        
        section.add(nav_group)
        
        # Clipboard group
        clip_group = Gtk.ShortcutsGroup()
        clip_group.set_title(_("Clipboard"))
        clip_group.set_visible(True)
        
        # Copy entry
        copy_shortcut = Gtk.ShortcutsShortcut()
        copy_shortcut.set_title(_("Copy Selected Entry"))
        copy_shortcut.set_accelerator("Return space")
        copy_shortcut.set_visible(True)
        clip_group.add(copy_shortcut)
        
        section.add(clip_group)
        
        self.add(section)