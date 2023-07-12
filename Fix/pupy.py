from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = None
wait = None

link = 'https://sourceforge.net/'
cloudflare_xpath='//*[@id="challenge-stage"]/div/label/input'

def create():
    chrome_options = Options()
    # chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_extension('./I-don-t-care-about-cookies.crx')
    chrome_options.add_extension('./Buster-Captcha-Solver-for-Humans.crx')
    chrome_options.add_extension('./I-m-not-robot-captcha-clicker.crx')
    # chrome_options.add_argument('--load-extension=./I-don-t-care-about-cookies')
    global driver
    driver = webdriver.Chrome(options=chrome_options)
    global wait
    wait = WebDriverWait(driver, 20)


def main():
    driver.get(link)
    # wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/nav')))
    time.sleep(30)
    strr = driver.title

    return strr


create()
i = 1
while True:
    print(f'[{i}] - {main()}')
    i += 1
