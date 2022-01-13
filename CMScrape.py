#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:33 2021

@author: mat
"""
import requests, re, sys, getopt, os, traceback, multiprocessing, time
import os.path

from bs4 import BeautifulSoup
from datetime import datetime
from graphicCMS import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication, QAction

from scrapers import *

#-##############################-#
# ---------- ✖︎ TODO ✔︎ -----------#
#  	✖︎ - Finish the PyDoc	 		#
#		✔︎ - Make a GUI			 		#
#		✖︎ - GUI Console show	 		#
#		✖︎ - Manage Exceptions   	#
#		✖︎ - Multi Threading	   	#
#		✖︎ - Remove console 			#
#		✖︎ - Cancel Button				#
#		✖︎ - Icon							#
#-##############################-#

"""
CMScrape is a scraping project with the objective to facilitate the use of CardMarket
when tracking prices of all kind of collectibles.
Find a full documentation here :
https://github.com/DrankRock/CMScrape
"""

TIMEOUT = 10


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
	toSort = open(file, 'r')
	# separator=toSort.readline().rstrip()
	toSortLines = toSort.read().splitlines()
	toSortLines.sort()
	toSort.close()

	out = open(file, 'w')
	# print(separator, file=out)
	for i in range(len(toSortLines)):
		print(toSortLines[i], file=out)

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


	def __init__(self, cores, parent=None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.nCores = cores
		self.setupUi(self)
		self._createMenuBar()
		self.inputBtn.clicked.connect(self.inputFileDialog)
		self.statBtn.clicked.connect(self.statFileDialog)
		self.outputBtn.clicked.connect(self.outputFileDialog)
		self.runBtn.clicked.connect(self.run)

	def inputFileDialog(self):
		self.fileDialog = QFileDialog()
		options = self.fileDialog.Options()
		options |= self.fileDialog.DontUseNativeDialog
		#options |= self.fileDialog.setDefaultSuffix(self.fileDialog, "csv")
		#filename, _ = self.fileDialog.getOpenFileName(self, 'Open File', '.')
		fileName, _ = self.fileDialog.getOpenFileName(self,"Chose desired input file","","All Files (*);;Text Files (*.txt)", options=options)
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
		fileName, _ = self.fileDialog.getSaveFileName(self,"Chose or create desired output file","","All Files (*);;Text Files (*.txt)", options=options)
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
		fileName, _ = self.fileDialog.getSaveFileName(self,"Chose or create desired statistics file","","All Files (*);;Text Files (*.txt)", options=options)
		if fileName:
			# print(fileName)
			self.statFileChosen = fileName
			self.chosenStatLbl.setText(str(fileName))
			self.chosenStatLbl.adjustSize()

	def run(self):

		if self.chosenFileLbl.text() == "No file chosen":
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error")
			msg.setInformativeText('Please chose an input file')
			msg.setWindowTitle("Error - No File Chosen")
			msg.exec_()
		else:
			isOut=False
			isStat=False
			args=[self.chosenFileLbl.text()]
			if self.chosenOutLbl.text() != "No file chosen":
				isOut=True;
				args.append(self.chosenOutLbl.text())
			if self.chosenStatLbl.text() != "No file chosen":
				isStat=True;
				args.append(self.chosenStatLbl.text())
			print("Running ...")
			MultipleLinkScraper(args, isOut, isStat, False, True, self, self.nCores)

#=############################################################=#
# ------------------------- GRAPHIC -------------------------- #

def graphic(cores):
	app = QtWidgets.QApplication(sys.argv)
	main = MainWindow(cores)
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
	try:
		opts, args = getopt.getopt(argv,"cghit:o:s",["ifile=","ofile=","stats=","cores="])
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
		graphic(nCores)

if __name__ == "__main__":
   main(sys.argv[1:])