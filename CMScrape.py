#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:33 2021

@author: mat
"""
import requests, re, sys, getopt, os, traceback, multiprocessing
import os.path
from bs4 import BeautifulSoup
from datetime import datetime
from graphicCMS import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication

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
# -------------------- SINGLE LINK SCRAPER ------------------- #
def SingleLinkScraper(url):
	"""
	scrape the parameters and output them in the cvs format
	"""
	def paramScrap(params_ref):
		"""
		for each parameters, get only the value
		:param params: the list containing all the a
		:param indexInParams: the index of the parameter in the parameters list
		:param paramString: a string containing the name of the parameter as used in cardmarket's url
		"""
		def singleParamScrap(params, indexInParams, paramString):
			if indexInParams >= 0:
				content = params[indexInParams]
				splitted_content = content.split("=")
				splitted_content = str(splitted_content[1]).replace(",",";")
				return splitted_content
			else:
				return 'None'

		# if the given list contains the given substring, 
		# Returns the index of the first occurence of the
		# substring in the list. Else, returns -1.
		def index_containing_substring(the_list, substring):
			for i, s in enumerate(the_list):
				if substring in s:
					return i
			return -1

		# get the list of all the parameters in the url
		params = params_ref.split("&")
		paramliste = []

		# these are the interesting parameters, that we will put in the cvs output, 
		# we want to get their values. Please note that this might not be complete
		# it seems like it is concerning Pokemon and YuGiOh, but if I missed any
		# in any other game please let me know
		possibleParameters = [
			"language",
			"sellerType",
			"minCondition",
			"isSigned",
			"isFirstEd",
			"isPlayset",
			"isAltered",
			"isReverseHolo",
			"isFoil"
		]
		# For each parameters, if it has a value, appends it, else, appends 'None'
		for parameter in possibleParameters:
			currentIndex = index_containing_substring(params, parameter)
			paramliste.append(singleParamScrap(params, currentIndex, parameter))

		return paramliste

	#=---- MAIN CODE ----=#
	# Variables initialisation
	splitted_URL = url.split("/")
	langage = splitted_URL[3]
	game = splitted_URL[4]
	item = splitted_URL[6]
	expansion = 'None'
	number = 'None'
	allPrices = []
	
	# Bs4 Request
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	
	# Checking if CardMarket is currently under maintenance
	title = soup.find('title')
	if "Maintenance | Cardmarket" in str(title):
		print("CardMarket is currently under Maintenance. Please try again later.")
		sys.exit(1)
	
	# Scraping the name of the object
	name_uncut = soup.find_all("div", class_="flex-grow-1")
	name = re.search('><h1>(.*)<span', str(name_uncut))
	name = name.group(1)
	name = name.replace('"','""') # in csv, if you want to show a " , you need to put a " before, so 24" tv -> 24"" tv

	# Scraping all the variables in the same box as prices
	Prices_uncut = soup.find_all("dd", class_="col-6 col-xl-7")
	# Only the last five results in the box interests us, they are the variable I'll be outputing
	Prices_uncut = Prices_uncut[-5:]
	for potential_price in Prices_uncut:
		# Scrape the price in € . If the price is not in euros, it will not be detected.
		search = re.search('>(\d.*€)<', str(potential_price))
		searchnone = re.search('>N/A<', str(potential_price))
		if searchnone != None:
			allPrices.append('None')
		elif search != None:
			allPrices.append(search.group(1))

	# The next if-else is because single cards contain more information than
	# Other objects such as deck boxes, they thus need more scraping to be done
	# When a value does not exist, its value is "None"
	# | inurlParams is the last block of a CM url, containing details about the product
	# If we are seeing cards
	if item=="Singles":
		inurlParams = splitted_URL[8]
		# Scrape the expansion
		expansion_uncut = soup.find_all("a", class_="mb-2")
		expansion = re.search('">(.*)</a',str(expansion_uncut))
		expansion = expansion.group(1)

		# Scrape the card number
		number = soup.find_all("dd", class_="d-none d-md-block col-6 col-xl-7")
		if number != []:
			number = re.search('">(.*)<',str(number)).group(1)
	else:
		# if the item is not a single card
		inurlParams = splitted_URL[7]
		# this value changes because when showing non-cards item, CM links
		# are shorter, not containing the expansion

	# Find the parameters specified in the url
	inurlParams_splitted = inurlParams.split("?")
	if len(inurlParams_splitted) == 1 :
		params_ref = ''
	else:
		params_ref = inurlParams_splitted[1]

	# Generates the first half of the output
	out = [game, item, expansion, number, name, allPrices[0].replace(".","").replace(",",".").replace("€",""), allPrices[1].replace(".","").replace(",",".").replace("€",""), allPrices[2].replace(".","").replace(",",".").replace("€","")]
	# Generates the second half of the output
	paramliste = paramScrap(params_ref)
	# url has to be quoted to be seen as a string by csv viewer such as libreOffice, because it
	# might contain coma, the seperator value.
	paramliste.append('"{}"'.format(url))
	returnListe = out+paramliste
	# Returns a normal list. The objects within the list might contain unwanted ",", especially in the name and url areas.
	return returnListe

#=############################################################=#
# ---------------------- MULTI SCRAPER ----------------------- #

# A rough description would be "an overly complicated way to make a for loop of SingleLinkScraper".
def MultipleLinkScraper(args, isFileOut, isFileStat, isSortOut, isGraphic, graphicUI, nCores):
	# Precision about the arguments : 
	# (String[] args, Bool fileOut, Bool fileStat, Bool sortOut, Bool isGraphic, Bool graphicUi, Integer nCPU)
	print("Running CMScrape on {} cores".format(nCores))
	# -- Files Opening -- #
	fileIn = open(args[0], 'r')
	# fileIn is necessary. It will always be here. If no input is given, an exception is thrown before this.
	if isFileOut:
		# If an output file is specified
		fileOut = open(args[1], 'w')
	else:
		# this line is necessary because i print a lot, and it's a pain in the ass to redirect everything
		# with a lot of "if" when the user doesn't want output. That's easier.
		# >Don't want to print? Just print to the nowhere!
		fileOut = open(os.devnull, 'w')
	if isFileStat:
		# if there is a stat file
		if isFileOut:
			# if there is an outfile, it is appended first in args, so args[1] is out and args[2] is stat
			indexOfStat=2
		else:
			# else, args[1] is stat and out is now here.
			indexOfStat=1
		fileStat = open(args[indexOfStat], 'a')

	# Initialisation of OutputFile
	# print("sep=,",file=fileOut) #separator is not read with libreoffice so I removed this idea.
	print("game,item,extension,number,name,min_price,price_trend,mean30d_price,language,sellerType,minCondition,isSigned,isFirstEd,isPlayset,isAltered,isReverseHolo,isFoil,url", file=fileOut)
	
	# -- Variable Initialisation -- #
	probablyURLs = fileIn.read().splitlines()
	nLines = len(probablyURLs)
	nURLScraped = 0
	iterator = 1
	i = 0
	minPrice = 0.0
	trendPrice = 0.0
	mean30Price = 0.0
	
	# Multi-Processing initialization
	p = multiprocessing.Pool(int(nCores))
	for scrapes in p.imap(SingleLinkScraper, probablyURLs):
		url = probablyURLs[i]
		i+=1
		text = "[{}/{}] scraping links...     \nScraping : {}".format(iterator,nLines,url)
		# If it's not lauched as a terminal app, update the console output in the window.
		if isGraphic:
			perc = iterator*100/nLines
			graphicUI.progressBar.setValue(round(perc))
			graphicUI.consoleDisp.setText(text)
			QApplication.processEvents()
		print("[{}/{}] scraping links...     ".format(iterator,nLines), end="\r", flush=True)
		
		# Remove the endOfLine character(\r, \n)
		url = str(url.strip())
		if scrapes[5] != 'None':
			minPrice+=float(scrapes[5])
		if scrapes[6] != 'None':
			trendPrice+=float(scrapes[6])
		if scrapes[7] != 'None':
			mean30Price+=float(scrapes[7])

		# adds quotes around the name in case of it containing a comma, which is the csv separator
		scrapes[4] = "\"{}\"".format(str(scrapes[4]))
		print(', '.join(scrapes), file=fileOut)
		nURLScraped+=1
		iterator+=1
		

	print("{} out of {} links successfully scraped.".format(nURLScraped,nLines))
	print("Total Min Price = {}\nTotal Trend Price = {}\nTotal Mean Price = {}".format(minPrice, trendPrice, mean30Price))
	print(",,Number of Cards:,{},Total Prices:,{},{},{}".format(nLines,minPrice,trendPrice,mean30Price), file=fileOut)
	if isFileStat==True:
		now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		print("{}, {}, {}, {}".format(now, minPrice, trendPrice, mean30Price), file=fileStat)

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
	def __init__(self, cores, parent=None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.nCores = cores
		self.setupUi(self)
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
		opts, args = getopt.getopt(argv,"ghit:o:s:c",["ifile=","ofile=","stats=","cores="])
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
	print("nCores : {}".format(nCores))
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