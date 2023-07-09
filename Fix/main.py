import os
import csv
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from PyQt5.QtCore import QThread, pyqtSignal

from gui import Ui_MainWindow
from core import core_run

default_button_stylesheet = "background-color: white; color: black;"
selected_button_stylesheet = "background-color: green; color: white;"

def write_list_of_lists_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "TCG"
            ,"Type"
            ,"Expansion"
            ,"Number"
            ,"Name"
            ,"Min Price"
            ,"Trending Price"
            ,"Mean 30 days"
            ,"Mean 7 days"
            ,"Mean 1 day"
            ,"language",
            "sellerCountry",
            "sellerType",
            "minCondition",
            "isSigned",
            "isFirstEd",
            "isPlayset",
            "isAltered",
            "isReverseHolo",
            "isFoil",
            "URL"
        ])
        for row in data:
            writer.writerow(row)

class Worker(QThread):
    signal = pyqtSignal(str)
    list_signal = pyqtSignal(list)


    def __init__(self, input_file, output_file):
        super(Worker, self).__init__()
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        core_run(self.input_file, self.output_file, self.signal, self.list_signal)

    def stop(self):
        self._isRunning = False


class MainWindow(QMainWindow, Ui_MainWindow):
	
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.output_file_btn.clicked.connect(self.on_output_clicked)
        self.input_file_btn.clicked.connect(self.on_input_clicked)
        self.run_btn.clicked.connect(self.on_run_clicked)
        self.reset()

    def reset(self):
        self.output_file = ""
        self.input_file = ""

        self.output_file_btn.setStyleSheet(default_button_stylesheet)
        self.input_file_btn.setStyleSheet(default_button_stylesheet)
        self.run_btn.setEnabled(False)
        self.on_worker_signal("Please select an input file\nPlease select an output file")

    def on_output_clicked(self):
        self.output_file, _ = QFileDialog.getSaveFileName(self, 'Save file')
        if not os.path.exists(self.output_file):
            open(self.output_file, 'a').close()
        # print("Selected output file: ", self.output_file)
        if self.output_file != "":
            self.output_file_btn.setStyleSheet(selected_button_stylesheet)
            if self.input_file != "":
                self.run_btn.setEnabled(True)
                self.on_worker_signal("Press run to continue\n          |          \n          |          \n          V          ")
            else:
                self.on_worker_signal("Please select an input file")

    def on_input_clicked(self):
        self.input_file, _ = QFileDialog.getOpenFileName(self, 'Open file')
        # print("Selected input file: ", self.input_file)
        if self.input_file != "":
            self.input_file_btn.setStyleSheet(selected_button_stylesheet)
            if self.output_file != "":
                self.run_btn.setEnabled(True)
                self.on_worker_signal("Press run to continue\n          |          \n          |          \n          V          ")
            else:
                self.on_worker_signal("Please select an output file")

    def on_run_clicked(self):
        self.worker = Worker(self.input_file, self.output_file)
        self.worker.signal.connect(self.on_worker_signal)
        self.worker.list_signal.connect(self.on_worker_list_signal)
        self.worker.start()
        # print("Worker started")

    def on_worker_signal(self, message):
    	self.console_plain_text_edit.setPlainText(message)

    def on_worker_list_signal(self, _list):
        # the worker has ended
        write_list_of_lists_to_csv(_list, self.output_file)
        self.worker.stop()
        self.execution_ended()
        self.reset()

    def execution_ended(self):
        msg_box = QMessageBox()
        msg_box.setText("Execution complete")
        msg_box.addButton(QMessageBox.Ok)
        result = msg_box.exec()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
