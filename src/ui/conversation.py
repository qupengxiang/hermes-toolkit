# src/ui/conversation.py
"""
Conversation History View
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List
from pathlib import Path
import json


class ConversationView:
    """Conversation history view."""

    def __init__(self, parent, app, i18n):
        self.parent = parent
        self.app = app
        self.i18n = i18n

        # Session directory
        self.sessions_dir = Path.home() / '.hermes' / 'sessions'
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self._sessions: List[Dict[str, Any]] = []
        self._selected_session: Optional[Dict[str, Any]] = None

        self._create_widgets()
        self._load_sessions()

    def _create_widgets(self) -> None:
        """Create all widgets."""
        colors = self.app.colors

        # Title
        title_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(
            title_frame,
            text=self.i18n.t('conversation.title'),
            font=('Segoe UI', 18, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        title.pack(side=tk.LEFT)

        # Main content
        main_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left - Sessions list
        left_frame = tk.Frame(main_frame, bg=colors['bg_secondary'], width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Search
        search_frame = tk.Frame(left_frame, bg=colors['bg_secondary'], padx=10, pady=10)
        search_frame.pack(fill=tk.X)

        self.search_entry = tk.Entry(
            search_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.FLAT,
        )
        self.search_entry.insert(0, self.i18n.t('conversation.search_placeholder'))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        self.search_entry.bind('<FocusIn>', lambda e: self._on_search_focus(True))
        self.search_entry.bind('<FocusOut>', lambda e: self._on_search_focus(False))
        self.search_entry.pack(fill=tk.X)

        # Listbox
        list_frame = tk.Frame(left_frame, bg=colors['bg_secondary'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
            selectbackground=colors['accent'],
            selectforeground='white',
            relief=tk.FLAT,
            font=('Segoe UI', 10),
            highlightthickness=0,
        )
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Right - Detail view
        self.right_frame = tk.Frame(main_frame, bg=colors['bg_primary'])
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Empty state
        self.empty_label = tk.Label(
            self.right_frame,
            text=self.i18n.t('conversation.no_conversations'),
            font=('Segoe UI', 12),
            bg=colors['bg_primary'],
            fg=colors['text_secondary'],
            justify='center',
        )
        self.empty_label.pack(expand=True)

        # Detail view (hidden initially)
        self.detail_frame = tk.Frame(self.right_frame, bg=colors['bg_primary'])

        # Header
        detail_header = tk.Frame(self.detail_frame, bg=colors['bg_primary'])
        detail_header.pack(fill=tk.X, pady=(0, 10))

        self.detail_title = tk.Label(
            detail_header,
            text='',
            font=('Segoe UI', 14, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        self.detail_title.pack(side=tk.LEFT)

        detail_actions = tk.Frame(detail_header, bg=colors['bg_primary'])
        detail_actions.pack(side=tk.RIGHT)

        self.favorite_btn = tk.Button(
            detail_actions,
            text='⭐ ' + self.i18n.t('conversation.favorite'),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2',
            command=self._on_favorite,
        )
        self.favorite_btn.pack(side=tk.LEFT, padx=5)

        self.delete_conv_btn = tk.Button(
            detail_actions,
            text='🗑️ ' + self.i18n.t('common.delete'),
            bg=colors['error'],
            fg='white',
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2',
            command=self._on_delete,
        )
        self.delete_conv_btn.pack(side=tk.LEFT)

        # Messages
        self.messages_frame = tk.Frame(self.detail_frame, bg=colors['bg_secondary'])
        self.messages_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(self.messages_frame, bg=colors['bg_secondary'], highlightthickness=0)
        scrollbar2 = tk.Scrollbar(self.messages_frame, command=canvas.yview)
        self.messages_container = tk.Frame(canvas, bg=colors['bg_secondary'])

        self.messages_container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        canvas.create_window((0, 0), window=self.messages_container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar2.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

    def _load_sessions(self) -> None:
        """Load sessions from disk."""
        self._sessions = []

        if self.sessions_dir.exists():
            for f in self.sessions_dir.iterdir():
                if f.suffix == '.json':
                    try:
                        with open(f, 'r', encoding='utf-8') as fp:
                            session = json.load(fp)
                            self._sessions.append(session)
                    except (json.JSONDecodeError, IOError):
                        pass

        # Sort by updated_at
        self._sessions.sort(
            key=lambda s: s.get('updated_at', ''),
            reverse=True
        )

        self._update_listbox()

    def _update_listbox(self, query: str = '') -> None:
        """Update the sessions listbox."""
        self.listbox.delete(0, tk.END)

        for session in self._sessions:
            title = session.get('title', 'Untitled')
            if query and query.lower() not in title.lower():
                continue

            favorite = '⭐' if session.get('favorite', False) else '  '
            self.listbox.insert(tk.END, f"{favorite} {title}")

    def _on_search(self, event=None) -> None:
        """Handle search."""
        query = self.search_entry.get()
        if query != self.i18n.t('conversation.search_placeholder'):
            self._update_listbox(query)
        else:
            self._update_listbox()

    def _on_search_focus(self, focused: bool) -> None:
        """Handle search focus."""
        placeholder = self.i18n.t('conversation.search_placeholder')
        if focused and self.search_entry.get() == placeholder:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.app.colors['text_primary'])
        elif not focused and not self.search_entry.get():
            self.search_entry.insert(0, placeholder)
            self.search_entry.config(fg=self.app.colors['text_secondary'])

    def _on_select(self, event=None) -> None:
        """Handle session selection."""
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index < len(self._sessions):
            self._selected_session = self._sessions[index]
            self._show_detail()

    def _show_detail(self) -> None:
        """Show session detail."""
        if not self._selected_session:
            return

        self.empty_label.pack_forget()
        self.detail_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = self._selected_session.get('title', 'Untitled')
        self.detail_title.config(text=title)

        # Favorite button
        if self._selected_session.get('favorite', False):
            self.favorite_btn.config(text='⭐ ' + self.i18n.t('conversation.unfavorite'))
        else:
            self.favorite_btn.config(text='☆ ' + self.i18n.t('conversation.favorite'))

        # Clear messages
        for widget in self.messages_container.winfo_children():
            widget.destroy()

        # Show messages
        messages = self._selected_session.get('messages', [])
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'user':
                bg = self.app.colors['accent']
                fg = 'white'
                anchor = 'e'
            elif role == 'assistant':
                bg = self.app.colors['bg_secondary']
                fg = self.app.colors['text_primary']
                anchor = 'w'
            else:
                bg = self.app.colors['bg_primary']
                fg = self.app.colors['text_secondary']
                anchor = 'w'

            msg_frame = tk.Frame(self.messages_container, bg=bg)
            msg_frame.pack(fill=tk.X, padx=10, pady=5)

            msg_label = tk.Label(
                msg_frame,
                text=content[:500] + ('...' if len(content) > 500 else ''),
                bg=bg,
                fg=fg,
                font=('Segoe UI', 10),
                wraplength=400,
                anchor=anchor,
                justify='left' if anchor == 'w' else 'right',
            )
            msg_label.pack(fill=tk.X, padx=10, pady=5)

    def _on_favorite(self) -> None:
        """Toggle favorite status."""
        if not self._selected_session:
            return

        current = self._selected_session.get('favorite', False)
        self._selected_session['favorite'] = not current

        # Save to disk
        session_file = self.sessions_dir / f"{self._selected_session.get('id', 'unknown')}.json"
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self._selected_session, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

        self._load_sessions()

    def _on_delete(self) -> None:
        """Delete the selected session."""
        if not self._selected_session:
            return

        if messagebox.askyesno(
            self.i18n.t('conversation.confirm_delete_title'),
            self.i18n.t('conversation.confirm_delete')
        ):
            session_id = self._selected_session.get('id', '')
            session_file = self.sessions_dir / f"{session_id}.json"

            if session_file.exists():
                session_file.unlink()

            self._selected_session = None
            self.detail_frame.pack_forget()
            self.empty_label.pack(expand=True)
            self._load_sessions()
