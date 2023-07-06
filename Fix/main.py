import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal

from gui import Ui_MainWindow
from core import core_run


class Worker(QThread):
    signal = pyqtSignal(str)

    def __init__(self, input_file, output_file):
        super(Worker, self).__init__()
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        core_run(self.input_file, self.output_file, self.signal)
        self.signal.emit("Background task running...")  # emit signal when task is done


class MainWindow(QMainWindow, Ui_MainWindow):
	
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.output_file_btn.clicked.connect(self.on_output_clicked)
        self.input_file_btn.clicked.connect(self.on_input_clicked)
        self.run_btn.clicked.connect(self.on_run_clicked)

    def on_output_clicked(self):
        self.output_file, _ = QFileDialog.getSaveFileName(self, 'Save file')
        if not os.path.exists(self.output_file):
            open(self.output_file, 'a').close()
        print("Selected output file: ", self.output_file)

    def on_input_clicked(self):
        self.input_file, _ = QFileDialog.getOpenFileName(self, 'Open file')
        print("Selected input file: ", self.input_file)

    def on_run_clicked(self):
        self.worker = Worker(self.input_file, self.output_file)
        self.worker.signal.connect(self.on_worker_signal)
        self.worker.start()
        print("Worker started")

    def on_worker_signal(self, message):
    	self.console_plain_text_edit.setPlainText(message)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
