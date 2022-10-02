import numpy as np
import traceback
from tools.config import Config
from PIL import Image
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QSplitter, QWidget, QScrollArea, QGroupBox, QPushButton, QHBoxLayout, QLabel, \
	QFrame, QPlainTextEdit, QFileDialog, QMessageBox, QColorDialog, QRadioButton
from tools.sd_engine import GeneratorType
from ui.base_tab import BaseTab
from ui.canvas_widget import CanvasWidget, CanvasMode
from ui.slider import Slider
from tools.utils import buttonStyle, textStyle, groupTitleStyle

class EditorTab(BaseTab):
	def __init__(self, cfg: Config):
		super(EditorTab, self).__init__(cfg)
		self.cfg = cfg
		self.canvas = None
		self.color = QColor(255, 255, 255)
		self.prev_color = QColor(0, 0, 0)
		# Create UI
		main_box = QVBoxLayout(self)
		main_box.setContentsMargins(8, 0, 8, 0)
		self.main_splitter = QSplitter(Qt.Horizontal)
		self.create_left_pane()
		self.create_right_pane()
		self.main_splitter.setStretchFactor(2, 3)
		self.main_splitter.setSizes([460, 690])
		main_box.addWidget(self.main_splitter)

	def create_left_pane(self):
		# Tool window
		tools_widget = QWidget()
		tools_layout = QVBoxLayout(tools_widget)
		scroll_area = QScrollArea()
		scroll_area.setWidgetResizable(True)

		# Image handling Section
		image_groupbox = QGroupBox('Image Handling')
		image_groupbox.setStyleSheet(groupTitleStyle)
		image_groupbox_layout = QVBoxLayout(image_groupbox)
		# Load Image
		self.b_load_image = QPushButton('Load Image')
		self.b_load_image.setToolTip('Load an image from the local drive and place it on the canvas')
		self.b_load_image.clicked.connect(self.do_load_image)
		image_groupbox_layout.addWidget(self.b_load_image)
		# Paste
		self.b_paste_image = QPushButton('Paste Image')
		self.b_paste_image.setToolTip('Load an image from the local drive and paste it on top of the canvas image matching the current brush size')
		self.b_paste_image.clicked.connect(self.do_paste_image)
		image_groupbox_layout.addWidget(self.b_paste_image)
		# Editing Section
		edit_groupbox = QGroupBox('Edit Controls')
		edit_groupbox.setStyleSheet(groupTitleStyle)
		edit_groupbox_layout = QVBoxLayout(edit_groupbox)
		tools_layout.addWidget(image_groupbox)
		# Increase size
		size_layout = QHBoxLayout()
		self.b_increase_size = QPushButton('Increase Canvas Size')
		self.b_increase_size.setToolTip('Increase the size of the drawing canvas for outpainting')
		self.b_increase_size.clicked.connect(self.increase_size)
		size_layout.addWidget(self.b_increase_size)
		# Decrease size
		self.b_decrease_size = QPushButton('Decrease Canvas Size')
		self.b_decrease_size.setToolTip('Reduce the size of the drawing canvas')
		self.b_decrease_size.clicked.connect(self.decrease_size)
		size_layout.addWidget(self.b_decrease_size)
		edit_groupbox_layout.addLayout(size_layout)
		# Color & mode section
		color_layout = QHBoxLayout()
		# Paint color
		color_label = QLabel('Paint Color')
		color_layout.addWidget(color_label)
		self.color_widget  = QPushButton()
		self.color_widget.setToolTip('Display the color picker to set the drawing color')
		self.color_widget.setFixedSize(36, 36)
		self.color_widget.clicked.connect(self.select_color)
		self.color_widget.setStyleSheet(f'background-color: {self.color.name()};')
		color_layout.addWidget(self.color_widget)
		color_layout.addStretch()
		# Previous colour
		color_label = QLabel('Previous Color')
		color_layout.addWidget(color_label)
		self.prev_color_widget  = QPushButton()
		self.prev_color_widget.setToolTip('Previous color - tap to switch current color to this.')
		self.prev_color_widget.setFixedSize(36, 36)
		self.prev_color_widget.clicked.connect(self.switch_color)
		self.prev_color_widget.setStyleSheet(f'background-color: {self.prev_color.name()};')
		color_layout.addWidget(self.prev_color_widget)
		edit_groupbox_layout.addLayout(color_layout)
		# Selection size
		self.selection_size = Slider("Selection Size", minimum=64, maximum=2048, step=64, edit_disabled=True, default=128,
			dtype=int, on_changed=self.brush_size_changed)
		self.selection_size.setToolTip('The selection rectangle size. Determines image placement or inpainting just for the current selection.')
		edit_groupbox_layout.addWidget(self.selection_size)
		# Brush size
		self.brush_size = Slider("Brush Size", minimum=1, maximum=1024, step=1, edit_disabled=True, default=96,
			dtype=int, on_changed=self.brush_size_changed)
		self.brush_size.setToolTip('The brush size for drawing. Determines the size of the brush when painting/erasing.')
		edit_groupbox_layout.addWidget(self.brush_size)
		self.brush_size.setEnabled(False)
		# Canvas modes section
		mode_widgets_layout = QHBoxLayout()
		# Select
		self.b_select = QPushButton()
		self.b_select.setCheckable(True)
		self.b_select.toggle()
		self.b_select.setStyleSheet('QPushButton{border: 0px solid; background-color : lightblue}')
		self.b_select.setIcon(QIcon('assets/select.png'))
		self.b_select.setIconSize(QSize(40, 40))
		self.b_select.setFixedSize(60, 60)
		self.b_select.setToolTip('Select mode - select a portion of the canvas for pasting, inpaiting etc.')
		self.b_select.clicked.connect(lambda: self.mode_button_clicked(self.b_select))
		self.previous_mode = self.b_select
		mode_widgets_layout.addWidget(self.b_select)
		# Erase
		self.b_erase = QPushButton()
		self.b_erase.setCheckable(True)
		self.b_erase.setStyleSheet('QPushButton{border: 0px solid;}')
		self.b_erase.setIcon(QIcon('assets/erase.png'))
		self.b_erase.setIconSize(QSize(40, 40))
		self.b_erase.setFixedSize(60, 60)
		self.b_erase.setToolTip('Erase mode - erase canvas by left-clicking and dragging')
		self.b_erase.clicked.connect(lambda: self.mode_button_clicked(self.b_erase))
		mode_widgets_layout.addWidget(self.b_erase)
		# Paint
		self.b_draw = QPushButton()
		self.b_draw.setCheckable(True)
		self.b_draw.setStyleSheet('QPushButton{border: 0px solid;}')
		self.b_draw.setIcon(QIcon('assets/draw.png'))
		self.b_draw.setIconSize(QSize(40, 40))
		self.b_draw.setFixedSize(60, 60)
		self.b_draw.setToolTip('Draw mode - draw on canvas by left-clicking and dragging')
		self.b_draw.clicked.connect(lambda: self.mode_button_clicked(self.b_draw))
		mode_widgets_layout.addWidget(self.b_draw)
		edit_groupbox_layout.addLayout(mode_widgets_layout)
		# Undo
		undo_redo_layout = QHBoxLayout()
		self.b_undo = QPushButton('Undo')
		self.b_undo.setToolTip('Undo previous drawing actions')
		self.b_undo.clicked.connect(self.do_undo)
		undo_redo_layout.addWidget(self.b_undo)
		# Redo
		self.b_redo = QPushButton('Redo')
		self.b_redo.setToolTip('Redo previously undone drawing actions')
		self.b_redo.clicked.connect(self.do_redo)
		undo_redo_layout.addWidget(self.b_redo)
		edit_groupbox_layout.addLayout(undo_redo_layout)
		tools_layout.addWidget(edit_groupbox)
		# Actions section
		action_groupbox = QGroupBox('Actions')
		action_groupbox.setStyleSheet(groupTitleStyle)
		action_groupbox_layout = QVBoxLayout(action_groupbox)
		tools_layout.addWidget(action_groupbox)
		# Inpaint type
		inpaint_layout = QHBoxLayout()
		action_groupbox_layout.addLayout(inpaint_layout)
		# Label
		mode_label = QLabel('Target')
		inpaint_layout.addWidget(mode_label)
		# Draw
		self.scope_full = QRadioButton()
		self.scope_full.setToolTip('Set the scope of actions within this group to be for the full image')
		self.scope_full.setText('Full Image')
		inpaint_layout.addWidget(self.scope_full)
		# Select
		self.scope_selected = QRadioButton()
		self.scope_selected.setToolTip('Set the scope of actions within this group to be just for the selected area')
		self.scope_selected.setText('Selection')
		self.scope_selected.toggle()
		inpaint_layout.addWidget(self.scope_selected)
		# Mask actions
		mask_layout = QHBoxLayout()
		action_groupbox_layout.addLayout(mask_layout)
		# Fill White
		self.b_fill = QPushButton('Fill White')
		self.b_fill.setToolTip('Fill transparent areas with white to create an inpainted area')
		self.b_fill.clicked.connect(self.fill_white)
		mask_layout.addWidget(self.b_fill)
		# Fill Black
		self.b_mask = QPushButton('Mask Black')
		self.b_mask.setToolTip('Fill any color that is not the currently selected color with black to create a masked area')
		self.b_mask.clicked.connect(self.mask_black)
		mask_layout.addWidget(self.b_mask)
		# Inpaint
		self.b_inpaint = QPushButton('Inpaint')
		self.b_inpaint.setToolTip('Generate a new image for the selected area or the full window')
		self.b_inpaint.setStyleSheet(buttonStyle)
		self.b_inpaint.clicked.connect(self.do_inpaint)
		action_groupbox_layout.addWidget(self.b_inpaint)

		tools_layout.addStretch()
		scroll_area.setWidget(tools_widget)
		scroll_area.resize(tools_widget.sizeHint())
		self.main_splitter.addWidget(scroll_area)

	def create_right_pane(self):
		frame = QFrame()
		frame.setFrameShape(QFrame.StyledPanel)
		frame.layout = QVBoxLayout(frame)
		self.edit_scroll = QScrollArea()
		self.edit_scroll.setWidgetResizable(True)
		self.edit_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.edit_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		# Prompt
		self.prompt_text = QPlainTextEdit()
		self.prompt_text.setToolTip('Enter the prompt text for the area you want to inpaint')
		self.prompt_text.setPlaceholderText('Prompt')
		self.prompt_text.setFixedHeight(60)
		self.prompt_text.setStyleSheet(textStyle)
		palette = self.prompt_text.palette()
		palette.setBrush(palette.Window, QBrush(Qt.transparent))
		self.prompt_text.setPalette(palette)
		frame.layout.addWidget(self.prompt_text)

		# Canvas
		def brush_changed():
			size = self.canvas.selection_size
			# Update size depending on mode
			if self.b_select.isChecked():
				self.brush_size.set_value(size)
			else:
				self.selection_size.set_value(size)

		self.canvas = CanvasWidget(on_brush_changed=brush_changed)
		bg = self.get_texture()
		self.canvas.set_np_image(bg)
		self.edit_scroll.setWidget(self.canvas)
		frame.layout.addWidget(self.edit_scroll)
		#  Actions
		action_layout = QHBoxLayout()
		b_save = QPushButton('Save Image')
		action_layout.addWidget(b_save)
		frame.layout.addLayout(action_layout)
		self.main_splitter.addWidget(frame)

	def load_image(self, image: Image):
		image_numpy = np.array(image)
		self.canvas.set_np_image(image_numpy, save_original=True)
		self.canvas.resize_to_image(only_if_smaller=True)
		self.canvas.update()

	def save_image(self):
		fn = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Image Files (*.png *.jpeg *.jpg)')
		if fn:
			image = Image.fromarray(np.uint8(self.canvas.np_image))
			image.save(fn)

	def paste_image(self, image: Image):
		wd = self.canvas.selection_rectangle.width()
		ht = self.canvas.selection_rectangle.height()
		resized = np.array(image.resize((wd, ht), Image.LANCZOS))
		self.canvas.set_selection_image(resized)
		self.canvas.update()

	def do_load_image(self):
		fn = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpeg *.jpg)', '')[0]
		if fn:
			image = Image.open(fn).convert('RGB')
			self.load_image(image)

	def do_paste_image(self):
		fn = QFileDialog.getOpenFileName(self, 'Paste Image', '', 'Image Files (*.png *.jpeg *.jpg)')[0]
		if fn:
			image = Image.open(fn)
			self.paste_image(image)

	def brush_size_changed(self, val):
		# Change selection size if we are in select mode
		self.canvas.set_rect_size(val)

	def do_inpaint(self):
		try:
			self.toggle_actions(False)
			# Get inputs
			prompt = self.prompt_text.toPlainText()
			# Do we take the full image or the selection?
			if self.scope_full.isChecked():
				iarr = self.canvas.np_original_image
				marr = self.canvas.np_image
			else:
				iarr = self.canvas.get_selection_original()
				marr = self.canvas.get_selection_np_image()
			# Convert any transparent areas in mask image to white

			# Convert NP arrays to images
			image = Image.fromarray(np.uint8(iarr)).convert('RGB')
			mask = Image.fromarray(np.uint8(marr)).convert('RGB')
			wd, ht = image.size
			# Configure
			self.cfg.type = GeneratorType.img2img
			self.cfg.scheduler = 'Default'
			self.cfg.num_inference_steps = 50
			# Get SD engine
			sd = self.get_server('local')
			# Inpaint
			image, seed = sd.inpaint(prompt, image, mask, wd, ht, -1 , 7.5, 0.6)
			if self.scope_full.isChecked():
				self.load_image(image)
			else:
				# Revert image to original
				self.canvas.revert_np_image()
				# Paste in inpainted section
				self.paste_image(image)
		except:
			print(traceback.format_exc())
			QMessageBox.warning(self, 'Failed', 'Running inpainting failed! Check console for details.')
		finally:
			self.toggle_actions(True)

	def toggle_actions(self, enabled: bool):
		self.b_load_image.setEnabled(enabled)
		self.b_inpaint.setEnabled(enabled)
		self.b_increase_size.setEnabled(enabled)
		self.b_decrease_size.setEnabled(enabled)
		self.b_erase.setEnabled(enabled)
		self.b_draw.setEnabled(enabled)
		self.color_widget.setEnabled(enabled)
		self.b_undo.setEnabled(enabled)
		self.b_redo.setEnabled(enabled)

	def increase_size(self):
		self.canvas.increase_image_size()
		self.canvas.resize_to_image(only_if_smaller=True)
		self.canvas.update()

	def decrease_size(self):
		self.canvas.decrease_image_size()
		self.canvas.update()

	def erase(self):
		self.canvas.erase_selection()
		self.canvas.update()

	def do_paint(self):
		self.canvas.paint_selection()
		self.canvas.update()

	def select_color(self):
		color = QColorDialog.getColor()
		if color.isValid():
			# Set previous color
			if self.color != self.prev_color:
				self.prev_color = self.color
				self.prev_color_widget.setStyleSheet(f'background-color: {self.prev_color.name()};')
			# Pass on selection canvas
			self.canvas.set_color(color)
			self.color = color
			self.color_widget.setStyleSheet(f'background-color: {color.name()};')

	def switch_color(self):
		curr = self.color
		self.color = self.prev_color
		self.canvas.set_color(self.color)
		self.prev_color = curr
		self.prev_color_widget.setStyleSheet(f'background-color: {self.prev_color.name()};')
		self.color_widget.setStyleSheet(f'background-color: {self.color.name()};')

	def mode_button_clicked(self, btn):
		# If this is the same as the previous, just toggle button back and return
		if self.previous_mode == btn:
			btn.toggle()
			return
		self.previous_mode.toggle()
		self.previous_mode.setStyleSheet('QPushButton{border: 0px solid; background-color : transparent}')
		btn.setStyleSheet('QPushButton{border: 0px solid; background-color : lightblue}')
		# Change mode
		if btn == self.b_select:
			self.canvas.set_mode(CanvasMode.select)
			self.selection_size.setEnabled(True)
			self.brush_size.setEnabled(False)
		elif btn == self.b_erase:
			self.canvas.set_mode(CanvasMode.erase)
		elif btn == self.b_draw:
			self.canvas.set_mode(CanvasMode.draw)
		elif btn == self.b_fill:
			self.canvas.set_mode(CanvasMode.fill)
		if btn != self.b_select:
			self.selection_size.setEnabled(False)
			self.brush_size.setEnabled(True)
		self.previous_mode = btn

	def do_undo(self):
		self.canvas.undo()
		self.canvas.update()

	def do_redo(self):
		self.canvas.redo()
		self.canvas.update()

	def fill_white(self):
		if self.scope_full:
			self.canvas.fill_transparent(full_image=True)
		else:
			self.canvas.fill_transparent()

	def mask_black(self):
		if self.scope_full:
			self.canvas.create_mask(full_image=True)
		else:
			self.canvas.create_mask()
