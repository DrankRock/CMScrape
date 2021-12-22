#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, re, sys, getopt, os
import os.path
from bs4 import BeautifulSoup

# Pokemon singles url : https://www.cardmarket.com/en/Pokemon/Products/Search

url = "https://www.cardmarket.com/en/Magic/Products/Search"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
title = soup.find('title')
if "Maintenance | Cardmarket" in str(title):
	print("CardMarket is currently under Maintenance. Please try again later.")
	sys.exit(1)
extension = 'None'

categories = soup.find_all(name='select', attrs={'name': 'idCategory'})
cat_soup = BeautifulSoup(str(categories), "html.parser")
categories2 = cat_soup.find_all(name='option')
categories = []
for cat in categories2:
	tempCat = re.search('>(.*)<', str(cat))
	categories.append(tempCat.group(1))
#print(categories)

expansions = soup.find_all(name='select', attrs={'name': 'idExpansion'})
exp_soup = BeautifulSoup(str(expansions), "html.parser")
expansions2 = exp_soup.find_all(name='option')
#print(expansions2)
expansions = []
for exp in expansions2:
	tempExp = re.search('value="(.*)">', str(exp))
	expansions.append(tempExp.group(1))
#print(expansions)



#-################ First Try
# ~ Access all expansions and get the number of cards and pages to travel.
#-#########
i = 1
expansions.sort()
lth = len(expansions)
for exp in expansions[1:]:
	current = exp.replace(" ","-")
	currentUrl = url+"?idExpansion="+exp
	currentPage = requests.get(currentUrl)
	currentSoup = BeautifulSoup(currentPage.content, "html.parser")
	nameExp = currentSoup.find_all(name="option", selected="selected", value=True)
	nameExps = []
	for exp in nameExp:
		tempExp = re.search('>(.*)<', str(exp))
		nameExps.append(tempExp.group(1))
	nameExp = nameExps[1]
	#nameExp = re.search('>(.*)<', str(nameExp)).group(1)
	#print(nameExp)
	if currentSoup.findAll(name="div", class_="mt-3 text-warning text-center font-weight-bold") :  
		print("[{}/{}] value : {}, hits : 0".format(i, lth, exp))
	else :
		hits = currentSoup.find(name="div", class_="col-auto d-none d-md-block")
		hit = re.search('>(.*)<', str(hits)).group(1)
		nHit = hit.split(" ")[0]

		pages =  currentSoup.find(name="span", class_="mx-1")
		page = re.search('>(.*)<', str(pages)).group(1)
		nPages = page.split(" ")[3]


		table = currentSoup.find(name="div", class_="table-body")
		rows=list()
		for row in table.findAll("a", href=True, class_=False):
		   rows.append(row)
		for row in rows:
			name = re.search('>(.*)<', str(row)).group(1) 
			urlOfcurrentRow = re.search('href="(.*)"', str(row)).group(1)
			print("'{}','{}','https://www.cardmarket.com{}'".format(nameExp,name,urlOfcurrentRow))
		



		print("[{}/{}] value : {}, hits : {}, pages : {}".format(i, lth, exp, nHit, nPages))
	soup.decompose()
	i = i+1