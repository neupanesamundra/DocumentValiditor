"""
Change tracking system for document autocorrect
Tracks every modification made to documents
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class DocumentChange:
    """Represents a single change made to a document"""
    change_type: str  # "phrase", "section_added", "grammar", "reorder", "spelling"
    original: str
    corrected: str
    location: str = ""  # section name or "global"


@dataclass
class ChangeLog:
    """Tracks all changes made during document improvement"""
    changes: List[DocumentChange] = field(default_factory=list)
    document_type: str = ""
    original_text: str = ""
    corrected_text: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def add(self, change_type: str, original: str, corrected: str, location: str = ""):
        """Add a change to the log"""
        self.changes.append(DocumentChange(change_type, original, corrected, location))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary dictionary for API responses"""
        return {
            "total_changes": len(self.changes),
            "document_type": self.document_type,
            "timestamp": self.timestamp,
            "changes": [
                {
                    "type": c.change_type,
                    "original": c.original[:200],
                    "corrected": c.corrected[:200],
                    "location": c.location
                }
                for c in self.changes
            ]
        }
    
    def has_changes(self) -> bool:
        """Check if any changes were made"""
        return len(self.changes) > 0
    
    def clear(self):
        """Clear all changes"""
        self.changes = []
        self.document_type = ""
        self.original_text = ""
        self.corrected_text = ""


# Global change log instance
_change_log: ChangeLog = None


def get_change_log() -> ChangeLog:
    """Get the current change log instance"""
    global _change_log
    if _change_log is None:
        _change_log = ChangeLog()
    return _change_log


def reset_change_log():
    """Reset the change log for a new document"""
    global _change_log
    _change_log = ChangeLog()


def set_document_context(doc_type: str, original_text: str = "", corrected_text: str = ""):
    """Set document context for the change log"""
    log = get_change_log()
    log.document_type = doc_type
    if original_text:
        log.original_text = original_text
    if corrected_text:
        log.corrected_text = corrected_text