from datetime import datetime
from sqlite3 import Connection
from sqlite3 import Error

class Image:
	id = -1
	batch_id = -1
	path = ''
	nsfw = False
	time_taken = 0.0
	seed = -1
	created = datetime.now()

	def __init__(self, db: Connection):
		self.db = db

	def save(self):
		try:
			is_insert = False
			if self.id == -1:
				dt = self.created.strftime('%Y-%m-%d %H:%M:%S')
				sql = f'INSERT INTO "images" (batch_id, path, nsfw, time_taken, seed, created) VALUES ({self.batch_id}, "{self.path}", {self.nsfw},' \
					f'{self.time_taken}, {self.seed}, "{dt}");'
				is_insert = True
			else:
				sql = f'UPDATE "images" SET batch_id = {self.batch_id}, path = "{self.path}", nsfw = {self.nsfw}, ' \
					  f'time_taken = {self.time_taken}, seed = {self.seed} WHERE "id" = {self.id};'
			# print(f'Image SQL: {sql}')
			cur = self.db.execute(sql)
			self.db.commit()
			if is_insert and cur.lastrowid is not None:
				self.id = cur.lastrowid
		except Error as error:
			print(f"Failed to update images sqlite table: {error}")

	def prompt_by_path(self, path: str):
		try:
			sql = f'SELECT p.prompt, i.created FROM "images" i, batches b, prompts p WHERE batch_id = b.id AND b.prompt_id = p.id AND ' \
				  f'path = "output/{path}"'
			# print(f'SQL: {sql}')
			cur = self.db.execute(sql)
			row = cur.fetchone()
			if row is None:
				return None
			return row
		except Error as error:
			print(f"Failed to query images sqlite table: {error}")
			return None

	def delete(self, path: str) -> bool:
		try:
			sql = f'SELECT id, batch_id FROM "images" WHERE path = "{path}"'
			# print(f'Image fetch SQL: {sql}')
			cur = self.db.execute(sql)
			row = cur.fetchone()
			if row is None:
				return False
			iid = row[0]
			bid = row[1]
			# Delete image
			sql = f'DELETE FROM "images" WHERE id = {iid}'
			# print(f'Image delete SQL: {sql}')
			self.db.execute(sql)
			# Are there other images in the batch?
			sql = f'SELECT COUNT(*) FROM images WHERE batch_id = {bid}'
			# print(f'Image batch count SQL: {sql}')
			cur = self.db.execute(sql)
			row = cur.fetchone()
			print(f'Images in batch: {row[0]}')
			if row[0] == 0:
				# If no other images in batch, remove batch
				sql = f'DELETE FROM "batches" WHERE id = {bid}'
				# print(f'Image batch delete SQL: {sql}')
				self.db.execute(sql)
			self.db.commit()
		except Error as error:
			print(f"Failed to query images sqlite table: {error}")
			return False
