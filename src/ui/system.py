# src/ui/system.py
"""
System Status View
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any


class SystemView:
    """System status view."""

    def __init__(self, parent, app, i18n, hermes_client):
        self.parent = parent
        self.app = app
        self.i18n = i18n
        self.hermes_client = hermes_client

        self._create_widgets()
        self._load_status()

    def _create_widgets(self) -> None:
        """Create all widgets."""
        colors = self.app.colors

        # Title
        title_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(
            title_frame,
            text=self.i18n.t('system.title'),
            font=('Segoe UI', 18, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        title.pack(side=tk.LEFT)

        # Refresh button
        self.refresh_btn = tk.Button(
            title_frame,
            text='🔄 ' + self.i18n.t('common.refresh'),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._load_status,
        )
        self.refresh_btn.pack(side=tk.RIGHT, padx=5)

        # Main content
        main_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left column
        left_frame = tk.Frame(main_frame, bg=colors['bg_primary'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Hermes Status card
        self._create_status_card(
            left_frame,
            self.i18n.t('system.system_info'),
            self._create_info_content,
        )

        # MCP Services
        self._create_status_card(
            left_frame,
            self.i18n.t('system.mcp_services'),
            self._create_mcp_content,
        )

        # Right column
        right_frame = tk.Frame(main_frame, bg=colors['bg_primary'])
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Connected Platforms
        self._create_status_card(
            right_frame,
            self.i18n.t('system.platforms'),
            self._create_platforms_content,
        )

        # Shortcuts
        self._create_status_card(
            right_frame,
            self.i18n.t('system.shortcuts'),
            self._create_shortcuts_content,
        )

    def _create_status_card(self, parent, title: str, content_func) -> None:
        """Create a status card."""
        colors = self.app.colors

        card = tk.Frame(
            parent,
            bg=colors['bg_secondary'],
            relief=tk.FLAT,
            bd=0,
        )
        card.pack(fill=tk.X, pady=(0, 15))

        # Card title
        card_title = tk.Label(
            card,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            anchor='w',
        )
        card_title.pack(fill=tk.X, padx=15, pady=(10, 5))

        # Card content
        content_frame = tk.Frame(card, bg=colors['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        content_func(content_frame)

    def _create_info_content(self, parent) -> None:
        """Create system info content."""
        colors = self.app.colors

        # Hermes status indicator
        status_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        status_frame.pack(fill=tk.X, pady=5)

        self.status_indicator = tk.Label(
            status_frame,
            text='🔴 Hermes - ' + self.i18n.t('system.status_disconnected'),
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['error'],
        )
        self.status_indicator.pack(side=tk.LEFT)

        # Version
        version_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        version_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            version_frame,
            text=self.i18n.t('system.version') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_secondary'],
        ).pack(side=tk.LEFT)

        self.version_label = tk.Label(
            version_frame,
            text='v0.1.0',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
        )
        self.version_label.pack(side=tk.LEFT, padx=(5, 0))

        # Uptime
        uptime_frame = tk.Frame(parent, bg=colors['bg_secondary'])
        uptime_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            uptime_frame,
            text=self.i18n.t('system.uptime') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_secondary'],
        ).pack(side=tk.LEFT)

        self.uptime_label = tk.Label(
            uptime_frame,
            text='-',
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
        )
        self.uptime_label.pack(side=tk.LEFT, padx=(5, 0))

    def _create_mcp_content(self, parent) -> None:
        """Create MCP services content."""
        colors = self.app.colors

        self.mcp_label = tk.Label(
            parent,
            text=self.i18n.t('system.no_mcp'),
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_secondary'],
        )
        self.mcp_label.pack(anchor='w', pady=5)

    def _create_platforms_content(self, parent) -> None:
        """Create platforms content."""
        colors = self.app.colors

        self.platforms_label = tk.Label(
            parent,
            text=self.i18n.t('system.no_platforms'),
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_secondary'],
        )
        self.platforms_label.pack(anchor='w', pady=5)

    def _create_shortcuts_content(self, parent) -> None:
        """Create shortcuts content."""
        colors = self.app.colors

        shortcuts = [
            (self.i18n.t('system.restart'), self._on_restart),
            (self.i18n.t('system.reload'), self._on_reload),
            (self.i18n.t('system.sync'), self._on_sync),
            (self.i18n.t('system.health_check'), self._on_health_check),
        ]

        for text, cmd in shortcuts:
            btn = tk.Button(
                parent,
                text=text,
                bg=colors['accent'],
                fg='white',
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor='hand2',
                command=cmd,
            )
            btn.pack(anchor='w', pady=3)

    def _load_status(self) -> None:
        """Load and display system status."""
        status = self.hermes_client.get_status()

        if status.running:
            self.status_indicator.config(
                text='🟢 Hermes - ' + self.i18n.t('system.status_connected'),
                fg=colors['success'] if hasattr(colors, 'success') else '#27ae60',
            )
            self.uptime_label.config(text=status.uptime)
        else:
            self.status_indicator.config(
                text='🔴 Hermes - ' + self.i18n.t('system.status_disconnected'),
                fg=colors['error'],
            )
            self.uptime_label.config(text='-')

        # MCP services
        mcp_services = status.mcp_services
        if mcp_services:
            mcp_text = '\n'.join([f"• {s.get('name', 'Unknown')}" for s in mcp_services])
            self.mcp_label.config(text=mcp_text, fg=colors['text_primary'])
        else:
            self.mcp_label.config(
                text=self.i18n.t('system.no_mcp'),
                fg=colors['text_secondary'],
            )

        # Platforms
        platforms = status.connected_platforms
        if platforms:
            plat_text = '\n'.join([f"• {p}" for p in platforms])
            self.platforms_label.config(text=plat_text, fg=colors['text_primary'])
        else:
            self.platforms_label.config(
                text=self.i18n.t('system.no_platforms'),
                fg=colors['text_secondary'],
            )

    def _on_restart(self) -> None:
        """Handle restart."""
        if messagebox.askyesno(
            self.i18n.t('system.restart'),
            '确定要重启 Hermes 吗？'
        ):
            if self.hermes_client.restart():
                messagebox.showinfo(self.i18n.t('common.success'), '重启请求已发送')
            else:
                messagebox.showerror(self.i18n.t('common.error'), '重启失败')

    def _on_reload(self) -> None:
        """Handle reload config."""
        if self.hermes_client.reload_config():
            messagebox.showinfo(self.i18n.t('common.success'), '配置已重载')
        else:
            messagebox.showerror(self.i18n.t('common.error'), '重载失败')

    def _on_sync(self) -> None:
        """Handle sync."""
        if self.hermes_client.sync_data():
            messagebox.showinfo(self.i18n.t('common.success'), '同步完成')
        else:
            messagebox.showerror(self.i18n.t('common.error'), '同步失败')

    def _on_health_check(self) -> None:
        """Handle health check."""
        self._load_status()
        messagebox.showinfo(
            self.i18n.t('system.health_check'),
            '状态已刷新，请查看上方信息'
        )
