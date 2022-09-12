import json
from os.path import exists
from sd_engine import GeneratorType

class Config:
	type = GeneratorType.txt2img
	scheduler = 'Default'
	prompt = 'highly-detailed disc world with a single big mountain in the middle and water pouring down over its edges, the lights of one city with short buildings visible on the world, the world is sitting on the back of a giant turtle swimming through space which has four elephants on its back holding up the world, dark sky full of stars. Massive scale, Highly detailed, Artstation, Cinematic, Colorful'
	prompts = ['highly-detailed disc world with a single big mountain in the middle and water pouring down over its edges, the lights of one city with short buildings visible on the world, the world is sitting on the back of a giant turtle swimming through space which has four elephants on its back holding up the world, dark sky full of stars. Massive scale, Highly detailed, Artstation, Cinematic, Colorful']
	input_image = ''
	noise_strength = 0.6
	num_inference_steps = 75
	guidance_scale = 7.5
	num_copies = 1
	seed = -1
	width = 512
	height = 512
	# is_nsfw = False
	# time_taken = ''

	def __init__(self):
		# Load saved JSOn data
		if exists('config.json'):
			with open('config.json') as file:
				data = json.load(file)
				# print(f'Loaded config data: {data}')
				type = data['type']
				self.type = GeneratorType.txt2img if type == 'Text Prompt' else GeneratorType.img2img
				self.scheduler = data['scheduler']
				self.prompt = data['prompt']
				self.prompts = data['prompts']
				self.input_image = data['input_image']
				self.noise_strength = data['noise_strength']
				self.num_inference_steps = data['num_inference_steps']
				self.guidance_scale = data['guidance_scale']
				self.num_copies = data['num_copies']
				self.seed = data['seed']
				self.width = data['width']
				self.height = data['height']
				file.close()

	def add_prompt(self, prompt):
		if prompt in self.prompts:
			return
		# Only 20 prompts are saved in app
		if len(self.prompts) >= 20:
			self.prompts.pop()
		# The first item is never overwritten
		self.prompts.insert(1, prompt)

	def save(self):
		type = 'Text Prompt' if self.type == GeneratorType.txt2img else 'Text + Image'
		data = {'type': type, 'scheduler': self.scheduler, 'prompt': self.prompt, 'prompts': self.prompts,
				'input_image': self.input_image, 'noise_strength': self.noise_strength,
				'num_inference_steps': self.num_inference_steps, 'guidance_scale': self.guidance_scale,
				'num_copies': self.num_copies, 'seed': self.seed, 'width': self.width, 'height': self.height}
		str = json.dumps(data)
		with open('config.json', 'w') as file:
			file.write(str)
			file.close()

	def display(self):
		print(
			f'Type: {self.type}\n'
			f'Scheduler: {self.scheduler}\n'
			f'Prompt: {self.prompt}\n'
			f'Width: {self.width}\n'
			f'Height: {self.height}\n'
			f'Strength: {self.noise_strength}\n'
			f'Num Stpes: {self.num_inference_steps}\n'
			f'Guidance: {self.guidance_scale}\n'
			f'Copies: {self.num_copies}\n'
			f'Seed: {self.seed}')
