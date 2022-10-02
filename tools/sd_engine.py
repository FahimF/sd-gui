import torch
from diffusers import StableDiffusionPipeline, StableDiffusionInpaintPipeline, StableDiffusionImg2ImgPipeline
from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from diffusers.schedulers import LMSDiscreteScheduler, DDPMScheduler, DDIMScheduler, PNDMScheduler
from enum import Enum
from PIL import Image

class GeneratorType(Enum):
	txt2img = 1
	img2img = 2

class SchedulerType(Enum):
	DEFAULT = 1
	LMS = 2
	PNDM = 3
	DDIM = 4

class NSFWChecker(StableDiffusionSafetyChecker):
	@torch.no_grad()
	def forward(self, clip_input, images):
		return images, [False] * len(images)

class SDEngine:
	def __init__(self, type, scheduler, steps):
		self.type = type
		self.scheduler = scheduler
		self.steps = steps
		self.checker = NSFWChecker.from_pretrained("safety_checker")
		self.generator = torch.Generator(device='cpu')
		# Device definition
		self.device = torch.device(
			"cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
		# Set up scheduler based on selection
		sched = None
		if self.scheduler == 'LMS':
			# beta_schedule can be linear or scaled_linear
			sched = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear")
		elif self.scheduler == 'PNDM':
			# beta_schedule can be linear, scaled_linear, or squaredcos_cap_v2
			sched = PNDMScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="linear")
		elif self.scheduler == 'DDIM':
			# beta_schedule can be linear, scaled_linear, or squaredcos_cap_v2
			sched = DDIMScheduler(beta_start=0.0009, beta_end=0.0120, beta_schedule="scaled_linear", clip_sample=False)
		# elif cfg.scheduler == 'DDPM':
		# 	# beta_schedule can be linear, scaled_linear, or squaredcos_cap_v2
		# 	sched = DDPMScheduler(num_train_timesteps=10, beta_start=0.0001, beta_end=0.02, beta_schedule="linear", clip_sample=False)
		# Set scheduler values
		if sched is not None:
			sched.num_inference_steps = self.steps
		# Set up pipeline based on type
		if self.type == GeneratorType.txt2img:
			if sched is None:
				self.pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-4").to(self.device)
			else:
				self.pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-4", scheduler=sched).to(
					self.device)
		else:
			if sched is None:
				self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained("stable-diffusion-v1-4").to(self.device)
			else:
				self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained("stable-diffusion-v1-4", scheduler=sched).to(
					self.device)
		# Disable NSFW checks - stops giving you black images
		self.pipe.safety_checker = lambda images, **kwargs: (images, False)

	def generate(self, prompt: str, width, height, seed, guidance, image:Image=None, strength=0):
		# Load and prepare image if type is img2img
		if self.type == GeneratorType.img2img:
			wd, ht = image.size
			if wd != width or ht != height:
				image = image.resize((width, height))
		# Get a new random seed, store it and use it as the generator state
		if seed == -1:
			seed = self.generator.seed()
		else:
			seed = seed
		print(f'Seed for new image: {seed}')
		# Update generator with seed
		generator = self.generator.manual_seed(seed)
		latent = torch.randn((1, self.pipe.unet.in_channels, height // 8, width // 8),
			generator=generator, device='cpu').to(self.device)
		if self.type == GeneratorType.img2img:
			result = self.pipe(prompt=prompt, init_image=image, strength=strength, num_inference_steps=self.steps,
				guidance_scale=guidance, generator=generator)
		else:
			result = self.pipe(prompt=prompt, num_inference_steps=self.steps, width=width, height=height,
				guidance_scale=guidance, latents=latent)
		img = result["sample"][0]
		is_nsfw = result["nsfw_content_detected"]
		return img, is_nsfw, seed

	def inpaint(self, prompt, image, mask, width, height, seed, guidance, strength):
		pipe = StableDiffusionInpaintPipeline.from_pretrained('stable-diffusion-v1-4').to(self.device)
		# Disable NSFW checks - stops giving you black images
		pipe.safety_checker = self.checker
		# Prepare image
		wd, ht = image.size
		if wd != width or ht != height:
			image = image.resize((width, height))
		# Prepare mask
		wd, ht = mask.size
		if wd != width or ht != height:
			mask = mask.resize((width, height))
		# Get a new random seed, store it and use it as the generator state
		if seed == -1:
			seed = self.generator.seed()
		else:
			seed = seed
		print(f'Seed for new image: {seed}')
		# Update generator with seed
		generator = self.generator.manual_seed(seed)
		# Generate image using inpaint pipeline
		result = pipe(prompt=prompt, init_image=image, mask_image=mask, strength=strength, num_inference_steps=self.steps,
			guidance_scale=guidance, generator=generator).images
		img = result[0]
		return img, seed