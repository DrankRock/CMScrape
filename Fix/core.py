import undetected_chromedriver as uc
import pandas as pd
import random

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

# As you can maybe see, the core has been heavily simplified
# multithreading is quite the bi**h and making it work was tough.

user_agents = []
urls_occurrences_dictionnary = {}
total_number_of_url = 0

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
	print(element.text)
	dl_elements = driver.find_element(By.CSS_SELECTOR,".labeled")
	print(dl_elements)
	# Iterate over each dl element and find dt and dd within
	data = []
	for dl in dl_elements:
		dt_elements = dl.find_elements_by_tag_name('dt')
		dd_elements = dl.find_elements_by_tag_name('dd')

		# Make sure we have the same number of dt and dd elements
		assert len(dt_elements) == len(dd_elements), "Mismatch in number of dt and dd elements"

		# Extract the text and create a list of [dt, dd] pairs
		data.extend([[dt.text, dd.text] for dt, dd in zip(dt_elements, dd_elements)])

	# Print the extracted data
	for pair in data:
		print(pair)

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


def core_run(input_file, output_file, signals):
	signals.emit("Load user agents")
	load_user_agents()
	signals.emit("Read input")
	input_data = file_to_list(input_file)
	signals.emit("Found "+str(len(input_data))+" lines")

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

	signals.emit("Reduced to "+str(len(url_list))+" single lines")

	for single_url in url_list :
		request(single_url)
	