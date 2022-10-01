from typing import List
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel

class ComboBox(QWidget):
	combobox = None

	def __init__(self, name: str, options: List[str], default=None, on_select=None):
		super(ComboBox, self).__init__()
		# self.setStyleSheet(debugStyle)
		layout = QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		# Label
		if len(name) > 0:
			label = QLabel(name)
			layout.addWidget(label)
		# Combobox
		self.combobox = QComboBox()
		self.combobox.addItems(options)
		if default is not None:
			self.combobox.setCurrentText(default)
		if on_select is not None:
			self.combobox.currentTextChanged.connect(on_select)
		layout.addWidget(self.combobox)

	def value(self) -> str:
		return self.combobox.currentText()

	def clear(self):
		self.combobox.clear()

	def addItems(self, items):
		self.combobox.addItems(items)