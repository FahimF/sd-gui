import numpy as np
from enum import Enum
from PIL import Image
from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QImage, QPen
from PyQt5.QtWidgets import QWidget

class CanvasMode(Enum):
	draw = 1
	select = 2
	erase = 3
	fill = 4

class CanvasWidget(QWidget):
	SIZE_INCREASE_INCREMENT = 64
	np_original_image = None
	np_image = None
	qt_image = None
	img_width = 512
	img_height = 512
	selection_rectangle = None
	selection_size = 128
	brush_rectangle = None
	brush_size = 32
	is_dragging = False
	image_rect = None
	history = []
	future = []
	prev_color = np.array([0, 0, 0])
	color = np.array([255, 255, 255])
	canvasMode = CanvasMode.select

	def __init__(self, on_brush_changed=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.on_brush_changed = on_brush_changed
		self.setAcceptDrops(True)

	def update_and(self, f):
		def update_and_f(*args, **kwargs):
			f(*args, **kwargs)
			self.update()
		return update_and_f

	def dragEnterEvent(self, e):
		if e.mimeData().hasImage:
			e.accept()
		else:
			e.ignore()

	def dropEvent(self, e):
		imdata = Image.open(e.mimeData().text()[8:])
		image_numpy = np.array(imdata)
		self.set_np_image(image_numpy)
		self.resize_to_image(only_if_smaller=True)
		self.update()

	def set_color(self, new_color):
		self.prev_color = self.color
		self.color = np.array([new_color.red(), new_color.green(), new_color.blue()])

	def set_mode(self, mode: CanvasMode):
		self.canvasMode = mode
		self.update()

	def undo(self):
		if len(self.history) > 0:
			self.future = [self.np_image.copy()] + self.future
			self.set_np_image(self.history[-1], add_to_history=False)
			self.history = self.history[:-1]

	def redo(self):
		if len(self.future) > 0:
			prev_image = self.np_image.copy()
			self.set_np_image(self.future[0], add_to_history=False)
			self.future = self.future[1:]
			self.history.append(prev_image)

	def set_np_image(self, arr, add_to_history=True, save_original=False):
		if arr.shape[-1] == 3:
			arr = np.concatenate([arr, np.ones(arr.shape[:2] + (1,)) * 255], axis=-1)
		if arr.dtype != np.uint8:
			arr = arr.astype(np.uint8)
		if add_to_history:
			self.future = []
		if add_to_history and  (self.np_image is not None):
			self.history.append(self.np_image.copy())
		self.np_image = arr
		if save_original:
			self.np_original_image = arr
		self.qt_image = self.qimage_from_array(self.np_image)

	def revert_np_image(self):
		self.np_image = self.np_original_image
		self.qt_image = self.qimage_from_array(self.np_image)

	def mousePressEvent(self, e):
		# Are we in fill mode?
		if self.canvasMode == CanvasMode.fill:
			print('Going to fill')
			# Replace everything except for previous color with current color
			new_image = self.np_image.copy()
			ncol = np.append(self.color, 255)
			new_image[np.where((new_image[:, :, :3] != self.prev_color).all(axis=2))] = ncol
			self.set_np_image(new_image)
			self.update()
			return

		size = self.selection_size if self.canvasMode == CanvasMode.select else self.brush_size
		top_left = QPoint(int(e.pos().x() - size / 2), int(e.pos().y() - size / 2))
		r = QRect(top_left, QSize(size, size))
		if self.canvasMode == CanvasMode.select:
			self.selection_rectangle = r
		else:
			self.brush_rectangle = r
		self.is_dragging = True
		if self.canvasMode == CanvasMode.draw:
			self.paint_selection()
		elif self.canvasMode == CanvasMode.erase:
			self.erase_selection()
		self.update()

	def mouseMoveEvent(self, e):
		if self.is_dragging:
			# Always move, but might do draw/ersae too
			if self.canvasMode == CanvasMode.select:
				self.selection_rectangle.moveCenter(e.pos())
			else:
				self.brush_rectangle.moveCenter(e.pos())
			# Do we paint or erase?
			if self.canvasMode == CanvasMode.draw:
				self.paint_selection(False)
			elif self.canvasMode == CanvasMode.erase:
				self.erase_selection(False)
			self.update()

	def mouseReleaseEvent(self, e):
		self.is_dragging = False

	def set_rect_size(self, size):
		if self.canvasMode == CanvasMode.select:
			self.selection_size = size
			center = self.selection_rectangle.center()
		else:
			self.brush_size = size
			center = self.brush_rectangle.center()
		sz = QSize(size, size)
		if self.canvasMode == CanvasMode.select:
			self.selection_rectangle.setSize(sz)
			self.selection_rectangle.moveCenter(center)
		else:
			self.brush_rectangle.setSize(sz)
			self.brush_rectangle.moveCenter(center)
		self.update()

	def resize_to_image(self, only_if_smaller=False):
		if self.qt_image is not None:
			if only_if_smaller:
				if self.qt_image.width() < self.width() and self.qt_image.height() < self.height():
					return
			self.resize(self.qt_image.width(), self.qt_image.height())

	def map_widget_to_image(self, pos):
		w, h = self.qt_image.width(), self.qt_image.height()
		window_width = self.width()
		window_height = self.height()
		offset_x = (window_width - w) / 2
		offset_y = (window_height - h) / 2
		return QPoint(int(pos.x() - offset_x), int(pos.y() - offset_y))

	def map_widget_to_image_rect(self, widget_rect):
		image_rect = QRect()
		image_rect.setTopLeft(self.map_widget_to_image(widget_rect.topLeft()))
		image_rect.setBottomRight(self.map_widget_to_image(widget_rect.bottomRight()))
		return image_rect

	def crop_image_rect(self, image_rect, use_brush: bool = False):
		width = self.brush_size if use_brush else self.selection_size
		source_rect = QRect(0, 0, width, width)
		if image_rect.left() < 0:
			source_rect.setLeft(-image_rect.left())
			image_rect.setLeft(0)
		if image_rect.right() >= self.qt_image.width():
			source_rect.setRight(width - image_rect.right() + self.qt_image.width() - 1)
			image_rect.setRight(self.qt_image.width())
		if image_rect.top() < 0:
			source_rect.setTop(-image_rect.top())
			image_rect.setTop(0)
		if image_rect.bottom() >= self.qt_image.height():
			source_rect.setBottom(width - image_rect.bottom() + self.qt_image.height() - 1)
			image_rect.setBottom(self.qt_image.height())
		return image_rect, source_rect

	def paint_selection(self, add_to_history=True):
		if self.brush_rectangle is not None:
			image_rect = self.map_widget_to_image_rect(self.brush_rectangle)
			image_rect, source_rect = self.crop_image_rect(image_rect, use_brush=True)
			new_image = self.np_image.copy()
			new_image[image_rect.top():image_rect.bottom(), image_rect.left():image_rect.right(), :3] = self.color
			new_image[image_rect.top():image_rect.bottom(), image_rect.left():image_rect.right(), 3] = 255
			self.set_np_image(new_image, add_to_history=add_to_history)

	def erase_selection(self, add_to_history=True):
		if self.brush_rectangle is not None:
			image_rect = self.map_widget_to_image_rect(self.brush_rectangle)
			image_rect, source_rect = self.crop_image_rect(image_rect, use_brush=True)
			new_image = self.np_image.copy()
			new_image[image_rect.top():image_rect.bottom(), image_rect.left():image_rect.right(), :] = 0
			self.set_np_image(new_image, add_to_history=add_to_history)

	def set_selection_image(self, patch_image):
		if self.selection_rectangle is not None:
			image_rect = self.map_widget_to_image_rect(self.selection_rectangle)
			image_rect, source_rect = self.crop_image_rect(image_rect)
			new_image = self.np_image.copy()
			# Copy original to update that too
			new_orig = self.np_original_image.copy()
			target_width = image_rect.width()
			target_height = image_rect.height()
			patch_np = np.array(patch_image)[source_rect.top():source_rect.bottom(), source_rect.left():source_rect.right(), :][:target_height, :target_width, :]
			if patch_np.shape[-1] == 4:
				patch_np, patch_alpha = patch_np[:, :, :3], patch_np[:, :, 3]
				patch_alpha = (patch_alpha > 128) * 255
			else:
				patch_alpha = np.ones((patch_np.shape[0], patch_np.shape[1])).astype(np.uint8) * 255
			new_image[image_rect.top():image_rect.top() + patch_np.shape[0],
			image_rect.left():image_rect.left() + patch_np.shape[1], :][patch_alpha > 128] = \
				np.concatenate([patch_np, patch_alpha[:, :, None]], axis=-1)[patch_alpha > 128]
			# Update original and replace it here itself since set_np_image gets called from lots of placess
			new_orig[image_rect.top():image_rect.top() + patch_np.shape[0],
			image_rect.left():image_rect.left() + patch_np.shape[1], :][patch_alpha > 128] = \
				np.concatenate([patch_np, patch_alpha[:, :, None]], axis=-1)[patch_alpha > 128]
			self.np_original_image = new_orig
			self.set_np_image(new_image)

	def get_selection_np_image(self):
		image_rect = self.map_widget_to_image_rect(self.selection_rectangle)
		image_rect, source_rect = self.crop_image_rect(image_rect)
		result = np.zeros((self.selection_rectangle.height(), self.selection_rectangle.width(), 4), dtype=np.uint8)
		if image_rect.width() != source_rect.width():
			source_rect.setRight(source_rect.right() - 1)
		if image_rect.height() != source_rect.height():
			source_rect.setBottom(source_rect.bottom() - 1)
		result[source_rect.top():source_rect.bottom(), source_rect.left():source_rect.right(), :] = \
			self.np_image[image_rect.top():image_rect.bottom(), image_rect.left():image_rect.right(), :]
		return result

	def get_selection_original(self):
		image_rect = self.map_widget_to_image_rect(self.selection_rectangle)
		image_rect, source_rect = self.crop_image_rect(image_rect)
		result = np.zeros((self.selection_rectangle.height(), self.selection_rectangle.width(), 4), dtype=np.uint8)
		if image_rect.width() != source_rect.width():
			source_rect.setRight(source_rect.right() - 1)
		if image_rect.height() != source_rect.height():
			source_rect.setBottom(source_rect.bottom() - 1)
		result[source_rect.top():source_rect.bottom(), source_rect.left():source_rect.right(), :] = \
			self.np_original_image[image_rect.top():image_rect.bottom(), image_rect.left():image_rect.right(), :]
		return result

	def increase_image_size(self):
		H = self.SIZE_INCREASE_INCREMENT // 2
		self.img_width += self.SIZE_INCREASE_INCREMENT
		self.img_height += self.SIZE_INCREASE_INCREMENT
		new_image = np.zeros((self.np_image.shape[0] + self.SIZE_INCREASE_INCREMENT, self.np_image.shape[1] +
			self.SIZE_INCREASE_INCREMENT, 4), dtype=np.uint8)
		new_image[H:-H, H:-H, :] = self.np_image
		self.set_np_image(new_image)

	def decrease_image_size(self):
		H = self.SIZE_INCREASE_INCREMENT // 2
		self.set_np_image(self.np_image[H:-H, H:-H, :])

	def paintEvent(self, e):
		painter = QPainter(self)
		checkerboard_brush = QBrush()
		checkerboard_brush.setColor(QColor('gray'))
		checkerboard_brush.setStyle(Qt.Dense5Pattern)
		if self.qt_image is not None:
			w, h = self.qt_image.width(), self.qt_image.height()
			window_width = self.width()
			window_height = self.height()
			offset_x = (window_width - w) / 2
			offset_y = (window_height - h) / 2
			self.image_rect = QRect(int(offset_x), int(offset_y), int(w), int(h))
			# Set initial selection rectangle
			if self.selection_rectangle is None:
				size = QSize(self.selection_size, self.selection_size)
				self.selection_rectangle = QRect(self.image_rect.topLeft(), size)
			# Set initial brush rectangle rectangle
			if self.brush_rectangle is None:
				size = QSize(self.brush_size, self.brush_size)
				self.brush_rectangle = QRect(self.image_rect.center(), size)
			prev_brush = painter.brush()
			painter.fillRect(self.image_rect, checkerboard_brush)
			painter.setBrush(prev_brush)
			painter.drawImage(self.image_rect, self.qt_image)
		# Always draw selection rectangle
		if self.selection_rectangle is not None:
			# painter.setBrush(redbrush)
			painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
			painter.drawRect(self.selection_rectangle)
		# Only draw brush rectangle if in draw/erase mode
		if self.brush_rectangle is not None and self.canvasMode != CanvasMode.select:
			painter.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
			painter.drawRect(self.brush_rectangle)

	def qimage_from_array(self, arr):
		maximum = arr.max()
		if maximum > 0 and maximum <= 1:
			return QImage((arr.astype('uint8') * 255).data, arr.shape[1], arr.shape[0], QImage.Format_RGBA8888)
		else:
			return QImage(arr.astype('uint8').data, arr.shape[1], arr.shape[0], QImage.Format_RGBA8888)
