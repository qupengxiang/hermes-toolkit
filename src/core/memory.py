# src/core/memory.py
"""
Memory management for Hermes Toolkit.
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class MemoryEntry:
    """Represents a single memory entry."""

    def __init__(
        self,
        content: str,
        target: str = 'memory',
        entry_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.id = entry_id or str(uuid.uuid4())
        self.target = target  # 'user' or 'memory'
        self.content = content
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'target': self.target,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        return cls(
            content=data.get('content', ''),
            target=data.get('target', 'memory'),
            entry_id=data.get('id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )


class MemoryManager:
    """
    Manages Hermes memory entries.
    """

    def __init__(self, memory_file: Optional[str] = None):
        if memory_file:
            self._memory_file = Path(memory_file)
        else:
            self._memory_file = Path.home() / '.hermes' / 'memory.json'

        self._memory_file.parent.mkdir(parents=True, exist_ok=True)
        self._entries: List[MemoryEntry] = []
        self._load()

    def _load(self) -> None:
        """Load memory from file."""
        self._entries = []
        if self._memory_file.exists():
            try:
                with open(self._memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entries_data = data if isinstance(data, list) else data.get('entries', [])
                    self._entries = [MemoryEntry.from_dict(e) for e in entries_data]
            except (json.JSONDecodeError, IOError):
                self._entries = []

    def _save(self) -> bool:
        """Save memory to file."""
        try:
            with open(self._memory_file, 'w', encoding='utf-8') as f:
                json.dump([e.to_dict() for e in self._entries], f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    def list_entries(self, target: Optional[str] = None) -> List[MemoryEntry]:
        """
        List all memory entries, optionally filtered by target.

        Args:
            target: Filter by 'user' or 'memory', or None for all

        Returns:
            List of MemoryEntry objects
        """
        if target:
            return [e for e in self._entries if e.target == target]
        return self._entries.copy()

    def get_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory entry by ID."""
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def add_entry(self, content: str, target: str = 'memory') -> Optional[MemoryEntry]:
        """Add a new memory entry."""
        entry = MemoryEntry(content=content, target=target)
        self._entries.append(entry)
        if self._save():
            return entry
        self._entries.remove(entry)
        return None

    def update_entry(self, entry_id: str, content: str) -> bool:
        """Update an existing memory entry."""
        entry = self.get_entry(entry_id)
        if not entry:
            return False

        old_content = entry.content
        entry.content = content
        entry.updated_at = datetime.now().isoformat()

        if self._save():
            return True

        entry.content = old_content
        return False

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        entry = self.get_entry(entry_id)
        if not entry:
            return False

        self._entries.remove(entry)
        if self._save():
            return True

        self._entries.append(entry)
        return False

    def search(self, query: str) -> List[MemoryEntry]:
        """
        Search memory entries by content.

        Args:
            query: Search query string

        Returns:
            List of matching MemoryEntry objects
        """
        query_lower = query.lower()
        return [
            e for e in self._entries
            if query_lower in e.content.lower()
        ]

    def clear(self, target: Optional[str] = None) -> int:
        """
        Clear memory entries.

        Args:
            target: Clear only 'user' or 'memory' entries, or None for all

        Returns:
            Number of entries cleared
        """
        if target:
            old_entries = [e for e in self._entries if e.target == target]
            self._entries = [e for e in self._entries if e.target != target]
        else:
            old_entries = self._entries.copy()
            self._entries = []

        count = len(old_entries)
        if self._save():
            return count
        else:
            self._entries = old_entries
            return 0

    @property
    def memory_file(self) -> Path:
        return self._memory_file
