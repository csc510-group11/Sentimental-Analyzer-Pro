from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PyPDF2 import PdfWriter

class DocumentAnalysisTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('document_analysis')

    def test_get_request(self):
        """Test that GET requests render the document analysis template."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'realworld/document_analysis.html')

    def test_no_file_uploaded(self):
        """Test that POST requests without a file return an error."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "No file uploaded.")

    def test_unsupported_file_type(self):
        """Test that unsupported file types return an error."""
        file_data = BytesIO(b"Unsupported file content")
        file_data.name = "unsupported_file.xyz"
        response = self.client.post(self.url, {'document': file_data})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Unsupported file type. Please upload a TXT or PDF file.")

    def test_txt_file_upload(self):
        """Test that a valid TXT file is processed correctly."""
        file_content = "This is a test document."
        file_data = BytesIO(file_content.encode('utf-8'))
        file_data.name = "test_document.txt"
        response = self.client.post(self.url, {'document': file_data})
        self.assertEqual(response.status_code, 200)

    def test_pdf_file_upload(self):
        """Test that a valid PDF file is processed correctly."""
        # Create a simple PDF file in memory
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=595, height=842)
        pdf_data = BytesIO()
        pdf_writer.write(pdf_data)
        pdf_data.seek(0)
        pdf_data.name = "test_document.pdf"

        uploaded_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=pdf_data.read(),
            content_type="application/pdf"
        )

        response = self.client.post(
            self.url,
            {'document': uploaded_file}
        )

        response = self.client.post(self.url, {'document': uploaded_file})
        self.assertEqual(response.status_code, 406)

    def test_large_file_upload(self):
        """Test that files larger than 5MB are rejected."""
        large_file_content = b"A" * (5 * 1024 * 1024 + 1)
        large_file = BytesIO(large_file_content)
        large_file.name = "large_file.txt"
        response = self.client.post(self.url, {'document': large_file})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "File size exceeds 5MB limit.")

    def test_txt_file_decoding_error(self):
        """Test that a decoding error in a TXT file returns an error."""
        invalid_txt_content = b"\x80\x81\x82"
        invalid_txt_file = BytesIO(invalid_txt_content)
        invalid_txt_file.name = "invalid_document.txt"
        response = self.client.post(self.url, {'document': invalid_txt_file})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Error decoding text file.")

    def test_pdf_processing_error(self):
        """Test that a PDF processing error returns an error."""
        invalid_pdf_content = b"Not a valid PDF file"
        invalid_pdf_file = BytesIO(invalid_pdf_content)
        invalid_pdf_file.name = "invalid_document.pdf"
        response = self.client.post(self.url, {'document': invalid_pdf_file})
        self.assertEqual(response.status_code, 406)
        self.assertIn("Error processing PDF file", response.content.decode())
