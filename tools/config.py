import json
import sqlite3
from data.category import Category
from data.modifier import Modifier
from data.prompt import Prompt
from os.path import exists
from tools.sd_engine import GeneratorType
from sqlite3 import Error

class Config:
	type = GeneratorType.txt2img
	scheduler = 'Default'
	prompt = None
	prompts = []
	input_image = ''
	noise_strength = 0.6
	num_inference_steps = 75
	guidance_scale = 7.5
	num_copies = 1
	seed = -1
	width = 512
	height = 512
	modifiers = {}
	server = 'local'
	server_address = 'http://127.0.0.1:5000'
	# is_nsfw = False
	# time_taken = ''

	def __init__(self):
		# Run DB set up
		try:
			self.db = sqlite3.connect('data.db')
			self.db_migrate()
		except Error as e:
			print(f'Error opening DB - Code: {e.sqlite_errorcode}, Name: {e.sqlite_errorname}')
		# Load saved config data
		if exists('config.json'):
			with open('config.json') as file:
				data = json.load(file)
				# print(f'Loaded config data: {data}')
				type = data['type']
				self.type = GeneratorType.txt2img if type == 'Text Prompt' else GeneratorType.img2img
				# Migration handling - do we have saved prompts?
				if 'prompts' in data:
					prompts = data['prompts']
					p = Prompt(self.db)
					if p.count() == 0:
						self.add_prompts(prompts)
				# Current prompt
				pd = data['prompt']
				p = Prompt(self.db)
				if isinstance(pd, int):
					# Find by ID
					pf = p.by_id(pd)
					if pf is not None:
						self.prompt = pf
				else:
					# Find by prompt
					pf = p.by_prompt(pd)
					if pf is not None:
						self.prompt = pf
				# Load rest of the data
				self.scheduler = data['scheduler']
				self.input_image = data['input_image']
				self.noise_strength = data['noise_strength']
				self.num_inference_steps = data['num_inference_steps']
				self.guidance_scale = data['guidance_scale']
				self.num_copies = data['num_copies']
				self.seed = data['seed']
				self.width = data['width']
				self.height = data['height']
				self.server = data['server']
				self.server_address = data['server_address']
				file.close()
		# Load modifiers
		c = Category(self.db)
		cats = c.list()
		for cat in cats:
			m = Modifier(self.db)
			mods = m.list_by_cat(cat)
			self.modifiers[cat] = mods

	def __del__(self):
		# Close DB
		self.db.close()

	def string_prompts(self):
		return list(map(lambda p: p.prompt, self.prompts))

	def add_prompt(self, prompt):
		# Does this prompt exist
		p = Prompt(self.db)
		np = p.by_prompt(prompt)
		if np is not None:
			self.prompt = np
			return
		# Save new prompt
		p = Prompt(self.db)
		p.prompt = prompt
		p.save()
		# Update new prompt
		self.prompt = p
		self.prompts.insert(0, p)
		return p

	def save(self):
		type = 'Text Prompt' if self.type == GeneratorType.txt2img else 'Text + Image'
		p = self.prompt.id
		data = {'type': type, 'scheduler': self.scheduler, 'prompt': p, 'input_image': self.input_image,
				'noise_strength': self.noise_strength, 'num_inference_steps': self.num_inference_steps,
				'guidance_scale': self.guidance_scale, 'num_copies': self.num_copies, 'seed': self.seed,
				'width': self.width, 'height': self.height, 'server': self.server, 'server_address': self.server_address}
		str = json.dumps(data)
		with open('config.json', 'w') as file:
			file.write(str)
			file.close()

	def display(self):
		print(
			f'Type: {self.type}\n'
			f'Scheduler: {self.scheduler}\n'
			f'Prompt: {self.prompt.prompt}\n'
			f'Width: {self.width}\n'
			f'Height: {self.height}\n'
			f'Strength: {self.noise_strength}\n'
			f'Num Stpes: {self.num_inference_steps}\n'
			f'Guidance: {self.guidance_scale}\n'
			f'Copies: {self.num_copies}\n'
			f'Seed: {self.seed}')

	def load_data(self):
		# Load prompts
		p = Prompt(self.db)
		self.prompts = p.all(limit=20)

	def save_generate_info(self, dtstr: str, is_nsfw: bool, tm: float, seed: int):
		# Convert information to dictionary
		dic = {'schduler': self.scheduler, 'prompt': self.prompt.prompt, 'width': self.width, 'height': self.height,
			'input_image': self.input_image, 'noise_strength': self.noise_strength, 'inference_steps': self.num_inference_steps,
			'guidance_scale': self.guidance_scale, 'is_nsfw': is_nsfw, 'time_taken': tm, 'seed': seed}
		# Convert dictionary to JSON string
		str = json.dumps(dic, indent = 4)
		# Save string
		with open(f'output/sample_{dtstr}.json', 'w') as h:
			h.write(str)
			h.close()

	def add_prompts(self, prompts):
		# First time migration - save current prompts
		for p in prompts:
			dp = Prompt(self.db)
			dp.prompt = p
			dp.save()
			self.prompts.append(dp)

	def db_migrate(self):
		db_ver = 1.0
		v, = self.db.execute("PRAGMA user_version").fetchone()
		# print(f'DB version: {v}')
		if v == db_ver:
			# No migration needed, just set up prompts from DB
			self.load_data()
			return
		elif v == 0:
			# Prompts table
			sql = f'CREATE TABLE IF NOT EXISTS "prompts" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,' \
				  f' "prompt" TEXT NOT NULL UNIQUE, "img_count" INTEGER NOT NULL DEFAULT 0);'
			self.db.execute(sql)
			# Batches table
			sql = f'CREATE TABLE IF NOT EXISTS "batches" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, ' \
				  f'"prompt_id" INTEGER NOT NULL, "scheduler" TEXT NOT NULL, "width" INTEGER NOT NULL, "height" INTEGER NOT NULL, ' \
				  f'"inference_steps" INTEGER NOT NULL, "guidance_scale" REAL NOT NULL, "num_copies" INTEGER NOT NULL, ' \
				  f'"time_taken" REAL NOT NULL DEFAULT 0.0, "seed" INTEGER NOT NULL DEFAULT -1, "noise_strength" REAL NOT NULL DEFAULT 0.0,' \
				  f'"input_image" TEXT);'
			self.db.execute(sql)
			# Images table
			sql = f'CREATE TABLE IF NOT EXISTS "images" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "batch_id" INTEGER NOT NULL,' \
				  f'"path" TEXT NOT NULL, "nsfw" BOOLEAN NOT NULL DEFAULT FALSE, "time_taken" REAL NOT NULL, ' \
				  f'"seed" INTEGER NOT NULL DEFAULT -1, "created" DATE NOT NULL);'
			self.db.execute(sql)
			# Categories table
			sql = f'CREATE TABLE IF NOT EXISTS "categories" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "category" ' \
				  f'TEXT NOT NULL UNIQUE)'
			self.db.execute(sql)
			# Modifiers table
			sql = f'CREATE TABLE IF NOT EXISTS "modifiers" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, ' \
				  f'"category_id" INTEGER NOT NULL,  "modifier" TEXT NOT NULL UNIQUE)'
			self.db.execute(sql)
		elif v == 1:
			self.db.execute("DROP TABLE IF EXISTS MyObsoleteTable")
		else:
			raise RuntimeError(
				f"Database is at version {v}. This is an unsupported version. Bailing out to avoid data loss.")
			return
		# If we got here and the version is not initial, load data
		if v != 0:
			self.load_data()
		# Update DB version
		print(f'DB Updated to version: {db_ver}')
		self.db.execute(f'PRAGMA user_version={db_ver}')
