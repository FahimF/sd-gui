from sqlite3 import Connection
from sqlite3 import Error
from typing import List

class Modifier:
	id = -1
	category_id = -1
	modifier = ''

	def __init__(self, db: Connection):
		self.db = db

	def list(self, cat_id: int, strList: bool = True) -> List:
		data = []
		try:
			sql = f'SELECT * FROM "modifiers" WHERE category_id = {cat_id} ORDER BY modifier'
			cur = self.db.execute(sql)
			rows = cur.fetchall()
			for row in rows:
				if strList:
					data.append(row[2])
				else:
					m = Modifier(self.db)
					m.load(row)
					data.append(m)
			return data
		except Error as error:
			print(f"Failed to query modifiers sqlite table: {error}")
			return data

	def list_by_cat(self, cat: str, strList: bool = True) -> List:
		data = []
		try:
			sql = f'SELECT * FROM "modifiers" WHERE category_id IN (SELECT id FROM "categories" WHERE category = "{cat}") ' \
				  f'ORDER BY modifier'
			cur = self.db.execute(sql)
			rows = cur.fetchall()
			for row in rows:
				if strList:
					data.append(row[2])
				else:
					m = Modifier(self.db)
					m.load(row)
					data.append(m)
			return data
		except Error as error:
			print(f"Failed to query modifiers sqlite table: {error}")
			return data

	def load(self, list):
		self.id = list[0]
		self.category_id = list[1]
		self.modifier = list[2]