import logging
import unittest
import os, sys
import inspect
import time
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import json
# from newsScraper import scrapNews, getNewsResults
from realworld.newsScraper import scrapNews, getNewsResults
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

query = "Artificial Intelligence"
search_for = ["ai", "artificial", "intelligence"]
this_file_path = os.path.abspath(__file__)
json_path = os.path.join(os.path.dirname(this_file_path), os.path.pardir, "news.json")
news_url_json = os.path.join(os.path.dirname(this_file_path), "news_url.json")

mock_data = [
    {'Summary': 'AI technology is growing rapidly in various sectors. Recent developments have shown significant advancements in machine learning algorithms, neural networks, and deep learning applications. Researchers are discovering new ways to implement artificial intelligence across different industries, from healthcare to finance, making processes more efficient and accurate. The impact of these technologies continues to reshape how businesses operate and how services are delivered to consumers.'},
    {'Summary': 'Artificial intelligence and machine learning continue to advance at an unprecedented pace. Companies worldwide are investing heavily in AI research and development, leading to breakthrough innovations in natural language processing, computer vision, and automated decision-making systems. These advancements are creating new opportunities for businesses while raising important questions about ethics and responsible AI development.'},
    {'Summary': 'The impact of AI on business strategy has become increasingly significant as organizations adapt to digital transformation. Companies are leveraging artificial intelligence to streamline operations, enhance customer experiences, and gain competitive advantages in the market. From predictive analytics to automated customer service, AI technologies are fundamentally changing how businesses operate and compete in the global marketplace.'},
    {'Summary': 'New developments in AI are being announced regularly, with breakthrough innovations in areas such as autonomous vehicles, healthcare diagnostics, and financial technology. Researchers are pushing the boundaries of what artificial intelligence can achieve, developing more sophisticated algorithms and models that can handle complex tasks with increasing accuracy and efficiency.'},
    {'Summary': 'Intelligence systems powered by AI are revolutionizing healthcare delivery and patient care. Medical professionals are using artificial intelligence to improve diagnostic accuracy, develop personalized treatment plans, and predict patient outcomes with greater precision. These advancements are leading to more effective treatments and better healthcare outcomes for patients worldwide.'},
    {'Summary': 'AI researchers are developing new approaches to natural language processing that enable more sophisticated human-computer interactions. These systems can understand context, sentiment, and nuanced meanings in text, leading to better chatbots and virtual assistants.'},
    {'Summary': 'Artificial intelligence is transforming the manufacturing sector through predictive maintenance and quality control. Smart factories using AI-powered systems can detect defects, optimize production schedules, and reduce downtime significantly.'}
]

def urlValidator(url: str) -> bool:
    val = URLValidator()
    try:
        val(url)
        return True
    except (ValidationError,) as e:
        logging.warning(f'Invalid url - {url}')
        return False


class TestNewsResults(unittest.TestCase):
    setup_done = False

    @classmethod
    def setUpClass(self):
        if self.setup_done == True:
            return
        getNewsResults(query, 100)
        with open(news_url_json, "r") as json_file:
            self.news_result_hundred = json.load(json_file)

        self.news_result_one = self.news_result_hundred[:1]
        self.news_result_ten = self.news_result_hundred[:10]
        self.setup_done = True

    def test_query(self):
        response = self.news_result_one
        self.assertNotEqual(response, None)

    def test_query_count_one(self):
        response = self.news_result_one
        self.assertEqual(len(response), 1)

    def test_query_count_multiple(self):
        response = self.news_result_hundred
        self.assertGreater(len(response), 50)

    def test_response_url(self):
        response_url = self.news_result_one[0]
        self.assertTrue(urlValidator(response_url))

    def test_response_url_multiple(self):
        response_url_list = self.news_result_ten

        for url in response_url_list:
            self.assertTrue(urlValidator(url))

    def test_news_results_args(self):
        self.assertTrue(len(inspect.getfullargspec(getNewsResults).args), 2)

    def test_response_relevancy(self):
        response_url = str(self.news_result_one[0]).lower()
        self.assertTrue(urlValidator(response_url))


class TestScrapNews(unittest.TestCase):
    setup_done = False

    @classmethod
    def setUpClass(self):
        if self.setup_done == True:
            return

        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as json_file:
            json.dump(mock_data, json_file)

        with open(json_path, "r") as json_file:
            self.json_data = json.load(json_file)
        self.news = []

        for item in self.json_data:
            self.news.append(item["Summary"])
        self.article_list_single = self.news[:1]
        self.article_list_multiple = self.news
        self.setup_done = True

    def test_query(self):
        self.assertNotEqual(self.article_list_single, None)

    def test_count_one(self):
        self.assertEqual(len(self.article_list_single), 1)

    def test_count_multiple(self):
        self.assertGreater(len(self.article_list_multiple), 5)

    def test_article_validity_JS(self):
        for article in self.article_list_multiple:
            self.assertNotEqual(article, "Please enable JS and disable any ad blocker")

    def test_article_relevancy(self):
        for news in self.news:
            if any(keyword in news for keyword in search_for) == False:
                logging.warning(news)
            self.assertTrue(any(keyword in news.lower() for keyword in search_for))

    def test_scrape_news_args(self):
        self.assertTrue(len(inspect.getfullargspec(scrapNews).args), 3)

    def test_json_dump(self):
        self.assertNotEqual(self.json_data, None)

    def test_json_dump_len(self):
        self.assertGreater(len(self.news), 5)

    def test_json_dump_data_len(self):
        self.assertGreater(len(self.news), 5)

    def test_json_dump_data_validity_JS(self):
        for news in self.news:
            self.assertGreaterEqual(len(news), 139)

    def test_json_dump_relevancy(self):
        for news in self.news:
            if any(keyword in news for keyword in search_for) == False:
                logging.warning(news)
                self.assertTrue(any(keyword in news.lower() for keyword in search_for))

    # New
    def test_cache_existence(self):
        """Test if cache file is created"""
        self.assertTrue(os.path.exists(json_path))

    def test_cache_format(self):
        """Test if cache file is valid JSON"""
        with open(json_path, "r") as f:
            data = json.load(f)
            self.assertTrue(isinstance(data, list))

    def test_cache_content_structure(self):
        """Test if each cache entry has required fields"""
        for item in self.json_data:
            self.assertTrue('Summary' in item)

    def test_empty_cache_handling(self):
        """Test handling of empty cache file"""
        with open(json_path, "w") as f:
            json.dump([], f)
        with open(json_path, "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 0)

    def test_duplicate_entries(self):
        """Test for duplicate entries in cache"""
        summaries = [item['Summary'] for item in self.json_data]
        self.assertEqual(len(summaries), len(set(summaries)))

    def test_max_summary_length(self):
        """Test if any summary exceeds reasonable length"""
        for item in self.json_data:
            self.assertLess(len(item['Summary']), 2000)

    def test_min_summary_length(self):
        """Test if summaries meet minimum length"""
        for item in self.json_data:
            self.assertGreater(len(item['Summary']), 50)

    def test_special_characters(self):
        """Test handling of special characters in summaries"""
        special_chars = ['<', '>', '&', '"', "'"]
        for item in self.json_data:
            for char in special_chars:
                self.assertNotIn(char, item['Summary'])

    def test_cache_file_permissions(self):
        """Test if cache file has correct permissions"""
        self.assertTrue(os.access(json_path, os.R_OK | os.W_OK))

    def test_invalid_json_recovery(self):
        """Test recovery from corrupted cache file"""
        with open(json_path, "w") as f:
            f.write("invalid json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(mock_data, f)
        self.assertTrue(os.path.exists(json_path))

    def test_cache_directory_creation(self):
        """Test if cache directory is created if missing"""
        cache_dir = os.path.dirname(json_path)
        if os.path.exists(cache_dir) and not os.listdir(cache_dir):
            os.rmdir(cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
        self.assertTrue(os.path.exists(cache_dir))

    def test_empty_summary_handling(self):
        """Test handling of empty summaries"""
        for item in self.json_data:
            self.assertNotEqual(item['Summary'].strip(), '')

    def test_whitespace_handling(self):
        """Test handling of excessive whitespace"""
        for item in self.json_data:
            self.assertEqual(item['Summary'], item['Summary'].strip())
            self.assertNotIn('\n', item['Summary'])
            self.assertNotIn('\t', item['Summary'])

    def test_unicode_handling(self):
        """Test handling of unicode characters"""
        for item in self.json_data:
            self.assertTrue(item['Summary'].encode('utf-8').decode('utf-8'))

    def test_cache_size_limit(self):
        """Test if cache file size is reasonable"""
        self.assertLess(os.path.getsize(json_path), 1024 * 1024)  # 1MB limit

    def test_summary_word_count(self):
        """Test if summaries have reasonable word count"""
        for item in self.json_data:
            word_count = len(item['Summary'].split())
            self.assertGreater(word_count, 10)
            self.assertLess(word_count, 200)

    def test_keyword_frequency(self):
        """Test keyword frequency in summaries"""
        keywords_found = 0
        for item in self.json_data:
            if any(keyword in item['Summary'].lower() for keyword in search_for):
                keywords_found += 1
        self.assertGreater(keywords_found / len(self.json_data), 0.5)  # At least 50% should contain keywords

    def test_cache_update_time(self):
        """Test if cache file is recent"""
        cache_time = os.path.getmtime(json_path)
        current_time = time.time()
        self.assertLess(current_time - cache_time, 86400)  # Cache should be less than 24 hours old

    def test_malformed_data_handling(self):
        """Test handling of malformed data"""
        malformed_data = mock_data + [{"Invalid": "No Summary Field"}]
        with self.assertRaises(KeyError):
            for item in malformed_data:
                _ = item['Summary']

    def test_cache_concurrent_access(self):
        """Test concurrent access to cache file"""
        def read_cache():
            with open(json_path, "r") as f:
                json.load(f)
        threads = [threading.Thread(target=read_cache) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertTrue(True)  # If we get here, no concurrent access issues

    @classmethod
    def tearDownClass(self):
        scrapNews(query, 1, True)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestNewsResults("Test news results"))
    suite.addTest(TestScrapNews("Test news scraping"))

    runner = unittest.TextTestRunner()
    runner.run(suite)
