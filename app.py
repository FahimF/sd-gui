import tkinter as tk
from tkinter import font
from tkinter import ttk
from frame_text import TextFrame
from frame_image import ImageFrame
from frame_prompts import PromptsFrame
from config import Config

class App(tk.Tk):
	def __init__(self):
		super().__init__()
		# Load configuration info
		cfg = Config()
		# Basic configuration
		self.title('Stable Diffusion')
		wd = 940
		ht = 870
		x = int((self.winfo_screenwidth() - wd) / 2)
		y = int((self.winfo_screenheight() - ht) / 2)
		self.geometry(f'{wd}x{ht}+{x}+{y}')
		self.resizable(True, True)
		self.iconphoto(False, tk.PhotoImage(file='assets/icon.png'))
		# Notebook
		style = ttk.Style()
		style.configure('TNotebook.Tab', padding=(12, 12, 12, 12))
		style.map("TNotebook.padding", background=[("selected", 'red')])
		# style.map('TNotebook.Tab', foreground=[('selected', '!background', 'systemWhite')])
		self.notebook = ttk.Notebook(self, width=wd, height=ht, padding=0)
		self.notebook.pack(expand=1, fill='both')
		# UI configuration values
		self.notebook.label_font = font.Font(self, weight=font.BOLD)
		# Text tab
		frm_text = TextFrame(self.notebook, cfg)
		frm_text.pack(fill='both', expand=1)
		# Image tab
		frm_image = ImageFrame(self.notebook, cfg)
		frm_image.pack(fill='both', expand=1)
		# Prompts tab
		frm_prompts = PromptsFrame(self.notebook, cfg)
		frm_prompts.pack(fill='both', expand=1)
		# Tabs
		self.notebook.add(frm_text, text='Text Prompt')
		self.notebook.add(frm_image, text='Image Prompt')
		self.notebook.add(frm_prompts, text='Prompts')

if __name__ == '__main__':
	app = App()
	app.mainloop()