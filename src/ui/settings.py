# src/ui/settings.py
"""
Settings View
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any


class SettingsView:
    """Settings view."""

    def __init__(self, parent, app, i18n, config):
        self.parent = parent
        self.app = app
        self.i18n = i18n
        self.config = config

        self._create_widgets()
        self._load_settings()

    def _create_widgets(self) -> None:
        """Create all widgets."""
        colors = self.app.colors

        # Title
        title = tk.Label(
            self.parent,
            text=self.i18n.t('settings.title'),
            font=('Segoe UI', 18, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        title.pack(anchor='w', pady=(0, 15))

        # Scrollable content
        canvas = tk.Canvas(self.parent, bg=colors['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.parent, command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=colors['bg_primary'])

        self.scroll_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Appearance section
        self._create_section(
            self.scroll_frame,
            self.i18n.t('settings.appearance'),
            self._create_appearance_content,
        )

        # Language section
        self._create_section(
            self.scroll_frame,
            self.i18n.t('settings.language'),
            self._create_language_content,
        )

        # Notifications section
        self._create_section(
            self.scroll_frame,
            self.i18n.t('settings.notifications'),
            self._create_notifications_content,
        )

        # Paths section
        self._create_section(
            self.scroll_frame,
            self.i18n.t('settings.paths'),
            self._create_paths_content,
        )

        # About section
        self._create_section(
            self.scroll_frame,
            self.i18n.t('settings.about'),
            self._create_about_content,
        )

    def _create_section(self, parent, title: str, content_func) -> None:
        """Create a settings section."""
        colors = self.app.colors

        section = tk.Frame(
            parent,
            bg=colors['bg_secondary'],
            relief=tk.FLAT,
        )
        section.pack(fill=tk.X, pady=(0, 15))

        # Section title
        section_title = tk.Label(
            section,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            anchor='w',
        )
        section_title.pack(fill=tk.X, padx=15, pady=(10, 5))

        # Section content
        content_frame = tk.Frame(section, bg=colors['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        content_func(content_frame)

    def _create_appearance_content(self, parent) -> None:
        """Create appearance settings content."""
        colors = self.app.colors

        # Theme
        theme_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        theme_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            theme_frame,
            text=self.i18n.t('settings.theme') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
        ).pack(side=tk.LEFT)

        self.theme_var = tk.StringVar(value='light')
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=['light', 'dark'],
            state='readonly',
            font=('Segoe UI', 10),
            width=10,
        )
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self._on_theme_change())

    def _create_language_content(self, parent) -> None:
        """Create language settings content."""
        colors = self.app.colors

        lang_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        lang_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            lang_frame,
            text=self.i18n.t('settings.language') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
        ).pack(side=tk.LEFT)

        languages = list(self.i18n.get_available_languages().items())
        lang_values = [f"{code} - {name}" for code, name in languages]

        self.lang_var = tk.StringVar()
        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=lang_values,
            state='readonly',
            font=('Segoe UI', 10),
            width=20,
        )
        self.lang_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.lang_combo.bind('<<ComboboxSelected>>', lambda e: self._on_language_change())

    def _create_notifications_content(self, parent) -> None:
        """Create notification settings content."""
        colors = self.app.colors

        # Task complete notification
        complete_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        complete_frame.pack(fill=tk.X, pady=5)

        self.notify_complete_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            complete_frame,
            text=self.i18n.t('settings.notify_task_complete'),
            variable=self.notify_complete_var,
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            selectcolor=colors['bg_primary'],
            font=('Segoe UI', 10),
            command=self._on_notification_change,
        ).pack(side=tk.LEFT)

        # Task fail notification
        fail_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        fail_frame.pack(fill=tk.X, pady=5)

        self.notify_fail_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            fail_frame,
            text=self.i18n.t('settings.notify_task_fail'),
            variable=self.notify_fail_var,
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            selectcolor=colors['bg_primary'],
            font=('Segoe UI', 10),
            command=self._on_notification_change,
        ).pack(side=tk.LEFT)

    def _create_paths_content(self, parent) -> None:
        """Create path settings content."""
        colors = self.app.colors

        # Skills path
        skills_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        skills_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            skills_frame,
            text=self.i18n.t('settings.skills_path') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
        ).pack(side=tk.LEFT)

        self.skills_path_entry = tk.Entry(
            skills_frame,
            font=('Segoe UI', 10),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
            width=30,
        )
        self.skills_path_entry.pack(side=tk.LEFT, padx=(10, 5))

        tk.Button(
            skills_frame,
            text=self.i18n.t('settings.browse'),
            bg=colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2',
            command=lambda: self._browse_path('skills'),
        ).pack(side=tk.LEFT)

        # Memory path
        memory_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        memory_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            memory_frame,
            text=self.i18n.t('settings.memory_path') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
        ).pack(side=tk.LEFT)

        self.memory_path_entry = tk.Entry(
            memory_frame,
            font=('Segoe UI', 10),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
            width=30,
        )
        self.memory_path_entry.pack(side=tk.LEFT, padx=(10, 5))

        tk.Button(
            memory_frame,
            text=self.i18n.t('settings.browse'),
            bg=colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2',
            command=lambda: self._browse_path('memory'),
        ).pack(side=tk.LEFT)

        # Sessions path
        sessions_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        sessions_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            sessions_frame,
            text=self.i18n.t('settings.sessions_path') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
        ).pack(side=tk.LEFT)

        self.sessions_path_entry = tk.Entry(
            sessions_frame,
            font=('Segoe UI', 10),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
            width=30,
        )
        self.sessions_path_entry.pack(side=tk.LEFT, padx=(10, 5))

        tk.Button(
            sessions_frame,
            text=self.i18n.t('settings.browse'),
            bg=colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2',
            command=lambda: self._browse_path('sessions'),
        ).pack(side=tk.LEFT)

    def _create_about_content(self, parent) -> None:
        """Create about content."""
        colors = self.app.colors

        about_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        about_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            about_frame,
            text=f"{self.i18n.t('app.name')} v0.1.0",
            font=('Segoe UI', 10, 'bold'),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
        ).pack(anchor='w')

        tk.Label(
            about_frame,
            text="A visual management tool for Hermes AI Assistant.",
            font=('Segoe UI', 9),
            bg=colors['bg_secondary'],
            fg=colors['text_secondary'],
        ).pack(anchor='w', pady=(5, 0))

    def _load_settings(self) -> None:
        """Load current settings."""
        settings = self.config.get_settings()

        # Theme
        theme = settings.get('settings', {}).get('theme', 'light')
        self.theme_var.set(theme)

        # Language
        lang = settings.get('settings', {}).get('language', 'zh_CN')
        lang_combo_value = f"{lang} - {self.i18n.get_available_languages().get(lang, lang)}"
        self.lang_var.set(lang_combo_value)

        # Notifications
        notifications = settings.get('settings', {}).get('notifications', {})
        self.notify_complete_var.set(notifications.get('task_complete', True))
        self.notify_fail_var.set(notifications.get('task_fail', True))

        # Paths
        paths = settings.get('settings', {}).get('paths', {})
        self.skills_path_entry.delete(0, tk.END)
        self.skills_path_entry.insert(0, paths.get('skills', ''))
        self.memory_path_entry.delete(0, tk.END)
        self.memory_path_entry.insert(0, paths.get('memory', ''))
        self.sessions_path_entry.delete(0, tk.END)
        self.sessions_path_entry.insert(0, paths.get('sessions', ''))

    def _on_theme_change(self) -> None:
        """Handle theme change."""
        theme = self.theme_var.get()
        self.config.set_setting('settings.theme', theme)
        self.app.toggle_theme()
        messagebox.showinfo(
            self.i18n.t('common.success'),
            self.i18n.t('settings.save_success')
        )

    def _on_language_change(self) -> None:
        """Handle language change."""
        lang_value = self.lang_var.get()
        lang_code = lang_value.split(' - ')[0]
        self.config.set_setting('settings.language', lang_code)
        self.i18n.set_language(lang_code)
        self.app._show_view('settings')
        messagebox.showinfo(
            self.i18n.t('common.success'),
            self.i18n.t('settings.save_success')
        )

    def _on_notification_change(self) -> None:
        """Handle notification settings change."""
        notifications = {
            'task_complete': self.notify_complete_var.get(),
            'task_fail': self.notify_fail_var.get(),
        }
        self.config.set_setting('settings.notifications', notifications)

    def _browse_path(self, path_type: str) -> None:
        """Browse for a path."""
        if path_type == 'skills':
            path = filedialog.askdirectory(title=self.i18n.t('settings.browse'))
            if path:
                self.skills_path_entry.delete(0, tk.END)
                self.skills_path_entry.insert(0, path)
                self._save_path_setting('skills', path)
        elif path_type == 'memory':
            path = filedialog.askopenfilename(
                title=self.i18n.t('settings.browse'),
                filetypes=[('JSON', '*.json'), ('All files', '*.*')],
            )
            if path:
                self.memory_path_entry.delete(0, tk.END)
                self.memory_path_entry.insert(0, path)
                self._save_path_setting('memory', path)
        elif path_type == 'sessions':
            path = filedialog.askdirectory(title=self.i18n.t('settings.browse'))
            if path:
                self.sessions_path_entry.delete(0, tk.END)
                self.sessions_path_entry.insert(0, path)
                self._save_path_setting('sessions', path)

    def _save_path_setting(self, path_type: str, path: str) -> None:
        """Save a path setting."""
        settings = self.config.get_settings()
        if 'settings' not in settings:
            settings['settings'] = {}
        if 'paths' not in settings['settings']:
            settings['settings']['paths'] = {}

        settings['settings']['paths'][path_type] = path
        self.config.save_settings(settings.get('settings', {}))
