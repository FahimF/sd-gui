import json
from os.path import exists

class Config:
	type = 'Text Prompt'
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
				self.type = data['type']
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
		data = {'type': self.type, 'scheduler': self.scheduler, 'prompt': self.prompt, 'prompts': self.prompts,
				'input_image': self.input_image, 'noise_strength': self.noise_strength,
				'num_inference_steps': self.num_inference_steps, 'guidance_scale': self.guidance_scale,
				'num_copies': self.num_copies, 'seed': self.seed, 'width': self.width, 'height': self.height}
		str = json.dumps(data)
		with open('config.json', 'w') as file:
			file.write(str)
			file.close()
