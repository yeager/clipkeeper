"""
ClipKeeper - Preferences window.
"""

import gettext
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

_ = gettext.gettext


class PreferencesWindow(Adw.PreferencesWindow):
    """Preferences window for ClipKeeper."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        
        self.set_title(_("Preferences"))
        self.set_default_size(600, 500)
        
        # General preferences page
        general_page = Adw.PreferencesPage()
        general_page.set_title(_("General"))
        general_page.set_icon_name("preferences-system-symbolic")
        
        # Clipboard group
        clipboard_group = Adw.PreferencesGroup()
        clipboard_group.set_title(_("Clipboard"))
        clipboard_group.set_description(_("Configure clipboard monitoring and history"))
        
        # Max history size
        max_history_row = Adw.SpinRow.new_with_range(50, 2000, 10)
        max_history_row.set_title(_("Maximum History Size"))
        max_history_row.set_subtitle(_("Number of clipboard entries to keep"))
        max_history_row.set_value(self.app.settings['max_history_size'])
        max_history_row.connect("value-changed", self.on_max_history_changed)
        clipboard_group.add(max_history_row)
        
        # Auto-start
        auto_start_row = Adw.SwitchRow()
        auto_start_row.set_title(_("Start with System"))
        auto_start_row.set_subtitle(_("Automatically start ClipKeeper when you log in"))
        auto_start_row.set_active(self.app.settings['auto_start'])
        auto_start_row.connect("notify::active", self.on_auto_start_changed)
        clipboard_group.add(auto_start_row)
        
        # System tray
        tray_row = Adw.SwitchRow()
        tray_row.set_title(_("Show Tray Indicator"))
        tray_row.set_subtitle(_("Show ClipKeeper in the system tray"))
        tray_row.set_active(self.app.settings['show_tray_indicator'])
        tray_row.connect("notify::active", self.on_tray_changed)
        clipboard_group.add(tray_row)
        
        general_page.add(clipboard_group)
        
        # Appearance group
        appearance_group = Adw.PreferencesGroup()
        appearance_group.set_title(_("Appearance"))
        
        # Theme selection
        theme_row = Adw.ComboRow()
        theme_row.set_title(_("Theme"))
        theme_row.set_subtitle(_("Choose the application theme"))
        
        theme_model = Gtk.StringList()
        theme_model.append(_("Follow System"))
        theme_model.append(_("Light"))
        theme_model.append(_("Dark"))
        theme_row.set_model(theme_model)
        
        # Set current selection
        theme_map = {'auto': 0, 'light': 1, 'dark': 2}
        current_theme = self.app.settings.get('theme', 'auto')
        theme_row.set_selected(theme_map.get(current_theme, 0))
        
        theme_row.connect("notify::selected", self.on_theme_changed)
        appearance_group.add(theme_row)
        
        general_page.add(appearance_group)
        
        # Actions group
        actions_group = Adw.PreferencesGroup()
        actions_group.set_title(_("Actions"))
        
        # Clear history button
        clear_row = Adw.ActionRow()
        clear_row.set_title(_("Clear Clipboard History"))
        clear_row.set_subtitle(_("Remove all clipboard entries except pinned ones"))
        
        clear_button = Gtk.Button()
        clear_button.set_label(_("Clear"))
        clear_button.set_valign(Gtk.Align.CENTER)
        clear_button.add_css_class("destructive-action")
        clear_button.connect("clicked", self.on_clear_history)
        clear_row.add_suffix(clear_button)
        
        actions_group.add(clear_row)
        general_page.add(actions_group)
        
        self.add(general_page)
        
        # Keyboard shortcuts page
        shortcuts_page = Adw.PreferencesPage()
        shortcuts_page.set_title(_("Keyboard Shortcuts"))
        shortcuts_page.set_icon_name("preferences-desktop-keyboard-shortcuts-symbolic")
        
        shortcuts_group = Adw.PreferencesGroup()
        shortcuts_group.set_title(_("Shortcuts"))
        shortcuts_group.set_description(_("Keyboard shortcuts for ClipKeeper"))
        
        # List of shortcuts
        shortcuts = [
            (_("Show/Hide ClipKeeper"), "Ctrl+Shift+V"),
            (_("Search History"), "Ctrl+F"),
            (_("Show Shortcuts"), "Ctrl+?"),
            (_("Quit"), "Ctrl+Q")
        ]
        
        for title, shortcut in shortcuts:
            row = Adw.ActionRow()
            row.set_title(title)
            
            shortcut_label = Gtk.Label()
            shortcut_label.set_text(shortcut)
            shortcut_label.add_css_class("dim-label")
            shortcut_label.set_valign(Gtk.Align.CENTER)
            row.add_suffix(shortcut_label)
            
            shortcuts_group.add(row)
            
        shortcuts_page.add(shortcuts_group)
        self.add(shortcuts_page)
        
    def on_max_history_changed(self, spin_row):
        """Handle max history size change."""
        self.app.settings['max_history_size'] = int(spin_row.get_value())
        self.app.save_settings()
        
    def on_auto_start_changed(self, switch_row, param):
        """Handle auto-start setting change."""
        self.app.settings['auto_start'] = switch_row.get_active()
        self.app.save_settings()
        
        # TODO: Actually implement auto-start functionality
        # This would involve creating/removing a .desktop file in ~/.config/autostart/
        
    def on_tray_changed(self, switch_row, param):
        """Handle tray indicator setting change."""
        self.app.settings['show_tray_indicator'] = switch_row.get_active()
        self.app.save_settings()
        
        # TODO: Implement tray indicator
        
    def on_theme_changed(self, combo_row, param):
        """Handle theme change."""
        selected = combo_row.get_selected()
        theme_map = {0: 'auto', 1: 'light', 2: 'dark'}
        theme = theme_map.get(selected, 'auto')
        
        self.app.settings['theme'] = theme
        self.app.save_settings()
        
        # Apply theme change
        style_manager = Adw.StyleManager.get_default()
        if theme == 'light':
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif theme == 'dark':
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
            
    def on_clear_history(self, button):
        """Handle clear history button click."""
        self.app.activate_action("clear-history")