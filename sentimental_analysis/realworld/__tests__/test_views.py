import unittest
import os, sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
#from views import detailed_analysis_sentence
from sentimental_analysis.realworld.views import detailed_analysis_sentence
from sentimental_analysis.realworld.utilityFunctions import get_clean_text, sentiment_scores
from sentimental_analysis.realworld.views import pdfparser, detailed_analysis, determine_language, create_word_correlation_heatmap, create_sentence_correlation_heatmap
from unittest.mock import patch, mock_open
import os
import json
from io import StringIO
import shutil
import base64
import seaborn as sns
import io
import subprocess
from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware

from .views import (
    analysis,
    pdfparser,
    get_clean_text,
    detailed_analysis,
    detailed_analysis_sentence,
    input,
    inputimage,
    productanalysis,
    create_word_correlation_heatmap,
    textanalysis,
    create_sentence_correlation_heatmap,
    batch_analysis,
    determine_language,
    fbanalysis,
    twitteranalysis,
    redditanalysis,
    audioanalysis,
    livespeechanalysis,
    recordaudio,
    newsanalysis,
    speech_to_text,
    sentiment_analyzer_scores,
)
from . import classifiers
from . import newsScraper
from . import utilityFunctions
from . import fb_scrap
from . import twitter_scrap
from . import reddit_scrap
    
class TestViews(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_analysis_view(self):
        request = self.factory.get(reverse('analysis'))
        request.user = self.user
        response = analysis(request)
        self.assertEqual(response.status_code, 200)

    def test_pdfparser(self):
        # Create a dummy PDF file for testing
        with open('test.pdf', 'w') as f:
            f.write('Test PDF content.')
        result = pdfparser('test.pdf')
        self.assertIsInstance(result, list)
        os.remove('test.pdf')
        os.remove('Output.txt')

    def test_get_clean_text(self):
        text = "This is a test. It includes links http://example.com and emojis 😊."
        cleaned_text = get_clean_text(text)
        self.assertIsInstance(cleaned_text, str)

    def test_detailed_analysis(self):
        result = ['This is a positive sentence.', 'This is a negative sentence.']
        analysis_result = detailed_analysis(result)
        self.assertIsInstance(analysis_result, dict)

    def test_detailed_analysis_sentence(self):
        result = 'This is a sentence.'
        analysis_result = detailed_analysis_sentence(result)
        self.assertIsInstance(analysis_result, dict)

    def test_input_view(self):
        file_data = b"Test file content"
        file = SimpleUploadedFile("test.txt", file_data)
        request = self.factory.post(reverse('input'), {'document': file})
        request.user = self.user
        response = input(request)
        self.assertEqual(response.status_code, 200)

    def test_sentiment_scores():
        text = "This is a positive sentence."
        scores = sentiment_scores(text)
        assert isinstance(scores, dict)
        assert "pos" in scores
        assert scores["pos"] > 0
        
    def test_determine_language_english():
        texts = ["This is English."]
        assert determine_language(texts) == True

    def test_determine_language_spanish():
        texts = ["Esto es español."]
        assert determine_language(texts) == False

    def test_create_word_correlation_heatmap():
        text = "word1 word2 word1 word3"
        heatmap_image = create_word_correlation_heatmap(text)
        assert isinstance(heatmap_image, str)

    def test_create_sentence_correlation_heatmap():
        texts = ["sentence1 sentence2", "sentence2 sentence3"]
        heatmap_image = create_sentence_correlation_heatmap(texts)
        assert isinstance(heatmap_image, str)

    def test_pdfparser():
        # Create a mock PDF file content
        mock_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Length 48 >>\nstream\n(This is a test PDF content.)\nendstream\nendobj\nxref\n0 2\n0000000000 65535 f \n0000000009 00000 n \ntrailer\n<< /Size 2 >>\nstartxref\n99\n%%EOF"

        with patch("builtins.open", mock_open(read_data=mock_pdf_content)) as mock_file:
            result = pdfparser("mock_pdf.pdf")
            assert "This is a test PDF content." in " ".join(result)

    def test_detailed_analysis():
        texts = ["This is good.", "This is bad."]
        result = detailed_analysis(texts)
        assert isinstance(result, dict)
        assert "pos" in result
        assert "neg" in result
        assert "neu" in result
        
    def test_get_clean_text_empty_input():
        assert get_clean_text("") == ""

    def test_get_clean_text_no_valid_tokens():
        text = "!@#$%^&*()"
        assert get_clean_text(text) == ""
             
    def test_sentiment_scores_mixed():
        text = "This is good, but also bad."
        scores = sentiment_scores(text)
        assert scores["neu"] > scores["pos"]
        assert scores["neu"] > scores["neg"]
                    
    def test_detailed_analysis_empty_list():
        assert detailed_analysis([]) == {}

    def test_detailed_analysis_single_item():
        result = detailed_analysis(["This is good."])
        assert result["pos"] > 0
        assert result["neg"] == 0
        assert result["neu"] < 1

    def test_detailed_analysis_sentence_positive():
        result = detailed_analysis_sentence("I love this!")
        assert result["compound"] > 0

    def test_detailed_analysis_sentence_negative():
        result = detailed_analysis_sentence("This is terrible!")
        assert result["compound"] < 0             
    
    def test_determine_language_empty_list():
        assert determine_language([]) == True

    def test_create_word_correlation_heatmap_empty_text():
        heatmap_image = create_word_correlation_heatmap("")
        assert isinstance(heatmap_image, str)

    def test_create_word_correlation_heatmap_single_word():
        heatmap_image = create_word_correlation_heatmap("test")
        assert isinstance(heatmap_image, str)

    def test_create_sentence_correlation_heatmap_empty_list():
        heatmap_image = create_sentence_correlation_heatmap([])
        assert isinstance(heatmap_image, str)                
                    
                    
    def test_detailed_analysis_sentence_negative_sentence(self):
        response = detailed_analysis_sentence("""I can't express how disappointed I am with the SuperClean 3000. Right out of the box, it felt cheap and flimsy. The suction is practically nonexistent—I've had better results using a broom! It barely picked up anything, leaving behind dirt and pet hair everywhere.

The design is another nightmare. It's so heavy and awkward that I dreaded using it. And don't get me started on the attachments; they just fell off at the worst times, making the whole experience even more frustrating.

After only a few uses, it started making a terrible grinding noise. I reached out to customer service, and it was a total waste of time. I was put on hold for ages, and when I finally got through, they were of no help at all.

Honestly, I regret purchasing this vacuum. Save your money and look for something else!""")
        self.assertLess(response['compound'], -0.4)

    def test_detailed_analysis_sentence_neutral_sentence(self):
        response = detailed_analysis_sentence("""The SuperClean 3000 vacuum is a functional product that meets basic cleaning needs. It picks up dust and small debris, although its suction power could be improved. The design is somewhat bulky, which may affect maneuverability in tighter spaces.

The included attachments work as intended, but they are fairly standard and do not offer any unique features. Overall, it performs adequately for everyday use, but it might not be the best option for those seeking advanced cleaning capabilities.""")
        self.assertGreater(response['compound'], -0.4)
        self.assertLess(response['compound'], 0.4)

    def test_detailed_analysis_sentence_positive_sentence(self):
        response = detailed_analysis_sentence("""\n\n\n\n\n\n\n\n\n\n  \n  \n    \n  These Palazzo Pants are GORGEOUS! The material IS very light and slightly see through, as others have mentioned, however if you wear a pair of nude colored undies it won't pose a problem :-) I am 5'4\" and about 190lbs. I normally wear a size 12/14- Large pant and I got these in an XL and they fit me VERY comfortably. In my opinion, get 1 size up for adequate comfort and you will NOT be disappointed. I have received lots of compliments on these and people actually think it is a skirt :-P I'm super cheap and almost died after I paid the $38 for these but I am happy I did because I really do like them a lot :-) I paired them with a dark green top, also from Amazon, called the LL Womens Boat Neck Dolman Top, for $12.95 and they work wonderfully together! Both are super flowey and comfy. Bring on the warm weather!!! :-D\n\n  \n""")
        self.assertGreater(response['compound'], 0.4)
if __name__ == '__main__':
    unittest.main()