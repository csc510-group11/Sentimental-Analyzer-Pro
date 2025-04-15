import requests
from bs4 import BeautifulSoup
import json

def scrape_goodreads_reviews(book_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(book_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    # print(soup)

    book_title = soup.select_one('h1[data-testid="bookTitle"]').get_text(strip=True)
    description = soup.select_one('div[data-testid="description"]').get_text(strip=True)
    shelfstatus = soup.select('div[class="ShelfStatus"]')
    all_reviews = soup.select('section[class="ReviewText__content"]')
    rating_histogram = soup.select('div[class="RatingsHistogram RatingsHistogram__interactive"]')
    reactions = {}
    bars = rating_histogram[0].find_all("div", class_="RatingsHistogram__bar")
    for bar in bars:
        star = bar.get("aria-label", "").split()[0]
        count = bar.select_one(".RatingsHistogram__labelTotal")
        if star and count:
            reactions[str(star)+' stars'] = count.get_text(strip=True)

    reviews = []
    i = 0
    for review_div in all_reviews:
        consider = shelfstatus[i].find('span', class_='RatingStars RatingStars__small') if shelfstatus[i] else None
        if consider == None:
            i += 1
            continue

        review_text = review_div.get_text(strip=True)
        if review_text:
            rating_text = consider.get("aria-label", None)
            reviews.append({"review": review_text, "rating": rating_text})
            i += 1

    response_dict = {
        "title": book_title,
        "description": description,
        "reactions": reactions,
        "reviews": reviews
    }
    return json.dumps(response_dict, indent=4)

# if __name__ == "__main__":
#     book_url = "https://www.goodreads.com/book/show/2767052-the-hunger-games"
#     book_title,description,reactions,reviews = scrape_goodreads_reviews(book_url)

 
    # for review in reviews:
    #     print(review, '\n\n\n\n')

