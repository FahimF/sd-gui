import os
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk
from sd_engine import SDEngine, GeneratorType
from datetime import datetime

class TextFrame(tk.Frame):
	def __init__(self, parent, cfg, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.cfg = cfg
		self.parent = parent
		# Configuration values
		lbl_font = parent.label_font
		# Field values
		self.prompt = tk.StringVar(self, cfg.prompts[0])
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
		self.files = []
		self.seeds = []
		self.nsfw = []
		self.file_pointer = -1
		# Create UI - Prompt label
		tk.Label(self, text='Prompt', font=lbl_font).grid(row=2, column=0, padx=(8, 8), pady=(4, 2), sticky='W')
		# Prompt text field
		self.m_prompt = tk.Text(self, width=125, height=4, wrap=tk.WORD)
		self.m_prompt.grid(row=3, column=0, columnspan=2, padx=8, pady=(2, 4), sticky='EW')
		self.m_prompt.insert('1.0', cfg.prompt)
		# Previous prompts picker
		self.m_prompts = ttk.Combobox(self, state="readonly", textvariable=self.prompt, values=cfg.prompts)
		self.m_prompts.grid(row=4, column=0, columnspan=2, padx=8, pady=(2, 4), sticky='EW')
		self.m_prompts.bind('<<ComboboxSelected>>', self.prompts_changed)
		# Left frame
		self.m_left = tk.Frame(self)
		self.m_left.grid(row=5, column=0, sticky='NS')
		# Right frame
		self.m_right = tk.Frame(self)
		self.m_right.grid(row=5, column=1, sticky='NSEW')
		# Left - Input image label
		self.m_lbl_input = tk.Label(self.m_left, text='Input Image', font=lbl_font)
		self.m_lbl_input.grid(row=0, column=0, padx=(8, 8), pady=(4, 2), sticky='W')
		self.m_lbl_input.grid_forget()
		# Input image entry
		self.m_txt_input = tk.Entry(self.m_left, textvariable=self.init_image, width=30, state=tk.DISABLED)
		self.m_txt_input.grid(row=1, column=0, padx=(8, 4), pady=(2, 4), sticky='W')
		self.m_txt_input.grid_forget()
		# Input image button - to show open dialog
		self.m_btn_input = tk.Button(self.m_left, text='...', command=self.pick_image)
		self.m_btn_input.grid(row=1, column=1, padx=(4, 8), pady=(2, 4), sticky='W')
		self.m_btn_input.grid_forget()
		# Scheduler label
		tk.Label(self.m_left, text='Scheduler', font=lbl_font).grid(row=2, column=0, columnspan=2, padx=(8, 8), pady=(4, 2),
															  sticky='W')
		# Scheduler combo
		self.m_sched = ttk.Combobox(self.m_left, state="readonly", textvariable=self.scheduler,
							   values=['Default', 'LMS', 'PNDM', 'DDIM'])
		self.m_sched.grid(row=3, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		# Width and height section
		self.m_size = tk.Frame(self.m_left)
		self.m_size.grid(row=4, column=0, sticky='W')
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
		# Noise strength label
		self.m_lbl_strength = tk.Label(self.m_left, text='Noise Strength', font=lbl_font)
		self.m_lbl_strength.grid(row=5, column=0, columnspan=2, padx=(8, 8), pady=(4, 2), sticky='W')
		self.m_lbl_strength.grid_forget()
		# Noise strength slider
		self.m_strength = tk.Scale(self.m_left, orient=tk.HORIZONTAL, from_=0.0, to=1.0, resolution=0.01, digits=3, variable=self.strength,
						   length=350)
		self.m_strength.grid(row=6, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		self.m_strength.grid_forget()
		# Inference steps label
		tk.Label(self.m_left, text='Number of Inference Steps', font=lbl_font).grid(row=7, column=0, columnspan=2,
																			  padx=(8, 8),
																			  pady=(4, 2), sticky='W')
		# Inference steps slider
		self.m_num_steps = tk.Scale(self.m_left, orient=tk.HORIZONTAL, from_=1, to=300, variable=self.num_inference_steps, length=350)
		self.m_num_steps.grid(row=8, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		# Guidance label
		tk.Label(self.m_left, text='Guidance', font=lbl_font).grid(row=9, column=0, columnspan=2, padx=(8, 8), pady=(4, 2),
															 sticky='W')
		# Guidance slider
		self.m_guidance = tk.Scale(self.m_left, orient=tk.HORIZONTAL, from_=-15.0, to=30.0, resolution=0.1, digits=3,
						   variable=self.guidance_scale,
						   length=350)
		self.m_guidance.grid(row=10, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		# Number of images label
		tk.Label(self.m_left, text='Number of Images', font=lbl_font).grid(row=11, column=0, columnspan=2, padx=(8, 8),
																	 pady=(4, 2),
																	 sticky='W')
		# Number of images spinner
		self.m_copies = tk.Spinbox(self.m_left, from_=1, to=20, textvariable=self.num_copies)
		self.m_copies.grid(row=12, column=0, columnspan=2, padx=(8, 8), pady=(2, 4), sticky='W')
		# Seed label
		tk.Label(self.m_left, text='Seed', font=lbl_font).grid(row=13, column=0, columnspan=2, padx=(8, 8), pady=(4, 2),
														 sticky='W')
		# Seed entry
		self.m_seed = tk.Entry(self.m_left, textvariable=self.seed, width=30)
		self.m_seed.grid(row=14, column=0, padx=(8, 4), pady=(2, 4), sticky='W')
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

	def prompts_changed(self, event):
		# Validate that the current prompt is saved
		curr = self.m_prompt.get(1.0, tk.END).strip()
		print(f'Current prompt: {curr}')
		print(f'Prompts: {self.cfg.prompts}')
		if not curr in self.cfg.prompts:
			result = tk.messagebox.askyesno(title='Are you sure?',
												 message='The current prompt is not in history. Do you want to replace it?',
												 icon='warning')
			if not result:
				return
		prompt = self.prompt.get()
		self.m_prompt.delete(1.0, tk.END)
		self.m_prompt.insert(tk.END, prompt)

	def pick_image(self):
		path = fd.askopenfilename(title='Select image file', filetypes=[('Images', ('*.png', '*.jpeg', '*.jpg'))])
		path = os.path.relpath(path)
		self.init_image.set(path)

	def previous_image(self):
		if self.file_pointer > 0:
			self.file_pointer -= 1
			if self.file_pointer == 0:
				self.m_prev['state'] = tk.DISABLED
			# Enable Next button if it was disabled
			if self.m_next['state'] == tk.DISABLED:
				self.m_next['state'] = tk.NORMAL
			self.show_image()

	def delete_image(self):
		file = self.files[self.file_pointer]
		os.remove(file)
		print(f"Deleted image: {file}")
		self.files.remove(file)
		self.seeds.pop(self.file_pointer)
		self.nsfw.pop(self.file_pointer)
		# Delete prompt file, if it exists
		fn = os.path.splitext(file)[0]
		pf = fn + ".txt"
		if os.path.exists(pf):
			os.remove(pf)
			print(f"Deleted prompt: {pf}")
		# If there are no more images, hide image part
		if len(self.files) == 0:
			self.file_pointer = -1
			self.toggle_image(False)
			self.count.set(f'Number of images: 0')
			return
		elif len(self.files) == 1:
			# Onlye one image, show it but disable buttons
			self.file_pointer = 0
			self.m_prev['state'] = tk.DISABLED
			self.m_next['state'] = tk.DISABLED
		else:
			# Change pointer to the next one
			if self.file_pointer != 0:
				self.file_pointer -= 1
		self.show_image()

	def next_image(self):
		global file_pointer

		if self.file_pointer != len(self.files) - 1:
			self.file_pointer += 1
			if self.file_pointer == len(self.files) - 1:
				self.m_next['state'] = tk.DISABLED
			# Enable Previous button if it was disabled
			if self.m_prev['state'] == tk.DISABLED:
				self.m_prev['state'] = tk.NORMAL
			self.show_image()

	def resized(self, event):
		# A widget was resized
		if event.widget == self.m_right:
			# Update the canvas width
			wd = event.width - 24
			self.m_image.config(width=wd)
			# Redisplay the current image if there is one
			if len(self.files) > 0:
				self.show_image()

	def show_image(self):
		# Image
		path = self.files[self.file_pointer]
		pi = Image.open(path)
		iw = int(self.m_image['width'])
		ih = int(self.m_image['height'])
		ratio = min(iw / self.cfg.width, ih / self.cfg.height)
		wd = int(self.cfg.width * ratio)
		ht = int(self.cfg.height * ratio)
		pi = pi.resize(size=(wd, ht), resample=Image.Resampling.LANCZOS)
		self.img = img = ImageTk.PhotoImage(pi)
		x = (iw - wd) / 2
		y = (ih - ht) / 2
		self.m_image.create_image((x, y), image=img, anchor='nw')
		# Image count
		self.count.set(f'Number of images: {len(self.files)}')
		# Seed
		seed = self.seeds[self.file_pointer]
		self.img_seed.set(seed)
		# NSFW
		self.m_nsfw.select() if self.nsfw[self.file_pointer] else self.m_nsfw.deselect()

	def toggle_image(self, show):
		if show:
			self.m_info.grid(row=1, column=0)
			self.m_actions.grid(row=3, column=0)
		else:
			self.m_image.delete('all')
			self.m_info.grid_forget()
			self.m_actions.grid_forget()

	def generate_images(self):
		# Get current values
		self.cfg.type = GeneratorType.txt2img
		self.cfg.prompt = self.m_prompt.get('1.0', tk.END).strip()
		# Add new prompt to the prompts array - deduping and other logic in method
		self.cfg.add_prompt(self.cfg.prompt)
		self.cfg.input_image = self.init_image.get()
		self.cfg.scheduler = self.scheduler.get()
		self.cfg.width = self.width.get()
		if self.cfg.width % 8 != 0:
			self.cfg.width = self.cfg.width - (self.cfg.width % 8)
		self.cfg.height = self.height.get()
		if self.cfg.height % 8 != 0:
			self.cfg.height = self.cfg.height - (self.cfg.height % 8)
		self.cfg.noise_strength = self.strength.get()
		self.cfg.num_inference_steps = self.num_inference_steps.get()
		self.cfg.guidance_scale = self.guidance_scale.get()
		self.cfg.num_copies = self.num_copies.get()
		self.cfg.seed = self.seed.get()
		# Save current configuration before image generation
		self.cfg.save()
		self.cfg.display()
		# Validations - must have image if IMG2IMG
		if self.cfg.type == GeneratorType.img2img:
			# Is there an image specified?
			if len(self.cfg.input_image) == 0 or not os.path.exists(self.cfg.input_image):
				tk.messagebox.showwarning(title='Error',
											   message='You need to select a valid Input Image if you want to use an image input.')
				return
		# TODO - If there's a non-random seed value but number of copies is not 1, should we warn/exit?
		# We are good to go - set up for process
		self.m_generate['state'] = tk.DISABLED
		self.files.clear()
		self.seeds.clear()
		self.nsfw.clear()
		self.file_pointer = 0
		sd = SDEngine(self.cfg)
		for i in range(self.cfg.num_copies):
			start = time.time()
			# Generate an image using engine
			image, is_nsfw, seed = sd.generate()
			self.nsfw.append(is_nsfw)
			self.seeds.append(self.cfg.seed)
			end = time.time()
			tm = end - start
			if is_nsfw:
				print("NSFW image detected!")
			else:
				dt = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
				fn = f"output/sample_{dt}.png"
				# Save image
				image.save(fn)
				self.files.append(fn)
				print(f"Saved image to: {fn}")
			# Save prompt
			tn = f"output/sample_{dt}.txt"
			h = open(tn, "w")
			h.write(f"Engine: {self.cfg.type}\n")
			h.write(f"Scheduler: {self.cfg.scheduler}\n")
			h.write(f"prompt={self.cfg.prompt}\n")
			h.write(f"width={self.cfg.width}\n")
			h.write(f"height={self.cfg.height}\n")
			if self.cfg.type == GeneratorType.img2img:
				h.write(f"image={self.cfg.input_image}\n")
				h.write(f"strength = {self.cfg.noise_strength}\n")
			h.write(f"num_inference_steps = {self.cfg.num_inference_steps}\n")
			h.write(f"guidance_scale = {self.cfg.guidance_scale}\n")
			h.write(f"Is NSFW? = {is_nsfw}\n")
			h.write(f"Time taken = {tm}s\n")
			h.write(f'Seed = {self.cfg.seed}\n')
			h.close()
			# Console output
			print(f"Time taken: {tm}s")
		# Done with copy loop
		print(f"Generated {self.num_copies.get()} images")
		# Show first image result and update UI
		self.m_generate['state'] = tk.NORMAL
		self.toggle_image(True)
		self.show_image()
		# Reset button states
		self.m_prev['state'] = tk.DISABLED
		if len(self.files) == 1:
			self.m_next['state'] = tk.DISABLED
		elif len(self.files) >= 2:
			self.m_next['state'] = tk.NORMAL
