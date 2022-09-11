import os
import torch
import time
import tkinter.messagebox
from config import Config
from tkinter import *
from tkinter import font, ttk
from tkinter import filedialog as fd
from diffusers import StableDiffusionPipeline
from diffusers.pipelines import StableDiffusionImg2ImgPipeline
from diffusers.schedulers import LMSDiscreteScheduler, DDPMScheduler, DDIMScheduler, PNDMScheduler
from PIL import Image, ImageTk
from datetime import datetime

# Action methods
def type_changed(event):
	global cfg

	# If the type is Text + images, show the image picker options
	type = g_type.get()
	if type == 'Text + Image Prompt':
		m_lbl_input.grid(row=0, column=0, padx=(16, 8), pady=(4, 2), sticky=W)
		m_txt_input.grid(row=1, column=0, padx=(16, 8), pady=(2, 4), sticky=W)
		m_btn_input.grid(row=1, column=1, padx=8, pady=(2, 4), sticky=W)
		m_lbl_strength.grid(row=4, column=0, columnspan=2, padx=(16, 8), pady=(4, 2), sticky=W)
		m_strength.grid(row=5, column=0, columnspan=2, padx=(16, 8), pady=(2, 4), sticky=W)
	else:
		m_lbl_input.grid_forget()
		m_txt_input.grid_forget()
		m_btn_input.grid_forget()
		m_lbl_strength.grid_forget()
		m_strength.grid_forget()

def prompts_changed(event):
	global cfg

	# Validate that the current prompt is saved
	curr = m_prompt.get(1.0, END).strip()
	print(f'Current prompt: {curr}')
	print(f'Prompts: {cfg.prompts}')
	if not curr in cfg.prompts:
		result = tkinter.messagebox.askyesno(title='Are you sure?',
			message='The current prompt is not in history. Do you want to replace it?',
			icon='warning')
		if not result:
			return
	prompt = g_prompt.get()
	m_prompt.delete(1.0, END)
	m_prompt.insert(END, prompt)

def pick_image():
	path = fd.askopenfilename(title='Select image file', filetypes=[('Images', ('*.png', '*.jpeg', '*.jpg'))])
	path = os.path.relpath(path)
	g_init_image.set(path)

def toggle_image(show):
	if show:
		# m_image.grid(row=0, column=0, padx=(8, 16), pady=(4, 4), sticky=E)
		m_info.grid(row=1, column=0)
		m_actions.grid(row=3, column=0)
	else:
		m_image.delete('all')
		m_info.grid_forget()
		m_actions.grid_forget()

def show_image():
	global cfg, g_img_seed, g_seeds, g_count

	# Image
	path = g_files[g_file_pointer]
	pi = Image.open(path)
	ratio = min(512 / cfg.width, 512 / cfg.height)
	wd = int(cfg.width * ratio)
	ht = int(cfg.height * ratio)
	pi = pi.resize(size=(wd, ht), resample=Image.Resampling.LANCZOS)
	root.img = img = ImageTk.PhotoImage(pi)
	x = (512 - wd) / 2
	y = (512 - ht) / 2
	m_image.create_image((x, y), image=img, anchor='nw')
	# Image count
	g_count.set(f'Number of images: {len(g_files)}')
	# Seed
	seed = g_seeds[g_file_pointer]
	g_img_seed.set(seed)
	# NSFW
	m_nsfw.select() if g_nsfw[g_file_pointer] else m_nsfw.deselect()

def previous_image():
	global g_file_pointer

	if g_file_pointer > 0:
		g_file_pointer -= 1
		if g_file_pointer == 0:
			m_prev['state'] = DISABLED
		# Enable Next button if it was disabled
		if m_next['state'] == DISABLED:
			m_next['state'] = NORMAL
		show_image()

def delete_image():
	global g_file_pointer, g_files, g_seeds, g_nsfw, g_count

	file = g_files[g_file_pointer]
	os.remove(file)
	print(f"Deleted image: {file}")
	g_files.remove(file)
	g_seeds.pop(g_file_pointer)
	g_nsfw.pop(g_file_pointer)
	# Delete prompt file, if it exists
	fn = os.path.splitext(file)[0]
	pf = fn + ".txt"
	if os.path.exists(pf):
		os.remove(pf)
		print(f"Deleted prompt: {pf}")
	# If there are no more images, hide image part
	if len(g_files) == 0:
		toggle_image(False)
		g_count.set(f'Number of images: 0')
		return
	elif len(g_files) == 1:
		# Onlye one image, show it but disable buttons
		g_file_pointer = 0
		m_prev['state'] = DISABLED
		m_next['state'] = DISABLED
	else:
		# Change pointer to the next one
		if g_file_pointer != 0:
			g_file_pointer -= 1
	show_image()

def next_image():
	global g_file_pointer

	if g_file_pointer != len(g_files) - 1:
		g_file_pointer += 1
		if g_file_pointer == len(g_files) - 1:
			m_next['state'] = DISABLED
		# Enable Previous button if it was disabled
		if m_prev['state'] == DISABLED:
			m_prev['state'] = NORMAL
		show_image()

def generate_images():
	global cfg, g_files, g_seeds, g_nsfw, g_file_pointer, g_init_image, generator

	# Get current values
	cfg.type = g_type.get()
	cfg.prompt = m_prompt.get('1.0', END).strip()
	# Add new prompt to the prompts array - deduping and other logic in method
	cfg.add_prompt(cfg.prompt)
	cfg.input_image = g_init_image.get()
	cfg.scheduler = g_scheduler.get()
	cfg.width = g_width.get()
	if cfg.width % 8 != 0:
		cfg.width = cfg.width - (cfg.width % 8)
	cfg.height = g_height.get()
	if cfg.height % 8 != 0:
		cfg.height = cfg.height - (cfg.height % 8)
	cfg.noise_strength = g_strength.get()
	cfg.num_inference_steps = g_num_inference_steps.get()
	cfg.guidance_scale = g_guidance_scale.get()
	cfg.num_copies = g_num_copies.get()
	cfg.seed = g_seed.get()
	# Save current configuration before image generation
	cfg.save()
	print(
		f'Type: {cfg.type}\nScheduler: {cfg.scheduler}\nPrompt: {cfg.prompt}\nWidth: {cfg.width}\nHeight: {cfg.height}\n'
		f'Strength: {cfg.noise_strength}\nNum Stpes: {cfg.num_inference_steps}\nGuidance: {cfg.guidance_scale}\n'
		f'Copies: {cfg.num_copies}\nSeed: {cfg.seed}')
	# Validations - must have image if IMG2IMG
	if cfg.type == 'Text + Image Prompt':
		# Is there an image specified?
		if len(cfg.input_image) == 0 or not os.path.exists(cfg.input_image):
			tkinter.messagebox.showwarning(title='Error',
				message='You need to select a valid Input Image if you want to use an image input.')
			return
	# TODO - If there's a non-random seed value but number of copies is not 1, should we warn/exit?
	# We are good to go - set up for process
	m_generate['state'] = DISABLED
	g_files.clear()
	g_seeds.clear()
	g_nsfw.clear()
	g_file_pointer = 0
	# Device definition
	device = torch.device(
		"cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
	# Set up scheduler based on selection
	sched = None
	if cfg.scheduler == 'LMS':
		# beta_schedule can be linear or scaled_linear
		sched = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear")
	elif cfg.scheduler == 'PNDM':
		# beta_schedule can be linear, scaled_linear, or squaredcos_cap_v2
		sched = PNDMScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="linear")
	elif cfg.scheduler == 'DDIM':
		# beta_schedule can be linear, scaled_linear, or squaredcos_cap_v2
		sched = DDIMScheduler(beta_start=0.0009, beta_end=0.0120, beta_schedule="scaled_linear", clip_sample=False)
	# Set scheduler values
	if sched is not None:
		sched.num_inference_steps = cfg.num_inference_steps
	# Set up pipeline based on type
	if cfg.type == 'Text Prompt':
		if sched is None:
			pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-4").to(device)
		else:
			pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-4", scheduler=sched).to(device)
	else:
		if sched is None:
			pipe = StableDiffusionImg2ImgPipeline.from_pretrained("stable-diffusion-v1-4").to(device)
		else:
			pipe = StableDiffusionImg2ImgPipeline.from_pretrained("stable-diffusion-v1-4", scheduler=sched).to(device)
	# Disable NSFW checks - stops giving you black images
	pipe.safety_checker = lambda images, **kwargs: (images, False)
	# Load and prepare image if type is img2img
	if cfg.type == 'Text + Image Prompt':
		image = Image.open(cfg.input_image).convert("RGB")
		wd, ht = image.size
		if wd != cfg.width or ht != cfg.height:
			image = image.resize((cfg.width, cfg.height))
	for i in range(cfg.num_copies):
		start = time.time()
		# Get a new random seed, store it and use it as the generator state
		if cfg.seed == -1:
			cfg.seed = generator.seed()
		print(f'Seed for new image: {cfg.seed}')
		# Update generator with seed
		generator = generator.manual_seed(cfg.seed)
		g_seeds.append(cfg.seed)
		latent = torch.randn((1, pipe.unet.in_channels, cfg.height // 8, cfg.width // 8),
			generator=generator, device=device)
		if cfg.type == 'Text + Image Prompt':
			result = pipe(prompt=cfg.prompt, init_image=image, strength=cfg.noise_strength,
				num_inference_steps=cfg.num_inference_steps, guidance_scale=cfg.guidance_scale,
				generator=generator)
		else:
			result = pipe(prompt=cfg.prompt, num_inference_steps=cfg.num_inference_steps, width=cfg.width, height=cfg.height,
				guidance_scale=cfg.guidance_scale, latents=latent)
		image = result["sample"][0]
		is_nsfw = result["nsfw_content_detected"]
		g_nsfw.append(is_nsfw)
		end = time.time()
		tm = end - start
		if is_nsfw:
			print("NSFW image detected!")
		else:
			dt = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
			fn = f"output/sample_{dt}.png"
			# Save image
			image.save(fn)
			g_files.append(fn)
			print(f"Saved image to: {fn}")
		# Save prompt
		tn = f"output/sample_{dt}.txt"
		h = open(tn, "w")
		h.write(f"Engine: {cfg.type}\n")
		h.write(f"Scheduler: {cfg.scheduler}\n")
		h.write(f"prompt={cfg.prompt}\n")
		h.write(f"width={cfg.width}\n")
		h.write(f"height={cfg.height}\n")
		if cfg.type == 'Text + Image Prompt':
			h.write(f"image={cfg.input_image}\n")
			h.write(f"strength = {cfg.noise_strength}\n")
		h.write(f"num_inference_steps = {cfg.num_inference_steps}\n")
		h.write(f"guidance_scale = {cfg.guidance_scale}\n")
		h.write(f"Is NSFW? = {is_nsfw}\n")
		h.write(f"Time taken = {tm}s\n")
		h.write(f'Seed = {cfg.seed}\n')
		h.close()
		# Console output
		print(f"Time taken: {tm}s")
	# Done with copy loop
	print(f"Generated {g_num_copies.get()} images")
	# Show first image result and update UI
	m_generate['state'] = NORMAL
	toggle_image(True)
	show_image()
	# Reset button states
	m_prev['state'] = DISABLED
	if len(g_files) == 1:
		m_next['state'] = DISABLED
	elif len(g_files) >=2:
		m_next['state'] = NORMAL

# GUI root
root = Tk()
root.title("Stable Diffusion")
wd = 930
ht = 860
x = int((root.winfo_screenwidth() - wd) / 2)
y = int((root.winfo_screenheight() - ht) / 2)
root.geometry(f'{wd}x{ht}+{x}+{y}')
Grid.columnconfigure(root, 1, weight=1)

# Config variables
g_lbl_font = font.Font(root, weight=font.BOLD)
cfg = Config()
g_type = StringVar(root, cfg.type)
g_scheduler = StringVar(root, cfg.scheduler)
g_prompt = StringVar(root, cfg.prompts[0])
g_files = []
g_seeds = []
g_nsfw = []
g_count = StringVar(root, 'Number of images: 0')
g_file_pointer = -1
g_init_image = StringVar(root, '')
g_width = IntVar(root, cfg.width)
g_height = IntVar(root, cfg.height)
g_strength = DoubleVar(root, cfg.noise_strength)
g_num_inference_steps = IntVar(root, cfg.num_inference_steps)
g_guidance_scale = DoubleVar(root, cfg.guidance_scale)
g_num_copies = IntVar(root, cfg.num_copies)
g_seed = IntVar(root, cfg.seed)
g_img_seed = StringVar(root, -1)
generator = torch.Generator(device='cpu')

# Type label
Label(root, text='Type', font=g_lbl_font).grid(row=0, column=0, padx=(16, 8), pady=(16, 2), sticky=W)
# Type combobox
m_type = ttk.Combobox(root, state="readonly", textvariable=g_type, values=['Text Prompt', 'Text + Image Prompt'])
m_type.grid(row=1, column=0, padx=(16, 8), pady=(2, 4), sticky=W)
m_type.bind('<<ComboboxSelected>>', type_changed)
# Prompt label
Label(root, text='Prompt', font=g_lbl_font).grid(row=2, column=0, padx=(16, 8), pady=(4, 2), sticky=W)
# Prompt text field
m_prompt = Text(root, width=125, height=4, wrap=WORD)
m_prompt.grid(row=3, column=0, columnspan=2, padx=16, pady=(2, 4), sticky=EW)
m_prompt.insert('1.0', cfg.prompt)
# Previous prompts picker
m_prompts = ttk.Combobox(root, state="readonly", textvariable=g_prompt, values=cfg.prompts)
m_prompts.grid(row=4, column=0, columnspan=2, padx=(16, 16), pady=(2, 4), sticky=EW)
m_prompts.bind('<<ComboboxSelected>>', prompts_changed)
# Left frame
m_left = Frame(root)
m_left.grid(row=5, column=0, sticky=N)
# Right frame
m_right = Frame(root)
m_right.grid(row=5, column=1, sticky=NSEW)
# Left - Input image label
m_lbl_input = Label(m_left, text='Input Image', font=g_lbl_font)
m_lbl_input.grid(row=0, column=0, padx=(16, 8), pady=(4, 2), sticky=W)
m_lbl_input.grid_forget()
# Input image entry
m_txt_input = Entry(m_left, textvariable=g_init_image, width=30, state=DISABLED)
m_txt_input.grid(row=1, column=0, padx=(16, 4), pady=(2, 4), sticky=W)
m_txt_input.grid_forget()
# Input image button - to show open dialog
m_btn_input = Button(m_left, text='...', command=pick_image)
m_btn_input.grid(row=1, column=1, padx=(4, 8), pady=(2, 4), sticky=W)
m_btn_input.grid_forget()
# Scheduler label
Label(m_left, text='Scheduler', font=g_lbl_font).grid(row=2, column=0, columnspan=2, padx=(16, 8), pady=(4, 2),
	sticky=W)
# Scheduler combo
m_sched = ttk.Combobox(m_left, state="readonly", textvariable=g_scheduler, values=['Default', 'LMS', 'PNDM', 'DDIM'])
m_sched.grid(row=3, column=0, columnspan=2, padx=(16, 8), pady=(2, 4), sticky=W)
# Width and height section
m_size = Frame(m_left)
m_size.grid(row=4, column=0, sticky=W)
# Title
Label(m_size, text='Image Size', font=g_lbl_font).grid(row=0, column=0, columnspan=2, padx=(16, 8), pady=(4, 2),
	sticky=W)
# Explanation
Label(m_size, text='Should be a multiple of 8. Preferably one size should be 512').grid(row=1, column=0, columnspan=2, padx=(16, 8), pady=(4, 2),
	sticky=W)
# Width label
Label(m_size, text='Width', font=g_lbl_font).grid(row=2, column=0, padx=(16, 8), pady=(4, 2), sticky=W)
# Height label
Label(m_size, text='Height', font=g_lbl_font).grid(row=2, column=1, padx=(16, 8), pady=(4, 2), sticky=W)
# Width field
m_width = Entry(m_size, textvariable=g_width, width=10)
m_width.grid(row=3, column=0, padx=(16, 4), pady=(2, 4), sticky=W)
# Height field
m_height = Entry(m_size, textvariable=g_height, width=10)
m_height.grid(row=3, column=1, padx=(16, 4), pady=(2, 4), sticky=W)
# Noise strength label
m_lbl_strength = Label(m_left, text='Noise Strength', font=g_lbl_font)
m_lbl_strength.grid(row=5, column=0, columnspan=2, padx=(16, 8), pady=(4, 2), sticky=W)
m_lbl_strength.grid_forget()
# Noise strength slider
m_strength = Scale(m_left, orient=HORIZONTAL, from_=0.0, to=1.0, resolution=0.01, digits=3, variable=g_strength,
	length=350)
m_strength.grid(row=6, column=0, columnspan=2, padx=(16, 8), pady=(2, 4), sticky=W)
m_strength.grid_forget()
# Inference steps label
Label(m_left, text='Number of Inference Steps', font=g_lbl_font).grid(row=7, column=0, columnspan=2, padx=(16, 8),
	pady=(4, 2), sticky=W)
# Inference steps slider
m_num_steps = Scale(m_left, orient=HORIZONTAL, from_=1, to=300, variable=g_num_inference_steps, length=350)
m_num_steps.grid(row=8, column=0, columnspan=2, padx=(16, 8), pady=(2, 4), sticky=W)
# Guidance label
Label(m_left, text='Guidance', font=g_lbl_font).grid(row=9, column=0, columnspan=2, padx=(16, 8), pady=(4, 2), sticky=W)
# Guidance slider
m_guidance = Scale(m_left, orient=HORIZONTAL, from_=-15.0, to=30.0, resolution=0.1, digits=3, variable=g_guidance_scale,
	length=350)
m_guidance.grid(row=10, column=0, columnspan=2, padx=(16, 8), pady=(2, 4), sticky=W)
# Number of images label
Label(m_left, text='Number of Images', font=g_lbl_font).grid(row=11, column=0, columnspan=2, padx=(16, 8), pady=(4, 2),
	sticky=W)
# Number of images spinner
m_copies = Spinbox(m_left, from_=1, to=20, textvariable=g_num_copies)
m_copies.grid(row=12, column=0, columnspan=2, padx=(16, 8), pady=(2, 4), sticky=W)
# Seed label
Label(m_left, text='Seed', font=g_lbl_font).grid(row=13, column=0, columnspan=2, padx=(16, 8), pady=(4, 2), sticky=W)
# Seed entry
m_seed = Entry(m_left, textvariable=g_seed, width=30)
m_seed.grid(row=14, column=0, padx=(16, 4), pady=(2, 4), sticky=W)
# Right - Output image
m_image = Canvas(m_right, width=512, height=512, bg='lightgrey')
m_image.grid(row=0, column=0, padx=(8, 16), pady=(4, 4))
# Info frame
m_info = Frame(m_right)
m_info.grid(row=1, column=0)
# Seed label
Label(m_info, text='Seed').grid(row=0, column=0, padx=(0, 8), pady=(4, 2), sticky=W)
# Seed entry
m_img_seed = Entry(m_info, textvariable=g_img_seed, width=30)
m_img_seed.grid(row=0, column=1, padx=(0, 8), pady=(4, 2), sticky=W)
# NSFW label
Label(m_info, text='NSFW Image?').grid(row=0, column=2, padx=(8, 8), pady=(4, 2), sticky=W)
# NSFW checkbox
m_nsfw = Checkbutton(m_info, state=DISABLED)
m_nsfw.grid(row=0, column=3, padx=(0, 8), pady=(4, 2), sticky=W)
m_info.grid_forget()
# Image count label
m_count = Label(m_right, textvariable=g_count)
m_count.grid(row=2, column=0, padx=(8, 8), pady=(4, 2))
# Actions Frame
m_actions = Frame(m_right)
m_actions.grid(row=3, column=0, pady=(16, 0))
# Previous button
m_prev = Button(m_actions, text="Previous", command=previous_image)
m_prev.grid(row=0, column=0, padx=(0, 24))
# Delete button
m_del = Button(m_actions, text="Delete", command=delete_image)
m_del.grid(row=0, column=1, padx=(0, 24))
# Next button
m_next = Button(m_actions, text="Next", command=next_image)
m_next.grid(row=0, column=2, padx=(0, 24))
m_actions.grid_forget()
# Main - Separator
ttk.Separator(root, orient='horizontal').grid(row=6, column=0, columnspan=2, pady=8, sticky='EW')
# Generate button
m_generate = Button(root, text="Generate!", command=generate_images)
m_generate.grid(row=7, column=0, columnspan=2)
# Start GUI loop
root.mainloop()
