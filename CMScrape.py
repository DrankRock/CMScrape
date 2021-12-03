#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:33 2021

@author: mat
"""
import requests, re, sys, getopt, os
import os.path
from bs4 import BeautifulSoup
from datetime import datetime
from graphicCMS import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
#-##############################-#
# ---------- ✖︎ TODO ✔︎ -----------#
#  	✖︎ - Finish the PyDoc	 		#
#		✔︎ - Make a GUI			 		#
#		✖︎ - GUI Console show	 		#
#		✖︎ - Manage Exceptions   	#
#		✖︎ - Multi Threading	   	#
#-##############################-#

"""
CMScrape is a scraping project with the objective to facilitate the use of CardMarket
when tracking prices of all kind of collectibles.
Find a full documentation here :
https://github.com/DrankRock/CMScrape
"""
COLOR = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m"
}

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
# ---------------------- SINGLE SCRAPER ---------------------- #
class SingleScraper():
	def __init__(self, url):
		self.url = url

	"""
	scrape the parameters and output them in the cvs format
	"""
	def paramScrap(self):
		"""
		for each parameters, get only the value
		:param parameter: the index of the parameter in the parameters list
		:param paramString: a string containing the name of the parameter as used in cardmarket's url
		"""
		def singleParamScrap(parameter, paramString):
			if parameter >= 0:
				content = self.params[parameter]
				splitted_content = content.split("=")
				splitted_content = str(splitted_content[1]).replace(",",";")
				self.paramliste.append(splitted_content)
			else:
				content = 'None'
				self.paramliste.append(content)
		# get the list of all the parameters in the url
		self.params = self.params_ref.split("&")
		self.paramliste = []
		# these are the interesting parameters, that we will put in the cvs output, we want to get their values
		language = self.index_containing_substring(self.params, "language")
		sellerType = self.index_containing_substring(self.params, "sellerType")
		minCondition = self.index_containing_substring(self.params, "minCondition")
		isSigned = self.index_containing_substring(self.params, "isSigned")
		isFirstEd = self.index_containing_substring(self.params, "isFirstEd")
		isPlayset = self.index_containing_substring(self.params, "isPlayset")
		isAltered = self.index_containing_substring(self.params, "isAltered")
		isReverseHolo = self.index_containing_substring(self.params, "isReverseHolo")
		isFoil = self.index_containing_substring(self.params, "isFoil")
		#isFoil=Y
		# make use of singleParamScrap to update paramliste with only the values
		singleParamScrap(language, "language")
		singleParamScrap(sellerType, "sellerType")
		singleParamScrap(minCondition, "minCondition")
		singleParamScrap(isSigned, "isSigned")
		singleParamScrap(isFirstEd, "isFirstEd")
		singleParamScrap(isPlayset, "isPlayset")
		singleParamScrap(isAltered, "isAltered")
		singleParamScrap(isReverseHolo, "isReverseHolo")
		singleParamScrap(isFoil, "isFoil")
		# No need of a return, we can use self.paramliste

	def index_containing_substring(self, the_list, substring):
	    for i, s in enumerate(the_list):
	        if substring in s:
	              return i
	    return -1

	def Main(self):
		# Variables that are always the same
		splitted_URL = self.url.split("/")
		langage = splitted_URL[3]
		jeu = splitted_URL[4]
		item = splitted_URL[6]

		page = requests.get(self.url)
		soup = BeautifulSoup(page.content, "html.parser")
		extension = 'None'
		name_uncut = soup.find_all("div", class_="flex-grow-1")
		name = re.search('><h1>(.*)<span', str(name_uncut))
		name = name.group(1)
		Prices_uncut = soup.find_all("dd", class_="col-6 col-xl-7")
		# print("Prices uncut before reduc : ",Prices_uncut) #DEBUG

		if item=="Singles":
			names_ref = splitted_URL[8]
			extension_uncut = soup.find_all("a", class_="mb-2")
			extension = re.search('">(.*)</a',str(extension_uncut))
			extension = extension.group(1)
			number = soup.find_all("dd", class_="d-none d-md-block col-6 col-xl-7")
			# print("Number : {}".format(number)) #DEBUG
			if number == []:
				number = 'None'
				Prices_uncut = Prices_uncut[4:]
			else:
				number = re.search('">(.*)<',str(number)).group(1)
				Prices_uncut = Prices_uncut[5:]
		else:
			names_ref = splitted_URL[7]
			extension = 'None'
			number = 'None'
			Prices_uncut = Prices_uncut[1:]

		name_ref_split = names_ref.split("?")
		if len(name_ref_split) == 1 :
			self.params_ref = ''
		else:
			self.params_ref = name_ref_split[1]
	
		# print("Prices uncut : {}".format(Prices_uncut))
		allPrices = []
		for potential_price in Prices_uncut:
			# print("Item : {}".format(str(potential_price)))
			search = re.search('>(\d.*€)<', str(potential_price))
			searchnone = re.search('>N/A<', str(potential_price))
			# print("Search : {}\n Search N/A : {}".format(search, searchnone)) #DEBUG
			if searchnone != None:
				allPrices.append('None')
			elif search != None:
				allPrices.append(search.group(1))

		# print("All Prices : {}".format(allPrices)) #DEBUG
		out = [jeu, item, extension, number, name, allPrices[0].replace(".","").replace(",",".").replace("€",""), allPrices[1].replace(".","").replace(",",".").replace("€",""), allPrices[2].replace(".","").replace(",",".").replace("€","")]
		self.paramScrap()
		self.paramliste.append(self.url)
		returnListe = out+self.paramliste
		return returnListe

#=############################################################=#
# ---------------------- MULTI SCRAPER ----------------------- #

def MultiScrap(args, isFileOut, isFileStat, isSortOut, isGraphic, graphicUI):
	#(String[] args, Bool fileOut, Bool fileStat, Bool sortOut)
	# -- Files Opening -- #
	fileIn = open(args[0], 'r')
	#fileIn is necessary. It will always be here.
	if isFileOut:
		fileOut = open(args[1], 'w')
	else:
		#this line is necessary because i print a lot, and it's a pain in the ass to redirect everything
		#with a lot of "if" when the user doesn't want output. That's easier.
		#>Don't want to print? Just print to the nowhere!
		fileOut = open(os.devnull, 'w')
	if isFileStat:
		# if there is a stat file
		if isFileOut:
			# if there is an outfile, it is appended first in args, so args[1] is out and args[2] is stat
			indexOfStat=2
		else:
			# else, args[1] is stat and out is nowhere.
			indexOfStat=1
		# if the string containing the name of the file exists
		try:
			# if the file exists, this will work, else it throws an error
			size = os.path.getsize(args[indexOfStat])
			fileStat = open(args[indexOfStat], 'a')
		except:
			# catch the error (please note that this is a shitty way to solve the problem.)
			# if fileStat needs to be created, a separator is specified at the top of the file
			fileStat = open(args[indexOfStat], 'a')
			# print("sep=,", file=fileStat)

	# Initialisation of OutputFile
	# print("sep=,",file=fileOut) #seems to do nothing..
	print("game,item,extension,number,name,min_price,price_trend,mean30d_price,language,sellerType,minCondition,isSigned,isFirstEd,isPlayset,isAltered,isReverseHolo,isFoil,url", file=fileOut)
	# -- Variable Initialisation -- #
	Lines = fileIn.readlines()
	nLines = len(Lines)
	iterator = 1
	minPrice = 0.0
	trendPrice = 0.0
	mean30Price = 0.0
	# -- Looping through the URLs -- #
	for line in Lines:
		if isGraphic:
			perc = iterator*100/nLines
			graphicUI.progressBar.setValue(perc)
		print("[{}/{}] scraping links...     ".format(iterator,nLines), end="\r", flush=True)
		currentline = str(line.strip())
		pk = SingleScraper(currentline)
		pkm = pk.Main()
		if pkm[5] != 'None':
			minPrice+=float(pkm[5])
		if pkm[6] != 'None':
			trendPrice+=float(pkm[6])
		if pkm[7] != 'None':
			mean30Price+=float(pkm[7])
		for i in range(len(pkm)):
			pkm[i] = "\"{}\"".format(str(pkm[i]))
		print(', '.join(pkm), file=fileOut)
		iterator+=1
	print("[{}] links successfully scraped.".format(nLines))
	nLinesp1=nLines+1
	print("Total Min Price = {}\nTotal Trend Price = {}\nTotal Mean Price = {}".format(minPrice, trendPrice, mean30Price))
	print(",Number of Cards:,{},Total Prices:,{},{},{},,,,,,,,".format(nLines,minPrice,trendPrice,mean30Price), file=fileOut)
	if isFileStat==True:
		now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		print("{}, {}, {}, {}".format(now, minPrice, trendPrice, mean30Price), file=fileStat)

#=############################################################=#
# ---------------------- CSV SORT FILE ----------------------- #

def csvSortFile(file):
	## We shall ignore the first line because it's the sep=,
	#[1:]
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
	def __init__(self, parent=None):
		QtWidgets.QMainWindow.__init__(self, parent)
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
			print("Error : no input file was chosen.")
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
			MultiScrap(args, isOut, isStat, False, True, self)


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
	grahicLaunch=False
	try:
		opts, args = getopt.getopt(argv,"ghi:o:s:",["ifile=","ofile=","stats="])
	except getopt.GetoptError:
		print ('usage: pokeScrap.0.2.py -i <input file or link> -o <outputfile> -s <statFile(optional)>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-g':
			print("Launch graphic version...")
			grahicLaunch=True
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

	for opt in opts:
		if opt in ("-so", "--sort-outfile"):
			sortOut=True
			
	if inputfile == '' and grahicLaunch == False:
		print('An input is needed !')
		print ('Type "CMscrap.0.1.py -h" for more infos')
		sys.exit(2)
	#print ('Input file is: ', inputfile)
	#print ('Output file is: ', outputfile)
	args = [inputfile]
	if outputfile != '':
		args.append(outputfile)
	if statfile != '':
		args.append(statfile)
	if grahicLaunch:
		graphic()
	else:
		MultiScrap(args, useOut, useStat, sortOut, grahicLaunch)

if __name__ == "__main__":
   main(sys.argv[1:])