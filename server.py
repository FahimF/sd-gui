import numpy as np
import requests
from flask import Flask, jsonify, request
from PIL import Image
from tools.sd_engine import SDEngine, GeneratorType

class SDServer:
	def __init__(self, server_address, scheduler, steps):
		self.addr = server_address
		self.scheduler = scheduler
		self.steps = steps
		if self.addr[-1] != '/':
			self.addr += '/'

	def generate(self, prompt: str, width, height, seed, guidance, image: Image = None, strength=0):
		request_data = {
			'scheduler': self.scheduler,
			'prompt': prompt,
			'width': width,
			'height': height,
			'seed': seed,
			'guidance': guidance,
			'steps': self.steps,
			'strength': strength,
		}
		if image is not None:
			request_data['image'] = image
		url = self.addr + 'generate'
		resp = requests.post(url, json=request_data)
		resp_data = resp.json()
		seed = resp_data['seed']
		is_nsfw = resp_data['is_nsfw']
		arr = np.array(resp_data['image'])
		image = Image.fromarray(np.uint8(arr))
		return image, is_nsfw, seed

	def inpaint(self, prompt, image, mask, width, height, seed, guidance, strength):
		request_data = {
			'scheduler': self.scheduler,
			'prompt': prompt,
			'image': np.array(image).tolist(),
			'mask': np.array(mask).tolist(),
			'width': width,
			'height': height,
			'seed': seed,
			'guidance': guidance,
			'strength': strength,
			'steps': self.steps,
		}
		url = self.addr + 'inpaint'
		resp = requests.post(url, json=request_data)
		resp_data = resp.json()
		seed = resp_data['seed']
		arr = np.array(resp_data['image'])
		image = Image.fromarray(np.uint8(arr))
		return image, seed

def run_app():
	app = Flask(__name__)

	@app.route('/')
	def home():
		return 'Home'

	@app.route('/generate', methods=['POST'])
	def generate():
		# get request data
		data = request.get_json()
		scheduler = data['scheduler']
		prompt = data['prompt']
		width = data['width']
		height = data['height']
		seed = data['seed']
		guidance = data['guidance']
		steps = data['steps']
		strength = data['strength']
		image = None
		type = GeneratorType.txt2img
		if 'image' in data:
			arr = np.array(data['image'])
			image = Image.fromarray(np.uint8(arr))
			type = GeneratorType.img2img
			image.save('input.png')
			print('Saved image')
		# Create SD instance
		sd = SDEngine(type, scheduler, steps)
		# Generate image
		img, is_nsfw, seed = sd.generate(prompt, width, height, seed, guidance, image, strength)
		return jsonify({
			'status': 'success',
			'is_nsfw': is_nsfw,
			'image': np.array(img).tolist(),
			'seed': seed
		})

	@app.route('/inpaint', methods=['POST'])
	def inpaint():
		# get request data
		data = request.get_json()
		scheduler = data['scheduler']
		prompt = data['prompt']
		iarr = np.array(data['image'])
		image = Image.fromarray(np.uint8(iarr))
		marr = np.array(data['mask'])
		mask = Image.fromarray(np.uint8(marr))
		width = data['width']
		height = data['height']
		seed = data['seed']
		guidance = data['guidance']
		strength = data['strength']
		steps = data['steps']
		# Create SD instance
		sd = SDEngine(type, scheduler, steps)
		# Generate image
		img, seed = sd.inpaint(prompt, image, mask, width, height, seed, guidance, strength)
		return jsonify({
			'status': 'success',
			'image': np.array(img).to_list(),
			'seed': seed
		})

	app.run(host= '0.0.0.0')

if __name__ == '__main__':
	run_app()