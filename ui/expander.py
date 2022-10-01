from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolButton, QScrollArea, QSizePolicy, QFrame
from PyQt5.uic.properties import QtCore

class Expander(QWidget):
	def __init__(self, title="", on_expand=None, parent=None):
		super(Expander, self).__init__(parent)
		self.on_expand = on_expand
		self.is_expanded = False
		# Main layout
		main_layout = QVBoxLayout(self)
		main_layout.setSpacing(0)
		main_layout.setContentsMargins(0, 0, 0, 0)
		# Toggle button
		self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
		self.toggle_button.setStyleSheet("QToolButton { border: none; }")
		self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.toggle_button.setArrowType(Qt.RightArrow)
		self.toggle_button.setChecked(self.is_expanded)
		self.toggle_button.pressed.connect(self.on_pressed)
		main_layout.addWidget(self.toggle_button)
		self.toggle_height = self.toggle_button.sizeHint().height()
		# Content area
		self.content_area = QScrollArea(maximumHeight=0, minimumHeight=0)
		self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.content_area.setFrameShape(QFrame.NoFrame)
		main_layout.addWidget(self.content_area)

	def on_pressed(self):
		self.is_expanded = not self.is_expanded
		self.toggle_button.setChecked(self.is_expanded)
		self.toggle_button.setArrowType(Qt.DownArrow if self.is_expanded else Qt.RightArrow)
		self.set_height()
		# Toggle state
		if self.on_expand is not None:
			self.on_expand(self.is_expanded)

	def set_height(self):
		ht = self.toggle_height
		c_ht = 0
		if self.is_expanded:
			ht += self.content_height
			c_ht = self.content_height
		self.setFixedHeight(ht)
		self.content_area.setFixedHeight(c_ht)

	def setContentLayout(self, layout):
		lay = self.content_area.layout()
		del lay
		self.content_layout = layout
		self.content_area.setLayout(layout)
		self.content_height = self.content_layout.sizeHint().height()
		self.set_height()