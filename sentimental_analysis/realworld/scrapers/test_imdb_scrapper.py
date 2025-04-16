import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import json
from imdb_scrapper import format_url, scrape_imdb_rating, scrape_imdb


class TestFormatUrl(unittest.TestCase):
    def test_format_url_removes_trailing_slash(self):
        url = "https://imdb.com/"
        formatted_url = format_url(url)
        self.assertEqual(formatted_url, "https://imdb.com")

    def test_format_url_no_trailing_slash(self):
        url = "https://imdb.com"
        formatted_url = format_url(url)
        self.assertEqual(formatted_url, "https://imdb.com")


class TestScrapeImdbSelenium(unittest.TestCase):
    @patch("selenium.webdriver.Chrome")
    def test_scrape_imdb_rating_success(self, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        mock_driver.page_source = """
        <svg>
            <text id="chart-bar-1-labels-10"><tspan>10</tspan></text>
            <text id="chart-bar-1-labels-9"><tspan>20</tspan></text>
            <text id="chart-bar-1-labels-8"><tspan>30</tspan></text>
        </svg>
        """
        mock_driver.quit = MagicMock()

        url = "https://imdb.com/ratings"
        reactions = scrape_imdb_rating(url)

        expected_reactions = {10: "10", 9: "20", 8: "30"}
        self.assertEqual(reactions, expected_reactions)

    @patch("selenium.webdriver.Chrome")
    def test_scrape_imdb_rating_histogram_not_found(self, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        mock_driver.page_source = "<html></html>"
        mock_driver.quit = MagicMock()

        url = "https://imdb.com/ratings"
        reactions = scrape_imdb_rating(url)

        self.assertEqual({},reactions)


class TestScrapeImdb(unittest.TestCase):
    @patch("requests.get")
    @patch("imdb_scrapper.scrape_imdb_rating")
    def test_scrape_imdb_success(self, mock_scrape_imdb_rating, mock_requests_get):
        mock_main_response = MagicMock()
        mock_main_response.text = """
        <html>
            <span class="hero__primary-text">Movie Title</span>
            <span data-testid="plot-xs_to_m">Movie Description</span>
        </html>
        """
        mock_requests_get.return_value = mock_main_response

        mock_scrape_imdb_rating.return_value = {10: "100", 9: "200"}

        mock_reviews_response = MagicMock()
        mock_reviews_response.text = """
        <html>
            <section class="ipc-page-section ipc-page-section--base ipc-page-section--sp-pageMargin">
                <article class="sc-8c92b587-1 cwztqu user-review-item">
                    <h3 class="ipc-title__text">Review Title</h3>
                    <span class="ipc-rating-star--rating">8</span>
                    <div class="ipc-html-content-inner-div">Review Text</div>
                </article>
            </section>
        </html>
        """
        mock_requests_get.side_effect = [mock_main_response, mock_reviews_response]

        url = "https://imdb.com/title/tt1234567"
        result = scrape_imdb(url)

        expected_result = {
            "title": "Movie Title",
            "description": "Movie Description",
            "reactions": {'9': "200", '10': "100"},
            # "reviews": [
            #     {"review": "Review Title\nReview Text", "rating": "8/10"}
            # ],
            "reviews": [],
        }
        self.assertEqual(json.loads(result), expected_result)

    @patch("requests.get")
    @patch("imdb_scrapper.scrape_imdb_rating")
    def test_scrape_imdb_no_reviews(self, mock_scrape_imdb_rating, mock_requests_get):
        mock_main_response = MagicMock()
        mock_main_response.text = """
        <html>
            <span class="hero__primary-text">Movie Title</span>
            <span data-testid="plot-xs_to_m">Movie Description</span>
        </html>
        """
        mock_requests_get.return_value = mock_main_response

        mock_scrape_imdb_rating.return_value = {10: "100", 9: "200"}

        mock_reviews_response = MagicMock()
        mock_reviews_response.text = """
        <html>
            <section class="ipc-page-section ipc-page-section--base ipc-page-section--sp-pageMargin">
            </section>
        </html>
        """
        mock_requests_get.side_effect = [mock_main_response, mock_reviews_response]

        url = "https://imdb.com/title/tt1234567"
        result = scrape_imdb(url)

        expected_result = {
            "title": "Movie Title",
            "description": "Movie Description",
            "reactions": {'10': "100", '9': "200"},
            "reviews": [],
        }
        self.assertEqual(json.loads(result), expected_result)


if __name__ == "__main__":
    unittest.main()