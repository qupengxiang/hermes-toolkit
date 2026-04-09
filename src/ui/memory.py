# src/ui/memory.py
"""
Memory Management View
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any


class MemoryView:
    """Memory management view."""

    def __init__(self, parent, app, i18n, memory_manager):
        self.parent = parent
        self.app = app
        self.i18n = i18n
        self.memory_manager = memory_manager

        self._selected_entry: Optional[Dict[str, Any]] = None

        self._create_widgets()
        self._load_entries()

    def _create_widgets(self) -> None:
        """Create all widgets for the memory view."""
        colors = self.app.colors

        # Title row
        title_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(
            title_frame,
            text=self.i18n.t('memory.title'),
            font=('Segoe UI', 18, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        title.pack(side=tk.LEFT)

        # Action buttons
        actions_frame = tk.Frame(title_frame, bg=colors['bg_primary'])
        actions_frame.pack(side=tk.RIGHT)

        self.new_btn = tk.Button(
            actions_frame,
            text='➕ ' + self.i18n.t('memory.new'),
            bg=colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_new,
        )
        self.new_btn.pack(side=tk.LEFT, padx=5)

        # Main content
        main_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left - Entries list
        left_frame = tk.Frame(main_frame, bg=colors['bg_secondary'], width=250)
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
        self.search_entry.insert(0, self.i18n.t('memory.search_placeholder'))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        self.search_entry.bind('<FocusIn>', lambda e: self._on_search_focus(True))
        self.search_entry.bind('<FocusOut>', lambda e: self._on_search_focus(False))
        self.search_entry.pack(fill=tk.X)

        # Filter
        filter_frame = tk.Frame(left_frame, bg=colors['bg_secondary'], padx=10, pady=(0, 5))
        filter_frame.pack(fill=tk.X)

        self.filter_var = tk.StringVar(value='all')
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=['all', 'user', 'memory'],
            state='readonly',
            font=('Segoe UI', 10),
        )
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self._load_entries())
        filter_combo.pack(fill=tk.X)

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

        # Right - Detail/Editor
        self.right_frame = tk.Frame(main_frame, bg=colors['bg_primary'])
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Empty state
        self.empty_label = tk.Label(
            self.right_frame,
            text=self.i18n.t('memory.no_memory'),
            font=('Segoe UI', 12),
            bg=colors['bg_primary'],
            fg=colors['text_secondary'],
            justify='center',
        )
        self.empty_label.pack(expand=True)

        # Editor (hidden initially)
        self.editor_frame = tk.Frame(self.right_frame, bg=colors['bg_primary'])

        # Editor header
        editor_header = tk.Frame(self.editor_frame, bg=colors['bg_primary'])
        editor_header.pack(fill=tk.X, pady=(0, 10))

        self.editor_title = tk.Label(
            editor_header,
            text=self.i18n.t('memory.new'),
            font=('Segoe UI', 14, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        self.editor_title.pack(side=tk.LEFT)

        editor_actions = tk.Frame(editor_header, bg=colors['bg_primary'])
        editor_actions.pack(side=tk.RIGHT)

        self.save_btn = tk.Button(
            editor_actions,
            text='💾 ' + self.i18n.t('common.save'),
            bg=colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self._on_save,
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = tk.Button(
            editor_actions,
            text='🗑️ ' + self.i18n.t('common.delete'),
            bg=colors['error'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self._on_delete,
        )
        self.delete_btn.pack(side=tk.LEFT)

        # Form
        form_frame = tk.Frame(self.editor_frame, bg=colors['bg_primary'])
        form_frame.pack(fill=tk.X, pady=10)

        # Target
        target_label = tk.Label(
            form_frame,
            text=self.i18n.t('memory.target') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        target_label.grid(row=0, column=0, sticky='w', pady=5)

        self.target_var = tk.StringVar(value='memory')
        target_combo = ttk.Combobox(
            form_frame,
            textvariable=self.target_var,
            values=['user', 'memory'],
            state='readonly',
            font=('Segoe UI', 10),
        )
        target_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0))

        # Content
        content_label = tk.Label(
            form_frame,
            text=self.i18n.t('memory.content') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
            anchor='nw',
        )
        content_label.grid(row=1, column=0, sticky='nw', pady=(10, 0))

        self.content_text = tk.Text(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
            wrap=tk.WORD,
            height=10,
        )
        self.content_text.grid(row=2, column=0, columnspan=2, sticky='ew', padx=(0, 0), pady=(5, 0))

        form_frame.columnconfigure(1, weight=1)

    def _load_entries(self) -> None:
        """Load and display memory entries."""
        filter_type = self.filter_var.get()
        if filter_type == 'all':
            entries = self.memory_manager.list_entries()
        else:
            entries = self.memory_manager.list_entries(target=filter_type)

        # Search filter
        query = self.search_entry.get()
        if query and query != self.i18n.t('memory.search_placeholder'):
            entries = [e for e in entries if query.lower() in e.content.lower()]

        self.listbox.delete(0, tk.END)
        for entry in entries:
            target_icon = '👤' if entry.target == 'user' else '🧠'
            self.listbox.insert(tk.END, f"{target_icon} {entry.content[:50]}...")

    def _on_search(self, event=None) -> None:
        """Handle search."""
        self._load_entries()

    def _on_search_focus(self, focused: bool) -> None:
        """Handle search focus."""
        placeholder = self.i18n.t('memory.search_placeholder')
        if focused and self.search_entry.get() == placeholder:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.app.colors['text_primary'])
        elif not focused and not self.search_entry.get():
            self.search_entry.insert(0, placeholder)
            self.search_entry.config(fg=self.app.colors['text_secondary'])

    def _on_select(self, event=None) -> None:
        """Handle entry selection."""
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        filter_type = self.filter_var.get()
        if filter_type == 'all':
            entries = self.memory_manager.list_entries()
        else:
            entries = self.memory_manager.list_entries(target=filter_type)

        query = self.search_entry.get()
        if query and query != self.i18n.t('memory.search_placeholder'):
            entries = [e for e in entries if query.lower() in e.content.lower()]

        if index < len(entries):
            self._selected_entry = entries[index]
            self._show_editor()

    def _show_editor(self) -> None:
        """Show the editor for selected entry."""
        self.empty_label.pack_forget()
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        if self._selected_entry:
            self.editor_title.config(text=f"📝 {self.i18n.t('memory.edit')}")
            self.target_var.set(self._selected_entry.target)
            self.content_text.delete('1.0', tk.END)
            self.content_text.insert('1.0', self._selected_entry.content)
            self.delete_btn.pack(side=tk.LEFT)
        else:
            self.editor_title.config(text='➕ ' + self.i18n.t('memory.new'))
            self.target_var.set('memory')
            self.content_text.delete('1.0', tk.END)
            self.delete_btn.pack_forget()

    def _on_new(self) -> None:
        """Create a new memory entry."""
        self._selected_entry = None
        self._show_editor()

    def _on_save(self) -> None:
        """Save the current entry."""
        target = self.target_var.get()
        content = self.content_text.get('1.0', tk.END).strip()

        if not content:
            messagebox.showwarning(
                self.i18n.t('common.field_required'),
                self.i18n.t('common.field_required')
            )
            return

        if self._selected_entry:
            if self.memory_manager.update_entry(self._selected_entry.id, content):
                messagebox.showinfo(
                    self.i18n.t('common.success'),
                    self.i18n.t('memory.save_success')
                )
        else:
            if self.memory_manager.add_entry(content, target):
                messagebox.showinfo(
                    self.i18n.t('common.success'),
                    self.i18n.t('memory.save_success')
                )

        self._load_entries()

    def _on_delete(self) -> None:
        """Delete the selected entry."""
        if not self._selected_entry:
            return

        if messagebox.askyesno(
            self.i18n.t('memory.confirm_delete_title'),
            self.i18n.t('skills.confirm_delete')
        ):
            if self.memory_manager.delete_entry(self._selected_entry.id):
                messagebox.showinfo(
                    self.i18n.t('common.success'),
                    self.i18n.t('memory.delete_success')
                )
                self._selected_entry = None
                self.editor_frame.pack_forget()
                self.empty_label.pack(expand=True)
                self._load_entries()
