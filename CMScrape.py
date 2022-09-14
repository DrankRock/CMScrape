#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:33 2021

@author: mat
"""
import requests, re, sys, getopt, os, traceback, multiprocessing, time, csv
import os.path

from bs4 import BeautifulSoup
from graphicCMS import Ui_MainWindow, UI_Preferences
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication, QAction
from PyQt5.QtCore import pyqtSignal

from scrapers import *
from multiProcess import *

"""
CMScrape is a scraping project with the objective to facilitate the use of CardMarket
when tracking prices of all kind of collectibles.
Find a full documentation here :
https://github.com/DrankRock/CMScrape
"""

TIMEOUT = 10
MAXTHREADS = 50

def helpMe():
	print("-- CardMarket Scraper --")
	print('usage: CMscrape.py -i <input file or link> -o <outputfile> -s <statFile(optional)>')
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


#=############################################################=#
# ---------------------- CSV SORT FILE ----------------------- #

# Sorts the lines contained in a csv in alphabetical order
def csvSortFile(file):
	## We shall ignore the first line because it's the sep=,
	#[1:] # The separator will not be precised as LibreOffice doesn't read it
	with open(file, 'r') as toSort:
		# separator=toSort.readline().rstrip()
		toSortLines = toSort.read().splitlines()
		toSortLines.sort()
		toSort.close()

	with open(file, 'w') as out:
		# print(separator, file=out)
		for i in range(len(toSortLines)):
			print(toSortLines[i], file=out)

#=############################################################=#
# ----------------------- WORKER SIGNAL ---------------------- #

class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.

    console
    	string console display

    progress
        int use of the progressBar

    '''
    progress = pyqtSignal(int)
    end = pyqtSignal(int, int)
    console = pyqtSignal(str)

#=############################################################=#
# ------------------------ WORKER CLASS ---------------------- #
# I followed https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
# This tutorial. To avoid pyqt5 freezes.
class Worker(QtCore.QRunnable):
	'''
	Worker thread
	'''
	def __init__(self, chosenFileLbl, chosenOutLbl, chosenStatLbl, nThreads, nProxiesThreads, nProxy, proxyFile, useProxyFile, checkProxyFile, noProxiesMax):
		super(Worker, self).__init__()
		# run's variables
		self.chosenIn = chosenFileLbl
		self.chosenOut = chosenOutLbl
		self.chosenStat = chosenStatLbl
		self.nThreads = nThreads
		self.nProxiesThreads = nProxiesThreads
		self.nProxy = nProxy
		self.proxyFile = proxyFile
		self.useProxyFile = useProxyFile
		self.checkProxyFile = checkProxyFile
		self.noProxiesMax = noProxiesMax

		self.signals = WorkerSignals()

	def run(self):
		if self.chosenIn == "No file chosen":
			self.signals.console.emit("[ERROR]\nPlease Chose an input file before running.")
		else:
			isOut = False
			isStat = False
			inFile = self.chosenIn
			if self.chosenOut != "No file chosen":
				isOut = self.chosenOut
			if self.chosenStat != "No file chosen":
				isStat = self.chosenStat
			if isOut == False and isStat == False:
				self.signals.console.emit("[WARNING]\nYou did not choose any type of output.")
			multiProcess(inFile, self.nThreads, self.nProxiesThreads, self.nProxy, isOut, isStat, self.proxyFile, self.useProxyFile, self.checkProxyFile, self.noProxiesMax, self.signals)



#=############################################################=#
# --------------------- PREFERENCE DIALOG -------------------- #

class PreferencesDialog(QtWidgets.QDialog, UI_Preferences):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.addbtn.clicked.connect(self.addButtonData)
        self.cancelbtn.clicked.connect(self.cancelButtonData)

    def addButtonData(self):
        self.accept()

    def cancelButtonData(self):
        self.reject()

    def getData(self):
        return self.getParameters()

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Q:
        	self.close()

#=############################################################=#
# ------------------------ MAIN WINDOW ----------------------- #

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	def _createMenuBar(self):
		# Actions of actions
		def quitTriggered():
			sys.exit(1)
		def aboutTriggered():
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			text = "This project was developped by\n- DrankRock -"
			msg.setInformativeText(text)
			msg.setWindowTitle("About")
			msg.exec_()
		def preferencesTriggered():
			dialog = PreferencesDialog(self)
			dialog.setParameters(self.nProxiesThreads, self.nProxy,self.nThreads, self.proxyFilePath, self.useProxyFileChk, self.checkProxyFileChk)
			result = dialog.exec_()
			if result == dialog.Accepted:
				resultList = dialog.getData()
				self.nProxiesThreads = resultList[0]
				self.nProxy = resultList[1]
				self.nThreads = resultList[2]
				self.proxyFilePath = resultList[3]
				self.useProxyFileChk = resultList[4]
				self.checkProxyFileChk = resultList[5]
				if self.nThreads > 50:
					self.nThreads = 50
					print("Number of thread can't be over 50, automatically maxed to 50.")
				if self.nProxiesThreads > 50:
					self.nProxiesThreads = 50
					print("Number of thread can't be over 50, automatically maxed to 50.")
				self.consoleDisp.setPlainText("Number of Proxies is now : {}, checked on {} threads\nA proxy file is used : {} - proxy file needs checking : {}\nIf a proxyFile is used, its path is :\"{}\"\n\nNumber of Threads for scraping is now : {}".format(self.nProxy, self.nProxiesThreads, self.useProxyFileChk, self.checkProxyFileChk, self.proxyFilePath, self.nThreads))
				with open('.cmscrape','w') as f:
					f.write("'ProxiesThreads' : {}\n'Threads' : {}\n'Proxies' : {}\n'ProxyFilePath' : {}\n'useProxyFile' : {}\n'checkProxyFile' : {}\n'InputFolder' : {}\n'OutputFolder' : {}\n'StatFolder' : {}\n'noProxiesMax' : {}".format(self.nProxiesThreads, self.nThreads, self.nProxy,  self.proxyFilePath, self.useProxyFileChk, self.checkProxyFileChk, self.inputFolderPath, self.outputFolderPath, self.statFolderPath, self.noProxiesMax))

		menuBar = self.menuBar()

		# Actions
		## about
		self.aboutAction = QAction("&About", self)
		self.aboutAction.setShortcut("Ctrl+B")
		self.aboutAction.triggered.connect(aboutTriggered)

		## help
		self.helpAction = QAction("&Help", self)
		self.helpAction.setShortcut("Ctrl+H")

		## preferences
		self.preferencesAction = QAction("&Preferences", self)
		self.preferencesAction.setShortcut("Ctrl+P")
		self.preferencesAction.triggered.connect(preferencesTriggered)

		## quit
		self.quitAction = QAction("&Quit", self)
		self.quitAction.setShortcut("Ctrl+Q")
		self.quitAction.triggered.connect(quitTriggered)

		# Settings menu
		settingsMenu = menuBar.addMenu("&Settings")
		settingsMenu.addAction(self.preferencesAction)

		# Help menu
		helpMenu = menuBar.addMenu("&Help")
		helpMenu.addAction(self.helpAction)
		helpMenu.addAction(self.aboutAction)
		helpMenu.addAction(self.quitAction)


	def __init__(self, parent=None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.setupUi(self)
		self.nThreads = 0
		self.nProxy = 0
		self.nProxiesThreads = 0
		self.proxyFilePath = ''
		self.useProxyFileChk = False
		self.checkProxyFileChk = False
		self.inputFolderPath = ''
		self.outputFolderPath = ''
		self.statFolderPath = ''
		self.noProxiesMax = 0
		self.threadpool = QtCore.QThreadPool()
		self.loadConfig()
		if "--no-proxies"in sys.argv:
			self.noProxiesMax = sys.argv[sys.argv.index("--no-proxies")+1]
			self.updateConfig(4, self.noProxiesMax)
		if self.noProxiesMax == "True":
			self.proxyBtn.setText("Without Proxies (limited to 30/min)")
		else:
			self.proxyBtn.setText("Using proxies (up to 1500/min but needs loading)")
		self._createMenuBar()
		self.inputBtn.clicked.connect(self.inputFileDialog)
		self.statBtn.clicked.connect(self.statFileDialog)
		self.outputBtn.clicked.connect(self.outputFileDialog)
		self.runBtn.clicked.connect(self.run)
		self.proxyBtn.clicked.connect(self.proxyChoice)
		

		self.DEBUG = False

	def updateConfig(self, toModify, value):
		if toModify == 1:
			self.inputFolderPath = value
		elif toModify == 2:
			self.outputFolderPath = value
		elif toModify == 3:
			self.statFolderPath = value
		elif toModify == 4:
			self.noProxiesMax = value
		with open('.cmscrape','w') as f:
			f.write("'ProxiesThreads' : {}\n'Threads' : {}\n'Proxies' : {}\n'ProxyFilePath' : {}\n'useProxyFile' : {}\n'checkProxyFile' : {}\n'InputFolder' : {}\n'OutputFolder' : {}\n'StatFolder' : {}\n'noProxiesMax' : {}".format(self.nProxiesThreads, self.nThreads, self.nProxy,  self.proxyFilePath, self.useProxyFileChk, self.checkProxyFileChk, self.inputFolderPath, self.outputFolderPath, self.statFolderPath, self.noProxiesMax))
	
	def proxyChoice(self):
		if(self.proxyBtn.text() == "Without Proxies (limited to 30/min)"):
			self.proxyBtn.setText("Using proxies (up to 1500/min but needs loading)")
			self.updateConfig(4, "False")
		else :
			self.proxyBtn.setText("Without Proxies (limited to 30/min)")
			self.updateConfig(4, "True")

	def loadConfig(self):
		if os.path.exists('.cmscrape'):
			with open('.cmscrape', 'r') as openRead:
				settings = openRead.read().splitlines()
			openRead.close()
			for line in settings:
				split_line = line.split(" : ")
				if split_line[0] == "'Threads'":
					self.nThreads = int(split_line[1])
					if self.nThreads > 50:
						self.nThreads = 50
						print("Number of thread can't be over 50, automatically maxed to 50.")
			## PROXIES
				if split_line[0] == "'Proxies'":
					self.nProxy = int(split_line[1])
				if split_line[0] == "'noProxiesMax'":
					self.noProxiesMax = str(split_line[1])
				if split_line[0] == "'ProxiesThreads'":
					self.nProxiesThreads = int(split_line[1])
					if self.nProxiesThreads > 50:
						self.nProxiesThreads = 50
						print("Number of thread can't be over 50, automatically maxed to 50.")
				if split_line[0] == "'ProxyFilePath'":
					self.proxyFilePath = str(split_line[1])
				if split_line[0] == "'useProxyFile'":
					if split_line[1] == 'True':
						self.useProxyFileChk = True
					else:
						self.useProxyFileChk = False
				if split_line[0] == "'checkProxyFile'":
					if split_line[1] == 'True':
						self.checkProxyFileChk = True
					else:
						self.checkProxyFileChk = False
			## I/O
				if split_line[0] == "'InputFolder'":
					self.inputFolderPath = str(split_line[1])
				if split_line[0] == "'OutputFolder'":
					self.outputFolderPath = str(split_line[1])
				if split_line[0] == "'StatFolder'":
					self.statFolderPath = str(split_line[1])
			if self.nThreads>MAXTHREADS or self.nProxiesThreads>MAXTHREADS:
				print("ERROR : Can't run with over 50 Proxies. Please modify them using CTRL+P")
		else:
			with open('.cmscrape','w') as f:
				self.nThreads = 40
				self.nProxy = 50
				self.nProxiesThreads = 50
				self.proxyFilePath = ''
				self.useProxyFileChk = False
				self.checkProxyFileChk = False
				self.inputFolderPath = ''
				self.outputFolderPath = ''
				self.statFolderPath = ''
				self.noProxiesMax = "True"
				f.write("'ProxiesThreads' : {}\n'Threads' : {}\n'Proxies' : {}\n'ProxyFilePath' : {}\n'useProxyFile' : {}\n'checkProxyFile' : {}\n'InputFolder' : {}\n'OutputFolder' : {}\n'StatFolder' : {}\n'noProxiesMax' : {}".format(self.nProxiesThreads, self.nThreads, self.nProxy,  self.proxyFilePath, self.useProxyFileChk, self.checkProxyFileChk, self.inputFolderPath, self.outputFolderPath, self.statFolderPath, self.noProxiesMax))

	def inputFileDialog(self):
		self.fileDialog = QFileDialog()
		options = self.fileDialog.Options()
		options |= self.fileDialog.DontUseNativeDialog
		#options |= self.fileDialog.setDefaultSuffix(self.fileDialog, "csv")
		#filename, _ = self.fileDialog.getOpenFileName(self, 'Open File', '.')
		fileName, _ = self.fileDialog.getOpenFileName(self,"Chose desired input file",self.inputFolderPath,"Text Files (*.txt)", options=options)
		if fileName:
			# print(fileName)
			self.inputFileChosen = fileName
			self.chosenFileLbl.setText(str(fileName))
			self.chosenFileLbl.adjustSize()

	def outputFileDialog(self):
		self.fileDialog = QFileDialog()
		options = self.fileDialog.Options()
		options |= self.fileDialog.DontUseNativeDialog
		#options |= self.fileDialog.setDefaultSuffix(self.fileDialog, "csv")
		#filename, _ = self.fileDialog.getOpenFileName(self, 'Open File', '.')
		fileName, _ = self.fileDialog.getSaveFileName(self,"Chose or create desired output file",self.outputFolderPath,"csv Files (*.csv)", options=options)
		if fileName:
			# print(fileName)
			self.outputFileChosen = fileName
			self.chosenOutLbl.setText(str(fileName))
			self.chosenOutLbl.adjustSize()

	def statFileDialog(self):
		self.fileDialog = QFileDialog()
		options = self.fileDialog.Options()
		options |= self.fileDialog.DontUseNativeDialog
		#options |= self.fileDialog.setDefaultSuffix(self.fileDialog, "csv")
		#filename, _ = self.fileDialog.getOpenFileName(self, 'Open File', '.')
		fileName, _ = self.fileDialog.getSaveFileName(self,"Chose or create desired statistics file",self.statFolderPath,"csv Files (*.csv)", options=options)
		if fileName:
			# print(fileName)
			self.statFileChosen = fileName
			self.chosenStatLbl.setText(str(fileName))
			self.chosenStatLbl.adjustSize()

	def update_progress(self,n):
		if n == -1:
			# Proxies !
			self.progressBar.setStyleSheet("QProgressBar{\n"
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
			self.progressBar.setStyleSheet("QProgressBar{\n"
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
			self.progressBar.setValue(n)

	def update_console(self,toPrint):
		self.consoleDisp.setPlainText(toPrint)
		if self.DEBUG == True:
			print(toPrint)
		QtWidgets.QApplication.processEvents()

	def endQMessageBox(self, worked, total):
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setInformativeText("Successfully scraped {} out of {} links.".format(worked, total))
			msg.setWindowTitle("CMScrape - Info")
			msg.exec_()

	def run(self):
		if self.chosenFileLbl.text() != "No file chosen":
			self.updateConfig(1, os.path.dirname(self.chosenFileLbl.text()))
		if self.chosenOutLbl.text() != "No file chosen":
			self.updateConfig(2, os.path.dirname(self.chosenOutLbl.text()))
		if self.chosenStatLbl.text() != "No file chosen":
			self.updateConfig(3, os.path.dirname(self.chosenStatLbl.text()))
		if self.nThreads>MAXTHREADS or self.nProxiesThreads>MAXTHREADS:
			print("ERROR : Can't run with over 50 Proxies. Please modify them using CTRL+P")
		else:
			worker = Worker(self.chosenFileLbl.text(), self.chosenOutLbl.text(), self.chosenStatLbl.text(), self.nThreads, self.nProxiesThreads, self.nProxy, self.proxyFilePath, self.useProxyFileChk, self.checkProxyFileChk, self.noProxiesMax)
			self.threadpool.start(worker)
			worker.signals.progress.connect(self.update_progress)
			worker.signals.console.connect(self.update_console)
			worker.signals.end.connect(self.endQMessageBox)

#=############################################################=#
# ------------------------- GRAPHIC -------------------------- #

def graphic():
	app = QtWidgets.QApplication(sys.argv)
	main = MainWindow()
	main.show()
	sys.exit(app.exec_())

#=############################################################=#
# --------------------------- MAIN --------------------------- #

def main(argv):
	# credit : https://www.tutorialspoint.com/python/python_command_line_arguments.htm
	inputfile = ''
	outputfile = ''
	statfile=''
	sortOut=False
	useOut=False
	useStat=False
	grahicLaunch=True #default launching mode
	termLaunch=False
	nCores=1
	nThreadsNP=0
	try:
		opts, args = getopt.getopt(argv,"c:ghi:to:s:",["ifile=","ofile=","stats=","cores=","no-proxies="])
	except getopt.GetoptError:
		print ('usage: pokeScrap.0.2.py -i <input file or link> -o <outputfile> -s <statFile(optional)>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-g':
			print("Launch graphic version...")
			grahicLaunch=True
		if opt == '-t':
			print("Launch Terminal version")
			termLaunch=True
		if opt == '-h':
			helpMe()
			sys.exit()
		elif opt in ("-i", "--infile"):
			inputfile = arg
		elif opt in ("-o", "--outfile"):
			outputfile = arg
			useOut=True
		elif opt in ("-s", "--stats"):
			statfile = arg
			useStat=True
		elif opt in ("-c", "--cores"):
			nCores = arg
		elif opt in ("--no-proxies"):
			nThreadsNP = arg
	for opt in opts:
		if opt in ("-so", "--sort-outfile"):
			sortOut=True
			
	if inputfile == '' and grahicLaunch == False:
		print('An input is needed !')
		print ('Type "CMscrapepy -h" for more infos')
		sys.exit(2)
	#print ('Input file is: ', inputfile)
	#print ('Output file is: ', outputfile)
	args = [inputfile]
	if outputfile != '':
		args.append(outputfile)
	if statfile != '':
		args.append(statfile)
	if termLaunch:
		MultipleLinkScraper(args, useOut, useStat, sortOut, grahicLaunch, nCores)
	else:
		graphic()

if __name__ == "__main__":
   main(sys.argv[1:])