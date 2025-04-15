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


def format_url(url):  
    if url.endswith('/'):
        url = url[:-1]
    return url

def scrape_imdb_selenium(url):
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=service,options=options)

    driver.get(url)

    # time.sleep(1)

    # Wait for the histogram to load
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





def scrape_imdb(url):
    url = format_url(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        # "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.select('span[class="hero__primary-text"]')[0].get_text(strip=True)
    description = soup.select('span[data-testid="plot-xs_to_m"]')[0].get_text(strip=True)
    reactions = {}


    # print(title)
    # print(description)

    imdb_rating_url = url+'/ratings/?ref_=tt_ov_rat'
    reactions = scrape_imdb_selenium(imdb_rating_url)
    # print(reactions)

    imdb_review_url = url+'/reviews/?ref_=tt_ururv_sm'
    response = requests.get(imdb_review_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_reviews = soup.select('section[class="ipc-page-section ipc-page-section--base ipc-page-section--sp-pageMargin"]')
    review_cards = all_reviews[0].find_all("article", class_="sc-8c92b587-1 cwztqu user-review-item")
    reviews = []
    for review in review_cards:
        review_title_raw = review.find("h3", class_="ipc-title__text")
        review_title = review_title_raw.get_text(strip=True) if review_title_raw else 'Not Given'
        star_raw = review.find("span", class_="ipc-rating-star--rating")
        star = star_raw.get_text(strip=True)+"/10" if star_raw else None
        review_text_raw = review.find("div", class_="ipc-html-content-inner-div")
        review_text = review_text_raw.get_text(strip=True) if review_text_raw else None

        if review_text is None:
            continue
            
        whole_review = review_title+'\n'+review_text
        reviews.append({"review": whole_review, "rating": star})
    
    # print(reviews)

    response_dict = {
        "title": title,
        "description": description,
        "reactions": reactions,
        "reviews": reviews
    } 
    
    # print("completed", len(reviews))
    
    return json.dumps(response_dict,indent=4)


