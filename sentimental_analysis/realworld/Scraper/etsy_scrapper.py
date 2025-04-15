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
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    # options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    reviews = []

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-buy-box-listing-title="true"]'))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.select_one('h1[data-buy-box-listing-title="true"]').get_text(strip=True)
        WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="same-listing-reviews-panel"]'))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        all_reviews = soup.select('div[id="same-listing-reviews-panel"]')
        review_cards = all_reviews[0].find_all("div", class_="wt-grid__item-xs-12 review-card")
        for review in review_cards:
            stars = review.select('span[class="wt-screen-reader-only"]')[0].get_text(strip=True)
            review_title = review.select('p[id^="review-preview-toggle-"]')[0].get_text(strip=True)
        # review_title = reviews_and_stars[0].select('p[id="review-preview-toggle-01744694165"]')
        # stars = reviews_and_stars[0].select('span[class="wt-screen-reader-only"]')
            print(stars, review_title)
            reviews.append({"review": review_title, "rating": stars})

        response_dict = {
            "title": title,
            "reviews": reviews
        }
        return json.dumps(response_dict, indent=4)
    except Exception as e:
        print("Title not found:")
        return None
    finally:
        driver.quit()