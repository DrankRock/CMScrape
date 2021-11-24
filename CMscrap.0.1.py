#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:33 2021

@author: mat
"""
import requests, re, sys, getopt
import os.path
from bs4 import BeautifulSoup
from datetime import datetime
#-##############################-#
# ---------- ✖︎ TODO ✔︎ -----------#
#  		✖︎ - Finish the PyDoc	 #
#		✖︎ - Make a GUI			 #
#		✖︎ - Manage Exceptions    #
#		✖︎ - Do the Git Doc       #
#		✖︎ - Add tools to track $ #
#-##############################-#

"""
PokeScraper is a scraping project with the objective to facilitate the use of CardMarket
for Pokemon when tracking prices of single cards.
Argument is either a link to a cardmarket page of a pokemon single card, or a file containing a bunch of https adresses.

Output currently is a cvs format in the terminal, but tends to be inside a file.
I will make it for a terminal use but will make a GUI for other users when I have the time.

    Usage : python pokeScrap.O.1.py [link to cardmarket page of card] or [file containing links]

"""
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

"""
	PokeScraper() is the main class
	:param url: the url of the card to scrape
"""

def helpMe():
	print("-- CardMarket Scraper --")
	print('usage: CMscrap.0.1.py -i <input file or link> -o <outputfile> -s <statFile(optional)>')
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

class PokeScraper():
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
		# make use of singleParamScrap to update paramliste with only the values
		singleParamScrap(language, "language")
		singleParamScrap(sellerType, "sellerType")
		singleParamScrap(minCondition, "minCondition")
		singleParamScrap(isSigned, "isSigned")
		singleParamScrap(isFirstEd, "isFirstEd")
		singleParamScrap(isPlayset, "isPlayset")
		singleParamScrap(isAltered, "isAltered")
		# No need of a return, we can use self.paramliste

	def index_containing_substring(self, the_list, substring):
	    for i, s in enumerate(the_list):
	        if substring in s:
	              return i
	    return -1

	def Main(self):
		splitted_URL = self.url.split("/")
		langage = splitted_URL[3]
		jeu = splitted_URL[4]
		extension_ref = splitted_URL[7]
		name_ref = splitted_URL[8]
		name_ref_split = name_ref.split("?")
		if len(name_ref_split) == 1 :
			self.params_ref = ''
		else:
			self.params_ref = name_ref_split[1]
		name_ref = name_ref_split[0]
		## About the name, I have two options, either replacing "," by something else ("-" ?)
		# Or I can make every string as " 'hello world', 'somedata',.. "
		# Second choice might be the most coherent.
		page = requests.get(self.url)
		soup = BeautifulSoup(page.content, "html.parser")
		name_uncut = soup.find_all("div", class_="flex-grow-1")
		name = re.search('><h1>(.*)<span', str(name_uncut))
		name = name.group(1)
		extension_uncut = soup.find_all("a", class_="mb-2")
		extension = re.search('">(.*)</a',str(extension_uncut))
		extension = extension.group(1)
		number = soup.find_all("dd", class_="d-none d-md-block col-6 col-xl-7")
		number = re.search('">(.*)<',str(number)).group(1)
		Prices_uncut = soup.find_all("dd", class_="col-6 col-xl-7")
		Prices_uncut = Prices_uncut[5:]
		allPrices = []
		for item in Prices_uncut:
		    allPrices.append(re.search('>(\d.*€)<', str(item)).group(1))

		out = [jeu, extension, number, name, allPrices[0].replace(",",".").replace("€",""), allPrices[1].replace(",",".").replace("€",""), allPrices[2].replace(",",".").replace("€","")]
		self.paramScrap()
		self.paramliste.append(self.url)
		returnListe = out+self.paramliste
		return returnListe

def MultiPokeScrapURL(args):
	# -- Files Opening -- #
	fileIn = open(args[0], 'r')
	fileOut = open(args[1], 'w')
	fileStat = ''
	if len(args)==3 :
		# if fileStat needs to be created, a separator is specified at the top of the file
		if fileStat.is_file():
			fileStat = open(args[2], 'a')
			print("sep=,", file=fileStat)
		else:
			fileStat = open(args[2], 'a')
	# Initialisation of OutputFile
	print("sep=,",file=fileOut)
	print("game,extension,number,name,min_price,price_trend,mean30d_price,language,sellerType,minCondition,isSigned,isFirstEd,isPlayset,isAltered,url", file=fileOut)
	# -- Variable Initialisation -- #
	Lines = fileIn.readlines()
	nLines = len(Lines)
	iterator = 1
	minPrice = 0.0
	trendPrice = 0.0
	mean30Price = 0.0
	# -- Looping through the URLs -- #
	for line in Lines:
		print("[{}/{}] scraping links...     ".format(iterator,nLines), end="\r", flush=True)
		#print(f"{bcolors.OKBLUE}[{}/{}] scraping links...     {bcolors.ENDC}".format(iterator,nLines), end="\r", flush=True)
		currentline = str(line.strip())
		pk = PokeScraper(currentline)
		pkm = pk.Main()
		minPrice+=float(pkm[4])
		trendPrice+=float(pkm[5])
		mean30Price+=float(pkm[6])
		for i in range(len(pkm)):
			pkm[i] = "\"{}\"".format(str(pkm[i]))
		print(', '.join(pkm), file=fileOut)
		iterator+=1
	nLinesp1=nLines+1
	print("Total Min Price = {}\nTotal Trend Price = {}\nTotal Mean Price = {}".format(minPrice, trendPrice, mean30Price))
	print(",Number of Cards:,{},Total Prices:,{},{},{},,,,,,,,".format(nLines,minPrice,trendPrice,mean30Price), file=fileOut)
	if fileStat != '':
		now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		print("{}, {}, {}, {}".format(now, minPrice, trendPrice, mean30Price), file=fileStat)

def csvSortFile(file):
	## We shall ignore the first line because it's the sep=,
	#[1:]
	toSort = open(file, 'r')
	separator=toSort.readline().rstrip()
	toSortLines = toSort.read().splitlines()[1:]
	toSortLines.sort()
	toSort.close()

	out = open(file, 'w')
	print(separator, file=out)
	for i in range(len(toSortLines)):
		print(toSortLines[i], file=out)



def main(argv):
	# credit : https://www.tutorialspoint.com/python/python_command_line_arguments.htm
	inputfile = ''
	outputfile = ''
	statfile=''
	sortStat=False
	sortOut=False
	try:
		opts, args = getopt.getopt(argv,"hi:o:s:",["ifile=","ofile=","stats="])
	except getopt.GetoptError:
		print ('usage: pokeScrap.0.2.py -i <input file or link> -o <outputfile> -s <statFile(optional)>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			helpMe()
			sys.exit()
		elif opt in ("-i", "--infile"):
			inputfile = arg
		elif opt in ("-o", "--outfile"):
			outputfile = arg
		elif opt in ("-s", "--stats"):
			statfile = arg

	for opt in opts:
		if opt in ("-ss", "--sort-stats"):
			sortStat=True
		elif opt in ("-so", "--sort-outfile"):
			sortOut=True
			
	if outputfile == '':
		outputfile = './pokeScraperOut.csv'
	if inputfile == '':
		print('An input is needed !')
		print ('usage: CMscrap.py -i <input file or link> -o <outputfile> -s <statFile(optional)>')
		sys.exit(2)
	print ('Input file is: ', inputfile)
	print ('Output file is: ', outputfile)
	args = [inputfile, outputfile]
	if statfile != '':
		args.append(statfile)
	MultiPokeScrapURL(args)

if __name__ == "__main__":
   main(sys.argv[1:])