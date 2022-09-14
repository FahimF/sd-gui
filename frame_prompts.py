import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class PromptsFrame(tk.Frame):
	def __init__(self, parent, cfg, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.cfg = cfg
		# Configuration values
		lbl_font = parent.label_font
		tk.Grid.columnconfigure(self, 0, weight=1)
		tk.Grid.rowconfigure(self, 3, weight=1)
		# Create UI
		self.m_prompt = tk.Text(self, width=125, height=4, wrap=tk.WORD)
		self.m_prompt.grid(row=0, column=0, columnspan=2, padx=8, pady=(4, 2), sticky='EW')
		self.m_prompt.insert('1.0', cfg.prompt.prompt)
		# Actions
		m_actions = tk.Frame(self)
		m_actions.grid(row=1, column=0, columnspan=2)
		# Add
		tk.Button(m_actions, text="Add", command=self.add_prompt).grid(row=0, column=0)
		# Edit
		tk.Button(m_actions, text="Edit", command=self.edit_prompt).grid(row=0, column=2)
		# Delete
		tk.Button(m_actions, text="Delete", command=self.delete_prompt).grid(row=0, column=3)
		# Instructions
		tk.Label(self, text='Manage Prompts - select from the list below to edit/delete. Or, type a new prompt and add it.').grid(row=2, column=0, padx=(8, 8), pady=(4, 2), sticky='W')
		# Tree view of prompts
		self.m_prompts = ttk.Treeview(self, columns=(1, 2), show='headings', selectmode='browse')
		# Tree columns
		self.m_prompts.column(1, width=0, stretch=False)
		# Tree headings
		self.m_prompts.heading(1, text='Id', anchor=tk.CENTER)
		self.m_prompts.heading(2, text='Prompt', anchor=tk.W)
		# Add data
		for i, p in enumerate(cfg.prompts):
			self.m_prompts.insert(parent='', index=i, iid=i, text='', values=(f'{p.id}', p.prompt))
		self.m_prompts.grid(row=3, column=0, padx=8, pady=(4, 8), sticky='NSEW')
		# Tree scrollbar
		self.m_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.m_prompts.yview)
		self.m_prompts.configure(yscroll=self.m_scroll.set)
		self.m_scroll.grid(row=3, column=1, sticky='ns')
		self.m_prompts.bind('<<TreeviewSelect>>', self.item_selected)

	def item_selected(self, event):
		ndx = int(self.m_prompts.selection()[0])
		prompt = self.cfg.prompts[ndx]
		self.m_prompt.delete(1.0, tk.END)
		self.m_prompt.insert(tk.END, prompt)

	def add_prompt(self):
		prompt = self.m_prompt.get('1.0', tk.END).strip()
		# Verify that the prompt isn't already in list
		if prompt in self.cfg.prompts:
			messagebox.showerror(title='Are you sure?',
				message='The new prompt is already in history. Please enter a different prompt!',
				icon='warning')
			return
		i = len(self.cfg.prompts)
		self.cfg.add_prompt(prompt)
		self.m_prompts.insert(parent='', index=i, iid=i, text='', values=(f'{i}', prompt))

	def edit_prompt(self):
		prompt = self.m_prompt.get('1.0', tk.END).strip()
		sel = self.m_prompts.selection()[0]
		ndx = int(sel)
		curr = self.cfg.prompts[ndx]
		# If the new value matches the old value, do nothing
		if curr == prompt:
			return
		# Verify that the prompt isn't already in list
		cnt = self.cfg.prompts.count(prompt)
		if cnt > 0:
			messagebox.showerror(title='Are you sure?',
				message='The updated prompt is already in history. Please enter a different prompt!',
				icon='warning')
			return
		self.cfg.prompts[ndx] = prompt
		self.m_prompts.item(sel, text='', values=(f'{ndx}', prompt))

	def delete_prompt(self):
		sel = self.m_prompts.selection()[0]
		result = messagebox.askyesno(title='Are you sure?',
			message='This will delete the selected prompt. Do you want to proceed?',
			icon='warning')
		if not result:
			return
		self.m_prompts.delete(sel)