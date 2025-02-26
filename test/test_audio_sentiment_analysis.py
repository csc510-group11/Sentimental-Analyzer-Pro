import sys
sys.path.append("./sentimental_analysis/audio/")
import unittest
import audio.audio_analyzer as audio_analyzer

# Unit Test Case for Audio Sentiment Analyzer
class AudioSentimentAnalyzerTestCase(unittest.TestCase):

    # Setup
    def setup(self):
        self.aa = audio_analyzer.AudioAnalyzer()

    # Test case for speech_to_text method
    def test_speech_to_text(self):
        aa = audio_analyzer.AudioAnalyzer()
        self.assertEqual(aa.speech_to_text("./test/test_wv.wav"), "hello how are you")

    # Test case for sentiment_analyzer_scores method
    def test_sentiment_analyzer_scores(self):
        aa = audio_analyzer.AudioAnalyzer()
        self.assertEqual(aa.sentiment_analyzer_scores("hello how are you")["pos"], 0)


# main function
if __name__ == '__main__':
     unittest.main()
