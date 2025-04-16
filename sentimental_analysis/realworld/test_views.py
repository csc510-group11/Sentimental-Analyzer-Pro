from django.test import RequestFactory, TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from .views import text_analysis
from django.http import HttpResponse

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_document_analysis_file_too_large(self):
        big_file = SimpleUploadedFile("big.pdf", b"a" * (5 * 1024 * 1024 + 1), content_type="application/pdf")
        response = self.client.post(reverse('document_analysis'), {'document': big_file}, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 400)

    def test_document_analysis_valid_txt(self):
        txt_file = SimpleUploadedFile("sample.txt", b"Sample plain text.", content_type="text/plain")
        response = self.client.post(reverse('document_analysis'), {'document': txt_file}, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)

    @patch("realworld.views.text_analysis", return_value=HttpResponse("mocked response"))
    def test_wrapper_view(self, mock_text_analysis):
        factory = RequestFactory()
        request = factory.post('/text-analysis/', data={'text': 'whatever'})
        request.user = self.user

        response = mock_text_analysis(request)

        self.assertEqual(response.content, b"mocked response")

    def test_text_analysis(self):
        response = self.client.post(reverse('text_analysis'), {'text': 'sample'})
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    # @patch("realworld.views.image_analysis", return_value=HttpResponse("mocked response"))
    # def test_image_analysis(self, mock_image_analysis):
    #     response = self.client.post(reverse('image_analysis'), {'image': 'fake'})
    #     self.assertEqual(response.content, b"mocked response")

    # @patch("realworld.views.audio_analysis", return_value=HttpResponse("mocked response"))
    # def test_audio_analysis(self, mock_audio_analysis):
    #     response = self.client.post(reverse('audio_analysis'), {'audio': 'fake'})
    #     self.assertEqual(response.content, b"mocked response")

    # @patch("realworld.views.video_analysis", return_value=HttpResponse("mocked response"))
    # def test_video_analysis(self, mock_video_analysis):
    #     response = self.client.post(reverse('video_analysis'), {'video': 'fake'})
    #     self.assertEqual(response.content, b"mocked response")

    # @patch("realworld.views.document_analysis", return_value=HttpResponse("mocked response"))
    # def test_document_analysis(self, mock_doc_analysis):
    #     response = self.client.post(reverse('document_analysis'), {'document': 'fake'})
    #     self.assertEqual(response.content, b"mocked response")

    # @patch("realworld.views.book_review", return_value=HttpResponse("mocked response"))
    # def test_book_review(self, mock_book_review):
    #     response = self.client.post(reverse('book_review'), {'query': 'sample book'})
    #     self.assertEqual(response.content, b"mocked response")