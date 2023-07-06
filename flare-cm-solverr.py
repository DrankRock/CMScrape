import subprocess
import requests
from scrapers import CMSoupScraper

from bs4 import BeautifulSoup

def exec_bash(script_path):
    command = f'bash {script_path}'
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error executing the bash script: {}".format(e))

init_bash = './init_flaresolverr.sh'

exec_bash(init_bash)

post_body = {
  "cmd": "request.get",
  "url":"https://www.cardmarket.com/en/YuGiOh/Products/Singles/Cyberstorm-Access/Time-Tearing-Morganite",
  "maxTimeout": 60000
}

response = requests.post('http://localhost:8191/v1', headers={'Content-Type': 'application/json'}, json=post_body)

print(response.text)
# convert to soup
soup = BeautifulSoup(response.text, 'lxml')
returnList = CMSoupScraper(post_body['url'], soup)
for elem in returnList :
    print("[X] ", elem)
