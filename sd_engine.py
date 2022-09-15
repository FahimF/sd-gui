import torch
from enum import Enum
from PIL import Image
from diffusers import StableDiffusionPipeline
from diffusers.pipelines import StableDiffusionImg2ImgPipeline
from diffusers.schedulers import LMSDiscreteScheduler, DDPMScheduler, DDIMScheduler, PNDMScheduler

class GeneratorType(Enum):
	txt2img = 1
	img2img = 2

class SchedulerType(Enum):
	DEFAULT = 1
	LMS = 2
	PNDM = 3
	DDIM = 4

class SDEngine:
	def __init__(self, cfg, type):
		self.cfg = cfg
		self.type = type
		self.generator = torch.Generator(device='cpu')
		# Device definition
		self.device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
		# Set up scheduler based on selection
		sched = None
		if self.cfg.scheduler == 'LMS':
			# beta_schedule can be linear or scaled_linear
			sched = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear")
		elif self.cfg.scheduler == 'PNDM':
			# beta_schedule can be linear, scaled_linear, or squaredcos_cap_v2
			sched = PNDMScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="linear")
		elif self.cfg.scheduler == 'DDIM':
			# beta_schedule can be linear, scaled_linear, or squaredcos_cap_v2
			sched = DDIMScheduler(beta_start=0.0009, beta_end=0.0120, beta_schedule="scaled_linear", clip_sample=False)
		# elif cfg.scheduler == 'DDPM':
		# 	# beta_schedule can be linear, scaled_linear, or squaredcos_cap_v2
		# 	sched = DDPMScheduler(num_train_timesteps=10, beta_start=0.0001, beta_end=0.02, beta_schedule="linear", clip_sample=False)
		# Set scheduler values
		if sched is not None:
			sched.num_inference_steps = self.cfg.num_inference_steps
		# Set up pipeline based on type
		if self.type == GeneratorType.txt2img:
			if sched is None:
				self.pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-4").to(self.device)
			else:
				self.pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-4", scheduler=sched).to(self.device)
		else:
			if sched is None:
				self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained("stable-diffusion-v1-4").to(self.device)
			else:
				self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained("stable-diffusion-v1-4", scheduler=sched).to(
					self.device)
		# Disable NSFW checks - stops giving you black images
		self.pipe.safety_checker = lambda images, **kwargs: (images, False)
		# Load and prepare image if type is img2img
		if self.type == GeneratorType.img2img:
			image = Image.open(self.cfg.input_image).convert("RGB")
			wd, ht = image.size
			if wd != self.cfg.width or ht != self.cfg.height:
				self.input_image = image.resize((self.cfg.width, self.cfg.height))

	def generate(self):
		# Get a new random seed, store it and use it as the generator state
		if self.cfg.seed == -1:
			seed = self.generator.seed()
		else:
			seed = self.cfg.seed
		print(f'Seed for new image: {seed}')
		# Update generator with seed
		generator = self.generator.manual_seed(seed)
		latent = torch.randn((1, self.pipe.unet.in_channels, self.cfg.height // 8, self.cfg.width // 8),
			generator=generator, device='cpu').to(self.device)
		if self.type == GeneratorType.img2img:
			result = self.pipe(prompt=self.cfg.prompt.prompt, init_image=self.input_image, strength=self.cfg.noise_strength,
				num_inference_steps=self.cfg.num_inference_steps, guidance_scale=self.cfg.guidance_scale,
				generator=generator)
		else:
			result = self.pipe(prompt=self.cfg.prompt.prompt, num_inference_steps=self.cfg.num_inference_steps, width=self.cfg.width, height=self.cfg.height,
				guidance_scale=self.cfg.guidance_scale, latents=latent)
		image = result["sample"][0]
		is_nsfw = result["nsfw_content_detected"]
		return image, is_nsfw, seed