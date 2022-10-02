from sqlite3 import Connection
from sqlite3 import Error
from typing import List

class Prompt:
	id = -1
	prompt = ''

	def __init__(self, db: Connection):
		self.db = db

	def save(self):
		try:
			is_insert = False
			if self.id == -1:
				sql = f'INSERT INTO "prompts" ("prompt") VALUES ("{self.prompt}");'
				is_insert = True
			else:
				sql = f'UPDATE "prompts" SET "prompt" = "{self.prompt}" WHERE "id" = {self.id};'
			# print(f'Prompt SQL: {sql}')
			cur = self.db.execute(sql)
			self.db.commit()
			if is_insert and cur.lastrowid is not None:
				self.id = cur.lastrowid
		except Error as error:
			print(f"Failed to update prompts sqlite table: {error}")

	def count(self):
		count = 0
		try:
			sql = f'SELECT COUNT(*) FROM "prompts"'
			cur = self.db.execute(sql)
			row = cur.fetchone()
			return row[0]
		except Error as error:
			print(f"Failed to query prompts sqlite table: {error}")
			return 0

	def all(self, limit = 0) -> List:
		data = []
		try:
			sql = f'SELECT * FROM "prompts" ORDER BY id DESC'
			if limit != 0:
				sql += f' LIMIT {limit}'
			cur = self.db.execute(sql)
			rows = cur.fetchall()
			for row in rows:
				p = Prompt(self.db)
				p.load(row)
				data.append(p)
			return data
		except Error as error:
			print(f"Failed to query prompts sqlite table: {error}")
			return data

	def by_id(self, id):
		try:
			sql = f'SELECT * FROM "prompts" WHERE id = {id}'
			cur = self.db.execute(sql)
			row = cur.fetchone()
			if row is None:
				return None
			p = Prompt(self.db)
			p.load(row)
			return p
		except Error as error:
			print(f"Failed to query prompts sqlite table: {error}")
			return None

	def by_prompt(self, prompt):
		try:
			sql = f'SELECT * FROM "prompts" WHERE prompt ="{prompt}"'
			cur = self.db.execute(sql)
			row = cur.fetchone()
			if row is None:
				return None
			p = Prompt(self.db)
			p.load(row)
			return p
		except Error as error:
			print(f"Failed to query prompts sqlite table: {error}")
			return None

	def load(self, list):
		self.id = list[0]
		self.prompt = list[1]
