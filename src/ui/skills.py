# src/ui/skills.py
"""
Skills Management View
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from typing import List, Optional, Dict, Any


class SkillsView:
    """Skills management view."""

    def __init__(self, parent, app, i18n, skills_manager):
        self.parent = parent
        self.app = app
        self.i18n = i18n
        self.skills_manager = skills_manager

        self._selected_skill: Optional[Dict[str, Any]] = None
        self._search_query: str = ''

        self._create_widgets()
        self._load_skills()

    def _create_widgets(self) -> None:
        """Create all widgets for the skills view."""
        colors = self.app.colors

        # Title row
        title_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(
            title_frame,
            text=self.i18n.t('skills.title'),
            font=('Segoe UI', 18, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        title.pack(side=tk.LEFT)

        # Action buttons frame
        actions_frame = tk.Frame(title_frame, bg=colors['bg_primary'])
        actions_frame.pack(side=tk.RIGHT)

        # New button
        self.new_btn = tk.Button(
            actions_frame,
            text='➕ ' + self.i18n.t('skills.new'),
            bg=colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_new_skill,
        )
        self.new_btn.pack(side=tk.LEFT, padx=5)

        # Import button
        self.import_btn = tk.Button(
            actions_frame,
            text='📥 ' + self.i18n.t('skills.import'),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_import,
        )
        self.import_btn.pack(side=tk.LEFT, padx=5)

        # Main content area (split view)
        main_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Skills list
        left_frame = tk.Frame(main_frame, bg=colors['bg_secondary'], width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Search box
        search_frame = tk.Frame(left_frame, bg=colors['bg_secondary'], padx=10, pady=10)
        search_frame.pack(fill=tk.X)

        self.search_entry = tk.Entry(
            search_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.FLAT,
            insertbackground=colors['text_primary'],
        )
        self.search_entry.insert(0, self.i18n.t('skills.search_placeholder'))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        self.search_entry.bind('<FocusIn>', lambda e: self._on_search_focus(True))
        self.search_entry.bind('<FocusOut>', lambda e: self._on_search_focus(False))
        self.search_entry.pack(fill=tk.X)

        # Category filter
        cat_frame = tk.Frame(left_frame, bg=colors['bg_secondary'], padx=10)
        cat_frame.pack(fill=tk.X, pady=(0, 5))

        self.category_var = tk.StringVar(value='all')
        self.category_combo = ttk.Combobox(
            cat_frame,
            textvariable=self.category_var,
            values=['all'],
            state='readonly',
            font=('Segoe UI', 10),
        )
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self._load_skills())
        self.category_combo.pack(fill=tk.X)

        # Skills listbox with scrollbar
        list_frame = tk.Frame(left_frame, bg=colors['bg_secondary'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.skills_listbox = tk.Listbox(
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
        self.skills_listbox.bind('<<ListboxSelect>>', self._on_skill_select)
        self.skills_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.skills_listbox.yview)

        # Right panel - Preview/Editor
        right_frame = tk.Frame(main_frame, bg=colors['bg_primary'])
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Preview area
        self.preview_frame = tk.Frame(right_frame, bg=colors['bg_primary'])
        self.preview_frame.pack(fill=tk.BOTH, expand=True)

        # Empty state
        self.empty_label = tk.Label(
            self.preview_frame,
            text=self.i18n.t('skills.no_skills'),
            font=('Segoe UI', 12),
            bg=colors['bg_primary'],
            fg=colors['text_secondary'],
            justify='center',
        )
        self.empty_label.pack(expand=True)

        # Editor area (initially hidden)
        self.editor_frame = tk.Frame(right_frame, bg=colors['bg_primary'])

        # Editor title
        editor_title_frame = tk.Frame(self.editor_frame, bg=colors['bg_primary'])
        editor_title_frame.pack(fill=tk.X, pady=(0, 10))

        self.editor_title = tk.Label(
            editor_title_frame,
            text=self.i18n.t('skills.editor'),
            font=('Segoe UI', 14, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        self.editor_title.pack(side=tk.LEFT)

        editor_actions = tk.Frame(editor_title_frame, bg=colors['bg_primary'])
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

        self.cancel_btn = tk.Button(
            editor_actions,
            text='✖ ' + self.i18n.t('common.cancel'),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self._on_cancel_edit,
        )
        self.cancel_btn.pack(side=tk.LEFT)

        # Form fields
        form_frame = tk.Frame(self.editor_frame, bg=colors['bg_primary'])
        form_frame.pack(fill=tk.X, pady=5)

        # Name field
        self._create_form_field(form_frame, self.i18n.t('skills.name'), 0)
        self.name_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.name_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0))

        # Category field
        self._create_form_field(form_frame, self.i18n.t('skills.category'), 1)
        self.category_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.category_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0))

        # Tags field
        self._create_form_field(form_frame, self.i18n.t('skills.tags'), 2)
        self.tags_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.tags_entry.grid(row=2, column=1, sticky='ew', padx=(10, 0))

        # Description field
        self._create_form_field(form_frame, self.i18n.t('skills.description'), 3)
        self.desc_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.desc_entry.grid(row=3, column=1, sticky='ew', padx=(10, 0))

        # Content field (larger)
        content_label = tk.Label(
            form_frame,
            text=self.i18n.t('skills.content') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
            anchor='nw',
        )
        content_label.grid(row=4, column=0, sticky='nw', pady=(10, 0))

        self.content_text = tk.Text(
            form_frame,
            font=('Consolas', 10),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
            wrap=tk.WORD,
            height=15,
        )
        self.content_text.grid(row=5, column=0, columnspan=2, sticky='ew', padx=(0, 0), pady=(5, 0))

        # Scrollbar for content
        content_scroll = tk.Scrollbar(form_frame, command=self.content_text.yview)
        content_scroll.grid(row=5, column=2, sticky='ns')
        self.content_text.config(yscrollcommand=content_scroll.set)

        # Column weights
        form_frame.columnconfigure(1, weight=1)

    def _create_form_field(self, parent, label_text: str, row: int) -> None:
        """Create a form field label."""
        colors = self.app.colors
        label = tk.Label(
            parent,
            text=label_text + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        label.grid(row=row, column=0, sticky='w', pady=5)

    def _load_skills(self) -> None:
        """Load and display skills list."""
        # Update categories
        categories = ['all'] + self.skills_manager.get_categories()
        self.category_combo['values'] = categories

        # Get skills
        selected_cat = self.category_var.get()
        if selected_cat == 'all':
            skills = self.skills_manager.list_skills()
        else:
            skills = self.skills_manager.list_skills(category=selected_cat)

        # Filter by search
        if self._search_query:
            query = self._search_query.lower()
            skills = [s for s in skills if query in s.name.lower() or query in s.title.lower()]

        # Update listbox
        self.skills_listbox.delete(0, tk.END)
        for skill in skills:
            self.skills_listbox.insert(tk.END, f"{skill.title} ({skill.category})")

    def _on_search(self, event=None) -> None:
        """Handle search input."""
        query = self.search_entry.get()
        if query != self.i18n.t('skills.search_placeholder'):
            self._search_query = query
        else:
            self._search_query = ''
        self._load_skills()

    def _on_search_focus(self, focused: bool) -> None:
        """Handle search entry focus."""
        placeholder = self.i18n.t('skills.search_placeholder')
        if focused and self.search_entry.get() == placeholder:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.app.colors['text_primary'])
        elif not focused and not self.search_entry.get():
            self.search_entry.insert(0, placeholder)
            self.search_entry.config(fg=self.app.colors['text_secondary'])

    def _on_skill_select(self, event=None) -> None:
        """Handle skill selection."""
        selection = self.skills_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        skills = self.skills_manager.list_skills()

        # Filter same as loaded
        selected_cat = self.category_var.get()
        if selected_cat != 'all':
            skills = [s for s in skills if s.category == selected_cat]
        if self._search_query:
            query = self._search_query.lower()
            skills = [s for s in skills if query in s.name.lower() or query in s.title.lower()]

        if index < len(skills):
            self._selected_skill = skills[index]
            self._show_skill_preview()

    def _show_skill_preview(self) -> None:
        """Show skill preview."""
        if not self._selected_skill:
            return

        self.preview_frame.pack_forget()
        self.editor_frame.pack_forget()

        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        # Populate form
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self._selected_skill['name'])

        self.category_entry.delete(0, tk.END)
        self.category_entry.insert(0, self._selected_skill['category'])

        self.tags_entry.delete(0, tk.END)
        self.tags_entry.insert(0, ', '.join(self._selected_skill.get('tags', [])))

        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, self._selected_skill.get('description', ''))

        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', self._selected_skill.get('content', ''))

        # Make name field readonly
        self.name_entry.config(state='readonly')

        self.editor_title.config(text=f"📝 {self._selected_skill['title']}")

    def _on_new_skill(self) -> None:
        """Create a new skill."""
        self._selected_skill = None
        self.preview_frame.pack_forget()
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        # Clear form
        self.name_entry.config(state='normal')
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.content_text.delete('1.0', tk.END)

        # Set defaults
        self.category_entry.insert(0, 'general')

        self.editor_title.config(text='➕ ' + self.i18n.t('skills.new'))

    def _on_import(self) -> None:
        """Import a skill from file."""
        file_path = filedialog.askopenfilename(
            title=self.i18n.t('skills.import'),
            filetypes=[('Markdown', '*.md'), ('All files', '*.*')],
        )

        if file_path:
            if self.skills_manager.import_skill(file_path):
                messagebox.showinfo(
                    self.i18n.t('common.success'),
                    self.i18n.t('skills.import_success')
                )
                self._load_skills()
            else:
                messagebox.showerror(
                    self.i18n.t('common.error'),
                    self.i18n.t('common.error')
                )

    def _on_save(self) -> None:
        """Save the current skill."""
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()
        tags_str = self.tags_entry.get().strip()
        description = self.desc_entry.get().strip()
        content = self.content_text.get('1.0', tk.END).strip()

        # Validation
        if not name:
            messagebox.showwarning(
                self.i18n.t('common.field_required'),
                self.i18n.t('common.field_required')
            )
            return

        tags = [t.strip() for t in tags_str.split(',') if t.strip()]

        if self._selected_skill:
            # Update existing
            from src.core.skills import SkillEntry
            skill = SkillEntry(
                name=name,
                category=category,
                title=name.replace('-', ' ').replace('_', ' ').title(),
                description=description,
                tags=tags,
                content=content,
            )
            if self.skills_manager.update_skill(skill):
                messagebox.showinfo(
                    self.i18n.t('common.success'),
                    self.i18n.t('skills.save_success')
                )
        else:
            # Create new
            title = name.replace('-', ' ').replace('_', ' ').title()
            if self.skills_manager.create_skill(
                name=name,
                title=title,
                category=category,
                content=content,
                description=description,
                tags=tags,
            ):
                messagebox.showinfo(
                    self.i18n.t('common.success'),
                    self.i18n.t('skills.save_success')
                )

        self._load_skills()
        self._on_cancel_edit()

    def _on_cancel_edit(self) -> None:
        """Cancel editing and go back to preview."""
        self._selected_skill = None
        self.editor_frame.pack_forget()
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        self.empty_label.config(text=self.i18n.t('skills.no_skills'))
