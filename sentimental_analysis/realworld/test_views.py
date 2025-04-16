import io
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_index_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('index'))  # make sure your urls.py uses name='index'
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'realworld/index.html')

    def test_document_analysis_file_too_large(self):
        self.client.login(username='testuser', password='testpass')
        big_file = SimpleUploadedFile("big.pdf", b"a" * (5 * 1024 * 1024 + 1), content_type="application/pdf")
        response = self.client.post(reverse('document_analysis'), {'document': big_file})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"File size exceeds 5MB limit.", response.content)

    def test_document_analysis_valid_pdf(self):
        self.client.login(username='testuser', password='testpass')
        small_pdf = io.BytesIO()
        small_pdf.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<<>>\n%%EOF")
        small_pdf.seek(0)
        pdf_file = SimpleUploadedFile("test.pdf", small_pdf.read(), content_type="application/pdf")

        response = self.client.post(reverse('document_analysis'), {'document': pdf_file})
        self.assertEqual(response.status_code, 200)  # Or whatever response is expected
