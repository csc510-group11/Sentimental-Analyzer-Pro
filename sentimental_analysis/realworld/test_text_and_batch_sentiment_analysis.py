import unittest
from unittest.mock import patch
# import os, sys
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(SCRIPT_DIR))
# from views import detailed_analysis_sentence
from views import detect_language, analyze_sentiment, textanalysis, batch_analysis
from django.test import RequestFactory


class SentimentAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    # Test cases for detect_language
    def test_detect_language_english(self):
        self.assertEqual(detect_language(["Hello, how are you?"]), "en")

    def test_detect_language_spanish(self):
        self.assertEqual(detect_language(["Hola, cómo estás?"]), "es")

    def test_detect_language_french(self):
        self.assertEqual(detect_language(["Bonjour, comment ça va?"]), "fr")

    def test_detect_language_mixed(self):
        self.assertEqual(detect_language(["How are you? Are you okay? bonjour!"]), "en")  # Most common language

    def test_detect_language_unknown(self):
        self.assertEqual(detect_language([""]), "unknown")

    def test_detect_language_unknown(self):
        self.assertEqual(detect_language(["1235.908"]), "unknown")

    # Test cases for analyze_sentiment
    @patch("views.classifiers.SpanishClassifier.predict")
    def test_analyze_sentiment_spanish(self, mock_predict):
        mock_predict.return_value = {"positive": 0.8, "neutral": 0.1, "negative": 0.1}
        result = analyze_sentiment("Este es un gran día", "es")
        self.assertEqual(result, {'pos': 0.8, 'neu': 0.1, 'neg': 0.1})

    def test_analyze_sentiment_english_translation(self):
        result = analyze_sentiment("C'est une belle journée", "fr")
        self.assertEqual(result, {"pos": 0.583, "neu":0.417, "neg": 0.0})

    # Test cases for textanalysis
    @patch("views.analyze_sentiment")
    @patch("views.detect_language")
    def test_textanalysis_post(self, mock_detect, mock_analyze):
        request = self.factory.post("/", {"textField": "Hello, this is a test."})
        mock_detect.return_value = "en"
        mock_analyze.return_value = {"pos": 0.5, "neu": 0.4, "neg": 0.1}
        response = textanalysis(request)
        self.assertEqual(response.status_code, 200)

    def test_textanalysis_get(self):
        request = self.factory.get("/")
        response = textanalysis(request)
        self.assertEqual(response.status_code, 200)

    # Test cases for batch_analysis
    @patch("views.analyze_sentiment")
    @patch("views.detect_language")
    def test_batch_analysis_post(self, mock_detect, mock_analyze):
        request = self.factory.post("/", {"batchTextField": "Hello world.\nThis is a test."})
        mock_detect.return_value = "en"
        mock_analyze.side_effect = [
            {"pos": 0.6, "neu": 0.3, "neg": 0.1},
            {"pos": 0.4, "neu": 0.5, "neg": 0.1}
        ]
        response = batch_analysis(request)
        self.assertEqual(response.status_code, 200)

    def test_batch_analysis_get(self):
        request = self.factory.get("/")
        response = batch_analysis(request)
        self.assertEqual(response.status_code, 200)

    # Additional tests for edge cases
    def test_detect_language_numbers(self):
        self.assertEqual(detect_language(["123456"]), "unknown")

    def test_detect_language_multiple_sentences(self):
        self.assertEqual(detect_language(["Hola. Adiós. Hello."]), "es")  # Most frequent

    @patch("views.Translator.translate")
    @patch("views.sentiment_analyzer_scores")
    def test_analyze_sentiment_empty_text(self, mock_scores, mock_translate):
        mock_translate.return_value.text = ""
        mock_scores.return_value = {"pos": 0.0, "neu": 1.0, "neg": 0.0}
        result = analyze_sentiment("", "en")
        self.assertEqual(result, {"pos": 0.0, "neu": 1.0, "neg": 0.0})

    @patch("views.analyze_sentiment")
    @patch("views.detect_language")
    def test_textanalysis_punctuation(self, mock_detect, mock_analyze):
        request = self.factory.post("/", {"textField": "!!! ??? ..."})
        mock_detect.return_value = "unknown"
        mock_analyze.return_value = {"pos": 0.0, "neu": 1.0, "neg": 0.0}
        response = textanalysis(request)
        self.assertEqual(response.status_code, 200)

    def test_detect_language_special_characters(self):
        self.assertEqual(detect_language(["@#$%^&*()"]), "unknown")

    @patch("views.analyze_sentiment")
    @patch("views.detect_language")
    def test_batch_analysis_empty_input(self, mock_detect, mock_analyze):
        request = self.factory.post("/", {"batchTextField": ""})
        mock_detect.return_value = "unknown"
        mock_analyze.return_value = {"pos": 0.0, "neu": 1.0, "neg": 0.0}
        response = batch_analysis(request)
        self.assertEqual(response.status_code, 200)

    @patch("views.analyze_sentiment")
    @patch("views.detect_language")
    def test_batch_analysis_large_texts(self, mock_detect, mock_analyze):
        large_text = "This is a long text. " * 1000
        request = self.factory.post("/", {"batchTextField": large_text})
        mock_detect.return_value = "en"
        mock_analyze.return_value = {"pos": 0.5, "neu": 0.4, "neg": 0.1}
        response = batch_analysis(request)
        self.assertEqual(response.status_code, 200)

    @patch("views.analyze_sentiment")
    @patch("views.detect_language")
    def test_batch_analysis_mixed_languages(self, mock_detect, mock_analyze):
        request = self.factory.post("/", {"batchTextField": "Hola mundo.\nBonjour le monde.\nHello world."})
        mock_detect.return_value = "en"
        mock_analyze.side_effect = [
            {"pos": 0.6, "neu": 0.3, "neg": 0.1},
            {"pos": 0.4, "neu": 0.4, "neg": 0.2},
            {"pos": 0.7, "neu": 0.2, "neg": 0.1}
        ]
        response = batch_analysis(request)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
