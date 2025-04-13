import json
import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
import logging
import html
from functools import lru_cache
from ..cache_manager import NewsCache


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"

news_cache = NewsCache()

# This method scraps article using google news that match the relevant query and dumps it on news.json file
def scrapNews(topicName, nums, jsonOutput=True):
    cache_key = f"{topicName}_{nums}"
    cached_result = news_cache.get(cache_key)
    if cached_result:
        logging.info(f"Retrieved results from cache for {topicName}")
        if jsonOutput:
            with open("sentimental_analysis/realworld/news.json", "w") as json_file:
                json.dump(cached_result, json_file)
        return cached_result


    article_list = []
    news_results = getNewsResults(topicName, nums * 20)
    config = Config()
    config.browser_user_agent = user_agent
    count = nums

    for url in news_results:
        if count == 0:
            break
        try:
            article = Article(url, config=config, language="en")
            article.download()
            article.parse()

            # Skipping websites requiring JS
            if len(article.text) < 250:
                logging.info(f"Skipping article as it requires JS - {url}")
                continue

            # NLP on the article
            article.nlp()
            summary_dict = {}

            # Extract summary and unescape the HTML entities
            summary_dict["Summary"] = html.unescape(article.summary)
            article_list.append(summary_dict)
            count -= 1
        except BaseException as e:
            logging.info(
                f"Error occured while extracting summary of article - {url}\nError - {e}"
            )

    news_cache.set(cache_key, article_list)

    if jsonOutput == True:
        with open("news.json", "w") as json_file:
            json.dump(article_list, json_file)

    logging.warning("Articles saved to news.json")
    return article_list


# This method returns URLs to news websites matching the relevant query
def getNewsResults(query, nums):
    headers = {"User-Agent": user_agent}

    base_url = f"https://www.google.com/search?q={query}&gl=us&tbm=nws&num={nums}"
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    news_results = []

    for el in soup.select("div.SoaBEf"):
        news_results.append(el.find("a")["href"])
    return news_results
