import tkinter as tk

class PromptsFrame(tk.Frame):
	def __init__(self, parent, cfg, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.cfg = cfg
		# Create UI
