import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import json
from goodreads_scrapper import scrape_goodreads_reviews

class TestScrapeGoodreadsReviews(unittest.TestCase):
    @patch("requests.get")
    def test_scrape_goodreads_reviews(self, mock_get):
        mock_html = """
        <html>
            <head><title>Mock Goodreads Page</title></head>
            <body>
                <h1 data-testid="bookTitle">Mock Book Title</h1>
                <div data-testid="description">This is a mock description of the book.</div>
                <div class="ShelfStatus">
                    <span class="RatingStars RatingStars__small" aria-label="5 stars"></span>
                </div>
                <section class="ReviewText__content">This is a mock review text.</section>
                <div class="RatingsHistogram RatingsHistogram__interactive">
                    <div class="RatingsHistogram__bar" aria-label="5 stars">
                        <span class="RatingsHistogram__labelTotal">100</span>
                    </div>
                    <div class="RatingsHistogram__bar" aria-label="4 stars">
                        <span class="RatingsHistogram__labelTotal">50</span>
                    </div>
                </div>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        book_url = "https://www.goodreads.com/book/show/mock-book"
        result = scrape_goodreads_reviews(book_url)

        result_dict = json.loads(result)

        self.assertEqual(result_dict["title"], "Mock Book Title")
        self.assertEqual(result_dict["description"], "This is a mock description of the book.")
        self.assertEqual(result_dict["reactions"], {
            "5 stars": "100",
            "4 stars": "50"
        })
        self.assertEqual(len(result_dict["reviews"]), 1)
        self.assertEqual(result_dict["reviews"][0]["review"], "This is a mock review text.")
        self.assertEqual(result_dict["reviews"][0]["rating"], "5 stars")

    @patch("requests.get")
    def test_scrape_goodreads_reviews_no_reviews(self, mock_get):
        mock_html = """
        <html>
            <head><title>Mock Goodreads Page</title></head>
            <body>
                <h1 data-testid="bookTitle">Mock Book Title</h1>
                <div data-testid="description">This is a mock description of the book.</div>
                <div class="RatingsHistogram RatingsHistogram__interactive">
                    <div class="RatingsHistogram__bar" aria-label="5 stars">
                        <span class="RatingsHistogram__labelTotal">100</span>
                    </div>
                </div>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        book_url = "https://www.goodreads.com/book/show/mock-book"
        result = scrape_goodreads_reviews(book_url)

        result_dict = json.loads(result)

        self.assertEqual(result_dict["title"], "Mock Book Title")
        self.assertEqual(result_dict["description"], "This is a mock description of the book.")
        self.assertEqual(result_dict["reactions"], {
            "5 stars": "100"
        })
        self.assertEqual(len(result_dict["reviews"]), 0)

if __name__ == "__main__":
    unittest.main()