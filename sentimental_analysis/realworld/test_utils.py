import unittest
from unittest.mock import patch, MagicMock
import hashlib
from .utils import (
    gemini_summarize,
    gemini_sentiment_analysis,
    gemini_caption_image,
    gemini_transcribe_audio,
    gemini_video_analysis,
    get_request_hash,
)
import json
import tempfile
import base64


class TestFunctions(unittest.TestCase):
    @patch("realworld.utils.genai.Client")
    def test_gemini_summarize(self, mock_client):
        mock_response = MagicMock()
        mock_response.text = "This is a summary."
        mock_client.return_value.models.generate_content.return_value = mock_response

        result = gemini_summarize("This is a long text.")

        self.assertEqual(result, "This is a summary.")
        mock_client.assert_called_once()

    @patch("realworld.utils.genai.Client")
    def test_gemini_sentiment_analysis(self, mock_client):
        mock_response = MagicMock()
        mock_response.text = json.dumps({"pos": 0.7, "neu": 0.2, "neg": 0.1})
        mock_client.return_value.models.generate_content.return_value = mock_response

        result = gemini_sentiment_analysis("This is a test text.")

        self.assertEqual(result, {"pos": 0.7, "neu": 0.2, "neg": 0.1})
        mock_client.assert_called_once()

    @patch("realworld.utils.genai.Client")
    def test_gemini_caption_image(self, mock_client):
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        mock_response.text = "A happy family in a park."
        mock_instance.models.generate_content.return_value = mock_response

        # Use a valid Base64 string here
        valid_base64_data = base64.b64encode(b"fake_image_bytes").decode("utf-8")
        result = gemini_caption_image(valid_base64_data)

        self.assertEqual(result, "A happy family in a park.")
        mock_instance.models.generate_content.assert_called_once()

    @patch("realworld.utils.genai.Client")
    def test_gemini_transcribe_audio(mock_client):
        # Create a mock instance for the client.
        mock_instance = mock_client.return_value
        # Create a mock response with the expected transcription in the text attribute.
        mock_response = MagicMock()
        mock_response.text = "This is a transcription."
        # Patch the generate_content method to return our mock_response.
        mock_instance.models.generate_content.return_value = mock_response

        # Provide dummy binary data (can be any bytes since it's not actually used).
        dummy_audio_data = b"dummy audio bytes"

        # Call your transcribe function.
        result = gemini_transcribe_audio(dummy_audio_data)

        # Assert that the function returns the expected transcription.
        assert result == "This is a transcription."
        
        # Also verify generate_content was called exactly once.
        mock_instance.models.generate_content.assert_called_once()

        @patch("realworld.utils.genai.Client")
        def test_gemini_video_analysis_with_url(self, mock_client):
            mock_response = MagicMock()
            mock_response.text = "This is a video analysis."
            mock_client.return_value.models.generate_content.return_value = mock_response

            result = gemini_video_analysis(video_bytes=None, video_url="http://example.com/video.mp4")

            self.assertEqual(result, "This is a video analysis.")
            mock_client.assert_called_once()

        @patch("realworld.utils.genai.Client")
        def test_gemini_video_analysis_with_bytes(self, mock_client):
            mock_response = MagicMock()
            mock_response.text = "This is a video analysis."
            mock_client.return_value.models.generate_content.return_value = mock_response

            video_bytes = tempfile.TemporaryFile()
            video_bytes.write(b"fake_video_data")
            video_bytes.seek(0)

            result = gemini_video_analysis(video_bytes=video_bytes, video_url=None)

            self.assertEqual(result, "This is a video analysis.")
            mock_client.assert_called_once()

        def test_get_request_hash(self):
            mock_request = MagicMock()
            mock_request.method = "POST"
            mock_request.path = "/api/test"
            mock_request.GET.dict.return_value = {"key1": "value1"}
            mock_request.POST.dict.return_value = {"key2": "value2"}
            # Make sure no files are uploaded:
            mock_request.FILES = {}

            result = get_request_hash(mock_request)

            expected_data = {
                "method": "POST",
                "path": "/api/test",
                "GET": {"key1": "value1"},
                "POST": {"key2": "value2"},
            }
            expected_hash = hashlib.sha256(json.dumps(expected_data, sort_keys=True).encode("utf-8")).hexdigest()

            self.assertEqual(result, expected_hash)

if __name__ == "__main__":
    unittest.main()
