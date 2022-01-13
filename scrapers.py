#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools, random, os
from functools import partial
from multiprocessing import Pool, freeze_support
from random import randrange
from datetime import datetime

from scrapeAndCheck import *

TIMEOUT = 5
PROXIES = []


#=############################################################=#
# -------------------- SINGLE LINK SCRAPER ------------------- #
def SingleLinkScraper(urlAndNum):
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
	url = urlAndNum[0]
	#print("url: {}".format(url))
	currentIteration = urlAndNum[1]
	splitted_URL = url.split("/")
	langage = splitted_URL[3]
	game = splitted_URL[4]
	item = splitted_URL[6]
	expansion = 'None'
	number = 'None'
	allPrices = []

	#print("\nStarting {} with {}\n".format(url,proxy))
	# Bs4 Request
	tries = 1
	while True:
		try:
			proxy = random.choice(PROXIES)
			proxyDict = {'http':proxy,'https':proxy}
			headers = random.choice(headers_list)
			page = requests.get(url, headers=headers, proxies=proxyDict, timeout=TIMEOUT)
			soup = BeautifulSoup(page.content, "html.parser")
			print("[{}] - {} tries".format(currentIteration, tries))
		except:
			tries += 1
			continue
		break

	
	# Checking if CardMarket is currently under maintenance
	title = soup.find('title')
	if "Maintenance | Cardmarket" in str(title):
		print("CardMarket is currently under Maintenance. Please try again later.")
		sys.exit(1)
	
	# Scraping the name of the object
	try:
		name_uncut = soup.find_all("div", class_="flex-grow-1")
		name = re.search('><h1>(.*)<span', str(name_uncut))
		name = name.group(1)
		name = name.replace('"','""') # in csv, if you want to show a " , you need to put a " before, so 24" tv -> 24"" tv
	except:
		print("error")
		print("Status : \n{}".format(page.status_code))
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
		expansion_uncut = soup.find_all("a", class_="mb-2")
		if expansion_uncut != []:
			expansion = re.search('">(.*)</a',str(expansion_uncut))
			expansion = expansion.group(1)
			
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
	#print("Done {}\n{}".format(url,returnListe))
	return returnListe

#=############################################################=#
# ---------------------- MULTI SCRAPER ----------------------- #

# A rough description would be "an overly complicated way to make a for loop of SingleLinkScraper".
def MultipleLinkScraper(args, isFileOut, isFileStat, isSortOut, isGraphic, graphicUI, nCores):
	# Precision about the arguments : 
	# (String[] args, Bool fileOut, Bool fileStat, Bool sortOut, Bool isGraphic, Bool graphicUi, Integer nCPU)
	multiLinkStart = time.time()

	nProcess = int(nCores)
	print("Available cores : {}\nUsing {} core(s)".format(multiprocessing.cpu_count(),nProcess))
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
	print("game,item,extension,number,name,min_price,price_trend,mean30d_price,language,sellerType,minCondition,isSigned,isFirstEd,isPlayset,isAltered,isReverseHolo,isFoil,url", file=fileOut)
	
	# -- Variable Initialisation -- #
	probablyURLs = fileIn.read().splitlines()
	nLines = len(probablyURLs)
	probablyURLs = zip(probablyURLs, range(len(probablyURLs)))
	nURLScraped = 0
	iterator = 1
	i = 0
	minPrice = 0.0
	trendPrice = 0.0
	mean30Price = 0.0
	
	# Proxies initialisation
	if nProcess > 1:
		print("Launching CMScrape on more than one process requires proxies")
		print("Scraping and checking proxies automatically : ")
		p = proxyClass(nThreads=40, nProxyNeeded=50, proxyFile=False) # launch checker on 40, for 100 proxies threads (my potato pc can take 150, anyone should be fine)
		global PROXIES 
		PROXIES = p.checkProxies()
		#print("Working Proxies :\n{}\n---------------".format("\n".join(workingProxies)))
	
	#print("global proxies : \n{}".format(PROXIES))

	multiProcessStart = time.time()
	print("Elapsed time since run : {}".format(multiProcessStart-multiLinkStart))
	print("Starting MultiProcess : ")
	# Multi-Processing initialization
	p = ThreadPool(int(nProcess))
	print("ThreadPool created")
	#for scrapes in p.map(partial(SingleLinkScraper, proxy=workingProxies), probablyURLs):
	for scrapes in p.map(SingleLinkScraper, probablyURLs):
		print("[{}/{}] scraping links...     ".format(iterator,nLines), end="\r", flush=True)
		
		# Remove the endOfLine character(\r, \n)
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

	print("Elapsed time for Scraping : {}".format(time.time()-multiProcessStart))
	print("Elapsed time since run : {}".format(time.time()-multiLinkStart))
		

	print("{} out of {} links successfully scraped.".format(nURLScraped,nLines))
	print("Total Min Price = {}\nTotal Trend Price = {}\nTotal Mean Price = {}".format(minPrice, trendPrice, mean30Price))
	print(",,Number of Cards:,{},Total Prices:,{},{},{}".format(nLines,minPrice,trendPrice,mean30Price), file=fileOut)
	if isFileStat==True:
		now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		print("{}, {}, {}, {}".format(now, minPrice, trendPrice, mean30Price), file=fileStat)
