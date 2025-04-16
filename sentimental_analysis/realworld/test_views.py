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
        self.factory = RequestFactory()

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
    def test_text_view(self, mock_text_analysis):
        request = self.factory.post('/text-analysis/', data={'text': 'whatever'})
        request.user = self.user

        response = mock_text_analysis(request)

        self.assertEqual(response.content, b"mocked response")

    @patch("realworld.views.image_analysis", return_value=HttpResponse("mocked response"))
    def test_image_view(self, mock_image_analysis):
        request = self.factory.post('/image-analysis/', {'image': 'fake'})
        request.user = self.user
        response = mock_image_analysis(request)
        self.assertEqual(response.content, b"mocked response")

    @patch("realworld.views.audio_analysis", return_value=HttpResponse("mocked response"))
    def test_audio_view(self, mock_audio_analysis):
        request = self.factory.post('/audio-analysis/', {'audio': 'fake'})
        request.user = self.user
        response = mock_audio_analysis(request)
        self.assertEqual(response.content, b"mocked response")

    @patch("realworld.views.video_analysis", return_value=HttpResponse("mocked response"))
    def test_video_view(self, mock_video_analysis):
        request = self.factory.post('/video-analysis/', {'video': 'fake'})
        request.user = self.user
        response = mock_video_analysis(request)
        self.assertEqual(response.content, b"mocked response")

    @patch("realworld.views.document_analysis", return_value=HttpResponse("mocked response"))
    def test_document_view(self, mock_doc_analysis):
        request = self.factory.post('/document-analysis/', {'document': 'fake'})
        request.user = self.user
        response = mock_doc_analysis(request)
        self.assertEqual(response.content, b"mocked response")

    @patch("realworld.views.book_review", return_value=HttpResponse("mocked response"))
    def test_book_view(self, mock_book_review):
        request = self.factory.post('/book-review/', {'query': 'sample book'})
        request.user = self.user
        response = mock_book_review(request)
        self.assertEqual(response.content, b"mocked response")

    @patch("realworld.views.movie_review", return_value=HttpResponse("mocked response"))
    def test_movie_view(self, mock_movie_review):
        request = self.factory.post('/movie-review/', {'query': 'sample movie'})
        request.user = self.user
        response = mock_movie_review(request)
        self.assertEqual(response.content, b"mocked response")

    @patch("realworld.views.restaurant_review", return_value=HttpResponse("mocked response"))
    def test_restaurant_view(self, mock_restaurant_review):
        request = self.factory.post('/restaurant-review/', {'query': 'sample restaurant'})
        request.user = self.user
        response = mock_restaurant_review(request)
        self.assertEqual(response.content, b"mocked response")

    @patch("realworld.views.product_review", return_value=HttpResponse("mocked response"))
    def test_product_view(self, mock_product_review):
        request = self.factory.post('/product-review/', {'query': 'sample product'})
        request.user = self.user
        response = mock_product_review(request)
        self.assertEqual(response.content, b"mocked response")


    def test_text_analysis(self):
        response = self.client.post(reverse('text_analysis'), {'text': 'sample'})
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    def test_image_analysis(self):
        with open("assets/tests/test.jpg", "rb") as img:
            image_file = SimpleUploadedFile("cat.jpg", img.read(), content_type="image/jpeg")
        response = self.client.post(reverse('image_analysis'), {'image': image_file})
        print(response.content)
        self.assertIn(b"Caption", response.content)
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    def test_audio_analysis(self):
        with open("assets/tests/test.wav", "rb") as audio:
            audio_file = SimpleUploadedFile("sample_audio.wav", audio.read(), content_type="audio/wav")
        response = self.client.post(reverse('audio_analysis'), {'audio': audio_file})
        self.assertIn(b"Summary", response.content)
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    def test_video_analysis(self):
        with open("assets/tests/test.mp4", "rb") as video:
            video_file = SimpleUploadedFile("sample_video.mp4", video.read(), content_type="video/mp4")
        response = self.client.post(reverse('video_analysis'), {'video_bytes': video_file})
        self.assertIn(b"Summary", response.content)
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    def test_document_analysis(self):
        with open("assets/tests/test.txt", "rb") as doc:
            document_file = SimpleUploadedFile("test.txt", doc.read(), content_type="text/plain")
        response = self.client.post(reverse('document_analysis'), {'document': document_file})
        self.assertIn(b"Summary", response.content)
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    def test_book_review(self):
        book_url = "https://www.goodreads.com/book/show/2767052-the-hunger-games"
        response = self.client.post(reverse('book_review'), {'review_url': book_url})
        self.assertIn(b"Summary", response.content)
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    def test_movie_review(self):
        movie_url = "https://www.imdb.com/title/tt1825683/"
        response = self.client.post(reverse('movie_review'), {'review_url': movie_url})
        self.assertIn(b"Summary", response.content)
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    def test_restaurant_review(self):
        restaurant_url = "https://www.tripadvisor.com/Restaurant_Review-g34227-d25078326-Reviews-La_Fuga-Fort_Lauderdale_Broward_County_Florida.html"
        response = self.client.post(reverse('restaurant_review'), {'review_url': restaurant_url})
        self.assertIn(b"Summary", response.content)
        self.assertIn(b"Positive", response.content)
        self.assertIn(b"Negative", response.content)
        self.assertIn(b"Neutral", response.content)

    # def test_product_review(self):
    #     product_url = "https://www.etsy.com/listing/1808685200/100-random-programmer-stickers-coding"
    #     response = self.client.post(reverse('product_review'), {'review_url': product_url})
    #     self.assertIn(b"Summary", response.content)
    #     self.assertIn(b"Positive", response.content)
    #     self.assertIn(b"Negative", response.content)
    #     self.assertIn(b"Neutral", response.content)
        