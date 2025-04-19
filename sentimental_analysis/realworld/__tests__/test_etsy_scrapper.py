import unittest
from unittest.mock import patch, MagicMock
import json
from ..scrapers.etsy_scrapper import scrape_etsy


class TestScrapeEtsy(unittest.TestCase):
    @patch("realworld.scrapers.etsy_scrapper.webdriver.Chrome")
    @patch("realworld.scrapers.etsy_scrapper.WebDriverWait")
    @patch("realworld.scrapers.etsy_scrapper.BeautifulSoup")
    def test_scrape_etsy_success(self, mock_bs, mock_wait, mock_driver):
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance
        mock_driver_instance.page_source = "<html><h1 data-buy-box-listing-title='true'>Test Product</h1>" \
                                           "<div id='same-listing-reviews-panel'>" \
                                           "<div class='wt-grid__item-xs-12 review-card'>" \
                                           "<span class='wt-screen-reader-only'>5 stars</span>" \
                                           "<p id='review-preview-toggle-1'>Great product!</p>" \
                                           "</div>" \
                                           "</div></html>"

        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        mock_soup.select_one.return_value.get_text.return_value = "Test Product"
        mock_soup.select.return_value = [
            MagicMock(find_all=lambda *args, **kwargs: [
                MagicMock(select=lambda *args, **kwargs: [
                    MagicMock(get_text=lambda *args, **kwargs: "ABCDEFG"),
                ])
            ])
        ]

        result = scrape_etsy("https://www.etsy.com/listing/123456789/test-product")

        result_dict = json.loads(result)

        self.assertEqual(result_dict["title"], "Test Product")
        self.assertEqual(len(result_dict["reviews"]), 1)
        self.assertEqual(result_dict["reviews"][0]["review"], "ABCDEFG")
        self.assertEqual(result_dict["reviews"][0]["rating"], "ABCDEFG")

    @patch("realworld.scrapers.etsy_scrapper.webdriver.Chrome")
    @patch("realworld.scrapers.etsy_scrapper.WebDriverWait")
    @patch("realworld.scrapers.etsy_scrapper.BeautifulSoup")
    def test_scrape_etsy_no_reviews(self, mock_bs, mock_wait, mock_driver):
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance
        mock_driver_instance.page_source = "<html><h1 data-buy-box-listing-title='true'>Test Product</h1>" \
                                           "<div id='same-listing-reviews-panel'></div></html>"

        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        mock_soup.select_one.return_value.get_text.return_value = "Test Product"
        mock_soup.select.return_value = [
            MagicMock(find_all=lambda *args, **kwargs: [
            ])
        ]

        result = scrape_etsy("https://www.etsy.com/listing/123456789/test-product")

        result_dict = json.loads(result)

        self.assertEqual(result_dict["title"], "Test Product")
        self.assertEqual(len(result_dict["reviews"]), 0)

    @patch("realworld.scrapers.etsy_scrapper.webdriver.Chrome")
    @patch("realworld.scrapers.etsy_scrapper.WebDriverWait")
    @patch("realworld.scrapers.etsy_scrapper.BeautifulSoup")
    def test_scrape_etsy_title_not_found(self, mock_bs, mock_wait, mock_driver):
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance
        mock_driver_instance.page_source = "<html></html>"

        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        mock_soup.select_one.return_value = None

        result = scrape_etsy("https://www.etsy.com/listing/123456789/test-product")

        self.assertIsNone(result)

    @patch("realworld.scrapers.etsy_scrapper.webdriver.Chrome")
    @patch("realworld.scrapers.etsy_scrapper.WebDriverWait")
    @patch("realworld.scrapers.etsy_scrapper.BeautifulSoup")
    def test_scrape_etsy_exception_handling(self, mock_bs, mock_wait, mock_driver):
        mock_wait.side_effect = Exception("Driver error")

        result = scrape_etsy("https://www.etsy.com/listing/123456789/test-product")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
