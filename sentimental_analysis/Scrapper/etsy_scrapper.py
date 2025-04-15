import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

def scrape_etsy(url):
    service = Service()
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-gpu')
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=service,options=options)
    driver.get(url)

    # input("Solve CAPTCHA manually in the browser, then press Enter here to continue...")
    time.sleep(1)  # Wait for a few seconds to ensure the page loads completely
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="sc-376e51f1-9 eDjlwl"]'))
        )
        i = 10
        soup = BeautifulSoup(driver.page_source, "html.parser")
        reactions = {}
        # r = soup.select('text[id="chart-bar-1-labels-0"]')\
        
        tspan = soup.select('text[id^="chart-bar-1-labels-"] tspan')
        for p in tspan:
            reactions[i] = p.text.split()[0]
            i -= 1
        return reactions
    except Exception as e:
        print("Histogram not found:")
        return None
    finally:
        driver.quit()



etsy_url = "https://www.etsy.com/listing/1807768177/set-of-3-black-kaws-in-shower-bathroom"