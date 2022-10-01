import traceback
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QSlider, QHBoxLayout, QLineEdit, QPushButton

class Slider(QWidget):
	slider = None
	value_text = None
	dtype = float
	minimum = 0
	maximum = 1
	default = 0.5
	step = 0.01
	on_changed = None

	def __init__(self, name: str, minimum=0, maximum=1, default=0.5, step=0.01, edit_disabled = False, dtype=float, on_changed=None):
		super(Slider, self).__init__()
		self.no_update = False
		self.dtype = dtype
		self.on_changed = on_changed
		self.step = step
		self.default = default
		# Layout
		main_layout = QVBoxLayout(self)
		main_layout.setSpacing(8)
		# Name
		name_label = QLabel(name)
		name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		main_layout.addWidget(name_label)
		# Slider
		self.slider = QSlider(Qt.Horizontal)
		# slider.setMinimum(minimum * 100)
		# slider.setMaximum(maximum * 100)
		# slider.setValue(int(default * 100))
		self.slider.setValue(int(default / step))
		# slider.setTickInterval(1)
		self.slider.setRange(int(minimum / step), int(maximum / step))
		self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.slider.valueChanged.connect(self.slider_changed)
		main_layout.addWidget(self.slider)
		# Info row
		info_layout = QHBoxLayout()
		# Min label
		min_label = QLabel(name)
		min_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		min_label.setText(f'{minimum}')
		info_layout.addWidget(min_label)
		# Spacer
		info_layout.addStretch()
		# Value
		self.value_text = QLineEdit()
		self.value_text.setText(f'{default}')
		self.value_text.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		self.value_text.setFixedSize(40, 20)
		if edit_disabled:
			self.value_text.setReadOnly(True)
		self.value_text.textChanged.connect(self.value_changed)
		info_layout.addWidget(self.value_text)
		# Reset value
		reset_button = QPushButton('↺')
		reset_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		reset_button.clicked.connect(self.reset)
		info_layout.addWidget(reset_button)
		# Spacer
		info_layout.addStretch()
		# Max label
		max_label = QLabel(name)
		max_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		max_label.setText(f'{maximum}')
		info_layout.addWidget(max_label)
		# Finalize info layout
		main_layout.addLayout(info_layout)

	def value(self):
		value = self.dtype(self.slider.value() * self.step)
		return value

	def set_value(self, value):
		self.no_update = True
		self.slider.setValue(value)
		self.no_update = False

	def slider_changed(self):
		value = self.dtype(self.slider.value() * self.step)
		self.value_text.setText(str(value))
		if self.on_changed and not self.no_update:
			self.on_changed(value)

	def value_changed(self):
		try:
			value = self.dtype(float(self.value_text.text()) / self.step)
			self.slider.setValue(int(value))
			if self.on_changed:
				self.on_changed(self.dtype(self.value_text.text()))
		except Exception:
			print(traceback.format_exc())

	def reset(self):
		self.slider.setValue(int(self.default / self.step))
		self.value_text.setText(str(self.default))
