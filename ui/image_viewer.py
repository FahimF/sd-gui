from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QFrame, QGraphicsPixmapItem, QVBoxLayout

class ImageViewer(QWidget):
	def __init__(self, file:str):
		print(f'Creating Image viewer for: {file}')
		super(ImageViewer, self).__init__()
		image = QPixmap(file)
		size = image.size()
		self.resize(size.width(), size.height())
		# Viewer
		self.view = QGraphicsView()
		self._zoom = 0
		self._scene = QGraphicsScene(self)
		self._photo = QGraphicsPixmapItem()
		self._scene.addItem(self._photo)
		self.view.setScene(self._scene)
		self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
		self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
		self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
		self.view.setFrameShape(QFrame.NoFrame)
		self.view.setDragMode(QGraphicsView.ScrollHandDrag)
		self._photo.setPixmap(image)
		self.fitInView()
		# Arrange layout
		main_layout = QVBoxLayout(self)
		main_layout.addWidget(self.view)

	def fitInView(self, scale=True):
		rect = QRectF(self._photo.pixmap().rect())
		if not rect.isNull():
			self.view.setSceneRect(rect)
			unity = self.view.transform().mapRect(QRectF(0, 0, 1, 1))
			self.view.scale(1 / unity.width(), 1 / unity.height())
			viewrect = self.view.viewport().rect()
			scenerect = self.view.transform().mapRect(rect)
			factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
			self.view.scale(factor, factor)
			self._zoom = 0

	def wheelEvent(self, event):
		if event.angleDelta().y() > 0:
			factor = 1.25
			self._zoom += 1
		else:
			factor = 0.8
			self._zoom -= 1
		if self._zoom > 0:
			self.view.scale(factor, factor)
		elif self._zoom == 0:
			self.fitInView()
		else:
			self._zoom = 0

	def resizeEvent(self, event):
		self.fitInView()
