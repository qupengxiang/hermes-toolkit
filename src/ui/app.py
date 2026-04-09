# src/ui/app.py
"""
Hermes Toolkit Main Application Window
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from pathlib import Path
from typing import Optional, Callable, Dict, Any

# Import i18n
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.i18n import I18nManager, get_i18n, _
from src.core import ConfigManager, SkillsManager, MemoryManager, CronManager, HermesClient


class HermesApp:
    """
    Main application window for Hermes Toolkit.
    """

    # Window dimensions
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 800
    MIN_WIDTH = 900
    MIN_HEIGHT = 600

    # Colors - Light theme
    COLORS_LIGHT = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f5f5f5',
        'bg_sidebar': '#2c3e50',
        'bg_sidebar_hover': '#34495e',
        'bg_sidebar_active': '#1abc9c',
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'text_sidebar': '#ecf0f1',
        'text_sidebar_active': '#ffffff',
        'accent': '#1abc9c',
        'accent_hover': '#16a085',
        'border': '#dcdcdc',
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c',
    }

    # Colors - Dark theme
    COLORS_DARK = {
        'bg_primary': '#1e1e1e',
        'bg_secondary': '#2d2d2d',
        'bg_sidebar': '#1a1a2e',
        'bg_sidebar_hover': '#16213e',
        'bg_sidebar_active': '#0f3460',
        'text_primary': '#e0e0e0',
        'text_secondary': '#a0a0a0',
        'text_sidebar': '#e0e0e0',
        'text_sidebar_active': '#ffffff',
        'accent': '#0f3460',
        'accent_hover': '#16537e',
        'border': '#3d3d3d',
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c',
    }

    def __init__(self):
        # Initialize i18n
        self.i18n = get_i18n()

        # Initialize config
        self.config = ConfigManager()

        # Initialize managers
        self.skills_manager = SkillsManager()
        self.memory_manager = MemoryManager()
        self.cron_manager = CronManager()
        self.hermes_client = HermesClient()

        # Current theme
        self.theme = self.config.get_setting('settings.theme', 'light')
        self.colors = self.COLORS_LIGHT if self.theme == 'light' else self.COLORS_DARK

        # Create main window
        self.root = tk.Tk()
        self.root.title(_('app.name'))
        self.root.geometry(f"{self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}")
        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Current view
        self.current_view: Optional[str] = None
        self.view_handlers: Dict[str, Callable] = {}

        # Setup UI
        self._setup_styles()
        self._create_widgets()
        self._setup_layout()
        self._apply_theme()

        # Load default view
        self._show_view('skills')

    def _setup_styles(self) -> None:
        """Configure ttk styles."""
        style = ttk.Style()

        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')

        # Configure Treeview
        style.configure(
            'Treeview',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            fieldbackground=self.colors['bg_primary'],
            borderwidth=0,
        )
        style.map('Treeview', background=[('selected', self.colors['accent'])])

        # Configure Button
        style.configure(
            'TButton',
            padding=(10, 5),
            font=('Segoe UI', 10),
        )

        # Configure Entry
        style.configure(
            'TEntry',
            padding=5,
        )

        # Configure Label
        style.configure(
            'TLabel',
            font=('Segoe UI', 10),
            foreground=self.colors['text_primary'],
        )

        # Configure Notebook
        style.configure(
            'TNotebook',
            background=self.colors['bg_secondary'],
            borderwidth=0,
        )
        style.configure(
            'TNotebook.TFrame',
            background=self.colors['bg_secondary'],
        )

    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Main container
        self.main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self._create_sidebar()

        # Content area
        self._create_content_area()

        # Status bar
        self._create_status_bar()

        # Header bar (top)
        self._create_header_bar()

    def _create_header_bar(self) -> None:
        """Create the header bar."""
        self.header_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=50)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)

        # Title
        self.header_title = tk.Label(
            self.header_frame,
            text=_('app.name'),
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
        )
        self.header_title.pack(side=tk.LEFT, padx=20, pady=10)

        # Header buttons
        self.header_buttons_frame = tk.Frame(self.header_frame, bg=self.colors['bg_secondary'])
        self.header_buttons_frame.pack(side=tk.RIGHT, padx=10)

        # Language button
        self.lang_button = tk.Menubutton(
            self.header_buttons_frame,
            text='🌐 ' + self.i18n.get_current_language(),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            font=('Segoe UI', 10),
        )
        self.lang_menu = tk.Menu(self.lang_button, tearoff=0)
        for code, name in self.i18n.get_available_languages().items():
            self.lang_menu.add_command(
                label=name,
                command=lambda c=code: self._change_language(c)
            )
        self.lang_button.config(menu=self.lang_menu)
        self.lang_button.pack(side=tk.RIGHT, padx=5)

        # Settings button
        self.settings_button = tk.Button(
            self.header_buttons_frame,
            text='⚙️ ' + _('menu.settings'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            font=('Segoe UI', 10),
            cursor='hand2',
            command=lambda: self._show_view('settings'),
        )
        self.settings_button.pack(side=tk.RIGHT, padx=5)

        # Help button
        self.help_button = tk.Button(
            self.header_buttons_frame,
            text='?',
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            font=('Segoe UI', 10, 'bold'),
            width=3,
            cursor='hand2',
            command=self._show_help,
        )
        self.help_button.pack(side=tk.RIGHT, padx=5)

    def _create_sidebar(self) -> None:
        """Create the sidebar navigation."""
        self.sidebar = tk.Frame(self.main_container, bg=self.colors['bg_sidebar'], width=180)
        self.main_container.add(self.sidebar, minsize=180)

        # Sidebar items
        self.sidebar_items = [
            ('skills', '📁', _('menu.skills')),
            ('memory', '🧠', _('menu.memory')),
            ('conversation', '💬', _('menu.conversation')),
            ('cron', '⏰', _('menu.cron')),
            ('agents', '🤖', _('menu.agents')),
            ('system', '🔌', _('menu.system')),
        ]

        self.sidebar_buttons: Dict[str, tk.Button] = {}
        self.sidebar_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        self.sidebar_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        for i, (view_id, icon, label) in enumerate(self.sidebar_items):
            btn = tk.Button(
                self.sidebar_frame,
                text=f"  {icon}  {label}",
                anchor='w',
                bg=self.colors['bg_sidebar'],
                fg=self.colors['text_sidebar'],
                activebackground=self.colors['bg_sidebar_active'],
                activeforeground=self.colors['text_sidebar_active'],
                relief=tk.FLAT,
                font=('Segoe UI', 11),
                cursor='hand2',
                command=lambda v=view_id: self._show_view(v),
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.sidebar_buttons[view_id] = btn

    def _create_content_area(self) -> None:
        """Create the main content area."""
        self.content_frame = tk.Frame(self.main_container, bg=self.colors['bg_primary'])
        self.main_container.add(self.content_frame, minsize=600)

        # Content will be dynamically loaded
        self.content_inner = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        self.content_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        self.status_bar = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Status items
        self.status_items_frame = tk.Frame(self.status_bar, bg=self.colors['bg_secondary'])
        self.status_items_frame.pack(fill=tk.X, padx=15, pady=5)

        # Hermes status
        self.hermes_status_label = tk.Label(
            self.status_items_frame,
            text='🔴 Hermes ' + _('system.status_disconnected'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 9),
        )
        self.hermes_status_label.pack(side=tk.LEFT, padx=10)

        # Skills count
        self.skills_count_label = tk.Label(
            self.status_items_frame,
            text=f"{len(self.skills_manager.list_skills())} Skills",
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 9),
        )
        self.skills_count_label.pack(side=tk.LEFT, padx=10)

        # Version
        self.version_label = tk.Label(
            self.status_items_frame,
            text='v0.1.0',
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 9),
        )
        self.version_label.pack(side=tk.RIGHT, padx=10)

        # Update status
        self._update_status()

    def _show_view(self, view_id: str) -> None:
        """Switch to a different view."""
        # Update sidebar highlight
        for vid, btn in self.sidebar_buttons.items():
            if vid == view_id:
                btn.config(
                    bg=self.colors['bg_sidebar_active'],
                    fg=self.colors['text_sidebar_active'],
                )
            else:
                btn.config(
                    bg=self.colors['bg_sidebar'],
                    fg=self.colors['text_sidebar'],
                )

        self.current_view = view_id

        # Clear content
        for widget in self.content_inner.winfo_children():
            widget.destroy()

        # Load view content
        if view_id == 'skills':
            self._show_skills_view()
        elif view_id == 'memory':
            self._show_memory_view()
        elif view_id == 'conversation':
            self._show_conversation_view()
        elif view_id == 'cron':
            self._show_cron_view()
        elif view_id == 'agents':
            self._show_agents_view()
        elif view_id == 'system':
            self._show_system_view()
        elif view_id == 'settings':
            self._show_settings_view()

    def _show_skills_view(self) -> None:
        """Show Skills management view."""
        from . import skills as skills_ui
        skills_ui.SkillsView(self.content_inner, self, self.i18n, self.skills_manager)

    def _show_memory_view(self) -> None:
        """Show Memory management view."""
        from . import memory as memory_ui
        memory_ui.MemoryView(self.content_inner, self, self.i18n, self.memory_manager)

    def _show_conversation_view(self) -> None:
        """Show Conversation history view."""
        from . import conversation as conv_ui
        conv_ui.ConversationView(self.content_inner, self, self.i18n)

    def _show_cron_view(self) -> None:
        """Show Cron tasks view."""
        from . import cron as cron_ui
        cron_ui.CronView(self.content_inner, self, self.i18n, self.cron_manager)

    def _show_agents_view(self) -> None:
        """Show Agents configuration view."""
        from . import agents as agents_ui
        agents_ui.AgentsView(self.content_inner, self, self.i18n, self.config)

    def _show_system_view(self) -> None:
        """Show System status view."""
        from . import system as system_ui
        system_ui.SystemView(self.content_inner, self, self.i18n, self.hermes_client)

    def _show_settings_view(self) -> None:
        """Show Settings view."""
        from . import settings as settings_ui
        settings_ui.SettingsView(self.content_inner, self, self.i18n, self.config)

    def _change_language(self, lang_code: str) -> None:
        """Change the current language."""
        if self.i18n.set_language(lang_code):
            self.config.set_setting('settings.language', lang_code)
            # Refresh UI
            self._apply_theme()
            self._show_view(self.current_view or 'skills')

    def _apply_theme(self) -> None:
        """Apply the current theme colors."""
        self.colors = self.COLORS_LIGHT if self.theme == 'light' else self.COLORS_DARK

        # Update root
        self.root.configure(bg=self.colors['bg_primary'])

        # Update header
        self.header_frame.configure(bg=self.colors['bg_secondary'])
        self.header_title.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        self.header_buttons_frame.configure(bg=self.colors['bg_secondary'])
        self.lang_button.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        self.settings_button.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        self.help_button.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])

        # Update sidebar
        self.sidebar.configure(bg=self.colors['bg_sidebar'])
        self.sidebar_frame.configure(bg=self.colors['bg_sidebar'])

        # Update content
        self.content_frame.configure(bg=self.colors['bg_primary'])
        self.content_inner.configure(bg=self.colors['bg_primary'])

        # Update status bar
        self.status_bar.configure(bg=self.colors['bg_secondary'])
        self.status_items_frame.configure(bg=self.colors['bg_secondary'])
        self.hermes_status_label.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        self.skills_count_label.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        self.version_label.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])

        # Update sidebar buttons
        for vid, btn in self.sidebar_buttons.items():
            if vid == self.current_view:
                btn.configure(
                    bg=self.colors['bg_sidebar_active'],
                    fg=self.colors['text_sidebar_active'],
                )
            else:
                btn.configure(
                    bg=self.colors['bg_sidebar'],
                    fg=self.colors['text_sidebar'],
                )

    def toggle_theme(self) -> None:
        """Toggle between light and dark theme."""
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.config.set_setting('settings.theme', self.theme)
        self._apply_theme()
        self._show_view(self.current_view or 'skills')

    def _update_status(self) -> None:
        """Update status bar information."""
        # Check Hermes status
        if self.hermes_client.is_running():
            self.hermes_status_label.config(
                text='🟢 Hermes ' + _('system.status_connected'),
                fg=self.colors['success'],
            )
        else:
            self.hermes_status_label.config(
                text='🔴 Hermes ' + _('system.status_disconnected'),
                fg=self.colors['error'],
            )

        # Update skills count
        count = len(self.skills_manager.list_skills())
        self.skills_count_label.config(text=f"📁 {count} Skills")

    def _setup_layout(self) -> None:
        """Setup the main layout."""
        pass

    def _show_help(self) -> None:
        """Show help dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            'Hermes Toolkit',
            f"{_('app.name')} v0.1.0\n\n"
            f"A visual management tool for Hermes AI Assistant.\n\n"
            f"Documentation: See README.md"
        )

    def run(self) -> None:
        """Start the application main loop."""
        self.root.mainloop()
