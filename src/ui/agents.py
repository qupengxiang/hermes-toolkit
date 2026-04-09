# src/ui/agents.py
"""
Agents Configuration View
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List
import uuid


class AgentsView:
    """Agents configuration view."""

    def __init__(self, parent, app, i18n, config):
        self.parent = parent
        self.app = app
        self.i18n = i18n
        self.config = config

        self._agents: List[Dict[str, Any]] = []
        self._selected_agent: Optional[Dict[str, Any]] = None

        self._create_widgets()
        self._load_agents()

    def _create_widgets(self) -> None:
        """Create all widgets."""
        colors = self.app.colors

        # Title
        title_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(
            title_frame,
            text=self.i18n.t('agents.title'),
            font=('Segoe UI', 18, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        title.pack(side=tk.LEFT)

        # Add button
        self.add_btn = tk.Button(
            title_frame,
            text='➕ ' + self.i18n.t('agents.new'),
            bg=colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_new,
        )
        self.add_btn.pack(side=tk.RIGHT, padx=5)

        # Main content
        main_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left - Agents list
        left_frame = tk.Frame(main_frame, bg=colors['bg_secondary'], width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Listbox
        list_frame = tk.Frame(left_frame, bg=colors['bg_secondary'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

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
            text=self.i18n.t('agents.no_agents'),
            font=('Segoe UI', 12),
            bg=colors['bg_primary'],
            fg=colors['text_secondary'],
            justify='center',
        )
        self.empty_label.pack(expand=True)

        # Editor frame (hidden initially)
        self.editor_frame = tk.Frame(self.right_frame, bg=colors['bg_primary'])

        # Editor header
        editor_header = tk.Frame(self.editor_frame, bg=colors['bg_primary'])
        editor_header.pack(fill=tk.X, pady=(0, 10))

        self.editor_title = tk.Label(
            editor_header,
            text=self.i18n.t('agents.new'),
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
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.default_btn = tk.Button(
            editor_actions,
            text='⭐ ' + self.i18n.t('agents.set_default'),
            bg=colors['warning'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self._on_set_default,
        )
        self.default_btn.pack(side=tk.LEFT, padx=5)

        # Form
        form_frame = tk.Frame(self.editor_frame, bg=colors['bg_primary'])
        form_frame.pack(fill=tk.X, pady=10)

        # Name
        self._create_field(form_frame, self.i18n.t('agents.name'), 0)
        self.name_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.name_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0))

        # Provider
        self._create_field(form_frame, self.i18n.t('agents.provider'), 1)
        self.provider_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.provider_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0))

        # Endpoint
        self._create_field(form_frame, self.i18n.t('agents.endpoint'), 2)
        self.endpoint_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.endpoint_entry.grid(row=2, column=1, sticky='ew', padx=(10, 0))

        # API Key
        self._create_field(form_frame, self.i18n.t('agents.api_key'), 3)
        self.apikey_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
            show='*',
        )
        self.apikey_entry.grid(row=3, column=1, sticky='ew', padx=(10, 0))

        # Default Model
        self._create_field(form_frame, self.i18n.t('agents.default_model'), 4)
        self.model_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.model_entry.grid(row=4, column=1, sticky='ew', padx=(10, 0))

        # Models (available)
        models_label = tk.Label(
            form_frame,
            text=self.i18n.t('agents.models') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        models_label.grid(row=5, column=0, sticky='nw', pady=(10, 0))

        self.models_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.models_entry.grid(row=6, column=0, columnspan=2, sticky='ew', pady=(5, 0), padx=(0, 10))

        models_hint = tk.Label(
            form_frame,
            text=self.i18n.t('agents.models_placeholder'),
            font=('Segoe UI', 8),
            bg=colors['bg_primary'],
            fg=colors['text_secondary'],
        )
        models_hint.grid(row=7, column=0, columnspan=2, sticky='w', pady=(0, 10))

        # System Prompt
        prompt_label = tk.Label(
            form_frame,
            text=self.i18n.t('agents.system_prompt') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
            anchor='nw',
        )
        prompt_label.grid(row=8, column=0, sticky='nw', pady=(10, 0))

        self.prompt_text = tk.Text(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
            wrap=tk.WORD,
            height=6,
        )
        self.prompt_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(5, 0))

        form_frame.columnconfigure(1, weight=1)

    def _create_field(self, parent, label_text: str, row: int) -> None:
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

    def _load_agents(self) -> None:
        """Load agents from config."""
        config = self.config.load_agents_config()
        self._agents = config.get('agents', [])

        self.listbox.delete(0, tk.END)
        for agent in self._agents:
            default = ' ⭐' if agent.get('is_default', False) else ''
            self.listbox.insert(tk.END, f"{agent.get('name', 'Unknown')}{default}")

    def _on_select(self, event=None) -> None:
        """Handle agent selection."""
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index < len(self._agents):
            self._selected_agent = self._agents[index]
            self._show_editor()

    def _show_editor(self) -> None:
        """Show the agent editor."""
        self.empty_label.pack_forget()
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        if self._selected_agent:
            self.editor_title.config(text=f"📝 {self._selected_agent.get('name', '')}")
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self._selected_agent.get('name', ''))
            self.provider_entry.delete(0, tk.END)
            self.provider_entry.insert(0, self._selected_agent.get('provider', ''))
            self.endpoint_entry.delete(0, tk.END)
            self.endpoint_entry.insert(0, self._selected_agent.get('endpoint', ''))
            # Decrypt API key for display
            encrypted_key = self._selected_agent.get('api_key', '')
            if encrypted_key.startswith('encrypted:'):
                api_key = self.config.decrypt_secret(encrypted_key[10:])
            else:
                api_key = encrypted_key
            self.apikey_entry.delete(0, tk.END)
            self.apikey_entry.insert(0, api_key)
            self.model_entry.delete(0, tk.END)
            self.model_entry.insert(0, self._selected_agent.get('default_model', ''))
            self.models_entry.delete(0, tk.END)
            self.models_entry.insert(0, ', '.join(self._selected_agent.get('models', [])))
            self.prompt_text.delete('1.0', tk.END)
            self.prompt_text.insert('1.0', self._selected_agent.get('system_prompt', ''))

            if self._selected_agent.get('is_default', False):
                self.default_btn.config(text='⭐ ' + '已是默认')
            else:
                self.default_btn.config(text='⭐ ' + self.i18n.t('agents.set_default'))
        else:
            self.editor_title.config(text='➕ ' + self.i18n.t('agents.new'))
            self.name_entry.delete(0, tk.END)
            self.provider_entry.delete(0, tk.END)
            self.endpoint_entry.delete(0, tk.END)
            self.apikey_entry.delete(0, tk.END)
            self.model_entry.delete(0, tk.END)
            self.models_entry.delete(0, tk.END)
            self.prompt_text.delete('1.0', tk.END)

    def _on_new(self) -> None:
        """Create a new agent."""
        self._selected_agent = None
        self._show_editor()

    def _on_save(self) -> None:
        """Save the current agent."""
        name = self.name_entry.get().strip()
        provider = self.provider_entry.get().strip()
        endpoint = self.endpoint_entry.get().strip()
        api_key = self.apikey_entry.get().strip()
        default_model = self.model_entry.get().strip()
        models_str = self.models_entry.get().strip()
        system_prompt = self.prompt_text.get('1.0', tk.END).strip()

        if not name:
            messagebox.showwarning(
                self.i18n.t('common.field_required'),
                self.i18n.t('common.field_required')
            )
            return

        models = [m.strip() for m in models_str.split(',') if m.strip()]

        # Encrypt API key
        encrypted_key = 'encrypted:' + self.config.encrypt_secret(api_key) if api_key else ''

        agent_data = {
            'id': self._selected_agent.get('id', str(uuid.uuid4())) if self._selected_agent else str(uuid.uuid4()),
            'name': name,
            'provider': provider,
            'endpoint': endpoint,
            'api_key': encrypted_key,
            'default_model': default_model,
            'models': models,
            'system_prompt': system_prompt,
            'is_default': self._selected_agent.get('is_default', False) if self._selected_agent else False,
            'status': self._selected_agent.get('status', 'active') if self._selected_agent else 'active',
        }

        if self._selected_agent:
            # Update existing
            for i, a in enumerate(self._agents):
                if a.get('id') == self._selected_agent.get('id'):
                    self._agents[i] = agent_data
                    break
        else:
            # Add new
            self._agents.append(agent_data)

        # Save to config
        config = self.config.load_agents_config()
        config['agents'] = self._agents
        self.config.save_agents_config(config)

        messagebox.showinfo(
            self.i18n.t('common.success'),
            self.i18n.t('agents.save_success')
        )
        self._load_agents()

    def _on_delete(self) -> None:
        """Delete the selected agent."""
        if not self._selected_agent:
            return

        if messagebox.askyesno(
            self.i18n.t('agents.confirm_delete_title'),
            self.i18n.t('agents.confirm_delete')
        ):
            agent_id = self._selected_agent.get('id')
            self._agents = [a for a in self._agents if a.get('id') != agent_id]

            # Save
            config = self.config.load_agents_config()
            config['agents'] = self._agents
            self.config.save_agents_config(config)

            messagebox.showinfo(
                self.i18n.t('common.success'),
                self.i18n.t('agents.delete_success')
            )
            self._selected_agent = None
            self.editor_frame.pack_forget()
            self.empty_label.pack(expand=True)
            self._load_agents()

    def _on_set_default(self) -> None:
        """Set the selected agent as default."""
        if not self._selected_agent:
            return

        agent_id = self._selected_agent.get('id')

        for agent in self._agents:
            agent['is_default'] = (agent.get('id') == agent_id)

        # Save
        config = self.config.load_agents_config()
        config['agents'] = self._agents
        self.config.save_agents_config(config)

        self._load_agents()
        self._selected_agent = next((a for a in self._agents if a.get('id') == agent_id), None)
        self._show_editor()
