import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import tempfile

def get_driver():
    # Use the correct path for the system-installed Chromium driver
    service = Service(executable_path="/usr/bin/chromedriver")

    options = Options()
    options.add_argument("--headless=new")  # new headless mode is more stable
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"  # this is key for Chromium!

    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

    # Avoid reusing user-data-dir between sessions
    temp_user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_user_data_dir}")

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def format_url(url):  
    if url.endswith('/'):
        url = url[:-1]
    return url

def scrape_imdb_rating(url, driver = None):

    if driver is None:
        service = Service()
        options = Options()
        options.add_argument("--headless=new")  # new headless mode is more stable
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        temp_user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_user_data_dir}")

        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(service=service,options=options)
    else:
        driver = get_driver()
    driver.get(url)

    # print("rating scrape", url)

    # time.sleep(1)

    # Wait for the histogram to load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="histogram-container"]'))
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


def scrape_imdb_review(url, driver = None):
    if driver is None:
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")


        driver = webdriver.Chrome(service=service,options=options)
        print('got driver')
    else:
        driver = get_driver()
    
    # print('here')
    driver.get(url)

    # print("review scrape", url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section[class="ipc-page-section ipc-page-section--base ipc-page-section--sp-pageMargin"]'))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        all_reviews = soup.select('section[class="ipc-page-section ipc-page-section--base ipc-page-section--sp-pageMargin"]')
        reviews = []
        review_cards = all_reviews[0].select('article[class$="user-review-item"]')

        # print(len(review_cards))
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
        
        return reviews
    except Exception as e:
        print("Reviews not found:")
        return None



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

    # inside docker, second arg = 1

    imdb_review_url = url+'/reviews/?ref_=tt_ururv_sm'
    reviews = scrape_imdb_review(imdb_review_url,1)


    imdb_rating_url = url+'/ratings/?ref_=tt_ov_rat'   
    reactions = scrape_imdb_rating(imdb_rating_url,1)
    # print(reactions)


    response_dict = {
        "title": title,
        "description": description,
        "reactions": reactions,
        "reviews": reviews
    } 
    
    # print("completed", len(reviews))
    
    return json.dumps(response_dict,indent=4)



# movie_url = 'https://www.imdb.com/title/tt1825683'
# review_dict = scrape_imdb(movie_url)
# print(review_dict)


