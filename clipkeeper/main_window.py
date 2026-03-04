"""
ClipKeeper - Main window implementation.
"""

import gettext
from typing import List

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GObject

from .clipboard_entry import ClipboardEntry

_ = gettext.gettext


class ClipboardEntryRow(Gtk.ListBoxRow):
    """A row widget for displaying clipboard entries."""
    
    def __init__(self, entry: ClipboardEntry):
        super().__init__()
        self.entry = entry
        
        # Main box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        
        # Type icon
        icon = Gtk.Image.new_from_icon_name(entry.get_type_icon())
        icon.set_icon_size(Gtk.IconSize.NORMAL)
        box.append(icon)
        
        # Content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        content_box.set_hexpand(True)
        
        # Content label
        content_label = Gtk.Label()
        content_label.set_text(entry.get_display_content(80))
        content_label.set_halign(Gtk.Align.START)
        content_label.set_ellipsize(3)  # ELLIPSIZE_END
        content_label.add_css_class("title")
        content_box.append(content_label)
        
        # Metadata box
        meta_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Type label
        type_label = Gtk.Label()
        type_label.set_text(entry.get_type_name())
        type_label.set_halign(Gtk.Align.START)
        type_label.add_css_class("dim-label")
        type_label.add_css_class("caption")
        meta_box.append(type_label)
        
        # Separator
        separator = Gtk.Label()
        separator.set_text("•")
        separator.add_css_class("dim-label")
        meta_box.append(separator)
        
        # Timestamp label
        time_label = Gtk.Label()
        time_label.set_text(entry.get_timestamp_display())
        time_label.set_halign(Gtk.Align.START)
        time_label.add_css_class("dim-label")
        time_label.add_css_class("caption")
        meta_box.append(time_label)
        
        content_box.append(meta_box)
        box.append(content_box)
        
        # Pin button
        pin_button = Gtk.Button()
        pin_button.set_icon_name("starred-symbolic" if entry.pinned else "non-starred-symbolic")
        pin_button.set_valign(Gtk.Align.CENTER)
        pin_button.add_css_class("flat")
        pin_button.connect("clicked", self.on_pin_clicked)
        box.append(pin_button)
        
        self.pin_button = pin_button
        self.set_child(box)
        
    def on_pin_clicked(self, button):
        """Handle pin button click."""
        self.entry.pinned = not self.entry.pinned
        button.set_icon_name("starred-symbolic" if self.entry.pinned else "non-starred-symbolic")
        
        # Emit signal to parent window
        window = self.get_root()
        if hasattr(window, 'on_entry_pinned'):
            window.on_entry_pinned(self.entry)


class MainWindow(Adw.ApplicationWindow):
    """Main application window."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.app = self.get_application()
        self.current_entries: List[ClipboardEntry] = []
        
        # Window setup
        self.set_title("ClipKeeper")
        self.set_default_size(600, 700)
        
        # Header bar
        header_bar = Adw.HeaderBar()
        
        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(self.create_menu_model())
        header_bar.pack_end(menu_button)
        
        # Clear button
        clear_button = Gtk.Button()
        clear_button.set_icon_name("user-trash-symbolic")
        clear_button.set_tooltip_text(_("Clear History"))
        clear_button.connect("clicked", lambda *_: self.app.activate_action("clear-history"))
        header_bar.pack_end(clear_button)
        
        # Use ToolbarView for Adw.ApplicationWindow
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header_bar)
        
        # Main content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Search bar
        search_bar = Gtk.SearchBar()
        search_entry = Gtk.SearchEntry()
        search_entry.set_hexpand(True)
        search_entry.set_placeholder_text(_("Search clipboard history..."))
        search_entry.connect("search-changed", self.on_search_changed)
        search_bar.set_child(search_entry)
        search_bar.connect_entry(search_entry)
        
        # Connect Ctrl+F to search
        search_action = Gio.SimpleAction.new("search", None)
        search_action.connect("activate", lambda *_: search_bar.set_search_mode(True))
        self.add_action(search_action)
        
        shortcut_controller = Gtk.ShortcutController()
        shortcut = Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string("<Ctrl>f"),
            Gtk.NamedAction.new("win.search")
        )
        shortcut_controller.add_shortcut(shortcut)
        self.add_controller(shortcut_controller)
        
        main_box.append(search_bar)
        
        # History list
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.connect("row-activated", self.on_row_activated)
        self.list_box.add_css_class("boxed-list")
        
        scrolled_window.set_child(self.list_box)
        main_box.append(scrolled_window)
        
        # Status bar
        self.status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.status_bar.set_margin_start(12)
        self.status_bar.set_margin_end(12)
        self.status_bar.set_margin_top(8)
        self.status_bar.set_margin_bottom(8)
        
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_hexpand(True)
        self.status_label.add_css_class("dim-label")
        self.status_bar.append(self.status_label)
        
        main_box.append(Gtk.Separator())
        main_box.append(self.status_bar)
        
        # Store references
        self.search_entry = search_entry
        self.search_bar = search_bar
        
        toolbar_view.set_content(main_box)
        self.set_content(toolbar_view)
        
        # Update the view
        self.update_history_view()
        
    def create_menu_model(self):
        """Create the main menu model."""
        menu = Gio.Menu()
        
        menu.append(_("Preferences"), "app.preferences")
        menu.append(_("Keyboard Shortcuts"), "app.shortcuts")
        menu.append(_("About ClipKeeper"), "app.about")
        
        return menu
        
    def update_history_view(self):
        """Update the history list view."""
        # Clear existing rows
        child = self.list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.list_box.remove(child)
            child = next_child
            
        # Get entries to display
        query = self.search_entry.get_text().strip()
        if query:
            entries = self.app.search_entries(query)
        else:
            entries = self.app.get_entries()
            
        self.current_entries = entries
        
        # Add empty state if no entries
        if not entries:
            if query:
                self.show_empty_search_state()
            else:
                self.show_empty_history_state()
        else:
            # Add entry rows
            for entry in entries:
                row = ClipboardEntryRow(entry)
                self.list_box.append(row)
                
        # Update status
        self.update_status_bar()
        
    def show_empty_history_state(self):
        """Show empty state when no clipboard history."""
        status_page = Adw.StatusPage()
        status_page.set_title(_("No Clipboard History"))
        status_page.set_description(_("Your clipboard history will appear here as you copy text and other content."))
        status_page.set_icon_name("edit-copy-symbolic")
        
        clamp = Adw.Clamp()
        clamp.set_child(status_page)
        
        self.list_box.append(clamp)
        
    def show_empty_search_state(self):
        """Show empty state when search has no results."""
        status_page = Adw.StatusPage()
        status_page.set_title(_("No Results"))
        status_page.set_description(_("Try a different search term."))
        status_page.set_icon_name("edit-find-symbolic")
        
        clamp = Adw.Clamp()
        clamp.set_child(status_page)
        
        self.list_box.append(clamp)
        
    def update_status_bar(self):
        """Update the status bar with current info."""
        total_entries = len(self.app.entries)
        pinned_entries = len(self.app.pinned_entries)
        displayed_entries = len(self.current_entries)
        
        if self.search_entry.get_text().strip():
            status_text = _("{} of {} entries").format(displayed_entries, total_entries)
        else:
            status_text = _("{} entries").format(total_entries)
            
        if pinned_entries > 0:
            status_text += _(", {} pinned").format(pinned_entries)
            
        self.status_label.set_text(status_text)
        
    def on_search_changed(self, search_entry):
        """Handle search text changes."""
        self.update_history_view()
        
    def on_row_activated(self, list_box, row):
        """Handle row activation (copy to clipboard)."""
        if hasattr(row, 'entry'):
            self.app.copy_entry_to_clipboard(row.entry)
            
            # Show toast notification
            toast = Adw.Toast()
            toast.set_title(_("Copied to clipboard"))
            toast.set_timeout(2)
            
            # Find the toast overlay (we need to add one)
            # For now just print
            print("Copied to clipboard")
            
    def on_entry_pinned(self, entry: ClipboardEntry):
        """Handle entry pin/unpin."""
        if entry.pinned:
            self.app.add_pinned_entry(entry)
        else:
            self.app.remove_pinned_entry(entry)
            
        self.app.save_history()
        self.update_history_view()