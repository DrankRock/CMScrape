import time, random
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

class headed_scraper:
    def __init__(self):
        load_user_agents()
        options = uc.ChromeOptions()
        options.add_argument("user-agent=" + random.choice(user_agents))

        # Add the Buster extension
        options.add_argument('--load-extension=./buster')

        self.driver = uc.Chrome(options=options)
        self.xpath_item_to_wait="/html/body/main/nav"

        time.sleep(5)

    def set_xpath_wait(self, xpath):
        self.xpath_item_to_wait = xpath

    def get(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.xpath_item_to_wait)))
        return self.driver.page_source

