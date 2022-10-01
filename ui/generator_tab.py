from tools.config import Config
from data.batch import Batch
import data.image as DImg
import pathlib
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QTextCursor, QBrush, QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QSplitter, QFrame, QPlainTextEdit, QMessageBox, QHBoxLayout, QLabel, \
	QFileDialog, QPushButton, QWidget, QScrollArea, QGroupBox, QSpinBox, QLineEdit, QToolButton
from ui.base_tab import BaseTab, SDWorker
from ui.combobox import ComboBox
from ui.expander import Expander
from ui.slider import Slider
from tools.utils import buttonStyle, groupTitleStyle, textStyle
from PIL import Image
from tools.sd_engine import  GeneratorType

class GeneratorTab(BaseTab):
	def __init__(self, cfg: Config):
		super(GeneratorTab, self).__init__(cfg)
		self.cfg = cfg
		# Config variables
		self.server_type = None
		self.files = []
		self.seeds = []
		self.file_index = -1
		self.prompt_height = 178
		self.mods_open = False
		self.category_change = False
		self.updating_prompts = False
		self.image_input_open = False
		self.asset_path = pathlib.Path(__file__).parent.parent / 'assets'
		# Create UI
		self.main_layout = QVBoxLayout(self)
		self.main_layout.setContentsMargins(8, 0, 8, 0)
		self.create_top_pane()
		self.main_splitter = QSplitter(Qt.Horizontal)
		self.create_left_pane()
		self.create_right_pane()
		self.main_splitter.setStretchFactor(2, 3)
		self.main_splitter.setSizes([460, 690])
		self.main_layout.addWidget(self.main_splitter)

	def create_top_pane(self):
		# Prompt Section
		prompt_frame = QFrame()
		prompt_frame_layout = QVBoxLayout(prompt_frame)
		# Prompt
		self.prompt_text = QPlainTextEdit()
		self.prompt_text.setToolTip('Enter the prompt text for the image you want to generate')
		self.prompt_text.setPlaceholderText('Prompt')
		if self.cfg.prompt is not None:
			self.prompt_text.setPlainText(self.cfg.prompt.prompt)
		elif len(self.cfg.string_prompts()) > 0:
			self.prompt_text.setPlainText(self.cfg.string_prompts()[0])
		self.prompt_text.setFixedHeight(60)
		self.prompt_text.setStyleSheet(textStyle)
		palette = self.prompt_text.palette()
		palette.setBrush(palette.Window, QBrush(Qt.transparent))
		self.prompt_text.setPalette(palette)
		prompt_frame_layout.addWidget(self.prompt_text)
		# Prompt history
		def prompts_changed(val):
			if self.updating_prompts:
				return
			# Check whether to replace
			curr = self.prompt_text.toPlainText()
			# print(f'Current prompt: {curr}')
			# print(f'Prompts: {self.cfg.string_prompts()}')
			if len(curr) > 0 and not curr in self.cfg.string_prompts():
				result = QMessageBox.question(self, 'Are you sure?',
					'The current prompt is not in history. Do you want to replace it?', QMessageBox.Yes | QMessageBox.No,
					QMessageBox.No)
				if result == QMessageBox.No:
					return
			self.prompt_text.setPlainText(val)

		prompts = self.cfg.string_prompts()
		self.prompts = ComboBox('', prompts, on_select=prompts_changed)
		self.prompts.setToolTip('Prompt history. Select a prompt from here to populate the prompt text box with it.')
		prompt_frame_layout.addWidget(self.prompts)

		# Modifiers collapsible section
		def mods_toggled(expanded):
			self.prompt_height = self.prompt_height + 60 if expanded else self.prompt_height - 60
			prompt_frame.setFixedHeight(self.prompt_height)

		mods_expander = Expander('Modifier', on_expand=mods_toggled)
		mods_layout = QHBoxLayout()
		# Categories
		def category_changed(val):
			# Change modifiers list
			mods = self.cfg.modifiers[val]
			self.category_change = True
			self.mod_widget.clear()
			self.mod_widget.addItems(mods)
			self.category_change = False

		cats = self.cfg.modifiers.keys()
		self.cat_widget = ComboBox('Category', cats, on_select=category_changed)
		self.cat_widget.setToolTip('Modifier category. Select a category to change the list of available modifiers.')
		mods_layout.addWidget(self.cat_widget)
		# Modifiers
		def mod_changed(val):
			if self.category_change:
				return
			# Create cursor
			cursor = QTextCursor(self.prompt_text.document())
			# Set the cursor position (defaults to 0 so this is redundant)
			cursor.movePosition(QTextCursor.End)
			self.prompt_text.setTextCursor(cursor)
			# Insert text at the cursor
			if len(self.prompt_text.toPlainText()):
				val = ', ' + val
			self.prompt_text.insertPlainText(val)

		keys = list(self.cfg.modifiers.keys())
		mods = self.cfg.modifiers[keys[0]]
		self.mod_widget = ComboBox('Modifiers', mods, on_select=mod_changed)
		self.mod_widget.setToolTip('Prompt modifier. Select from the list to add a modifier to the current prompt.')
		mods_layout.addWidget(self.mod_widget)
		mods_layout.addStretch()
		# Finalize modifiers section
		mods_expander.setContentLayout(mods_layout)
		prompt_frame_layout.addWidget(mods_expander)

		# Input image collapsible section
		def input_image_toggled(expanded):
			self.prompt_height = self.prompt_height + 200 if expanded else self.prompt_height - 200
			prompt_frame.setFixedHeight(self.prompt_height)

		img_expander = Expander('Input Image', on_expand=input_image_toggled)
		img_layout = QHBoxLayout()
		# Image info section
		img_info_layout = QVBoxLayout()
		img_layout.addLayout(img_info_layout)
		# Label
		lbl = QLabel('Input Image')
		img_info_layout.addWidget(lbl)
		# Image path
		img_path_layout = QHBoxLayout()
		img_info_layout.addLayout(img_path_layout)
		self.input_image_path = QLabel()
		img_path_layout.addWidget(self.input_image_path)
		# Image picker
		def pick_image():
			options = QFileDialog.Options()
			fn, _ = QFileDialog.getOpenFileName(self, 'Pick Input Image', '', 'Image Files (*.png *.jpeg *.jpg)', options=options)
			if fn:
				self.input_image_path.setText(fn)
				self.input_image.setPixmap(QPixmap(fn))
		img_picker = QPushButton('...')
		img_picker.setToolTip('Select an input image to be passed to Stable Diffusion for img2img generation.')
		img_picker.setFixedSize(40, 36)
		img_picker.clicked.connect(pick_image)
		img_path_layout.addWidget(img_picker)
		# Reeset image page
		def clear_image():
			self.input_image_path.setText('')
			self.input_image.clear()
		reset_image = QPushButton('↺')
		reset_image.setToolTip('Clear the current image so that no image is passed to Stable Diffusion.')
		reset_image.setFixedSize(40, 36)
		reset_image.clicked.connect(clear_image)
		img_path_layout.addWidget(reset_image)
		# Noise strength
		self.strength = Slider("Noise Strength", default=self.cfg.noise_strength)
		self.strength.setToolTip('How strongly the input image affects the generated image.')
		img_info_layout.addWidget(self.strength)
		# Image
		self.input_image = QLabel(self)
		self.input_image.setToolTip('Preview of input image')
		self.input_image.setScaledContents(True)
		self.input_image.setFixedSize(128, 128)
		img_layout.addWidget(self.input_image)
		# Finalize input image section
		img_expander.setContentLayout(img_layout)
		prompt_frame_layout.addWidget(img_expander)

		# Finalize section
		prompt_frame.setFixedHeight(self.prompt_height)
		self.main_layout.addWidget(prompt_frame)

	def create_left_pane(self):
		# Tool window
		tools_widget = QWidget()
		tools_layout = QVBoxLayout(tools_widget)
		scroll_area = QScrollArea()
		scroll_area.setWidgetResizable(True)

		# SD Parameters Section
		params_groupbox = QGroupBox("Settings")
		params_groupbox.setStyleSheet(groupTitleStyle)
		params_groupbox_layout = QVBoxLayout(params_groupbox)
		# Scheduler
		sched_options = ['Default', 'LMS', 'PNDM', 'DDIM']
		self.scheduler = ComboBox('Scheduler', sched_options, default=self.cfg.scheduler)
		self.scheduler.setToolTip('Which scheduler/sampler to use for generating images.')
		params_groupbox_layout.addWidget(self.scheduler)
		# Width and height section
		size_layout = QVBoxLayout()
		params_groupbox_layout.addLayout(size_layout)
		lbl = QLabel('Output Image Size')
		size_layout.addWidget(lbl)
		# Width
		self.width = Slider("Image Width", minimum=64, maximum=2048, step=64, edit_disabled=True, default=self.cfg.width,
			dtype=int)
		self.width.setToolTip('The width of the generated image. Should be a multiplier of 64.')
		params_groupbox_layout.addWidget(self.width)
		# Height
		self.height = Slider("Image Height", minimum=64, maximum=2048, step=64, edit_disabled=True, default=self.cfg.height,
			dtype=int)
		self.height.setToolTip('The height of the generated image. Should be a multiplier of 64.')
		params_groupbox_layout.addWidget(self.height)
		# Steps
		self.num_steps = Slider("Number of Inference Steps", minimum=1, maximum=300, step=1, default=self.cfg.num_inference_steps,
			dtype=int)
		self.num_steps.setToolTip('The number of inference steps to be used to generate the image. The higher the number, better the quality, but longer the time.')
		params_groupbox_layout.addWidget(self.num_steps)
		# Guidance
		self.guidance = Slider("Guidance", minimum=-15, maximum=30, step = 0.1, default=self.cfg.guidance_scale)
		self.guidance.setToolTip('How much the text prompt affects the final image with higher numbers having more of an effect.')
		params_groupbox_layout.addWidget(self.guidance)
		# Number of images
		layout = QVBoxLayout()
		params_groupbox_layout.addLayout(layout)
		lbl = QLabel("Number of Images")
		layout.addWidget(lbl)
		self.num_copies = QSpinBox()
		self.num_copies.setToolTip('How many images to generate for this batch.')
		self.num_copies.setValue(self.cfg.num_copies)
		layout.addWidget(self.num_copies)
		# Seed
		seed_layout = QVBoxLayout()
		params_groupbox_layout.addLayout(seed_layout)
		seed_label = QLabel('Seed')
		seed_layout.addWidget(seed_label)
		self.seed_text = QLineEdit()
		self.seed_text.setToolTip('The seed to use for image generation. Default is -1. If you specify a seed, the generated image will always be the same for that particular seed.')
		self.seed_text.setText(f'{self.cfg.seed}')
		seed_layout.addWidget(self.seed_text)
		# Finalize params section
		tools_layout.addWidget(params_groupbox)

		# Generate image Section
		run_groupbox = QGroupBox('Generate')
		run_groupbox.setStyleSheet(groupTitleStyle)
		run_groupbox_layout = QVBoxLayout(run_groupbox)

		# Server
		def server_changed(val):
			if val == 'local':
				self.server_address.setDisabled(True)
			else:
				self.server_address.setEnabled(True)
		server_options = ['local', 'remote']
		self.server_type = ComboBox('Server', server_options, on_select=server_changed)
		self.server_type.setToolTip('Whether to run the image generation locally or connect to a remote server to do so.')
		run_groupbox_layout.addWidget(self.server_type)
		self.server_address = QLineEdit()
		self.server_address.setToolTip('The address and port for the remote server.')
		self.server_address.setPlaceholderText('server address')
		if self.server_type.value() == 'local':
			self.server_address.setDisabled(True)
		self.server_address.setText('http://127.0.0.1:5000')
		run_groupbox_layout.addWidget(self.server_address)
		# Generate
		self.b_generate = QPushButton('Generate')
		self.b_generate.setStyleSheet(buttonStyle)
		self.b_generate.clicked.connect(self.do_generate)
		run_groupbox_layout.addWidget(self.b_generate)
		tools_layout.addWidget(run_groupbox)
		tools_layout.addStretch()

		scroll_area.setWidget(tools_widget)
		scroll_area.resize(tools_widget.sizeHint())
		self.main_splitter.addWidget(scroll_area)

	def create_right_pane(self):
		# Tab - Viewer
		frame = QFrame()
		frame.setFrameShape(QFrame.StyledPanel)
		frame.layout = QVBoxLayout(frame)
		frame.layout.addStretch()
		iv_hbox = QHBoxLayout()
		frame.layout.addLayout(iv_hbox)
		frame.layout.addStretch()
		iv_hbox.addStretch()
		# Previous button
		icon = QIcon(str(self.asset_path / 'previous.png'))
		self.b_prev = QToolButton()
		self.b_prev.setToolTip('Show the previous image')
		self.b_prev.clicked.connect(self.previous_image)
		self.b_prev.setVisible(False)
		self.b_prev.setIcon(icon)
		iv_hbox.addWidget(self.b_prev)
		# Image section - image, info, and actions
		image_layout = QVBoxLayout()
		iv_hbox.addLayout(image_layout)
		# Image view
		self.image = QLabel(self)
		self.image.setToolTip('Preview of the current image')
		self.image.setVisible(False)
		image_layout.addWidget(self.image)
		# Info section - seed and number of images
		info_layout = QHBoxLayout()
		image_layout.addLayout(info_layout)
		# Seed
		self.seed_lbl = QLabel('Image Seed')
		self.seed_lbl.setVisible(False)
		info_layout.addWidget(self.seed_lbl)
		self.img_seed = QLineEdit()
		self.img_seed.setToolTip('The seed for the currently displayed image.')
		self.img_seed.setReadOnly(True)
		self.img_seed.setVisible(False)
		info_layout.addWidget(self.img_seed)
		info_layout.addStretch()
		# Number of images
		self.lbl_images = QLabel('Images: None')
		self.lbl_images.setVisible(False)
		info_layout.addWidget(self.lbl_images)
		# Action section - delete
		action_layout = QHBoxLayout()
		image_layout.addLayout(action_layout)
		action_layout.addStretch()
		# Delete
		self.b_del = QPushButton('Delete')
		self.b_del.setToolTip('Delete the currently displayed image and any of its data')
		self.b_del.clicked.connect(self.delete_image)
		self.b_del.setVisible(False)
		action_layout.addWidget(self.b_del)
		# Send to Editor
		self.b_edit = QPushButton('Send to Editor')
		self.b_edit.setToolTip('Send the current image to the editor tab for inpainting/outpainting')
		self.b_edit.clicked.connect(self.send_to_editor)
		self.b_edit.setVisible(False)
		action_layout.addWidget(self.b_edit)
		action_layout.addStretch()
		# Next button
		icon = QIcon(str(self.asset_path / 'next.png'))
		self.b_next = QToolButton()
		self.b_next.setToolTip('Show the next image')
		self.b_next.clicked.connect(self.next_image)
		self.b_next.setVisible(False)
		self.b_next.setIcon(icon)
		iv_hbox.addWidget(self.b_next)
		iv_hbox.addStretch()
		self.main_splitter.addWidget(frame)

	def do_generate(self):
		self.setEnabled(False)
		# Do initial data saving/setup in main thread
		img_path = self.input_image_path.text()
		self.cfg.type = GeneratorType.img2img if len(img_path) > 0 else GeneratorType.txt2img
		# Get current prompt
		prompt = self.prompt_text.toPlainText().strip()
		# Add new prompt to the prompts array - deduping and other logic is in method
		self.cfg.add_prompt(prompt)
		# Update prompts list
		self.updating_prompts = True
		self.prompts.clear()
		self.prompts.addItems(self.cfg.string_prompts())
		self.updating_prompts = False
		# Create new batch record and save it
		self.batch = Batch(self.cfg.db)
		self.batch.prompt_id = self.cfg.prompt.id
		# Get batch settings
		self.batch.input_image = self.cfg.input_image = img_path
		self.batch.scheduler = self.cfg.scheduler = self.scheduler.value()
		self.batch.width = self.cfg.width = self.width.value()
		if self.cfg.width % 64 != 0:
			self.cfg.width = self.cfg.width - (self.cfg.width % 64)
			self.batch.width = self.cfg.width
		self.batch.height = self.cfg.height = self.height.value()
		if self.cfg.height % 64 != 0:
			self.cfg.height = self.cfg.height - (self.cfg.height % 64)
			self.batch.height = self.cfg.height
		self.batch.noise_strength = self.cfg.noise_strength = self.strength.value()
		self.batch.inference_steps = self.cfg.num_inference_steps = self.num_steps.value()
		self.batch.guidance_scale = self.cfg.guidance_scale = self.guidance.value()
		self.batch.num_copies = self.cfg.num_copies = self.num_copies.value()
		self.batch.seed = self.cfg.seed = int(self.seed_text.text())
		# Save current configuration before image generation
		self.cfg.save()
		self.cfg.display()
		self.batch.save()
		# Convert image path to image
		self.iimg = None
		if len(img_path) > 0:
			self.iimg = Image.open(img_path).convert("RGB")
		# Validations
		# TODO - If there's a non-random seed value but number of copies is not 1, should we warn/exit?
		# We are good to go - set up for process
		self.total = 0.0
		self.sd = self.get_server(self.server_type.value())
		self.copy_counter = 0
		self.generate_image()

	def generate_image(self):
		# Start image generation in separate thread
		self.worker = SDWorker()
		self.thread = QThread()
		self.worker.parent = self
		self.worker.batch_id = self.batch.id
		self.worker.finished.connect(self.image_generated)
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.generate)
		self.thread.start()

	def image_generated(self):
		self.thread.parent = None
		self.thread.exit(0)
		self.thread.quit()
		self.copy_counter +=1
		self.seeds.append(self.seed)
		self.file_index = len(self.files)
		self.files.append(self.file_name)
		# Save Image info
		di = DImg.Image(self.cfg.db)
		di.batch_id = self.batch.id
		di.path = self.file_name
		di.seed = self.seed
		di.nsfw = self.is_nsfw
		di.time_taken = self.time
		di.save()
		# Display image
		if not self.image.isVisible():
			self.image.setVisible(True)
		self.show_image()
		# Save prompt data
		self.cfg.save_generate_info(self.dtstr, self.is_nsfw, self.time, self.seed)
		# Garbage collect thread
		self.thread = None
		self.worker = None
		if self.copy_counter < self.cfg.num_copies:
			# Launch another image generation
			self.generate_image()
		else:
			# Finish batch
			self.update_batch_info()

	def update_batch_info(self):
		# Save final batch info
		self.batch.time_taken = self.total
		self.batch.save()
		# Show first image result and update UI
		self.show_image_controls()
		if len(self.files) <= 1:
			self.b_prev.setVisible(False)
			self.b_next.setVisible(False)
		elif len(self.files) >= 2:
			self.b_prev.setVisible(True)
			self.b_next.setVisible(True)
		# Show image
		self.setEnabled(True)
		# Done with copy loop
		print(f"Generated {self.cfg.num_copies} images")

	def save_file(self, fn):
		path = QFileDialog.getSaveFileName()
		if path[0]:
			img = Image.open(fn)
			img.save(path)

	def show_image_controls(self, show=True):
		self.b_prev.setVisible(show)
		self.b_next.setVisible(show)
		self.image.setVisible(show)
		self.seed_lbl.setVisible(show)
		self.img_seed.setVisible(show)
		self.lbl_images.setVisible(show)
		self.b_del.setVisible(show)
		self.b_edit.setVisible(show)

	def show_image(self):
		# Image
		path = self.files[self.file_index]
		self.image.setPixmap(QPixmap(path))
		# Image count
		self.lbl_images.setText(f'Images: {self.file_index+1} / {len(self.files)}')
		# Seed
		seed = self.seeds[self.file_index]
		self.img_seed.setText(f'{seed}')

	def previous_image(self):
		if self.file_index > 0:
			self.file_index -= 1
			if self.file_index == 0:
				self.b_prev.setVisible(False)
			# Enable Next button if it was disabled
			if not self.b_next.isVisible():
				self.b_next.setVisible(True)
			self.show_image()

	def next_image(self):
		if self.file_index != len(self.files) - 1:
			self.file_index += 1
			if self.file_index == len(self.files) - 1:
				self.b_next.setVisible(False)
			# Enable Previous button if it was disabled
			if not self.b_prev.isVisible():
				self.b_prev.setVisible(True)
			self.show_image()

	def delete_image(self):
		file = self.files[self.file_index]
		if not self.delete_file(file):
			return
		# Clean up
		self.files.remove(file)
		self.seeds.pop(self.file_index)
		# If there are no more images, hide image part
		if len(self.files) == 0:
			self.file_index = -1
			self.show_image(False)
			self.count.set(f'Number of images: 0')
			return
		elif len(self.files) == 1:
			# Onlye one image, show it but disable buttons
			self.file_index = 0
			self.b_prev.setVisible(False)
			self.b_next.setVisible(False)
		else:
			# Change pointer to the next one
			if self.file_index != 0:
				self.file_index -= 1
		self.show_image()

	def send_to_editor(self):
		file = self.files[self.file_index]
		image = Image.open(file)
		self.editor_tab.load_image(image)