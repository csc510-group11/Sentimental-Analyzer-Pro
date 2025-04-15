import requests
from bs4 import BeautifulSoup
import json

def scrape_tripadvisor(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(response.status_code)

    # Get title/heading
    title = soup.find("h1").get_text(strip=True)
    description = soup.select_one('div[class="biGQs _P pZUbB avBIb KxBGd"]').get_text(strip=True)
    rating_histogram = soup.select('div[class="AugPH w u"]')
    bars = rating_histogram[0].find_all("div", class_="jxnKb")
    reactions = {}
    for bar in bars:
        label = bar.find("div", class_="Ygqck o W q").get_text(strip=True)
        count = bar.find("div", class_="biGQs _P fiohW biKBZ osNWb").get_text(strip=True)
        reactions[label] = count

    all_reviews = soup.select('div[class="zwgAY"]')
    review_cards = all_reviews[0].find_all("div", class_="_c")
    reviews = []
    # print(review_cards[0])
    for card in review_cards:
        review_title = card.find("div", class_="biGQs _P fiohW qWPrE ncFvv fOtGX").get_text(strip=True)
        review_text = card.find("div", class_="biGQs _P pZUbB KxBGd").get_text(strip=True) 
        bubble = card.find("title", string=lambda text: "bubbles" in text).get_text(strip=True)
        whole_review = review_title+'\n'+review_text
        reviews.append({"review": whole_review, "rating": bubble})

    response_dict = {
        "title": title,
        "description": description,
        "reactions": reactions,
        "reviews": reviews
    }

    return json.dumps(response_dict, indent=4)

# Example usage
# title, description, reactions, reviews = scrape_tripadvisor("https://www.tripadvisor.com/Restaurant_Review-g34227-d3192530-Reviews-15th_Street_Fisheries-Fort_Lauderdale_Broward_County_Florida.html")
# print(f"Title: {title}")
# print(f"Description: {description}")
# print(f"Reactions: {reactions}")
# print(f"Reviews: {reviews}")

