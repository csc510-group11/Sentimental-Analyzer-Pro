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
    def test_generate_emotion_caption(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"generated_text": "A happy family in a park."}]
        mock_post.return_value = mock_response

        result = gemini_caption_image("encoded_image_data")

        self.assertEqual(result, "A happy family in a park.")
        mock_post.assert_called_once()

    @patch("realworld.utils.genai.Client")
    def test_transcribe_audio(self, mock_transcriber):
        mock_transcription = MagicMock()
        mock_transcription.text = "This is a transcription."
        mock_transcriber.return_value.transcribe.return_value = mock_transcription

        audio_data = b"fake_audio_data"

        result = gemini_transcribe_audio(audio_data)

        self.assertEqual(result, "This is a transcription.")
        mock_transcriber.assert_called_once()

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
