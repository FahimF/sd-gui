import os
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog as fd
from PIL import Image, ImageTk
from sd_engine import SDEngine, GeneratorType
from datetime import datetime
from data.batch import Batch
from data.image import Image as DImg

class BaseFrame(tk.Frame):
	def __init__(self, parent, cfg, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.cfg = cfg
		self.parent = parent

	def prompts_changed(self, event):
		# Validate that the current prompt is saved
		curr = self.m_prompt.get(1.0, tk.END).strip()
		print(f'Current prompt: {curr}')
		print(f'Prompts: {self.cfg.prompts}')
		if not curr in self.cfg.string_prompts():
			result = messagebox.askyesno(title='Are you sure?',
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
		# Display thumbnail
		pi = Image.open(path)
		self.thumb = self.fit_image(self.m_input_image, pi, 128, 128)

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

	def fit_image(self, dest, image, width, height):
		iw = int(dest['width'])
		ih = int(dest['height'])
		ratio = min(iw / width, ih / height)
		wd = int(width * ratio)
		ht = int(height * ratio)
		image = image.resize(size=(wd, ht), resample=Image.Resampling.LANCZOS)
		x = (iw - wd) / 2
		y = (ih - ht) / 2
		img = ImageTk.PhotoImage(image)
		dest.create_image((x, y), image=img, anchor='nw')
		return img

	def show_image(self):
		# Image
		path = self.files[self.file_pointer]
		pi = Image.open(path)
		self.img = self.fit_image(self.m_image, pi, self.cfg.width, self.cfg.height)
		# self.img = ImageTk.PhotoImage(pi)
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
		# Get current prompt
		prompt = self.m_prompt.get('1.0', tk.END).strip()
		# Add new prompt to the prompts array - deduping and other logic is in method
		self.cfg.add_prompt(prompt)
		# Update prompts list
		self.m_prompts['values'] = self.cfg.string_prompts
		# Create new batch record and save it
		batch = Batch(self.cfg.db)
		batch.prompt_id = self.cfg.prompt.id
		# Get batch settings
		batch.input_image = self.cfg.input_image = self.init_image.get()
		batch.scheduler = self.cfg.scheduler = self.scheduler.get()
		batch.width = self.cfg.width = self.width.get()
		if self.cfg.width % 8 != 0:
			self.cfg.width = self.cfg.width - (self.cfg.width % 8)
			batch.width = self.cfg.width
		batch.height = self.cfg.height = self.height.get()
		if self.cfg.height % 8 != 0:
			self.cfg.height = self.cfg.height - (self.cfg.height % 8)
			batch.height = self.cfg.height
		batch.noise_strength = self.cfg.noise_strength = self.strength.get()
		batch.inference_steps = self.cfg.num_inference_steps = self.num_inference_steps.get()
		batch.guidance_scale = self.cfg.guidance_scale = self.guidance_scale.get()
		batch.num_copies = self.cfg.num_copies = self.num_copies.get()
		batch.seed = self.cfg.seed = self.seed.get()
		# Save current configuration before image generation
		self.cfg.save()
		self.cfg.display()
		batch.save()
		# Validations - must have image if IMG2IMG
		if self.type == GeneratorType.img2img:
			# Is there an image specified?
			if len(self.cfg.input_image) == 0 or not os.path.exists(self.cfg.input_image):
				messagebox.showwarning(title='Error',
					message='You need to select a valid Input Image if you want to use an image input.')
				return
		# TODO - If there's a non-random seed value but number of copies is not 1, should we warn/exit?
		# We are good to go - set up for process
		self.m_generate['state'] = tk.DISABLED
		self.files.clear()
		self.seeds.clear()
		self.nsfw.clear()
		self.file_pointer = 0
		sd = SDEngine(self.cfg, self.type)
		total = 0.0
		for i in range(self.cfg.num_copies):
			start = time.time()
			# Generate an image using engine
			image, is_nsfw, seed = sd.generate()
			self.nsfw.append(is_nsfw)
			self.seeds.append(seed)
			end = time.time()
			tm = end - start
			total += tm
			if is_nsfw:
				print("NSFW image detected!")
			else:
				dt = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
				fn = f"output/sample_{dt}.png"
				# Save image
				image.save(fn)
				self.files.append(fn)
				print(f"Saved image to: {fn}")
			# Save Image info
			di = DImg(self.cfg.db)
			di.batch_id = batch.id
			di.path = fn
			di.seed = seed
			di.nsfw = is_nsfw
			di.time_taken = tm
			di.save()
			# Save prompt data
			tn = f"output/sample_{dt}.txt"
			h = open(tn, "w")
			h.write(f"Engine: {self.type}\n")
			h.write(f"Scheduler: {self.cfg.scheduler}\n")
			h.write(f"prompt={self.cfg.prompt.prompt}\n")
			h.write(f"width={self.cfg.width}\n")
			h.write(f"height={self.cfg.height}\n")
			if self.type == GeneratorType.img2img:
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
		# Save final batch info
		batch.time_taken = total
		batch.save()
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
