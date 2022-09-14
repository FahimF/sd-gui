from sqlite3 import Connection
from sqlite3 import Error

class Image:
	id = -1
	batch_id = -1
	path = ''
	nsfw = False
	time_taken = 0.0
	seed = -1

	def __init__(self, db: Connection):
		self.db = db

	def save(self):
		try:
			is_insert = False
			if self.id == -1:
				sql = f'INSERT INTO "images" (batch_id, path, nsfw, time_taken, seed) VALUES ({self.batch_id}, "{self.path}", {self.nsfw}' \
					f'{self.time_taken}, {self.seed});'
				is_insert = True
			else:
				sql = f'UPDATE "images" SET batch_id = {self.batch_id}, path = "{self.path}", nsfw = {self.nsfw}, ' \
					  f'time_taken = {self.time_taken}, seed = {self.seed} WHERE "id" = {self.id};'
			cur = self.db.execute(sql)
			self.db.commit()
			if is_insert and cur.lastrowid is not None:
				self.id = cur.lastrowid
		except Error as error:
			print(f"Failed to update images sqlite table: {error}")

