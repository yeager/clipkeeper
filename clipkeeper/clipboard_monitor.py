"""
ClipKeeper - Clipboard monitoring functionality.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')

from gi.repository import GObject, Gdk, GLib
from .clipboard_entry import ClipboardType


class ClipboardMonitor(GObject.Object):
    """Monitor clipboard changes."""
    
    __gsignals__ = {
        'clipboard-changed': (GObject.SignalFlags.RUN_FIRST, None, (str, int))
    }
    
    def __init__(self):
        super().__init__()
        self.clipboard = None
        self.last_content = None
        self.last_content_type = None
        self.monitoring = False
        
    def start_monitoring(self):
        """Start monitoring clipboard changes."""
        if self.monitoring:
            return
            
        self.clipboard = Gdk.Display.get_default().get_clipboard()
        self.monitoring = True
        
        # Start monitoring loop
        GLib.timeout_add(500, self.check_clipboard)
        
    def stop_monitoring(self):
        """Stop monitoring clipboard changes."""
        self.monitoring = False
        
    def check_clipboard(self):
        """Check if clipboard content has changed."""
        if not self.monitoring:
            return False
            
        try:
            # Check for text content first
            self.clipboard.read_text_async(None, self.on_text_read)
            
            # Check for image content
            formats = self.clipboard.get_formats()
            if formats and formats.contain_gtype(GObject.TYPE_BYTES):
                # Has image data
                pass  # We'll handle this separately if needed
                
        except Exception as e:
            print(f"Error checking clipboard: {e}")
            
        return True  # Continue monitoring
        
    def on_text_read(self, clipboard, result):
        """Handle text content read from clipboard."""
        try:
            text = clipboard.read_text_finish(result)
            if text and text != self.last_content:
                content_type = self.detect_content_type(text)
                self.last_content = text
                self.last_content_type = content_type
                self.emit('clipboard-changed', text, content_type.value)
        except Exception as e:
            # No text content or error
            pass
            
    def detect_content_type(self, content: str) -> ClipboardType:
        """Detect the type of clipboard content."""
        content = content.strip()
        
        if not content:
            return ClipboardType.TEXT
            
        # Check for URLs
        if (content.startswith(('http://', 'https://', 'ftp://', 'file://')) or
            content.startswith('www.') and '.' in content):
            return ClipboardType.URL
            
        # Check for color codes
        if (content.startswith('#') and len(content) in [4, 7, 9] and
            all(c in '0123456789ABCDEFabcdef' for c in content[1:])):
            return ClipboardType.COLOR
            
        if (content.startswith(('rgb(', 'rgba(', 'hsl(', 'hsla(')) and 
            content.endswith(')')):
            return ClipboardType.COLOR
            
        # Check for code (contains programming keywords or symbols)
        code_indicators = [
            'def ', 'function ', 'class ', 'import ', 'from ',
            'if __name__', 'return ', 'var ', 'let ', 'const ',
            '#!/', '<?php', '<!DOCTYPE', '<html', '<script',
            '{', '}', '[];', '&&', '||', '=>', '!=', '=='
        ]
        
        if any(indicator in content for indicator in code_indicators):
            return ClipboardType.CODE
            
        # Check for file paths
        if ('/' in content and 
            (content.startswith('/') or content.count('/') > 2)):
            return ClipboardType.TEXT  # Treat as text for now
            
        return ClipboardType.TEXT
        
    def set_clipboard_content(self, content: str, content_type: ClipboardType):
        """Set clipboard content (for pasting back)."""
        if self.clipboard:
            # Temporarily stop monitoring to avoid loop
            was_monitoring = self.monitoring
            self.monitoring = False
            
            self.clipboard.set(content)
            
            # Resume monitoring after a short delay
            if was_monitoring:
                GLib.timeout_add(100, lambda: setattr(self, 'monitoring', True))