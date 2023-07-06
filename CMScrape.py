#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:33 2021

@author: mat
"""
import getopt
import os.path
import sys

from graphicCMS import UiMainWindow, UIpreferences
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QAction, QMessageBox
from PyQt5.QtCore import pyqtSignal

from multiProcess import *


"""
CMScrape is a scraping project with the objective to facilitate the use of CardMarket
when tracking prices of all kind of collectibles.
Find a full documentation here :
https://github.com/DrankRock/CMScrape
"""

TIMEOUT = 10
MAXTHREADS = 50


def help_me():
    print("-- CardMarket Scraper --")
    print('usage: CMscrape.py -i <input file or link> -o <outputfile> -s <stat_file(optional)>')
    print("Precisions about the results :")
    print(" _____________________")
    print("|     minCondition    |")
    print("|_____________________|")
    print("| None = Poor         |")
    print("| 6    = Played       |")
    print("| 5    = Light Played |")
    print("| 4    = Good         |")
    print("| 3    = Excellent    |")
    print("| 2    = Near Mint    |")
    print("| 1    = Mint         |")
    print("|_____________________|")
    print("|      language       |")
    print("|_____________________|")
    print("| None = None         |")
    print("| 1    = English      |")
    print("| 2    = French       |")
    print("| 3    = German       |")
    print("| 4    = Spanish      |")
    print("| 5    = Italian      |")
    print("| 6    = S-Chinese    |")
    print("| 7    = Japanese     |")
    print("| 8    = Portuguese   |")
    print("| 9    = Russian      |")
    print("| 10   = Korean       |")
    print("| 11   = T-Chinese    |")
    print("| 12   = Dutch        |")
    print("| 13   = Polish       |")
    print("| 14   = Czech        |")
    print("| 15   = Hungarian    |")
    print("|_____________________|")


# =############################################################=#
# ---------------------- CSV SORT FILE ----------------------- #

# Sorts the lines contained in a csv in alphabetical order
def csv_sort_file(file):
    with open(file, 'r') as to_sort:
        to_sort_lines = to_sort.read().splitlines()
        to_sort_lines.sort()
        to_sort.close()

    with open(file, 'w') as out:
        # print(separator, file=out)
        for i in range(len(to_sort_lines)):
            print(to_sort_lines[i], file=out)


# =############################################################=#
# ----------------------- WORKER SIGNAL ---------------------- ####
# The worker part is necessary to launch the GUI without stopping #
# the functional core. Freezes are to expect without this      ####
class WorkerSignals(QtCore.QObject):
    progress = pyqtSignal(int)
    end = pyqtSignal(int, int)
    console = pyqtSignal(str)


# =############################################################=#
# ------------------------ WORKER CLASS ---------------------- #
# I followed https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
# This tutorial. To avoid pyqt5 freezes.
class Worker(QtCore.QRunnable):
    def __init__(self, chosen_file_lbl, chosen_out_lbl, chosen_stat_lbl, n_threads, n_proxies_threads, n_proxy,
                 proxy_file, use_proxy_file, check_proxy_file, no_proxies_max, check_top_sellers, n_top_sellers, name_top_seller):
        super(Worker, self).__init__()
        # run's variables
        self.chosen_in = chosen_file_lbl
        self.chosen_out = chosen_out_lbl
        self.chosen_stat = chosen_stat_lbl
        self.n_threads = n_threads
        self.n_proxies_threads = n_proxies_threads
        self.n_proxy = n_proxy
        self.proxy_file = proxy_file
        self.use_proxy_file = use_proxy_file
        self.check_proxy_file = check_proxy_file
        self.no_proxies_max = no_proxies_max
        self.check_top_sellers = check_top_sellers
        self.n_top_sellers = n_top_sellers
        self.name_top_seller = name_top_seller

        self.signals = WorkerSignals()

    def run(self):
        if self.chosen_in == "No file chosen":
            self.signals.console.emit("[ERROR]\nPlease Chose an input file before running.")
        else:
            isOut = False
            isStat = False
            inFile = self.chosen_in
            if self.chosen_out != "No file chosen":
                isOut = self.chosen_out
            if self.chosen_stat != "No file chosen":
                isStat = self.chosen_stat
            if isOut == False and isStat == False:
                self.signals.console.emit("[WARNING]\nYou did not choose any type of output.")
            multiProcess(inFile, self.n_threads, self.n_proxies_threads, self.n_proxy, isOut, isStat, self.proxy_file,
                         self.use_proxy_file, self.check_proxy_file, self.no_proxies_max, self.check_top_sellers,
                         self.n_top_sellers, self.name_top_seller , self.signals)


# =############################################################=#
# --------------------- PREFERENCE DIALOG -------------------- #

class PreferencesDialog(QtWidgets.QDialog, UIpreferences):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setup_ui(self)
        self.add_btn.clicked.connect(self.add_button_data)
        self.cancel_btn.clicked.connect(self.cancel_button_data)

    def add_button_data(self):
        self.accept()

    def cancel_button_data(self):
        self.reject()

    def get_data(self):
        return self.get_parameters()

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Q:
            self.close()


# =############################################################=#
# ------------------------ MAIN WINDOW ----------------------- #

class MainWindow(QtWidgets.QMainWindow, UiMainWindow):
    def _createMenuBar(self):
        # Actions of actions
        def quit_triggered():
            sys.exit(1)

        def about_triggered():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            text = "This project was developed by\n- DrankRock -"
            msg.setInformativeText(text)
            msg.setWindowTitle("About")
            msg.exec_()

        def preferences_triggered():
            dialog = PreferencesDialog(self)
            dialog.set_parameters(self.n_proxies_threads, self.n_proxy, self.n_threads, self.proxy_file_path,
                                  self.use_proxy_file_chk, self.check_proxy_file_chk, self.use_top_sellers_chk,
                                  self.n_top_sellers, self.name_top_seller)
            result = dialog.exec_()
            if result == dialog.Accepted:
                resultList = dialog.get_data()
                self.n_proxies_threads = resultList[0]
                self.n_proxy = resultList[1]
                self.n_threads = resultList[2]
                self.proxy_file_path = resultList[3]
                self.use_proxy_file_chk = resultList[4]
                self.check_proxy_file_chk = resultList[5]
                self.use_top_sellers_chk = resultList[6]
                self.n_top_sellers = resultList[7]
                self.name_top_seller = resultList[8]
                if self.n_threads > 50:
                    self.n_threads = 50
                    print("Number of thread can't be over 50, automatically maxed to 50.")
                if self.n_proxies_threads > 50:
                    self.n_proxies_threads = 50
                    print("Number of thread can't be over 50, automatically maxed to 50.")
                self.console_disp.setPlainText(
                    "Number of Proxies is now : {}, checked on {} threads\n\
                    A proxy file is used : {} - proxy file needs checking : {}\n\
                    If a proxy_file is used, its path is :\"{}\"\n\n\
                    Number of Threads for scraping is now : {}\nSaving the top {} sellers : {} in file {} ".format(
                        self.n_proxy, self.n_proxies_threads, self.use_proxy_file_chk, self.check_proxy_file_chk,
                        self.proxy_file_path, self.n_threads, self.n_top_sellers, self.use_top_sellers_chk, self.name_top_seller)
                )
                with open('.cmscrape', 'w') as f:
                    f.write(
                        "'ProxiesThreads' : {}\n'Threads' : {}\n'Proxies' : {}\n'Proxy_file_path' : {}\n"
                        "'use_proxy_file' : {}\n'check_proxy_file' : {}\n'InputFolder' : {}\n'OutputFolder' : {}\n"
                        "'StatFolder' : {}\n'no_proxies_max' : {}\n'use_top_sellers_chk' : {}\n'n_top_sellers' : {}\n"
                        "'name_top_seller' : {}".format(
                            self.n_proxies_threads, self.n_threads, self.n_proxy, self.proxy_file_path,
                            self.use_proxy_file_chk, self.check_proxy_file_chk, self.inputFolderPath,
                            self.outputFolderPath, self.statFolderPath, self.no_proxies_max, self.use_top_sellers_chk,
                            self.n_top_sellers, self.name_top_seller)
                    )

        menuBar = self.menuBar()

        # Actions
        # about
        self.about_action = QAction("&About", self)
        self.about_action.setShortcut("Ctrl+B")
        self.about_action.triggered.connect(about_triggered)

        # help
        self.helpAction = QAction("&Help", self)
        self.helpAction.setShortcut("Ctrl+H")

        # preferences
        self.preferencesAction = QAction("&Preferences", self)
        self.preferencesAction.setShortcut("Ctrl+P")
        self.preferencesAction.triggered.connect(preferences_triggered)

        # quit
        self.quitAction = QAction("&Quit", self)
        self.quitAction.setShortcut("Ctrl+Q")
        self.quitAction.triggered.connect(quit_triggered)

        # Settings menu
        settingsMenu = menuBar.addMenu("&Settings")
        settingsMenu.addAction(self.preferencesAction)

        # Help menu
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.helpAction)
        helpMenu.addAction(self.about_action)
        helpMenu.addAction(self.quitAction)

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.inputFileChosen = None
        self.outputFileChosen = None
        self.fileDialog = None
        self.statFileChosen = None
        self.setupUi(self)
        self.n_threads = 0
        self.n_proxy = 0
        self.n_proxies_threads = 0
        self.proxy_file_path = ''
        self.use_proxy_file_chk = False
        self.check_proxy_file_chk = False
        self.inputFolderPath = ''
        self.outputFolderPath = ''
        self.statFolderPath = ''
        self.no_proxies_max = 0
        self.use_top_sellers_chk = False
        self.n_top_sellers = 0
        self.name_top_seller = ""
        self.threadpool = QtCore.QThreadPool()
        self.loadConfig()
        if "--no-proxies" in sys.argv:
            self.no_proxies_max = sys.argv[sys.argv.index("--no-proxies") + 1]
            self.updateConfig(4, self.no_proxies_max)
        if self.no_proxies_max == "True":
            self.proxy_btn.setText("Without Proxies (limited to 30/min)")
        else:
            self.proxy_btn.setText("Using proxies (up to 1500/min but needs loading)")
        self._createMenuBar()
        self.input_btn.clicked.connect(self.inputFileDialog)
        self.stat_btn.clicked.connect(self.stat_file_dialog)
        self.output_btn.clicked.connect(self.output_file_dialog)
        self.run_btn.clicked.connect(self.run)
        # self.proxy_btn.clicked.connect(self.proxyChoice)

        self.DEBUG = False

    def updateConfig(self, to_modify, value):
        if to_modify == 1:
            self.inputFolderPath = value
        elif to_modify == 2:
            self.outputFolderPath = value
        elif to_modify == 3:
            self.statFolderPath = value
        elif to_modify == 4:
            self.no_proxies_max = value
        with open('.cmscrape', 'w') as f:
            f.write(
                "'ProxiesThreads' : {}\n'Threads' : {}\n'Proxies' : {}\n'Proxy_file_path' : {}\n'use_proxy_file' : {}\n"
                "'check_proxy_file' : {}\n'InputFolder' : {}\n'OutputFolder' : {}\n'StatFolder' : {}\n"
                "'no_proxies_max' : {}\n'use_top_sellers_chk' : {}\n'n_top_sellers' : {}\n'name_top_seller' : {}".format(
                    self.n_proxies_threads, self.n_threads, self.n_proxy, self.proxy_file_path, self.use_proxy_file_chk,
                    self.check_proxy_file_chk, self.inputFolderPath, self.outputFolderPath, self.statFolderPath,
                    self.no_proxies_max, self.use_top_sellers_chk, self.n_top_sellers, self.name_top_seller)
            )

    def proxyChoice(self):
        if self.proxy_btn.text() == "Without Proxies (limited to 30/min)":
            self.proxy_btn.setText("Using proxies (up to 1500/min but needs loading)")
            self.updateConfig(4, "False")
        else:
            self.proxy_btn.setText("Without Proxies (limited to 30/min)")
            self.updateConfig(4, "True")

    def loadConfig(self):
        if os.path.exists('.cmscrape'):
            with open('.cmscrape', 'r') as openRead:
                settings = openRead.read().splitlines()
            openRead.close()
            for line in settings:
                split_line = line.split(" : ")
                if split_line[0] == "'Threads'":
                    self.n_threads = int(split_line[1])
                    if self.n_threads > 50:
                        self.n_threads = 50
                        print("Number of thread can't be over 50, automatically maxed to 50.")
                # PROXIES
                if split_line[0] == "'Proxies'":
                    self.n_proxy = int(split_line[1])
                if split_line[0] == "'no_proxies_max'":
                    self.no_proxies_max = str(split_line[1])
                if split_line[0] == "'ProxiesThreads'":
                    self.n_proxies_threads = int(split_line[1])
                    if self.n_proxies_threads > 50:
                        self.n_proxies_threads = 50
                        print("Number of thread can't be over 50, automatically maxed to 50.")
                if split_line[0] == "'Proxy_file_path'":
                    self.proxy_file_path = str(split_line[1])
                if split_line[0] == "'use_proxy_file'":
                    if split_line[1] == 'True':
                        self.use_proxy_file_chk = True
                    else:
                        self.use_proxy_file_chk = False
                if split_line[0] == "'check_proxy_file'":
                    if split_line[1] == 'True':
                        self.check_proxy_file_chk = True
                    else:
                        self.check_proxy_file_chk = False
                if split_line[0] == "'use_top_sellers_chk'":
                    if split_line[1] == 'True':
                        self.use_top_sellers_chk = True
                    else:
                        self.use_top_sellers_chk = False
                if split_line[0] == "'n_top_sellers'":
                    self.n_top_sellers = int(split_line[1])
                #  I/O
                if split_line[0] == "'InputFolder'":
                    self.inputFolderPath = str(split_line[1])
                if split_line[0] == "'OutputFolder'":
                    self.outputFolderPath = str(split_line[1])
                if split_line[0] == "'StatFolder'":
                    self.statFolderPath = str(split_line[1])
                if split_line[0] == "'name_top_seller'":
                    if len(split_line[1]) < 1:
                        self.name_top_seller = ""
                    else :
                        self.name_top_seller = split_line[1]

            if self.n_threads > MAXTHREADS or self.n_proxies_threads > MAXTHREADS:
                print("ERROR : Can't run with over 50 Proxies. Please modify them using CTRL+P")
        else:
            with open('.cmscrape', 'w') as f:
                self.n_threads = 40
                self.n_proxy = 50
                self.n_proxies_threads = 50
                self.proxy_file_path = ''
                self.use_proxy_file_chk = False
                self.check_proxy_file_chk = False
                self.inputFolderPath = ''
                self.outputFolderPath = ''
                self.statFolderPath = ''
                self.no_proxies_max = "True"
                self.use_top_sellers_chk = False
                self.n_top_sellers = 0
                self.name_top_seller = ""
                f.write(
                    "'ProxiesThreads' : {}\n'Threads' : {}\n'Proxies' : {}\n'Proxy_file_path' : {}\n"
                    "'use_proxy_file' : {}\n'check_proxy_file' : {}\n'InputFolder' : {}\n'OutputFolder' : {}\n"
                    "'StatFolder' : {}\n'no_proxies_max' : {}\n'use_top_sellers_chk' : {}\n'n_top_sellers' : {}\n"
                    "'name_top_seller' : {}".format(
                        self.n_proxies_threads, self.n_threads, self.n_proxy, self.proxy_file_path,
                        self.use_proxy_file_chk,
                        self.check_proxy_file_chk, self.inputFolderPath, self.outputFolderPath, self.statFolderPath,
                        self.no_proxies_max, self.use_top_sellers_chk, self.n_top_sellers, self.name_top_seller)
                )

    def inputFileDialog(self):
        self.fileDialog = QFileDialog()
        options = self.fileDialog.Options()
        options |= self.fileDialog.DontUseNativeDialog
        # options |= self.fileDialog.setDefaultSuffix(self.fileDialog, "csv")
        # filename, _ = self.fileDialog.getOpenFileName(self, 'Open File', '.')
        fileName, _ = self.fileDialog.getOpenFileName(self, "Chose desired input file", self.inputFolderPath,
                                                      "*", options=options)
        if fileName:
            # print(fileName)
            self.inputFileChosen = fileName
            self.chosen_file_lbl.setText(str(fileName))
            self.chosen_file_lbl.adjustSize()

    def output_file_dialog(self):
        self.fileDialog = QFileDialog()
        options = self.fileDialog.Options()
        options |= self.fileDialog.DontUseNativeDialog
        # options |= self.fileDialog.setDefaultSuffix(self.fileDialog, "csv")
        # filename, _ = self.fileDialog.getOpenFileName(self, 'Open File', '.')
        file_name, _ = self.fileDialog.getSaveFileName(self, "Chose or create desired output file",
                                                       self.outputFolderPath, "csv Files (*.csv)", options=options)
        if file_name:
            # print(file_name)
            self.outputFileChosen = file_name
            self.chosen_out_lbl.setText(str(file_name))
            self.chosen_out_lbl.adjustSize()

    def stat_file_dialog(self):
        self.fileDialog = QFileDialog()
        options = self.fileDialog.Options()
        options |= self.fileDialog.DontUseNativeDialog
        # options |= self.fileDialog.setDefaultSuffix(self.fileDialog, "csv")
        # filename, _ = self.fileDialog.getOpenFileName(self, 'Open File', '.')
        file_name, _ = self.fileDialog.getSaveFileName(self, "Chose or create desired statistics file",
                                                       self.statFolderPath, "csv Files (*.csv)", options=options)
        if file_name:
            # print(file_name)
            self.statFileChosen = file_name
            self.chosen_stat_lbl.setText(str(file_name))
            self.chosen_stat_lbl.adjustSize()

    def update_progress(self, n):
        if n == -1:
            # Proxies !
            self.progress_bar.setStyleSheet("QProgressBar{\n"
                                            "    border: 2px solid rgb(19, 148, 195);\n"
                                            "    border-radius: 5px;\n"
                                            "    text-align: center\n"
                                            "}\n"
                                            "\n"
                                            "QProgressBar::chunk {\n"
                                            "    background-color: rgb(56, 188, 236);\n"
                                            "    width: 10px;\n"
                                            "}")
        elif n == -2:
            # Scraper !
            self.progress_bar.setStyleSheet("QProgressBar{\n"
                                            "    border: 2px solid rgb(139, 28, 59);\n"
                                            "    border-radius: 5px;\n"
                                            "    text-align: center\n"
                                            "}\n"
                                            "\n"
                                            "QProgressBar::chunk {\n"
                                            "    background-color: rgb(172, 35, 72);\n"
                                            "    width: 10px;\n"
                                            "}")
        else:
            self.progress_bar.setValue(n)

    def update_console(self, to_print):
        self.console_disp.setPlainText(to_print)
        if self.DEBUG:
            print(to_print)
        QtWidgets.QApplication.processEvents()

    def endQMessageBox(self, worked, total):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText("Successfully scraped {} out of {} links.".format(worked, total))
        msg.setWindowTitle("CMScrape - Info")
        msg.exec_()

    def run(self):
        if self.chosen_file_lbl.text() != "No file chosen":
            self.updateConfig(1, os.path.dirname(self.chosen_file_lbl.text()))
        if self.chosen_out_lbl.text() != "No file chosen":
            self.updateConfig(2, os.path.dirname(self.chosen_out_lbl.text()))
        if self.chosen_stat_lbl.text() != "No file chosen":
            self.updateConfig(3, os.path.dirname(self.chosen_stat_lbl.text()))
        if self.n_threads > MAXTHREADS or self.n_proxies_threads > MAXTHREADS:
            print("ERROR : Can't run with over 50 Proxies. Please modify them using CTRL+P")
        else:
            worker = Worker(self.chosen_file_lbl.text(), self.chosen_out_lbl.text(), self.chosen_stat_lbl.text(),
                            self.n_threads, self.n_proxies_threads, self.n_proxy, self.proxy_file_path,
                            self.use_proxy_file_chk, self.check_proxy_file_chk, self.no_proxies_max,
                            self.use_top_sellers_chk, self.n_top_sellers, self.name_top_seller)
            self.threadpool.start(worker)
            worker.signals.progress.connect(self.update_progress)
            worker.signals.console.connect(self.update_console)
            worker.signals.end.connect(self.endQMessageBox)


# =############################################################=#
# ------------------------- GRAPHIC -------------------------- #

def graphic():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


# =############################################################=#
# --------------------------- MAIN --------------------------- #

def main(argv):
    # credit : https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    input_file = ''
    output_file = ''
    stat_file = ''
    sortOut = False
    useOut = False
    useStat = False
    graphic_launch = True  # default launching mode
    termLaunch = False
    nCores = 1
    n_threadsNP = 0
    try:
        opts, args = getopt.getopt(argv, "c:ghi:to:s:", ["ifile=", "ofile=", "stats=", "cores=", "no-proxies="])
    except getopt.GetoptError:
        print('usage: pokeScrap.0.2.py -i <input file or link> -o <outputfile> -s <stat_file(optional)>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-g':
            # print("Launch graphic version...")
            graphic_launch = True
        if opt == '-t':
            # print("Launch Terminal version")
            termLaunch = True
        if opt == '-h':
            help_me()
            sys.exit()
        elif opt in ("-i", "--infile"):
            input_file = arg
        elif opt in ("-o", "--outfile"):
            output_file = arg
            useOut = True
        elif opt in ("-s", "--stats"):
            stat_file = arg
            useStat = True
        elif opt in ("-c", "--cores"):
            nCores = arg
        elif opt in "--no-proxies":
            n_threadsNP = arg
    for opt in opts:
        if opt in ("-so", "--sort-outfile"):
            sortOut = True

    if input_file == '' and graphic_launch == False:
        print('An input is needed !')
        print('Type "CMscrapepy -h" for more infos')
        sys.exit(2)

    args = [input_file]
    if output_file != '':
        args.append(output_file)
    if stat_file != '':
        args.append(stat_file)
    else:
        graphic()


if __name__ == "__main__":
    main(sys.argv[1:])
