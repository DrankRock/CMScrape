import undetected_chromedriver as uc
import pandas as pd
import random
import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import scrapers

# As you can maybe see, the core has been heavily simplified
# multithreading is quite the bi**h and making it work was tough.

user_agents = []
urls_occurrences_dictionnary = {}
total_number_of_url = 0
output_data = []
global _signals

def file_to_list(filename):
	with open(filename, 'r') as file:
		lines = file.read().splitlines()
	return lines

def load_user_agents():
	global user_agents
	user_agents = file_to_list("chrome_useragents.csv")

def get_header():
	user_agent = random.choice(user_agents)	
	return {
		'Host': 'www.cardmarket.com',
		'User-Agent': user_agent,
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
	}

def request(url):
	# randomized header data for realism
	try:
		# options (header data, headless)
		options = uc.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument("user-agent="+random.choice(user_agents))
		  


		# driver is what's dwelling in the web
		driver = uc.Chrome(options=options)

		# *drum rolls*
		driver.get(url)

		# wait for the title of the page to be there
		element = WebDriverWait(driver, 70).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div[3]/div[1]/h1')))
		_signals.emit(element.text)
		soup = BeautifulSoup(driver.page_source, 'lxml')
		list_scrap = scrapers.CMSoupScraper(url, soup)
		output_data.append(list_scrap)
		''' # Temporarily commented, i will use the previous code for now, then switch there
		# because this snippet is objectively better, shorter, clearer, and processes less info
		dl_elements = driver.find_element(By.CSS_SELECTOR,".labeled")
		inner_html = dl_elements.get_attribute("innerHTML")
		dd_elements = re.findall(r'<dd(.*?)</dd>', inner_html)
		dt_elements = re.findall(r'<dt(.*?)</dt>', inner_html)
		if (len(dd_elements) != len(dt_elements)):
			print("Uh Oh ... (it seems like the scraping failed somewhere)")
		else :
			out_data = []
			for i in range(0, len(dd_elements)):
				name = re.findall(r'\">(.*)', dt_elements[i])[0]
				value = re.findall(r'\">(.*)', dd_elements[i])[0].replace("<span>", "").replace("</span>", "")
				if name == "Rarity":
					value = re.findall(r'data-original-title="(.*?)"', value)[0]
				if name == "Reprints":
					value = re.findall(r' \((.*?)\)</a>', value)[0]
				if name == "Printed in":
					value = re.findall(r'class="mb-2">(.*?)</a>', value)[0]
				out_data.append(value)
				#print("["+str(i)+"]"+" "+name+" | "+value)
			global output_data
			output_data.append(out_data)
			'''


	except Exception as exp:
		print("An error occured while trying to scrape "+url)
		print("Please note that this version was never tested on anything else than yugioh.")
		print("If you want to report the error, it is : \n"+str(exp))
	# Getting the HTML content of the page
	#return driver

def scrape_data(driver):
	# dl_elements = driver.find_elements_by_xpath('//dl[@class="labeled row mx-auto no-gutters"]')

	# Iterate over each dl element and find dt and dd within
	data = []
	for dl in dl_elements:
		dt_elements = dl.find_elements_by_tag_name('dt')
		dd_elements = dl.find_elements_by_tag_name('dd')

		# Make sure we have the same number of dt and dd elements
		assert len(dt_elements) == len(dd_elements), "Mismatch in number of dt and dd elements"

		# Extract the text and create a list of [dt, dd] pairs
		data.extend([[dt.text, dd.text] for dt, dd in zip(dt_elements, dd_elements)])
	for elem in data:
		print(elem[0]+" : "+elem[1])


def core_run(input_file, output_file, signals, signal_list):
	global _signals
	_signals = signals
	_signals.emit("Load user agents")
	load_user_agents()
	_signals.emit("Read input")
	input_data = file_to_list(input_file)
	_signals.emit("Found "+str(len(input_data))+" lines")

	global urls_occurrences_dictionnary
	global total_number_of_url
	urls_occurrences_dictionnary = {}
	total_number_of_url = len(input_data)

	for url in input_data:
		if not url in urls_occurrences_dictionnary:
			urls_occurrences_dictionnary[url] = 1
		else:
			urls_occurrences_dictionnary[url] += 1
		# print(urls_occurrences_dictionnary)
	url_list = list(urls_occurrences_dictionnary.keys())

	_signals.emit("Reduced to "+str(len(url_list))+" single lines")

	for single_url in url_list :
		request(single_url)

	print ("Successfully scraped "+str(len(output_data))+" urls")
	signal_list.emit(output_data)

	