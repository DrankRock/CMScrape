import multiprocessing, time, requests, random, cchardet, lxml, csv, os, sys

from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
from requests.adapters import HTTPAdapter
from datetime import datetime
from PyQt5 import QtWidgets

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

def multiProcessMap(urlList, poolSize, outFile, statFile,consoleDisp):
	if outFile != False:		
		opened_outFile = open(outFile, 'w')
	else:
		opened_outFile = open(os.devnull, 'w')
	csv_writer = csv.writer(opened_outFile)
	csv_writer.writerow(['game','item','extension','number','name','min_price','price_trend','mean30d_price','language','sellerType','minCondition','isSigned','isFirstEd','isPlayset','isAltered','isReverseHolo','isFoil','url'])

	iterator = 1
	workingIterator = 0
	nURL = len(urlList)
	minPrice = 0.0
	trendPrice = 0.0
	mean30Price = 0.0
	with Pool(poolSize, initializer=init_process) as p:
		try:
			for scrapes in p.imap(fun1, urlList):
				if scrapes != -1:
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
					consoleDisp.setPlainText("[{}/{}] Prices: \n\tTotal minimum price = {}; \n\tTotal trending price = {}; \n\tTotal mean 30d price = {}".format(iterator, nURL,round(minPrice,3),round(trendPrice,3),round(mean30Price,3)))
					QtWidgets.QApplication.processEvents()
					workingIterator += 1
					csv_writer.writerow(scrapes)
				iterator += 1
		except:
			print("[WARNING]\nPlease wait for the processes to safely quit")
			p.terminate()
			p.join()
			print("Processes stopped.")
	print("\nSuccessfully scraped {} out of {} links.".format(workingIterator, nURL))
	p.terminate()
	p.join()
	csv_writer.writerow(['','','Number of cards',workingIterator,'Total Prices:',minPrice,trendPrice,mean30Price])
	if statFile != False:		
		with open(statFile, 'a') as f:
			now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
			print("{}, {}, {}, {}".format(now, minPrice, trendPrice, mean30Price), file=f)

#def multiThreadMap(urlList):
#	with ThreadPool(20, initializer=init_process) as p:
#		results = p.map(fun1, urlList):
#		for line in results:

def multiProcess(inputFile, poolSize, nProxy, outFile, statFile, consoleDisp):
	global prox
	if poolSize < 1:
		print("ERROR : NUMBER OF THREADS CAN'T BE BELOW 1")
		sys.exit(1)
	prox = proxyClass(False, nProxy, consoleDisp)
	prox.checkProxies()

	start = time.time()

	with open(inputFile, 'r') as f:
		urlList = f.read().splitlines()
	f.close()

	output_list = multiProcessMap(urlList, poolSize, outFile, statFile, consoleDisp)
	consoleDisp.setPlainText(consoleDisp.toPlainText()+"\n"+"Operation laster {} seconds".format(round(time.time()-start),3))
	QtWidgets.QApplication.processEvents()