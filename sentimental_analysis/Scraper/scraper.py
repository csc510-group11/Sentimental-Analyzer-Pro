def scrape_data(url, category):
    if category == "restaurant":
        from tripadvisor_scrapper import scrape_tripadvisor
        return scrape_tripadvisor(url)
    elif category == "product":
        from etsy_scrapper import scrape_etsy
        return scrape_etsy(url)
    elif category == "movie":
        from imdb_scrapper import scrape_imdb
        return scrape_imdb(url)
    elif category == "book":
        from goodreads_scrapper import scrape_goodreads_reviews
        return scrape_goodreads_reviews(url)
    else:
        raise ValueError("Invalid category. Choose from 'restaurant', 'product', 'movie', or 'book'.")
    
if __name__ == "__main__":
    # Example usage
    url = "https://www.tripadvisor.com/Restaurant_Review-g1535800-d3811703-Reviews-Innachorion_Restaurant-Elafonissi_Chania_Prefecture_Crete.html"
    category = "restaurant"
    print(scrape_data(url, category))