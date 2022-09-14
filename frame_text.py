import tkinter as tk
from tkinter import ttk
from frame_base import BaseFrame
from sd_engine import GeneratorType

class TextFrame(BaseFrame):
	def __init__(self, parent, cfg, *args, **kwargs):
		BaseFrame.__init__(self, parent, cfg, *args, **kwargs)
		# Configuration values
		lbl_font = parent.label_font
		# Field values
		self.prompt = tk.StringVar(self, cfg.prompt.prompt)
		self.init_image = tk.StringVar(self, '')
		self.scheduler = tk.StringVar(self, cfg.scheduler)
		self.width = tk.IntVar(self, cfg.width)
		self.height = tk.IntVar(self, cfg.height)
		self.strength = tk.DoubleVar(self, cfg.noise_strength)
		self.num_inference_steps = tk.IntVar(self, cfg.num_inference_steps)
		self.guidance_scale = tk.DoubleVar(self, cfg.guidance_scale)
		self.num_copies = tk.IntVar(self, cfg.num_copies)
		self.seed = tk.IntVar(self, cfg.seed)
		self.img_seed = tk.StringVar(self, cfg.seed)
		self.count = tk.StringVar(self, 'Number of images: 0')
		# Other values
		self.type = GeneratorType.txt2img
		self.files = []
		self.seeds = []
		self.nsfw = []
		self.file_pointer = -1
		tk.Grid.columnconfigure(self, 1, weight=1)
		# Create UI - Prompt label
		tk.Label(self, text='Prompt', font=lbl_font).grid(row=0, column=0, padx=(8, 8), pady=(4, 2), sticky='W')
		# Prompt text field
		self.m_prompt = tk.Text(self, width=125, height=4, wrap=tk.WORD)
		self.m_prompt.grid(row=1, column=0, columnspan=2, padx=8, pady=(2, 4), sticky='EW')
		self.m_prompt.insert('1.0', cfg.prompt.prompt)
		# Previous prompts picker
		items = cfg.string_prompts()
		self.m_prompts = ttk.Combobox(self, state="readonly", textvariable=self.prompt, values=items)
		self.m_prompts.grid(row=2, column=0, columnspan=2, padx=8, pady=(2, 4), sticky='EW')
		self.m_prompts.bind('<<ComboboxSelected>>', self.prompts_changed)
		# Left frame
		self.m_left = tk.Frame(self)
		self.m_left.grid(row=3, column=0, sticky='NS')
		# Right frame
		self.m_right = tk.Frame(self)
		self.m_right.grid(row=3, column=1, sticky='NSEW')
		# Scheduler label
		tk.Label(self.m_left, text='Scheduler', font=lbl_font).grid(row=0, column=0, columnspan=2, padx=(8, 8), pady=(4, 2),
															  sticky='W')
		# Scheduler combo
		self.m_sched = ttk.Combobox(self.m_left, state="readonly", textvariable=self.scheduler,
							   values=['Default', 'LMS', 'PNDM', 'DDIM'])
		self.m_sched.grid(row=1, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		# Width and height section
		self.m_size = tk.Frame(self.m_left)
		self.m_size.grid(row=2, column=0, sticky='W')
		# Title
		tk.Label(self.m_size, text='Image Size', font=lbl_font).grid(row=0, column=0, columnspan=2, padx=(8, 8), pady=(4, 2),
															   sticky='W')
		# Explanation
		tk.Label(self.m_size, text='Should be a multiple of 8. Preferably one size should be 512').grid(row=1, column=0,
																								columnspan=2,
																								padx=(8, 8),
																								pady=(4, 2),
																								sticky='W')
		# Width label
		tk.Label(self.m_size, text='Width', font=lbl_font).grid(row=2, column=0, padx=(8, 8), pady=(4, 2), sticky='W')
		# Height label
		tk.Label(self.m_size, text='Height', font=lbl_font).grid(row=2, column=1, padx=(8, 8), pady=(4, 2), sticky='W')
		# Width field
		self.m_width = tk.Entry(self.m_size, textvariable=self.width, width=10)
		self.m_width.grid(row=3, column=0, padx=(8, 4), pady=(2, 4), sticky='W')
		# Height field
		self.m_height = tk.Entry(self.m_size, textvariable=self.height, width=10)
		self.m_height.grid(row=3, column=1, padx=(8, 4), pady=(2, 4), sticky='W')
		# Inference steps label
		tk.Label(self.m_left, text='Number of Inference Steps', font=lbl_font).grid(row=3, column=0, columnspan=2,
																			  padx=(8, 8),
																			  pady=(4, 2), sticky='W')
		# Inference steps slider
		self.m_num_steps = tk.Scale(self.m_left, orient=tk.HORIZONTAL, from_=1, to=300, variable=self.num_inference_steps, length=350)
		self.m_num_steps.grid(row=4, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		# Guidance label
		tk.Label(self.m_left, text='Guidance', font=lbl_font).grid(row=5, column=0, columnspan=2, padx=(8, 8), pady=(4, 2),
															 sticky='W')
		# Guidance slider
		self.m_guidance = tk.Scale(self.m_left, orient=tk.HORIZONTAL, from_=-15.0, to=30.0, resolution=0.1, digits=3,
						   variable=self.guidance_scale,
						   length=350)
		self.m_guidance.grid(row=6, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		# Number of images label
		tk.Label(self.m_left, text='Number of Images', font=lbl_font).grid(row=7, column=0, columnspan=2, padx=(8, 8),
																	 pady=(4, 2),
																	 sticky='W')
		# Number of images spinner
		self.m_copies = tk.Spinbox(self.m_left, from_=1, to=20, textvariable=self.num_copies)
		self.m_copies.grid(row=8, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		# Seed label
		tk.Label(self.m_left, text='Seed', font=lbl_font).grid(row=9, column=0, columnspan=2, padx=(8, 8), pady=(4, 2),
														 sticky='W')
		# Seed entry
		self.m_seed = tk.Entry(self.m_left, textvariable=self.seed, width=30)
		self.m_seed.grid(row=10, column=0, padx=(8, 4), pady=(2, 4), sticky='W')
		# Right - Output image
		self.m_image = tk.Canvas(self.m_right, width=512, height=512, bg='lightgrey')
		self.m_image.grid(row=0, column=0, padx=8, pady=(4, 4))
		# Info frame
		self.m_info = tk.Frame(self.m_right)
		self.m_info.grid(row=1, column=0, sticky='EW')
		# Seed label
		tk.Label(self.m_info, text='Seed').grid(row=0, column=0, padx=(0, 8), pady=(4, 2), sticky='W')
		# Seed entry
		self.m_img_seed = tk.Entry(self.m_info, textvariable=self.img_seed, width=30)
		self.m_img_seed.grid(row=0, column=1, padx=(0, 8), pady=(4, 2), sticky='W')
		# NSFW label
		tk.Label(self.m_info, text='NSFW Image?').grid(row=0, column=2, padx=(8, 8), pady=(4, 2), sticky='W')
		# NSFW checkbox
		self.m_nsfw = tk.Checkbutton(self.m_info, state=tk.DISABLED)
		self.m_nsfw.grid(row=0, column=3, padx=(0, 8), pady=(4, 2), sticky='W')
		self.m_info.grid_forget()
		# Image count label
		self.m_count = tk.Label(self.m_right, textvariable=self.count)
		self.m_count.grid(row=2, column=0, padx=(8, 8), pady=(4, 2), sticky='EW')
		# Actions Frame
		self.m_actions = tk.Frame(self.m_right)
		self.m_actions.grid(row=3, column=0, pady=(16, 0), sticky='EW')
		# Previous button
		self.m_prev = tk.Button(self.m_actions, text="Previous", command=self.previous_image)
		self.m_prev.grid(row=0, column=0, padx=(0, 24))
		# Delete button
		self.m_del = tk.Button(self.m_actions, text="Delete", command=self.delete_image)
		self.m_del.grid(row=0, column=1, padx=(0, 24))
		# Next button
		self.m_next = tk.Button(self.m_actions, text="Next", command=self.next_image)
		self.m_next.grid(row=0, column=2, padx=(0, 24))
		self.m_actions.grid_forget()
		# Main - Separator
		ttk.Separator(self, orient='horizontal').grid(row=6, column=0, columnspan=2, pady=8, sticky='EW')
		# Generate button
		self.m_generate = tk.Button(self, text="Generate!", command=self.generate_images)
		self.m_generate.grid(row=7, column=0, columnspan=2)
		# Resize handling
		self.m_right.update_idletasks()
		self.m_right.bind("<Configure>", self.resized)