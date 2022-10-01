from tools.config import Config
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QTableView, QFrame, QHBoxLayout, QPushButton, QMessageBox

class PromptsTab(QWidget):
	def __init__(self, cfg: Config):
		super(PromptsTab, self).__init__()
		self.cfg = cfg
		self.sel_cat = -1
		# Set up DB
		self.db = QSqlDatabase.addDatabase('QSQLITE')
		path = 'data.db'
		self.db.setDatabaseName(path)
		# Main UI
		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(8, 0, 8, 0)
		main_splitter = QSplitter(Qt.Vertical)
		sub_splitter = QSplitter(Qt.Horizontal)
		# Prompts model
		self.m_prompts = QSqlTableModel()
		self.m_prompts.setTable('prompts')
		self.m_prompts.setEditStrategy(QSqlTableModel.OnFieldChange)
		self.m_prompts.select()
		self.m_prompts.setHeaderData(1, Qt.Horizontal, "Prompt")
		# Prompts view
		self.v_prompts = QTableView()
		self.v_prompts.setModel(self.m_prompts)
		self.v_prompts.sortByColumn(0, Qt.DescendingOrder)
		self.v_prompts.hideColumn(0)
		self.v_prompts.hideColumn(2)
		self.v_prompts.resizeColumnToContents(1)
		# Prompts layout
		prompts_frame = QFrame()
		main_splitter.addWidget(prompts_frame)
		main_splitter.addWidget(sub_splitter)
		prompts_layout = QVBoxLayout(prompts_frame)
		prompts_layout.addWidget(self.v_prompts)
		# Prompts Actions
		p_action_layout = QHBoxLayout()
		prompts_layout.addLayout(p_action_layout)
		# Add prompt
		b_add_prompt = QPushButton('Add a Prompt')
		b_add_prompt.clicked.connect(self.add_prompt)
		p_action_layout.addWidget(b_add_prompt)
		# Delete prompt
		b_del_prompt = QPushButton('Delete Current Prompt')
		b_del_prompt.clicked.connect(self.delete_prompt)
		p_action_layout.addWidget(b_del_prompt)
		# Categories model
		self.m_cat = QSqlTableModel()
		self.m_cat.setTable('categories')
		self.m_cat.setEditStrategy(QSqlTableModel.OnFieldChange)
		self.m_cat.select()
		self.m_cat.setHeaderData(1, Qt.Horizontal, "Category")
		# Categories view
		self.v_cat = QTableView()
		self.v_cat.setModel(self.m_cat)
		self.v_cat.sortByColumn(1, Qt.AscendingOrder)
		self.v_cat.hideColumn(0)
		self.v_cat.resizeColumnToContents(1)
		self.v_cat.selectionModel().selectionChanged.connect(self.cat_selection_changed)
		# Categories layout
		cat_frame = QFrame()
		sub_splitter.addWidget(cat_frame)
		cat_layout = QVBoxLayout(cat_frame)
		cat_layout.addWidget(self.v_cat)
		# Categories Actions
		c_action_layout = QHBoxLayout()
		cat_layout.addLayout(c_action_layout)
		# Add category
		b_add_cat = QPushButton('Add a Category')
		b_add_cat.clicked.connect(self.add_cat)
		c_action_layout.addWidget(b_add_cat)
		# Delete category
		b_del_cat = QPushButton('Delete Current Category')
		b_del_cat.clicked.connect(self.delete_cat)
		c_action_layout.addWidget(b_del_cat)
		# Modifiers model
		self.m_mod = QSqlTableModel()
		self.m_mod.setTable('modifiers')
		self.m_mod.setEditStrategy(QSqlTableModel.OnFieldChange)
		self.m_mod.select()
		self.m_mod.setHeaderData(2, Qt.Horizontal, "Modifier")
		# Modifiers view
		self.v_mod = QTableView()
		self.v_mod.setModel(self.m_mod)
		self.v_mod.sortByColumn(2, Qt.AscendingOrder)
		self.v_mod.hideColumn(0)
		self.v_mod.hideColumn(1)
		self.v_mod.resizeColumnToContents(2)
		# Modifiers layout
		mod_frame = QFrame()
		sub_splitter.addWidget(mod_frame)
		mod_layout = QVBoxLayout(mod_frame)
		mod_layout.addWidget(self.v_mod)
		# Modifiers Actions
		m_action_layout = QHBoxLayout()
		mod_layout.addLayout(m_action_layout)
		# Add modifier
		b_add_mod = QPushButton('Add a Modifier')
		b_add_mod.clicked.connect(self.add_mod)
		m_action_layout.addWidget(b_add_mod)
		# Delete modifier
		b_del_mod = QPushButton('Delete Current Modifier')
		b_del_mod.clicked.connect(self.delete_mod)
		m_action_layout.addWidget(b_del_mod)
		# Finalize layout
		main_layout.addWidget(main_splitter)
		# Set up mods view
		row = self.v_cat.currentIndex().row()
		self.filter_mods(row)

	def add_prompt(self):
		success = self.m_prompts.insertRows(self.m_prompts.rowCount(), 1)
		if not success:
			print('Error inserting new Prompt row')

	def delete_prompt(self):
		row = self.v_prompts.currentIndex().row()
		pid = self.m_prompts.record(row).value('id')
		# Verify if used
		qry = QSqlQuery(f'SELECT COUNT(*) AS count FROM "prompts" p, batches b, images i WHERE p.id = b.prompt_id AND b.id = i.batch_id AND p.id = {pid}')
		qry.next()
		count = qry.value(0)
		# Warn/confirm
		if count > 0:
			ret = QMessageBox.question(self, 'Are you sure?', f'This prompt has images in the gallery. If you remove it, '
				f'the gallery will not be able to dsiplay prompt info for those images later. Do you want to proceed?',
				QMessageBox.Yes | QMessageBox.No)
			if ret == QMessageBox.No:
				return
		self.m_prompts.removeRow(row)
		self.v_prompts.hideRow(row)

	def cat_selection_changed(self, new, old):
		rnew = -1 if new.isEmpty() else new.indexes()[0].row()
		# rold = -1 if old.isEmpty() else old.indexes()[0].row()
		self.filter_mods(rnew)

	def add_cat(self):
		success = self.m_cat.insertRows(self.m_cat.rowCount(), 1)
		if not success:
			print('Error inserting new Category row')

	def delete_cat(self):
		row = self.v_cat.currentIndex().row()
		if row == -1:
			QMessageBox.warning(self, 'Error', 'You have not selected a category. Select a category first!', QMessageBox.Ok)
			return
		# Confirmation
		cid = self.m_cat.record(row).value('id')
		cat = self.m_cat.record(row).value('category')
		ret = QMessageBox.question(self, 'Are you sure?', f'This will delete the {cat} category and associated modifiers. '
			f'Do you want to proceed?', QMessageBox.Yes | QMessageBox.No)
		if ret == QMessageBox.No:
			return
		# Remove all modifiers
		qry = QSqlQuery(f'DELETE FROM modifiers WHERE category_id = {cid}')
		qry.exec()
		# Remove category
		self.m_cat.removeRow(row)
		self.v_cat.hideRow(row)

	def add_mod(self):
		if self.sel_cat == -1:
			QMessageBox.warning(self, 'Error', 'You have not selected a category. Select a category first!', QMessageBox.Ok)
			return
		row = self.m_mod.rowCount()
		success = self.m_mod.insertRows(row, 1)
		if not success:
			print('Error inserting new Modifier row')
			return
		self.m_mod.setData(self.m_mod.index(row, 1), self.sel_cat)
		self.m_mod.submit()

	def delete_mod(self):
		row = self.v_mod.currentIndex().row()
		if row == -1:
			QMessageBox.warning(self, 'Error', 'You have not selected a modifier. Select a modifier first!', QMessageBox.Ok)
			return
		# Confirmation
		mod = self.m_mod.record(row).value('modifier')
		ret = QMessageBox.question(self, 'Are you sure?', f'This will delete the {mod} modifier. '
			f'Do you want to proceed?', QMessageBox.Yes | QMessageBox.No)
		if ret == QMessageBox.No:
			return
		self.m_mod.removeRow(row)
		self.v_mod.hideRow(row)

	def filter_mods(self, row):
		if row < 0:
			self.sel_cat = -1
		else:
			self.sel_cat = self.m_cat.record(row).value('id')
		self.m_mod.setFilter(f'category_id = {self.sel_cat}')

