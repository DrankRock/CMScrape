import undetected_chromedriver as uc
import pandas as pd
import random
import re
import json

from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

user_agents = []
urls_occurrences_dictionnary = {}
total_number_of_url = 0
output_data = []
global _signals


def request(url):
    # options (header data, headless)
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("user-agent=" + random.choice(user_agents))

    # driver is what's dwelling in the web
    driver = uc.Chrome(options=options)

    # *drum rolls*
    driver.get(url)
    return driver.page_source


def file_to_list(filename):
    with open(filename, 'r') as file:
        lines = file.read().splitlines()
    return lines


def geonode():
    link = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&filterLastChecked=30&filterUpTime=90&anonymityLevel=elite&anonymityLevel=anonymous"
    page_source = request(link)
    _list = []
    ips = re.findall(r'\"ip\":\"(.*?)\"', page_source)
    ports = re.findall('\",\"port\":\"(.*?)\",\"', page_source)
    protocols = re.findall(r'protocols\":\[(.*?)]', page_source)
    for i in range(len(ips)):
        prot = protocols[i]
        prot = prot.replace('"', '')
        if "," in prot:
            for pro in prot.split(','):
                print(f'{pro}://{ips[i]}:{ports[i]}')
                _list.append(f'{pro}://{ips[i]}:{ports[i]}')
        else:
            print(f'{prot}://{ips[i]}:{ports[i]}')
            _list.append(f'{prot}://{ips[i]}:{ports[i]}')
    return _list

def proxyscrape():
    link = "https://api.proxyscrape.com/proxytable.php?nf=true&country=all"
    page_source = request(link)
    json_data = page_source.replace("<html><head></head><body>", "").replace("</body></html>", "")
    data = json.loads(json_data)

    for key, value in data.items():
        print(value)
        regex = re.findall(r'{\'(.*?)\': \{\'ano', str(value))
        for elem in regex:
            print(f'{key}://{elem}')
        # load_json = json.loads(value)
        # print(value)
    # print(data)


def load_user_agents():
    global user_agents
    user_agents = file_to_list("chrome_useragents.csv")


class ProxyChecker:
    def __init__(self):
        self.proxy_list = []
        load_user_agents()

    def scrape(self):
        #for elem in geonode():
        #    self.proxy_list.append(elem)

        proxyscrape()


pc = ProxyChecker()
pc.scrape()
