from sqlite3 import Connection
from sqlite3 import Error

class Batch:
	id = -1
	prompt_id = -1
	scheduler = ''
	width = 0
	height = 0
	inference_steps = 0
	guidance_scale = 0.0
	num_copies = 0
	time_taken = 0.0
	seed = -1
	noise_strength = 0.0
	input_image = ''

	def __init__(self, db: Connection):
		self.db = db

	def save(self):
		try:
			is_insert = False
			if self.id == -1:
				is_insert = True
				sql = f'INSERT INTO "batches" (prompt_id, scheduler, width, height, inference_steps, guidance_scale, num_copies, ' \
					  f'time_taken, seed, noise_strength, input_image) VALUES ({self.prompt_id}, "{self.scheduler}", {self.width}, ' \
					  f'{self.height}, {self.inference_steps}, {self.guidance_scale}, {self.num_copies}, {self.time_taken}, {self.seed}, ' \
					  f'{self.noise_strength}, "{self.input_image}")'
			else:
				sql = f'UPDATE "batches" SET "prompt_id" = {self.prompt_id}, scheduler = "{self.scheduler}", width = {self.width}, ' \
					  f'height = {self.height}, inference_steps = {self.inference_steps}, guidance_scale = {self.guidance_scale}, ' \
					  f'num_copies = {self.num_copies}, time_taken = {self.time_taken}, seed = {self.seed}, ' \
					  f'noise_strength = {self.noise_strength}, input_image = "{self.input_image}" WHERE "id" = {self.id}'
			print(f'Batch SQL: {sql}')
			cur = self.db.execute(sql)
			self.db.commit()
			if is_insert and cur.lastrowid is not None:
				self.id = cur.lastrowid
		except Error as error:
			print(f"Failed to update batches sqlite table: {error}")
