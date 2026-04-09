# src/core/config.py
"""
Configuration management for Hermes Toolkit.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
import base64


class ConfigManager:
    """
    Manages application configuration and secrets.
    """

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir:
            self._config_dir = Path(config_dir)
        else:
            self._config_dir = Path.home() / '.hermes' / 'config'

        self._config_dir.mkdir(parents=True, exist_ok=True)

        # Encryption key for secrets (in production, use keychain)
        self._key_file = self._config_dir / '.key'
        self._fernet = self._load_or_create_key()

        # Config files
        self._settings_file = self._config_dir / 'settings.json'
        self._agents_file = self._config_dir / 'agents.yaml'
        self._secrets_file = self._config_dir / 'secrets.yaml'

        self._settings = self._load_settings()

    def _load_or_create_key(self) -> Fernet:
        """Load existing encryption key or create new one."""
        if self._key_file.exists():
            with open(self._key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self._key_file, 'wb') as f:
                f.write(key)
            os.chmod(self._key_file, 0o600)

        return Fernet(key)

    def _load_settings(self) -> Dict[str, Any]:
        """Load application settings."""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._get_default_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings."""
        return {
            'language': 'zh_CN',
            'theme': 'light',
            'window': {
                'width': 1200,
                'height': 800,
            },
            'paths': {
                'skills': str(Path.home() / '.hermes' / 'skills'),
                'memory': str(Path.home() / '.hermes' / 'memory.json'),
                'sessions': str(Path.home() / '.hermes' / 'sessions'),
            },
            'notifications': {
                'task_complete': True,
                'task_fail': True,
            },
            'log_level': 'INFO',
        }

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save application settings."""
        try:
            self._settings.update(settings)
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving settings: {e}")
            return False

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        return self._settings.copy()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        keys = key.split('.')
        value = self._settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting value."""
        keys = key.split('.')
        settings = self._settings
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        settings[keys[-1]] = value
        return self.save_settings(self._settings)

    def encrypt_secret(self, value: str) -> str:
        """Encrypt a secret value."""
        encrypted = self._fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_secret(self, encrypted: str) -> str:
        """Decrypt a secret value."""
        try:
            data = base64.b64decode(encrypted.encode())
            decrypted = self._fernet.decrypt(data)
            return decrypted.decode()
        except Exception:
            return ""

    def load_agents_config(self) -> Dict[str, Any]:
        """Load agents configuration."""
        if not self._agents_file.exists():
            return {'agents': [], 'presets': [], 'rate_limits': {}}

        try:
            with open(self._agents_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {'agents': [], 'presets': [], 'rate_limits': {}}
        except yaml.YAMLError:
            return {'agents': [], 'presets': [], 'rate_limits': {}}

    def save_agents_config(self, config: Dict[str, Any]) -> bool:
        """Save agents configuration."""
        try:
            with open(self._agents_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            return True
        except IOError:
            return False

    @property
    def config_dir(self) -> Path:
        return self._config_dir
