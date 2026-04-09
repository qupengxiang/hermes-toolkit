# src/ui/cron.py
"""
Cron Tasks View
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List


class CronView:
    """Cron tasks management view."""

    def __init__(self, parent, app, i18n, cron_manager):
        self.parent = parent
        self.app = app
        self.i18n = i18n
        self.cron_manager = cron_manager

        self._selected_job: Optional[Dict[str, Any]] = None

        self._create_widgets()
        self._load_jobs()

    def _create_widgets(self) -> None:
        """Create all widgets."""
        colors = self.app.colors

        # Title
        title_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(
            title_frame,
            text=self.i18n.t('cron.title'),
            font=('Segoe UI', 18, 'bold'),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        title.pack(side=tk.LEFT)

        # New button
        self.new_btn = tk.Button(
            title_frame,
            text='➕ ' + self.i18n.t('cron.new'),
            bg=colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_new,
        )
        self.new_btn.pack(side=tk.RIGHT, padx=5)

        # Main content
        main_frame = tk.Frame(self.parent, bg=colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left - Jobs list
        left_frame = tk.Frame(main_frame, bg=colors['bg_secondary'], width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Jobs listbox
        list_frame = tk.Frame(left_frame, bg=colors['bg_secondary'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('name', 'status', 'schedule')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            style='Custom.Treeview',
        )
        self.tree.heading('name', text=self.i18n.t('cron.name'))
        self.tree.heading('status', text=self.i18n.t('cron.status'))
        self.tree.heading('schedule', text=self.i18n.t('cron.schedule'))
        self.tree.column('name', width=120)
        self.tree.column('status', width=80)
        self.tree.column('schedule', width=100)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Right - Detail/Editor
        self.right_frame = tk.Frame(main_frame, bg=colors['bg_primary'])
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Empty state
        self.empty_label = tk.Label(
            self.right_frame,
            text=self.i18n.t('cron.no_jobs'),
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
            text=self.i18n.t('cron.new'),
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

        self.pause_btn = tk.Button(
            editor_actions,
            text=self.i18n.t('cron.pause'),
            bg=colors['warning'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self._on_toggle_status,
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        # Form
        form_frame = tk.Frame(self.editor_frame, bg=colors['bg_primary'])
        form_frame.pack(fill=tk.X, pady=10)

        # Name
        name_label = tk.Label(
            form_frame,
            text=self.i18n.t('cron.name') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        name_label.grid(row=0, column=0, sticky='w', pady=5)

        self.name_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.name_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)

        # Schedule
        schedule_label = tk.Label(
            form_frame,
            text=self.i18n.t('cron.schedule') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        schedule_label.grid(row=1, column=0, sticky='w', pady=5)

        self.schedule_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
        )
        self.schedule_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)

        # Deliver
        deliver_label = tk.Label(
            form_frame,
            text=self.i18n.t('cron.deliver') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
        )
        deliver_label.grid(row=2, column=0, sticky='w', pady=5)

        self.deliver_var = tk.StringVar(value='origin')
        deliver_combo = ttk.Combobox(
            form_frame,
            textvariable=self.deliver_var,
            values=['origin', 'local', 'telegram'],
            state='readonly',
            font=('Segoe UI', 10),
        )
        deliver_combo.grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)

        # Prompt
        prompt_label = tk.Label(
            form_frame,
            text=self.i18n.t('cron.prompt') + ':',
            font=('Segoe UI', 10),
            bg=colors['bg_primary'],
            fg=colors['text_primary'],
            anchor='nw',
        )
        prompt_label.grid(row=3, column=0, sticky='nw', pady=(10, 0))

        self.prompt_text = tk.Text(
            form_frame,
            font=('Segoe UI', 11),
            bg='white',
            fg=colors['text_primary'],
            relief=tk.SOLID,
            insertbackground=colors['text_primary'],
            wrap=tk.WORD,
            height=8,
        )
        self.prompt_text.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(5, 0))

        form_frame.columnconfigure(1, weight=1)

    def _load_jobs(self) -> None:
        """Load and display jobs."""
        jobs = self.cron_manager.list_jobs()

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add jobs
        for job in jobs:
            status = '🟢' if job.status == 'active' else '⏸'
            self.tree.insert('', 'end', iid=job.job_id, values=(
                job.name,
                status,
                job.schedule,
            ))

    def _on_select(self, event=None) -> None:
        """Handle job selection."""
        selection = self.tree.selection()
        if not selection:
            return

        job_id = selection[0]
        job = self.cron_manager.get_job(job_id)
        if job:
            self._selected_job = job
            self._show_editor()

    def _show_editor(self) -> None:
        """Show the job editor."""
        self.empty_label.pack_forget()
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        if self._selected_job:
            self.editor_title.config(text=f"📝 {self._selected_job.name}")
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self._selected_job.name)
            self.schedule_entry.delete(0, tk.END)
            self.schedule_entry.insert(0, self._selected_job.schedule)
            self.deliver_var.set(self._selected_job.deliver)
            self.prompt_text.delete('1.0', tk.END)
            self.prompt_text.insert('1.0', self._selected_job.prompt)

            if self._selected_job.status == 'active':
                self.pause_btn.config(text=self.i18n.t('cron.pause'))
            else:
                self.pause_btn.config(text=self.i18n.t('cron.resume'))

            self.delete_btn.pack(side=tk.LEFT, padx=5)
        else:
            self.editor_title.config(text='➕ ' + self.i18n.t('cron.new'))
            self.name_entry.delete(0, tk.END)
            self.schedule_entry.delete(0, tk.END)
            self.schedule_entry.insert(0, 'every 1h')
            self.deliver_var.set('origin')
            self.prompt_text.delete('1.0', tk.END)
            self.delete_btn.pack_forget()

    def _on_new(self) -> None:
        """Create a new job."""
        self._selected_job = None
        self._show_editor()

    def _on_save(self) -> None:
        """Save the current job."""
        name = self.name_entry.get().strip()
        schedule = self.schedule_entry.get().strip()
        deliver = self.deliver_var.get()
        prompt = self.prompt_text.get('1.0', tk.END).strip()

        if not name or not schedule:
            messagebox.showwarning(
                self.i18n.t('common.field_required'),
                self.i18n.t('common.field_required')
            )
            return

        if self._selected_job:
            # Update
            self.cron_manager.update_job(
                self._selected_job.job_id,
                name=name,
                schedule=schedule,
                deliver=deliver,
                prompt=prompt,
            )
        else:
            # Create
            self.cron_manager.create_job(
                name=name,
                schedule=schedule,
                prompt=prompt,
                deliver=deliver,
            )

        messagebox.showinfo(
            self.i18n.t('common.success'),
            self.i18n.t('cron.save_success')
        )
        self._load_jobs()

    def _on_delete(self) -> None:
        """Delete the selected job."""
        if not self._selected_job:
            return

        if messagebox.askyesno(
            self.i18n.t('cron.confirm_delete_title'),
            self.i18n.t('skills.confirm_delete')
        ):
            if self.cron_manager.delete_job(self._selected_job.job_id):
                messagebox.showinfo(
                    self.i18n.t('common.success'),
                    self.i18n.t('cron.delete_success')
                )
                self._selected_job = None
                self.editor_frame.pack_forget()
                self.empty_label.pack(expand=True)
                self._load_jobs()

    def _on_toggle_status(self) -> None:
        """Toggle job pause/resume."""
        if not self._selected_job:
            return

        if self._selected_job.status == 'active':
            self.cron_manager.pause_job(self._selected_job.job_id)
        else:
            self.cron_manager.resume_job(self._selected_job.job_id)

        self._load_jobs()
        # Reload current job
        if self._selected_job:
            self._selected_job = self.cron_manager.get_job(self._selected_job.job_id)
            self._show_editor()
