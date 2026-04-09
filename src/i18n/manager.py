# src/i18n/manager.py
"""
Hermes Toolkit i18n Manager

Supports runtime language switching without restart.
Loads translations from JSON locale files.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any
from functools import lru_cache

# Supported languages
SUPPORTED_LANGUAGES = {
    'zh_CN': '简体中文',
    'en_US': 'English',
    'ja_JP': '日本語',
    'zh_TW': '繁體中文',
}

# Default language
DEFAULT_LANGUAGE = 'zh_CN'


class I18nManager:
    """
    Internationalization manager for Hermes Toolkit.

    Loads translation files from locales/ directory and provides
    translation lookup with dot-notation keys.
    """

    _instance: Optional['I18nManager'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, locales_dir: Optional[str] = None):
        if self._initialized:
            return

        self._initialized = True
        self._current_language = DEFAULT_LANGUAGE
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._locale_file_cache: Dict[str, str] = {}

        # Determine locales directory
        if locales_dir:
            self._locales_dir = Path(locales_dir)
        else:
            # Default: look for locales in project root
            self._locales_dir = self._find_locales_dir()

        self._load_all_translations()

    def _find_locales_dir(self) -> Path:
        """Find the locales directory relative to this file."""
        # Try multiple possible locations
        possible_paths = [
            Path(__file__).parent.parent.parent / 'locales',  # project_root/locales
            Path(__file__).parent.parent / 'locales',         # src/locales
            Path.cwd() / 'locales',                            # cwd/locales
        ]

        for p in possible_paths:
            if p.exists() and p.is_dir():
                return p

        # Fallback: create in project root
        project_root = Path(__file__).parent.parent.parent
        locales = project_root / 'locales'
        locales.mkdir(parents=True, exist_ok=True)
        return locales

    def _load_all_translations(self) -> None:
        """Load all translation files."""
        for lang_code in SUPPORTED_LANGUAGES.keys():
            self._load_translation(lang_code)

    def _load_translation(self, lang_code: str) -> bool:
        """Load a single translation file."""
        locale_file = self._locales_dir / f'{lang_code}.json'

        if not locale_file.exists():
            print(f"Warning: Locale file not found: {locale_file}", file=sys.stderr)
            # Fall back to default language
            if lang_code != DEFAULT_LANGUAGE:
                self._translations[lang_code] = self._translations.get(DEFAULT_LANGUAGE, {})
            return False

        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self._translations[lang_code] = json.load(f)
            self._locale_file_cache[lang_code] = str(locale_file)
            return True
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse locale file {locale_file}: {e}", file=sys.stderr)
            return False

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[Any]:
        """Get a nested value from a dictionary using dot notation."""
        keys = key.split('.')
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        return value

    def t(self, key: str, lang: Optional[str] = None) -> str:
        """
        Translate a key to the current language.

        Args:
            key: Dot-notation translation key (e.g., 'menu.skills')
            lang: Optional language code override

        Returns:
            Translated string, or the key itself if not found
        """
        language = lang or self._current_language
        translations = self._translations.get(language, {})

        value = self._get_nested_value(translations, key)

        if value is None:
            # Try default language as fallback
            if language != DEFAULT_LANGUAGE:
                default_translations = self._translations.get(DEFAULT_LANGUAGE, {})
                value = self._get_nested_value(default_translations, key)

        if value is None:
            # Return key itself if not found
            return key

        return str(value)

    def get_current_language(self) -> str:
        """Get the current language code."""
        return self._current_language

    def set_language(self, lang_code: str) -> bool:
        """
        Change the current language.

        Args:
            lang_code: Language code (e.g., 'zh_CN', 'en_US')

        Returns:
            True if language was changed successfully
        """
        if lang_code not in SUPPORTED_LANGUAGES:
            print(f"Error: Unsupported language: {lang_code}", file=sys.stderr)
            return False

        if lang_code not in self._translations:
            # Try to load the translation
            if not self._load_translation(lang_code):
                return False

        self._current_language = lang_code
        return True

    def get_available_languages(self) -> Dict[str, str]:
        """Get all available languages as {code: name} dict."""
        return SUPPORTED_LANGUAGES.copy()

    def reload(self) -> None:
        """Reload all translation files."""
        self._translations.clear()
        self._load_all_translations()

    @property
    def locales_dir(self) -> Path:
        """Get the locales directory path."""
        return self._locales_dir


# Global i18n instance
_i18n: Optional[I18nManager] = None


def get_i18n() -> I18nManager:
    """Get or create the global i18n instance."""
    global _i18n
    if _i18n is None:
        _i18n = I18nManager()
    return _i18n


def _(key: str, lang: Optional[str] = None) -> str:
    """
    Shorthand translation function.

    Usage:
        from i18n import _
        label = _('menu.skills')
    """
    return get_i18n().t(key, lang)


# Convenience function for template usage
def translate(key: str, **kwargs) -> str:
    """
    Translate a key with string interpolation.

    Usage:
        msg = translate('skills.count', count=32)
    """
    template = get_i18n().t(key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template
