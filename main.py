import os
import scrape
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# make sure no other browers are open
os.system("pkill -f -9 chromium")

options = Options()
options.add_argument('--headless')

service = Service(executable_path='/usr/bin/chromedriver')

driver = webdriver.Chrome(options, service)

#start_url = "https://parkingtickets.cityofmadison.com/"

#driver.get(start_url)
driver.get("https://www.google.com")
print(driver.title)
driver.quit()
