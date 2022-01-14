#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools, random, os, cchardet, lxml, traceback
from functools import partial
from multiprocessing import Pool, freeze_support
from random import randrange
from datetime import datetime

from scrapeAndCheck import *

def CMSoupScraper(url, soup):
	def priceToFloat(price):
		return round(float(price.replace(".","").replace(",",".").replace("€","")),3)

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

		# If there are no parameters, return none.
		if params_ref == '':
			l = ["None"] * 9
			return l

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
	splitted_URL = url.split("/")
	langage = splitted_URL[3]
	game = splitted_URL[4]
	item = splitted_URL[6]
	expansion = 'None'
	number = 'None'
	allPrices = []

	# Checking if CardMarket is currently under maintenance
	title = soup.find('title')
	if "Maintenance | Cardmarket" in str(title):
		print("CardMarket is currently under Maintenance. Please try again later.")
		return -1
	
	# Scraping the name of the object
	try:
		name_uncut = soup.find_all("div", class_="flex-grow-1")
		
		# in csv, if you want to show a " , you need to put a " before, so 24" tv -> 24"" tv
		name = re.search('><h1>(.*)<span', str(name_uncut)).group(1).replace('"','""') 

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
		out = [game, item, expansion, number, name, priceToFloat(allPrices[0]), priceToFloat(allPrices[1]), priceToFloat(allPrices[2])]
		# Generates the second half of the output
		paramliste = paramScrap(params_ref)
		# url has to be quoted to be seen as a string by csv viewer such as libreOffice, because it
		# might contain coma, the seperator value.
		paramliste.append('"{}"'.format(url))
		returnListe = out+paramliste
		# Returns a normal list. The objects within the list might contain unwanted ",", especially in the name and url areas.
		#print("Done {}\n{}".format(url,returnListe))
		return returnListe
	except:
		print("WARNING - The url \"{}\" does not work. This could mean that the page was updated and the url changed. Please update it !".format(url))
		#print("Exception : \n{}".format(exp))
		return -1