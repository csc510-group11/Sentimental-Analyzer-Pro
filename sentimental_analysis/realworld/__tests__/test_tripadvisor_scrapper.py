import unittest
import json
from unittest.mock import patch, Mock
from ..scrapers.tripadvisor_scrapper import scrape_tripadvisor

class TestScrapeTripAdvisor(unittest.TestCase):
    @patch("realworld.scrapers.tripadvisor_scrapper.requests.get")
    def test_scrape_tripadvisor_success(self, mock_get):
        mock_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Hotel</h1>
                <div class="biGQs _P pZUbB avBIb KxBGd">This is a test description.</div>
                <div class="AugPH w u">
                    <div class="jxnKb">
                        <div class="Ygqck o W q">Excellent</div>
                        <div class="biGQs _P fiohW biKBZ osNWb">123</div>
                    </div>
                    <div class="jxnKb">
                        <div class="Ygqck o W q">Very Good</div>
                        <div class="biGQs _P fiohW biKBZ osNWb">45</div>
                    </div>
                </div>
                <div class="zwgAY">
                    <div class="_c">
                        <div class="biGQs _P fiohW qWPrE ncFvv fOtGX">Great stay!</div>
                        <div class="biGQs _P pZUbB KxBGd">The hotel was clean and comfortable.</div>
                        <title>5 bubbles</title>
                    </div>
                    <div class="_c">
                        <div class="biGQs _P fiohW qWPrE ncFvv fOtGX">Not bad</div>
                        <div class="biGQs _P pZUbB KxBGd">The service could be better.</div>
                        <title>3 bubbles</title>
                    </div>
                </div>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        url = "https://www.tripadvisor.com/Hotel_Review"
        result = scrape_tripadvisor(url)

        expected_result = {
            "title": "Test Hotel",
            "description": "This is a test description.",
            "reactions": {
                "Excellent": "123",
                "Very Good": "45"
            },
            "reviews": [
                {
                    "review": "Great stay!\nThe hotel was clean and comfortable.",
                    "rating": "5 bubbles"
                },
                {
                    "review": "Not bad\nThe service could be better.",
                    "rating": "3 bubbles"
                }
            ]
        }

        self.assertEqual(json.loads(result), expected_result)

    @patch("realworld.scrapers.tripadvisor_scrapper.requests.get")
    def test_scrape_tripadvisor_no_reviews(self, mock_get):
        mock_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Hotel</h1>
                <div class="biGQs _P pZUbB avBIb KxBGd">This is a test description.</div>
                <div class="AugPH w u">
                    <div class="jxnKb">
                        <div class="Ygqck o W q">Excellent</div>
                        <div class="biGQs _P fiohW biKBZ osNWb">123</div>
                    </div>
                </div>
                <div class="zwgAY"></div>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        url = "https://www.tripadvisor.com/Hotel_Review"
        result = scrape_tripadvisor(url)

        expected_result = {
            "title": "Test Hotel",
            "description": "This is a test description.",
            "reactions": {
                "Excellent": "123"
            },
            "reviews": []
        }

        self.assertEqual(json.loads(result), expected_result)

    @patch("realworld.scrapers.tripadvisor_scrapper.requests.get")
    def test_scrape_tripadvisor_invalid_html(self, mock_get):
        mock_html = "<html><head><title>Invalid Page</title></head><body></body></html>"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        url = "https://www.tripadvisor.com/Hotel_Review"
        with self.assertRaises(AttributeError):
            scrape_tripadvisor(url)

    @patch("realworld.scrapers.tripadvisor_scrapper.requests.get")
    def test_scrape_tripadvisor_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        url = "https://www.tripadvisor.com/Hotel_Review"
        with self.assertRaises(Exception):
            scrape_tripadvisor(url)


if __name__ == "__main__":
    unittest.main()
