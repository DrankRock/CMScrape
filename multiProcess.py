import csv
import os
import sys
import traceback
import random
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Pool

import undetected_chromedriver as uc
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import findTopSellers
import scrapers
from scrapeAndCheck import *
from findTopSellers import *

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
}, {
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
}, {
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
}, {
    'Host': 'www.cardmarket.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/91.0.4472.124 Safari/537.36',
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


@dataclass(frozen=True)
class URLDataclass:
    url: str
    attribute: str


# input_url = 'https://www.cardmarket.com/en'
global TIME_MAX
global CURRENT_VALUE_PROXYLESS
global MAX_PROXYLESS_REQUESTS
global ACTIVATE_ATTRIBUTES

ACTIVATE_ATTRIBUTES = False

prox = None
session = None
currentText = ""
urls_occurrences_dictionnary = {}
total_number_of_url = 0
check_sellers = False
n_sellers = 0

SLEEP_TIME = 5

'''
STATUS : 
 -- 200 : OK
 -- 404 : NOT FOUND	
 -- 429 : TOO MANY REQUESTS
'''

def read_csv_file(filename):
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # Extract the data from the first column and remove the surrounding double quotes
            if len(row) > 0:
                first_column_data = row[0].strip('"')
                data.append(first_column_data)
    return data

user_agents_data = read_csv_file("chrome_useragents.csv")

def get_header():
    user_agent = random.choice(user_agents_data)    
    return {
        'Host': 'www.cardmarket.com',
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }

def init_process():
    global session
    session = requests.Session()


def fun1(input_url):
    tries = 1
    working = True
    while True:
        try:
            if tries >= 13:
                raise ValueError("REQUEST NOT WORKING AFTER 70 SEC")
            '''
            proxy = prox.randomProxy()
            proxyDict = {'http': proxy, 'https': proxy}
            headers = get_header()
            response = session.get(input_url.url, headers=headers, proxies=proxyDict, timeout=5)
            if response.status_code == 429:
                raise ValueError("TOO MANY REQUESTS")
                '''
            options = uc.ChromeOptions()

            

            driver = uc.Chrome(options=options)

            driver.get(input_url.url)

            element = WebDriverWait(driver, 70).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div[3]/div[1]/h1')))

            # Print the content of the element
            print(element.text)


            # Note: We can't directly access HTTP status code via Selenium

            # Getting the HTML content of the page
            html_content = driver.page_source


        # text = "Status_code : {} - proxy : {} - {} tries".format(response.status_code,proxy,tries)
        except Exception as exp:
            if tries >= 14:
                working = False
                break
            else:
                tries = tries + 1
                time.sleep(SLEEP_TIME)
                continue
        break
    if working:
        soup = BeautifulSoup(html_content, 'lxml')
        list_scrap = scrapers.CMSoupScraper(input_url.url, soup)
        sellers = []
        if check_sellers and list_scrap != -1:
            sellers = findTopSellers.soupToTopXSellers(soup, n_sellers)
        if list_scrap != -1:
            list_scrap.insert(0, input_url.attribute)
        return list_scrap, sellers
    else:
        return -1, -1


def fun1_noProxies(input_url):
    tries = 0
    working = True
    while True:
        try:
            print("Trying ...")
            if tries >= 13:
                raise ValueError("REQUEST NOT WORKING AFTER 70 SEC")
            headers = get_header()
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            for key, value in get_header().items():
                options.add_argument(f"--header={key}:{value}")

            # options.add_argument('--proxy-server=%s' % proxy)
            driver = uc.Chrome(options=options)

            

            driver.get(input_url.url)

            element = WebDriverWait(driver, 70).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div[3]/div[1]/h1')))

            # Print the content of the element
            print(element.text)


            # Note: We can't directly access HTTP status code via Selenium

            # Getting the HTML content of the page
            html_content = driver.page_source

        # text = "Status_code : {} - proxy : {} - {} tries".format(response.status_code,proxy,tries)
        except Exception as e:
            print("Error : "+str(e))
            if tries >= 14:
                working = False
                break
            else:
                tries = tries + 1
                time.sleep(SLEEP_TIME)
                continue
        break
    if working :
        soup = BeautifulSoup(html_content, 'lxml')
        list_scrap = scrapers.CMSoupScraper(input_url.url, soup)
        sellers = []
        if check_sellers and list_scrap != -1:
            sellers = findTopSellers.soupToTopXSellers(soup, n_sellers)
        if list_scrap != -1 :
            list_scrap.insert(0, input_url.attribute)
        return list_scrap, sellers
    else :
        return -1, -1


def multiMap(url_list, pool_size, out_file, stat_file, signals, no_proxies_max, check_top_sellers, n_top_sellers,
             top_seller_name, pool_type):
    global currentText
    # print("multimap start")

    if out_file:
        opened_outfile = open(out_file, 'w', newline='', encoding='utf-8')
    else:
        opened_outfile = open(os.devnull, 'w', newline='')

    # if out_file is not set, it is "False".
    if not out_file :
        output_file_name = "output.csv"
    else :
        output_file_name = out_file
    extension = output_file_name.split(".")[-1]
    name = ''.join(output_file_name.split(".")[:-1])
    opened_outfile_sellers = name+"_sellers"+extension

    if check_top_sellers :
        if top_seller_name != "":
            if not "." in top_seller_name :
                top_seller_name = top_seller_name+".csv"
            opened_outfile_sellers = open(top_seller_name, 'w', newline='', encoding='utf-8')
        else :
            opened_outfile_sellers = open(opened_outfile_sellers, 'w', newline='', encoding='utf-8')
    global check_sellers
    check_sellers = check_top_sellers
    global n_sellers
    n_sellers = n_top_sellers
    # setup csv_writer for the output file
    csv_writer = csv.writer(opened_outfile)
    csv_writer.writerow(
        ['attribute', 'game', 'item', 'extension', 'number', 'name', 'min_price', 'price_trend', 'mean30d_price',
         'language', 'sellerCountry', 'sellerType', 'minCondition', 'isSigned', 'isFirstEd', 'isPlayset', 'isAltered', 'isReverseHolo',
         'isFoil', 'input_url'])
    csv_writer_sellers = None
    if check_top_sellers :
        csv_writer_sellers = csv.writer(opened_outfile_sellers,delimiter=',', quotechar='"')
        csv_writer_sellers.writerow(
            ['Game', 'Card extension', 'Number', 'Card name','seller country', 'seller name', 'seller type', 'badge', 'infos', 'price', 'number', 'url']
        )

    currentText = "Starting multithreading for scraping ..."
    signals.console.emit(currentText)

    # variables
    iterator = 1
    working_iterator = 0
    minPrice = 0.0
    trendPrice = 0.0
    mean30Price = 0.0

    if no_proxies_max == "True":
        pool_size = 1
    if pool_type == 'Threads':
        p = ThreadPool(pool_size, initializer=init_process)
    elif pool_type == 'Processes':
        p = Pool(pool_size, initializer=init_process)
    else:
        print("Unknown PoolType '{}' in multiMap (multiprocess.py).".format(pool_type))
        sys.exit(1)
    # print("multimap start scraping")
    # Force single thread
    pool_size = 1

    if pool_size == 1:
        for currentURL in url_list:
            scrapes, sellers = fun1_noProxies(currentURL)
            if scrapes != -1:
                for iteration in range(urls_occurrences_dictionnary.get(currentURL)):
                    try:
                        if scrapes[6] != "N/A":
                            minPrice += float(scrapes[6])
                        if scrapes[7] != "N/A":
                            trendPrice += float(scrapes[7])
                        if scrapes[8] != "N/A":
                            mean30Price += float(scrapes[8])
                    except Exception as e:
                        pass
                    currentText = "[{}/{}] Prices: \n\tTotal minimum price = {}; \n\tTotal trending price = {}; \n" \
                                  "\tTotal mean 30d price = {}\n(please be patient, it takes some time, " \
                                  "and the console output isn't very smooth)".format(
                        iterator, total_number_of_url, round(minPrice, 3), round(trendPrice, 3), round(mean30Price, 3))
                    signals.console.emit(currentText)
                    signals.progress.emit(round(float(iterator) / total_number_of_url * 100))
                    working_iterator += 1
                    csv_writer.writerow(scrapes)
                    iterator += 1
                if len(sellers) != 0:
                    if check_top_sellers:
                        list_scrap = [scrapes[1], scrapes[3], scrapes[4], scrapes[5]]
                        for seller in sellers:
                            seller_list = list_scrap[:]
                            seller_list += seller
                            seller_list.append(scrapes[-1])
                            csv_writer_sellers.writerow(seller_list)

    else:
        my_function = fun1
        try:
            for scrapes, sellers in p.imap(my_function, url_list):
                if scrapes != -1:
                    current_url = str(scrapes[len(scrapes) - 1]).replace('"', '')
                    temp_url_dc = URLDataclass(current_url, scrapes[0])
                    for iteration in range(urls_occurrences_dictionnary.get(temp_url_dc)):
                        try:
                            if scrapes[6] != 'None':
                                minPrice += float(scrapes[6])
                            if scrapes[7] != 'None':
                                trendPrice += float(scrapes[7])
                            if scrapes[8] != 'None':
                                mean30Price += float(scrapes[8])
                        except:
                            pass
                        currentText = "[{}/{}] Prices: \n\tTotal minimum price = {}; \n\tTotal trending price = {}; \n" \
                                      "\tTotal mean 30d price = {}\n(please be patient, it takes some time, " \
                                      "and the console output isn't very smooth)".format(
                            iterator, total_number_of_url, round(minPrice, 3), round(trendPrice, 3),
                            round(mean30Price, 3))
                        signals.console.emit(currentText)
                        signals.progress.emit(round(float(iterator) / total_number_of_url * 100))
                        working_iterator += 1
                        csv_writer.writerow(scrapes)
                        iterator += 1
                    if len(sellers) != 0:
                        if check_top_sellers:
                            list_scrap = [scrapes[1], scrapes[2], scrapes[3]]
                            for seller in sellers:
                                seller_list = list_scrap[:]
                                seller_list += seller
                                seller_list.append(scrapes[-1])
                                csv_writer_sellers.writerow(seller_list)

        except Exception as e:
            print("Exception caught during scraping : \n{}".format(traceback.format_exc()))
            print("[WARNING]\nPlease wait for the processes to safely quit")
        finally:
            p.close()
            p.join()
            print("Processes stopped.")
    currentText = currentText + "\nSuccessfully scraped {} out of {} links.".format(working_iterator,
                                                                                    total_number_of_url)
    signals.console.emit(currentText)
    csv_writer.writerow(
        ['', '', '', 'Number of cards', working_iterator, 'Total Prices:', minPrice, trendPrice, mean30Price])
    if not ACTIVATE_ATTRIBUTES and out_file != False:
        opened_outfile.close()
        opened_outfile = open(out_file, 'r', newline='', encoding='utf-8')
        csv_reader = csv.reader(opened_outfile)
        csv_copy = []
        for row in csv_reader:
            csv_copy.append(row)
        opened_outfile.close()
        opened_outfile = open(out_file, 'w+', newline='', encoding='utf-8')
        opened_outfile.close()
        opened_outfile = open(out_file, 'w', newline='', encoding='utf-8')
        csv_writer = csv.writer(opened_outfile)
        for row in csv_copy:
            csv_writer.writerow(row[1:])
        opened_outfile.close()

    if stat_file:
        with open(stat_file, 'a', newline='', encoding='utf-8') as f:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print("{}, {}, {}, {}".format(now, minPrice, trendPrice, mean30Price), file=f)
    return working_iterator


def multiProcess(input_file, pool_size, proxy_pool_size, n_proxy, out_file, stat_file, proxy_file, use_proxy_file,
                 check_proxy_file, no_proxies_max, check_top_sellers, n_top_sellers, top_seller_name, signals):
    global prox
    global currentText

    # Error case situations :
    if pool_size < 1:
        print("ERROR : NUMBER OF THREADS CAN'T BE BELOW 1")
        sys.exit(1)
    signals.progress.emit(-1)  # change stylesheet to proxy
    # print("-- pool_size : {}, no_proxies_max : {}".format(pool_size, no_proxies_max)) ## DEBUG
    # Proxy scraping/checking :
    # virtually the same thing, no proxies or single thread are the same, no proxies gives more control
    # removed if because proxies are always happening
    # prox = proxyClass(n_proxy, proxy_pool_size, proxy_file, use_proxy_file, check_proxy_file, signals)

    signals.console.emit(currentText)
    start = time.time()

    # Get input links
    global ACTIVATE_ATTRIBUTES
    with open(input_file, 'r') as f:
        urlList = []
        currentAttribute = ""
        allLines = f.read().splitlines()
        for url in allLines:
            if url.startswith("#"):
                ACTIVATE_ATTRIBUTES = True
                currentAttribute = url[1:]
            if url.startswith("http") or url.startswith("www."):
                u = URLDataclass(url, currentAttribute)
                urlList.append(u)
        f.close()

    # For each link, put it in dictionary to check how many occurrences there are:
    global urls_occurrences_dictionnary
    global total_number_of_url
    urls_occurrences_dictionnary = {}
    total_number_of_url = len(urlList)

    for url in urlList:
        if not url in urls_occurrences_dictionnary:
            urls_occurrences_dictionnary[url] = 1
        else:
            urls_occurrences_dictionnary[url] += 1
        # print(urls_occurrences_dictionnary)
    urlList = list(urls_occurrences_dictionnary.keys())

    signals.progress.emit(-2)  # change stylesheet to scraping
    signals.progress.emit(0)
    working_iterator = multiMap(urlList, pool_size, out_file, stat_file, signals, no_proxies_max, check_top_sellers,
                                n_top_sellers, top_seller_name, 'Threads')
    currentText = currentText + "\nOperation lasted {} seconds.".format(round(time.time() - start), 3)
    if out_file:
        currentText = currentText + "\nSuccessfully wrote output file in :\n{}".format(out_file)
    if stat_file:
        currentText = currentText + "\nSuccessfully wrote statistics file in :\n{}".format(stat_file)
    signals.console.emit(currentText)
    signals.end.emit(working_iterator, total_number_of_url)
