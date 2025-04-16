def scrape_reviews(url, category):
    if category == "restaurant":
        from .tripadvisor_scrapper import scrape_tripadvisor
        return scrape_tripadvisor(url)
    elif category == "product":
        from .etsy_scrapper import scrape_etsy
        return scrape_etsy(url)
    elif category == "movie":
        from .imdb_scrapper import scrape_imdb
        return scrape_imdb(url)
    elif category == "book":
        from .goodreads_scrapper import scrape_goodreads_reviews
        return scrape_goodreads_reviews(url)
    else:
        raise ValueError("Invalid category. Choose from 'restaurant', 'product', 'movie', or 'book'.")
    