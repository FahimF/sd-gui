from sqlite3 import Connection
from sqlite3 import Error
from typing import List

class Category:
	id = -1
	category = ''

	def __init__(self, db: Connection):
		self.db = db

	def list(self, strList: bool = True) -> List:
		data = []
		try:
			sql = f'SELECT * FROM "categories" ORDER BY category'
			cur = self.db.execute(sql)
			rows = cur.fetchall()
			for row in rows:
				if strList:
					data.append(row[1])
				else:
					c = Category(self.db)
					c.load(row)
					data.append(c)
			return data
		except Error as error:
			print(f"Failed to query categories sqlite table: {error}")
			return data

	def load(self, list):
		self.id = list[0]
		self.category = list[1]