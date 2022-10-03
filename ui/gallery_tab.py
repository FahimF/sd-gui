import data.image as DImg
import shutil
from datetime import datetime
from tools.config import Config
from PIL import Image
from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QPixmap, QPen
from PyQt5.QtWidgets import QStyledItemDelegate, QStyle, QFileSystemModel, QListView, QVBoxLayout, QHBoxLayout, \
	QPushButton, QMessageBox, QFileDialog
from ui.base_tab import BaseTab
from ui.image_viewer import ImageViewer

class ImageFileDelegate(QStyledItemDelegate):
	def __init__(self, db, width=256, height=256, padding=8):
		super().__init__()
		self.previews = {'None': None}
		self.width = width
		self.height = height
		self.padding = padding
		self.db = db
		self.ncols = 2

	def getPreview(self, itemName):
		if itemName not in self.previews:
			qpm = QPixmap("output/" + itemName)
			if qpm and not qpm.isNull():
				qpm = qpm.scaled(self.height, self.height, Qt.KeepAspectRatio)
			self.previews[itemName] = qpm
		return self.previews[itemName]

	def paint(self, painter, option, index):
		data = index.model().data(index, Qt.DisplayRole)
		if data is None:
			return
		# Show selected stte
		painter.save()
		if option.state & QStyle.State_Selected:
			painter.fillRect(option.rect, option.palette.highlight())
		# Draw content
		img = self.getPreview(data)
		width = self.width + self.padding * 2
		height = self.height + self.padding * 2
		# Position of image
		x = self.padding
		y = self.padding
		painter.drawPixmap(option.rect.x() + x, option.rect.y() + y, img)
		# Get image prompt
		i = DImg.Image(self.db)
		row = i.prompt_by_path(data)
		if row is None:
			prompt = 'Prompt: Unknown'
		else:
			dt = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
			str = dt.strftime('%d %b %Y %I:%M:%S %p')
			prompt = str + '\n\n' + row[0]
		# Rect for drawing
		x = option.rect.x() + self.padding * 2 + self.height
		y = option.rect.y() + self.padding
		wd = self.width - self.height - self.padding
		ht = self.height
		r = QRectF(x, y, wd, ht)
		# painter.drawText(r, Qt.AlignLeft and Qt.TextWordWrap and Qt.AlignVCenter, prompt)
		if option.state & QStyle.State_Selected:
			pen = QPen(Qt.white)
			painter.setPen(pen)
		painter.drawText(r, Qt.TextWordWrap, prompt)
		painter.restore()

	def sizeHint(self, option, index):
		wd = self.width + (self.padding * 2)
		ht = self.height + (self.padding * 2)
		return QSize(wd, ht)
	
class GalleryTab(BaseTab):
	def __init__(self, cfg: Config):
		super(GalleryTab, self).__init__(cfg)
		self.cfg = cfg
		# Configure
		self.cell_width = 330
		self.image_height = 220
		self.cell_padding = 8
		wd = self.cell_width + (self.cell_padding * 2)
		ht = self.image_height + (self.cell_padding * 2)
		self.gridSize = QSize(wd, ht)
		self.path = './output'
		self.files = QFileSystemModel()
		self.files.setNameFilters(['*.png', '*.jpg', '*.jpeg'])
		self.files.setNameFilterDisables(False)
		self.files.setRootPath(self.path)
		# Layout
		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(8, 0, 8, 0)
		# Gallery view
		self.gallery = QListView()
		self.gallery.setModel(self.files)
		self.gallery.setSelectionMode(QListView.MultiSelection)
		self.gallery.setRootIndex(self.files.index(self.path))
		self.gallery.setViewMode(QListView.IconMode)
		ifd = ImageFileDelegate(cfg.db, width=self.cell_width, height=self.image_height, padding=self.cell_padding)
		self.gallery.setItemDelegate(ifd)
		self.gallery.setGridSize(self.gridSize)
		self.gallery.setSpacing(8)
		self.gallery.doubleClicked.connect(self.show_item)
		self.gallery.setWordWrap(True)
		self.gallery.setResizeMode(QListView.Adjust)
		main_layout.addWidget(self.gallery)
		# Actions
		act_layout = QHBoxLayout()
		main_layout.addLayout(act_layout)
		act_layout.addStretch()
		# Delete
		b_del = QPushButton('Delete Selection')
		b_del.clicked.connect(self.delete_selection)
		act_layout.addWidget(b_del)
		# Copy
		b_share = QPushButton('Copy Selection')
		b_share.clicked.connect(self.copy_selection)
		act_layout.addWidget(b_share)
		# Edit
		b_edit = QPushButton('Send to Editor')
		b_edit.clicked.connect(self.send_to_editor)
		act_layout.addWidget(b_edit)
		act_layout.addStretch()

	def show_item(self, index):
		self.viewer = ImageViewer(self.files, index)
		self.viewer.show()

	def delete_selection(self):
		indices = self.gallery.selectedIndexes()
		count = len(indices)
		if count == 0:
			return
		word = 'image' if count == 1 else 'images'
		ret = QMessageBox.question(self, 'Are you sure?', f'This will delete the selected {count} {word} and associated data. '
			f'Do you want to proceed?', QMessageBox.Yes | QMessageBox.No)
		if ret == QMessageBox.No:
			return
		for index in indices:
			file = self.files.data(index, Qt.DisplayRole)
			fn = f'output/{file}'
			self.delete_file(fn, False)

	def copy_selection(self):
		indices = self.gallery.selectedIndexes()
		count = len(indices)
		if count == 0:
			return
		# Get destination folder
		dest = QFileDialog.getExistingDirectory(self, "Select Directory")
		if len(dest) == 0:
			return
		# Copy files over one by one
		for index in indices:
			file = self.files.data(index, Qt.DisplayRole)
			fn = f'output/{file}'
			to = f'{dest}/{file}'
			print(f'Copying to: {to}')
			shutil.copy2(fn, to)

	def send_to_editor(self):
		indices = self.gallery.selectedIndexes()
		count = len(indices)
		if count == 0:
			QMessageBox.warning(self, 'No Files Selected', 'You neeed to select a file and try again.')
			return
		# Only one image can be selected for this feature
		if count > 1:
			QMessageBox.warning(self, 'Too Many Files', 'You have too many files selected. Select ONE file and try again.')
			return
		# Load image in editor
		file = self.files.data(indices[0], Qt.DisplayRole)
		image = Image.open(f'output/{file}')
		self.editor_tab.load_image(image)