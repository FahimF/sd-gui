from tools.config import Config
from datetime import datetime
import numpy as np
import os
import time
from data.image import Image
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QMessageBox, QWidget
from tools.sd_engine import SDEngine
from server import SDServer

class SDWorker(QObject):
	finished = pyqtSignal()
	parent = None

	@pyqtSlot()
	def generate(self):
		cfg = self.parent.cfg
		start = time.time()
		# Generate an image using engine
		image, self.parent.is_nsfw, self.parent.seed = self.parent.sd.generate(cfg.prompt.prompt, cfg.width, cfg.height, cfg.seed,
			cfg.guidance_scale, self.parent.iimg, cfg.noise_strength)
		end = time.time()
		self.parent.time = end - start
		self.parent.total += self.parent.time
		if self.parent.is_nsfw:
			print("NSFW image detected!")
		else:
			self.parent.dtstr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
			self.parent.file_name = f"output/sample_{self.parent.dtstr}.png"
			# Save image
			image.save(self.parent.file_name)
			print(f"Saved image to: {self.parent.file_name}")
		# Console output
		print(f"Time taken: {self.parent.time}s")
		self.finished.emit()

class BaseTab(QWidget):
	editor_tab = None

	def __init__(self, cfg: Config):
		super(BaseTab, self).__init__()
		self.cfg = cfg

	def delete_file(self, file: str, confirm: bool = True) -> bool:
		print(f'Will delete: {file}')
		ret = QMessageBox(QMessageBox.Question, 'Are you sure?', f'This will delete {file} and associated data. '
			f'Do you want to proceed?', QMessageBox.Yes | QMessageBox.No)
		if ret == QMessageBox.No:
			return False
		os.remove(file)
		print(f"Deleted image: {file}")
		# Delete prompt file, if it exists
		fn = os.path.splitext(file)[0]
		pf = fn + ".json"
		if os.path.exists(pf):
			os.remove(pf)
			print(f"Deleted prompt: {pf}")
		# Delete file info from DB
		img = Image(self.cfg.db)
		img.delete(file)

	def get_texture(self):
		SIZE = 512
		Z = np.zeros((SIZE, SIZE), dtype=np.uint8)
		return np.stack([Z, Z, Z, Z], axis=2)

	def get_server(self, type: str):
		if type == 'local':
			return SDEngine(self.cfg.type, self.cfg.scheduler, self.cfg.num_inference_steps)
		else:
			addr = self.server_address.text()
			return SDServer(addr, self.cfg.scheduler, self.cfg.num_inference_steps)