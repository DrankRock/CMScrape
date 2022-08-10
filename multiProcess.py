import multiprocessing, time, requests, random, cchardet, lxml, csv, os, sys, traceback

from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
from requests.adapters import HTTPAdapter
from datetime import datetime, timedelta
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from scrapeAndCheck import *
import scrapers

headers_list = [{
		'Host': 'www.cardmarket.com',
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate, br',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'none',
		'Sec-Fetch-User': '?1',
	},{
		'Host': 'www.cardmarket.com',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate, br',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'none',
		'Sec-Fetch-User': '?1',
	},{
		'Host': 'www.cardmarket.com',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate, br',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'none',
		'Sec-Fetch-User': '?1',
	},{
		'Host': 'www.cardmarket.com',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate, br',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'none',
		'Sec-Fetch-User': '?1',
	}]

#url = 'https://www.cardmarket.com/en'
prox = None
session = None
currentText = ""
urls_occurence_dictionnary = {}
total_number_of_url = 0
global TIME_MAX
global CURRENT_VALUE_PROXYLESS
global MAX_PROXYLESS_REQUESTS

INCREMENT_VALUE = 120

def incrementTime():
	global TIME_MAX
	TIME_MAX = TIME_MAX + timedelta(seconds=INCREMENT_VALUE)

def init_process():
	global session
	session = requests.Session()


def fun1(url):
	tries = 1
	while True:
		try:
			proxy = prox.randomProxy()
			proxyDict = {'http':proxy,'https':proxy}
			headers = random.choice(headers_list)
			response = session.get(url,headers=headers, proxies=proxyDict, timeout=5)
			#text = "Status_code : {} - proxy : {} - {} tries".format(response.status_code,proxy,tries)
			#print("Done - {}".format(url))
		except:
			tries += 1
			continue
		break
	soup = BeautifulSoup(response.text, 'lxml')
	return scrapers.CMSoupScraper(url, soup)

def fun1_noProxies(url):
	global CURRENT_VALUE_PROXYLESS, MAX_PROXYLESS_REQUESTS, TIME_MAX
	CURRENT_VALUE_PROXYLESS += 1
	# if the current value is above the max authorized value per minutes, and the current time is below the one minute mark
	# inform me that wait is needed

	# while i'm in an impossible to link situation, 
	while CURRENT_VALUE_PROXYLESS > MAX_PROXYLESS_REQUESTS and datetime.now() < TIME_MAX:
		print("Waiting before new request. Time Remaining = {}".format(TIME_MAX-datetime.now()), end="\r")
		time.sleep(1)
	# if time issue is resolved
	if CURRENT_VALUE_PROXYLESS > MAX_PROXYLESS_REQUESTS:
		# increment time
		incrementTime()
		# set this link as the first
		CURRENT_VALUE_PROXYLESS = 1


	'''
	while CURRENT_VALUE_PROXYLESS > MAX_PROXYLESS_REQUESTS :
		if datetime.now() > TIME_MAX:
			CURRENT_VALUE_PROXYLESS = 0
			incrementTime()'''


	while True:
		try:
			headers = random.choice(headers_list)
			response = session.get(url,headers=headers,timeout=5)
			#text = "Status_code : {} - proxy : {} - {} tries".format(response.status_code,proxy,tries)
			#print("Done - {}".format(url))
		except:
			continue
		break
	soup = BeautifulSoup(response.text, 'lxml')
	return scrapers.CMSoupScraper(url, soup)

def multiMap(urlList, poolSize, outFile, statFile, signals, noProxiesMax, poolType):
	#print("multimap start")
	global currentText, MAX_PROXYLESS_REQUESTS, CURRENT_VALUE_PROXYLESS, TIME_MAX
	noProxiesMax = int(noProxiesMax)
	TIME_MAX = datetime.now()+timedelta(seconds=INCREMENT_VALUE)
	MAX_PROXYLESS_REQUESTS = noProxiesMax # max requests = given value
	CURRENT_VALUE_PROXYLESS = 0

	if outFile != False:		
		opened_outFile = open(outFile, 'w', newline='', encoding='utf-8')
	else:
		opened_outFile = open(os.devnull, 'w', newline='')
	# setup csv_writer for the output file
	csv_writer = csv.writer(opened_outFile)
	csv_writer.writerow(['game','item','extension','number','name','min_price','price_trend','mean30d_price','language','sellerType','minCondition','isSigned','isFirstEd','isPlayset','isAltered','isReverseHolo','isFoil','url'])
	
	currentText = "Starting multithreading for scraping ..."
	signals.console.emit(currentText)
	
	# variables
	iterator = 1
	workingIterator = 0
	minPrice = 0.0
	trendPrice = 0.0
	mean30Price = 0.0

	if poolType == 'Threads':
		p = ThreadPool(poolSize, initializer=init_process)
	elif poolType == 'Processes':
		p = Pool(poolSize, initializer=init_process)
	else :
		print("Unknown PoolType '{}' in multiMap (multiprocess.py).".format(poolType))
		sys.exit(1)
	#print("multimap start scraping")

	if poolSize == 1 or noProxiesMax > 0:
		if noProxiesMax != 1 :
			poolSize = noProxiesMax
		for currentURL in urlList:
			scrapes=fun1_noProxies(currentURL)
			if scrapes != -1:
				current_URL = str(scrapes[len(scrapes)-1]).replace('"', '')
				#print("current URL : {} ;\nURL in scrapes : {}\n value : {}\n------------------".format(current_URL,scrapes[len(scrapes)-1], urls_occurence_dictionnary.get(current_URL)))
				for iteration in range(urls_occurence_dictionnary.get(current_URL)):
					try:
						if scrapes[5] != 'None':
							minPrice+=float(scrapes[5])
						if scrapes[6] != 'None':
							trendPrice+=float(scrapes[6])
						if scrapes[7] != 'None':
							mean30Price+=float(scrapes[7])
					except:
						pass
					#print("[{}/{}] Prices: min={}; trend={}; mean30={}".format(iterator, nURL,minPrice,trendPrice,mean30Price), end="\r", flush=True)
					currentText = "[{}/{}] Prices: \n\tTotal minimum price = {}; \n\tTotal trending price = {}; \n\tTotal mean 30d price = {}\n(please be patient, it takes some time, and the console output isn't very smooth)".format(iterator, total_number_of_url,round(minPrice,3),round(trendPrice,3),round(mean30Price,3))
					signals.console.emit(currentText)
					signals.progress.emit(round(float(iterator)/total_number_of_url*100))
					workingIterator += 1
					csv_writer.writerow(scrapes)
					iterator += 1
	else:
		myFunction = fun1
		try:

			for scrapes in p.imap(myFunction, urlList):
				if scrapes != -1:
					current_URL = str(scrapes[len(scrapes)-1]).replace('"', '')
					#print("current URL : {} ;\nURL in scrapes : {}\n value : {}\n------------------".format(current_URL,scrapes[len(scrapes)-1], urls_occurence_dictionnary.get(current_URL)))
					for iteration in range(urls_occurence_dictionnary.get(current_URL)):
						try:
							if scrapes[5] != 'None':
								minPrice+=float(scrapes[5])
							if scrapes[6] != 'None':
								trendPrice+=float(scrapes[6])
							if scrapes[7] != 'None':
								mean30Price+=float(scrapes[7])
						except:
							pass
						#print("[{}/{}] Prices: min={}; trend={}; mean30={}".format(iterator, nURL,minPrice,trendPrice,mean30Price), end="\r", flush=True)
						currentText = "[{}/{}] Prices: \n\tTotal minimum price = {}; \n\tTotal trending price = {}; \n\tTotal mean 30d price = {}\n(please be patient, it takes some time, and the console output isn't very smooth)".format(iterator, total_number_of_url,round(minPrice,3),round(trendPrice,3),round(mean30Price,3))
						signals.console.emit(currentText)
						signals.progress.emit(round(float(iterator)/total_number_of_url*100))
						workingIterator += 1
						csv_writer.writerow(scrapes)
						iterator += 1
		except Exception as e:
			print("Exception caught during scraping : \n{}".format(traceback.format_exc()))
			print("[WARNING]\nPlease wait for the processes to safely quit")
		finally:
			p.close()
			p.join()
			print("Processes stopped.")
	currentText = currentText + "\nSuccessfully scraped {} out of {} links.".format(workingIterator, total_number_of_url)
	signals.console.emit(currentText)
	csv_writer.writerow(['','','Number of cards',workingIterator,'Total Prices:',minPrice,trendPrice,mean30Price])
	if statFile != False:		
		with open(statFile, 'a', newline='', encoding='utf-8') as f:
			now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
			print("{}, {}, {}, {}".format(now, minPrice, trendPrice, mean30Price), file=f)
	return workingIterator


#def multiThreadMap(urlList):
#	with ThreadPool(20, initializer=init_process) as p:
#		results = p.map(fun1, urlList):
#		for line in results:

def multiProcess(inputFile, poolSize, proxyPoolSize, nProxy, outFile, statFile, proxyFile, useProxyFile, checkProxyFile, noProxiesMax, signals):
	global prox
	global currentText

	# Error case situations :
	if poolSize < 1:
		print("ERROR : NUMBER OF THREADS CAN'T BE BELOW 1")
		sys.exit(1)
	signals.progress.emit(-1) # change stylesheet to proxy

	# print("-- poolSize : {}, noProxiesMax : {}".format(poolSize, noProxiesMax)) ## DEBUG
	# Proxy scraping/checking :
	if poolSize != 1 and noProxiesMax == 0: # virtually the same thing, noproxies or single thread are the same, no proxies gives more control
		prox = proxyClass(nProxy, proxyPoolSize, proxyFile, useProxyFile, checkProxyFile, signals)

		if proxyFile != '' and checkProxyFile == False and useProxyFile == True:
			currentText = currentText+"\nLaunching scraping without testing the proxies.. \n*pssst* be careful we have a badass here..\n"
			signals.console.emit(currentText)
		else:
			prox.checkProxies()

	currentText = "Setting up the multithreading... \n(please be patient, it takes some time, and the console output isn't very smooth)"
	signals.console.emit(currentText)
	start = time.time()

	# Get input links
	with open(inputFile, 'r') as f:
		urlList=[]
		allLines = f.read().splitlines()
		for url in allLines :
			if url.startswith("http") or url.startswith("www.") :
				urlList.append(url)
		f.close()

	# For each link, put it in dictionnary to check how many occurences there are:
	global urls_occurence_dictionnary
	urls_occurence_dictionnary = {}
	global total_number_of_url
	total_number_of_url = len(urlList)

	for url in urlList:
	    if not url in urls_occurence_dictionnary:
	        urls_occurence_dictionnary[url] = 1
	    else:
	        urls_occurence_dictionnary[url] += 1
	#print(urls_occurence_dictionnary)
	urlList = list(urls_occurence_dictionnary.keys())
	#print(urlList)
	#print("UrlList[0] : {}\nurls_occurence_dictionnary.get(urlList[0]) : {}\n".format(urlList[0], urls_occurence_dictionnary.get(urlList[0])))
	#sys.exit(1)

	signals.progress.emit(-2) # change stylesheet to scraping
	signals.progress.emit(0)
	working_iterator = multiMap(urlList, poolSize, outFile, statFile, signals, noProxiesMax, 'Threads')
	currentText = currentText + "\nOperation lasted {} seconds.".format(round(time.time()-start),3)
	if outFile != False:
		currentText = currentText + "\nSuccessfully wrote output file in :\n{}".format(outFile)
	if statFile != False:
		currentText = currentText + "\nSuccessfully wrote statistics file in :\n{}".format(statFile)
	signals.console.emit(currentText)
	signals.end.emit(working_iterator, total_number_of_url)
