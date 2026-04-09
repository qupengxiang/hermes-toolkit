# src/utils/helpers.py
"""
Helper utilities for Hermes Toolkit.
"""

import os
import sys
import uuid
import hashlib
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar
from functools import wraps
import threading

T = TypeVar('T')


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def hash_string(s: str) -> str:
    """Generate a SHA256 hash of a string."""
    return hashlib.sha256(s.encode()).hexdigest()


def ensure_dir(path: str) -> Path:
    """Ensure a directory exists, creating it if needed."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_hermes_running() -> bool:
    """Check if Hermes daemon is running."""
    sock_path = Path.home() / '.hermes' / 'hermes.sock'
    if sock_path.exists():
        try:
            import socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(str(sock_path))
            sock.close()
            return True
        except (OSError, socket.error):
            pass
    return False


def format_timestamp(dt_str: str) -> str:
    """
    Format an ISO timestamp to a human-readable string.

    Args:
        dt_str: ISO format datetime string

    Returns:
        Formatted string like "2026-04-09 12:30:45"
    """
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return dt_str


def format_relative_time(dt_str: str) -> str:
    """
    Format an ISO timestamp to a relative time string.

    Args:
        dt_str: ISO format datetime string

    Returns:
        Relative time string like "5分钟前", "2小时前"
    """
    try:
        from datetime import datetime, timedelta

        dt = datetime.fromisoformat(dt_str)
        now = datetime.now()
        diff = now - dt

        if diff < timedelta(minutes=1):
            return "刚刚"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}分钟前"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}小时前"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}天前"
        else:
            return format_timestamp(dt_str)
    except (ValueError, TypeError):
        return dt_str


def truncate_string(s: str, max_length: int = 50, suffix: str = '...') -> str:
    """Truncate a string to a maximum length."""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def validate_json(s: str) -> bool:
    """Validate if a string is valid JSON."""
    import json
    try:
        json.loads(s)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def read_file_safe(file_path: str, default: str = '') -> str:
    """Safely read a file, returning default if it fails."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (IOError, OSError):
        return default


def write_file_safe(file_path: str, content: str) -> bool:
    """Safely write to a file, returning success status."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except (IOError, OSError):
        return False


def thread_safe(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to make a function thread-safe."""
    lock = threading.Lock()

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        with lock:
            return func(*args, **kwargs)
    return wrapper


class LazyLoader:
    """Lazy loader for deferred imports."""

    def __init__(self, import_func: Callable[[], Any]):
        self._import_func = import_func
        self._loaded = False
        self._value = None

    def get(self) -> Any:
        if not self._loaded:
            self._value = self._import_func()
            self._loaded = True
        return self._value
