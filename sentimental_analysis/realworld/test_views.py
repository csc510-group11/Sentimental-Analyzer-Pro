from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    @patch("realworld.decorators.ApiCache.objects.get", side_effect=Exception("Bypass cache"))
    def test_index_view(self, mock_cache):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    @patch("realworld.decorators.ApiCache.objects.get", side_effect=Exception("Bypass cache"))
    def test_document_analysis_file_too_large(self, mock_cache):
        big_file = SimpleUploadedFile("big.pdf", b"a" * (5 * 1024 * 1024 + 1), content_type="application/pdf")
        response = self.client.post(reverse('document_analysis'), {'document': big_file}, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 400)

    @patch("realworld.utils.gemini_summarize", return_value="Mock summary")
    @patch("realworld.decorators.ApiCache.objects.get", side_effect=Exception("Bypass cache"))
    def test_document_analysis_valid_txt(self, mock_cache, mock_summarize):
        txt_file = SimpleUploadedFile("sample.txt", b"Sample plain text.", content_type="text/plain")
        response = self.client.post(reverse('document_analysis'), {'document': txt_file}, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)

    @patch("realworld.utils.gemini_summarize", return_value="Mock summary")
    @patch("realworld.decorators.ApiCache.objects.get", side_effect=Exception("Bypass cache"))
    def test_text_analysis(self, mock_cache, mock_summarize):
        response = self.client.post(reverse('text_analysis'), {'text': 'Hello world'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Mock summary", response.content)

    @patch("realworld.utils.gemini_caption_image", return_value="Mock caption")
    @patch("realworld.utils.gemini_sentiment_analysis", return_value={"pos": 0.6, "neg": 0.2, "neu": 0.2})
    @patch("realworld.decorators.ApiCache.objects.get", side_effect=Exception("Bypass cache"))
    def test_image_analysis(self, mock_cache, mock_sentiment, mock_caption):
        image = SimpleUploadedFile("image.png", b"fakeimage", content_type="image/png")
        response = self.client.post(reverse('image_analysis'), {'image': image})
        self.assertEqual(response.status_code, 200)

    @patch("realworld.utils.gemini_transcribe_audio", return_value="Mock transcription")
    @patch("realworld.utils.gemini_sentiment_analysis", return_value={"pos": 0.5, "neg": 0.3, "neu": 0.2})
    @patch("realworld.decorators.ApiCache.objects.get", side_effect=Exception("Bypass cache"))
    def test_audio_analysis(self, mock_cache, mock_sentiment, mock_transcribe):
        audio = SimpleUploadedFile("audio.wav", b"fakeaudio", content_type="audio/wav")
        response = self.client.post(reverse('audio_analysis'), {'audio': audio})
        self.assertEqual(response.status_code, 200)

    @patch("realworld.utils.gemini_video_analysis", return_value="Mock video summary")
    @patch("realworld.utils.gemini_sentiment_analysis", return_value={"pos": 0.4, "neg": 0.4, "neu": 0.2})
    @patch("realworld.decorators.ApiCache.objects.get", side_effect=Exception("Bypass cache"))
    def test_video_analysis(self, mock_cache, mock_sentiment, mock_video):
        video = SimpleUploadedFile("video.mp4", b"fakevideo", content_type="video/mp4")
        response = self.client.post(reverse('video_analysis'), {'video': video})
        self.assertEqual(response.status_code, 200)

    @patch("realworld.utils.scrape_data", return_value="review1\nreview2")
    @patch("realworld.utils.gemini_sentiment_analysis", return_value={"pos": 0.6, "neg": 0.2, "neu": 0.2})
    @patch("realworld.decorators.ApiCache.objects.get", side_effect=Exception("Bypass cache"))
    def test_book_review(self, mock_cache, mock_sentiment, mock_scrape):
        response = self.client.post(reverse('book_review'), {'review_url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)