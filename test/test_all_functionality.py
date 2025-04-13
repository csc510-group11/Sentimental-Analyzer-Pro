import os
import json

import unittest
import re
import string
import speech_recognition as sr
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from django.template.defaulttags import register
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from io import StringIO


# Unit Test Case for Audio, Product, Document Sentiment Analyzer
class AllFunctionalityTestCase(unittest.TestCase):

    def removeLinks(self, text):
        linkPattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(linkPattern, '', text)

    def stripEmojis(self, text):
        return text.encode('ascii', 'ignore').decode('ascii')

    def stripPunctuations(self, text):
        return text.translate(str.maketrans('', '', string.punctuation))

    def stripExtraWhiteSpaces(self, text):
        return text.strip()

    def removeSpecialChar(self, text):
        return re.sub(r'\W+ ', '', text)

    def sentiment_scores(self, sentence):
        # Create a SentimentIntensityAnalyzer object.
        sid_obj = SentimentIntensityAnalyzer()

        # polarity_scores method of SentimentIntensityAnalyzer
        # object gives a sentiment dictionary.
        # which contains pos, neg, neu, and compound scores.
        sentiment_dict = sid_obj.polarity_scores(sentence)
        return sentiment_dict

    def pdfparser(self, data):
        fp = open(data, 'rb')
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
            data = retstr.getvalue()

        text_file = open("Output.txt", "w", encoding="utf-8")
        text_file.write(data)

        text_file = open("Output.txt", 'r', encoding="utf-8")
        a = ""
        for x in text_file:
            if len(x) > 2:
                b = x.split()
                for i in b:
                    a += " " + i
        final_comment = a.split('.')
        return final_comment

    def get_clean_text(self, text):
        text = self.removeLinks(text)
        text = self.stripEmojis(text)
        text = self.removeSpecialChar(text)
        text = self.stripPunctuations(text)
        text = self.stripExtraWhiteSpaces(text)

        # Tokenize using nltk
        tokens = nltk.word_tokenize(text)

        # Import stopwords
        stop_words = set(stopwords.words('english'))
        stop_words.add('rt')
        stop_words.add('')

        # Remove tokens which are in stop_words
        newtokens = [item for item in tokens if item not in stop_words]

        textclean = ' '.join(newtokens)
        return textclean

    def detailed_analysis(self, result):
        result_dict = {}
        neg_count = 0
        pos_count = 0
        neu_count = 0

        for item in result:
            cleantext = self.get_clean_text(str(item))
            sentiment = self.sentiment_scores(cleantext)

            pos_count += sentiment['pos']
            neu_count += sentiment['neu']
            neg_count += sentiment['neg']

        total = pos_count + neu_count + neg_count
        result_dict['pos'] = (pos_count / total)
        result_dict['neu'] = (neu_count / total)
        result_dict['neg'] = (neg_count / total)

        return result_dict

    def input(self, pathname):
        extension_name = pathname[len(pathname) - 3:]
        result = {}
        if extension_name == 'pdf':
            value = self.pdfparser(pathname)
            result = self.detailed_analysis(value)
        elif extension_name == 'txt':
            text_file = open(pathname, 'r', encoding="utf-8")
            a = ""
            for x in text_file:
                if len(x) > 2:
                    b = x.split()
                    for i in b:
                        a += " " + i
            final_comment = a.split('.')
            result = self.detailed_analysis(final_comment)
        elif extension_name == 'wav':
            r = sr.Recognizer()
            with sr.AudioFile(pathname) as source:
                # listen for the data (load audio to memory)
                audio_data = r.record(source)
                # recognize (convert from speech to text)
                text = r.recognize_google(audio_data)
                value = text.split('.')
                result = self.detailed_analysis(value)
        # Sentiment Analysis
        return result

    def productanalysis(self):
        os.system('scrapy runspider "./sentimental_analysis/realworld/amazon_test.py"/ -o "/sentimental_analysis/realworld/reviews.json"/')
        final_comment = []
        with open('sentimental_analysis/realworld/reviews.json') as json_file:
            data = json.load(json_file)
            for p in range(1, len(data) - 1):
                a = data[p]['comment']
                final_comment.append(a)

        # final_comment is a list of strings!
        result = self.detailed_analysis(final_comment)
        return result

    def textanalysis(self, final_comment):
        final_comment = final_comment.split('.')
        result = self.detailed_analysis(final_comment)
        return result

    @register.filter(name='get_item')
    def get_item(self, dictionary, key):
        return dictionary.get(key, 0)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        nltk.download('vader_lexicon')
        nltk.download('stopwords')
        nltk.download('punkt')

    def test_text_analysis(self):
        string_name = "Its been a pleasure working with you! The lunch was great and the ambience was amazing"
        test_output = self.textanalysis(string_name)
        expected_output = {'pos': 0.699, 'neu': 0.301, 'neg': 0.0}
        self.assertEqual(test_output, expected_output)

    def test_product_analysis(self):
        test_output = self.productanalysis()
        message = "Test value is not greater or equal than expected value."
        expected_output = {'pos': 0.07, 'neu': 0.8, 'neg': 0.09}
        self.assertGreaterEqual(
            test_output["pos"], expected_output["pos"], message)
        self.assertGreaterEqual(
            test_output["neu"], expected_output["neu"], message)
        self.assertGreaterEqual(
            test_output["neg"], expected_output["neg"], message)

    def test_document_analysis(self):
        test_output = self.input(
            "./sentimental_analysis/media/document/Nischal_Badarinath_Kashyap.pdf")
        expected_output = {'pos': 0.05, 'neu': 0.9, 'neg': 0.01}
        message = "Test value is not greater or equal than expected value."
        self.assertGreaterEqual(
            test_output["pos"], expected_output["pos"], message)
        self.assertGreaterEqual(
            test_output["neu"], expected_output["neu"], message)
        self.assertGreaterEqual(
            test_output["neg"], expected_output["neg"], message)
        # self.assertGre(test_output, expected_output)
# main function
if __name__ == '__main__':
    unittest.main()
