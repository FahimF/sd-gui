import sys
import pathlib

from tools.config import Config
from PyQt5.QtCore import Qt, pyqtSlot, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QIcon, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QSplitter, QPlainTextEdit
from queue import Queue
from ui.gallery_tab import GalleryTab
from ui.generator_tab import GeneratorTab
from ui.editor_tab import EditorTab
from ui.prompts_tab import PromptsTab

class LogStream(object):
    save_stdout = sys.stdout
    save_stderr = sys.stderr

    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)
        self.save_stdout.write(text)

    def flush(self):
        pass

class LogReceiver(QObject):
    signal = pyqtSignal(str)

    def __init__(self, queue, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.queue = queue

    @pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.signal.emit(text)

class Window(QMainWindow):
    prev_line = ''

    def __init__(self):
        super(Window, self).__init__()
        self.cfg = Config()
        # System color changes
        palette = QPalette()
        palette.setColor(QPalette.Highlight, QColor.fromRgb(2, 113, 177))
        QApplication.setPalette(palette)
        # UI elements
        self.setWindowTitle("Stable Diffusion")
        self.asset_path = pathlib.Path(__file__).parent / 'assets'
        self.move(0, 0)
        # self.setGeometry(0, 0, 1020, 1150)
        self.resize(1150, 1150)
        self.setup()
        self.show()

    def setup(self):
        # Main splitter
        main_split = QSplitter(Qt.Vertical)
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(0, 0, 0, 0)
        self.tabGen = GeneratorTab(self.cfg)
        self.tabGen.setContentsMargins(0, 0, 0, 0)
        self.tabs.addTab(self.tabGen, "Generate Images")
        self.tabEditor = EditorTab(self.cfg)
        self.tabEditor.setContentsMargins(0, 0, 0, 0)
        self.tabs.addTab(self.tabEditor, "Edit Images")
        self.tabPrompts = PromptsTab(self.cfg)
        self.tabPrompts.setContentsMargins(0, 0, 0, 0)
        self.tabs.addTab(self.tabPrompts, "Prompts")
        self.tabGallery = GalleryTab(self.cfg)
        self.tabGallery.setContentsMargins(0, 0, 0, 0)
        self.tabs.addTab(self.tabGallery, "Gallery")
        main_split.addWidget(self.tabs)
        # Log area
        self.logs = QPlainTextEdit()
        self.logs.setContentsMargins(0, 0, 0, 0)
        self.logs.setReadOnly(True)
        main_split.addWidget(self.logs)
        main_split.setSizes([1150, 50])
        main_split.setStretchFactor(23, 1)
        self.setCentralWidget(main_split)
        # Pass editor to other tabs which need it
        self.tabGen.editor_tab = self.tabEditor
        self.tabGallery.editor_tab = self.tabEditor

    @pyqtSlot(str)
    def log_text(self, line):
        self.logs.moveCursor(QTextCursor.End)
        if self.prev_line.endswith('it/s]') or self.prev_line.endswith('s/it]'):
            if line.endswith('it/s]') or line.endswith('s/it]'):
                # Replace last line and move on
                cursor = self.logs.textCursor()
                cursor.select(QTextCursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deletePreviousChar()
        # Insert new line
        self.logs.insertPlainText(line)
        self.prev_line = line

if __name__ == '__main__':
    # Create Queue and redirect system output to this queue
    queue = Queue()
    # sys.stdout = sys.stderr = LogStream(queue)
    # The app
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str('assets/icon.png')))
    win = Window()
    # Create thread that will listen on the other end of the queue, and send the text to log console
    thread = QThread()
    receiver = LogReceiver(queue)
    receiver.signal.connect(win.log_text)
    receiver.moveToThread(thread)
    thread.started.connect(receiver.run)
    thread.start()
    # Start app
    sys.exit(app.exec_())
