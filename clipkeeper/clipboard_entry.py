"""
ClipKeeper - Clipboard entry data model.
"""

import time
from enum import Enum
from typing import Dict, Any
import hashlib


class ClipboardType(Enum):
    """Types of clipboard content."""
    TEXT = 0
    URL = 1
    CODE = 2
    IMAGE = 3
    COLOR = 4


class ClipboardEntry:
    """Represents a clipboard entry."""
    
    def __init__(self, content: str, content_type: ClipboardType, timestamp: float = None):
        self.content = content
        self.content_type = content_type
        self.timestamp = timestamp or time.time()
        self.pinned = False
        self.hash = self._calculate_hash()
        
    def _calculate_hash(self) -> str:
        """Calculate hash for content comparison."""
        return hashlib.sha256(self.content.encode()).hexdigest()[:16]
        
    def equals(self, other: 'ClipboardEntry') -> bool:
        """Check if two entries are equal based on content."""
        return self.hash == other.hash
        
    def get_display_content(self, max_length: int = 100) -> str:
        """Get truncated content for display."""
        if len(self.content) <= max_length:
            return self.content
            
        # For multi-line content, just show first line
        first_line = self.content.split('\n')[0]
        if len(first_line) <= max_length:
            return first_line + "..."
            
        return first_line[:max_length-3] + "..."
        
    def get_type_icon(self) -> str:
        """Get icon name for the content type."""
        icons = {
            ClipboardType.TEXT: "text-x-generic-symbolic",
            ClipboardType.URL: "emblem-web-symbolic", 
            ClipboardType.CODE: "text-x-script-symbolic",
            ClipboardType.IMAGE: "image-x-generic-symbolic",
            ClipboardType.COLOR: "applications-graphics-symbolic"
        }
        return icons.get(self.content_type, "text-x-generic-symbolic")
        
    def get_type_name(self) -> str:
        """Get human-readable type name."""
        names = {
            ClipboardType.TEXT: "Text",
            ClipboardType.URL: "URL",
            ClipboardType.CODE: "Code", 
            ClipboardType.IMAGE: "Image",
            ClipboardType.COLOR: "Color"
        }
        return names.get(self.content_type, "Text")
        
    def get_timestamp_display(self) -> str:
        """Get formatted timestamp for display."""
        now = time.time()
        diff = now - self.timestamp
        
        if diff < 60:
            return "Just now"
        elif diff < 3600:
            minutes = int(diff / 60)
            return f"{minutes} min ago"
        elif diff < 86400:
            hours = int(diff / 3600)
            return f"{hours}h ago"
        else:
            days = int(diff / 86400)
            return f"{days}d ago"
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            'content': self.content,
            'content_type': self.content_type.value,
            'timestamp': self.timestamp,
            'pinned': self.pinned,
            'hash': self.hash
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClipboardEntry':
        """Create entry from dictionary."""
        entry = cls(
            content=data['content'],
            content_type=ClipboardType(data['content_type']),
            timestamp=data.get('timestamp', time.time())
        )
        entry.pinned = data.get('pinned', False)
        entry.hash = data.get('hash', entry._calculate_hash())
        return entry