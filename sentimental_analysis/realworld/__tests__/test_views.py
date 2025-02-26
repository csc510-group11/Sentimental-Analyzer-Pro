import unittest
from django.test import TestCase
from django.urls import reverse
import os, sys
import csv
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# from views import detailed_analysis_sentence
from realworld.views import detailed_analysis_sentence, determine_language
class TestViews(unittest.TestCase):

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

class TestTextAnalysis(TestCase):
    # kwilso24
    def test_text_analysis_get(self):
        response = self.client.get(reverse('text analysis'))
        self.assertEqual(response.status_code, 200)
        # content should be html
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    # kwilso24
    def test_text_analysis_get_fields(self):
        response = self.client.get(reverse('text analysis'))
        self.assertIn('note', response.context)


    # kwilso24
    def test_text_analysis_post(self):
        response = self.client.post(reverse('text analysis'), {'textField': 'This is a test sentence'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    # kwilso24
    def test_text_analysis_post_fields(self):
        response = self.client.post(reverse('text analysis'), {'textField': 'This is a test sentence'})
        self.assertIn('sentiment', response.context)
        self.assertIn('text', response.context)
        self.assertIn('reviewsRatio', response.context)
        self.assertIn('showReviewsRatio', response.context)
        self.assertEqual(['This is a test sentence'], response.context['text'])

    # kwilso24
    def test_text_analysis_output_structure_text(self):
        response = self.client.post(reverse('text analysis'), {'textField': 'This is a test sentence. This is another'})
        # text is split by period
        self.assertEqual(2, len(response.context['text']))
        self.assertEqual(['This is a test sentence', ' This is another'], response.context['text'])

    # kwilso24
    def test_text_analysis_output_structure_sentiment(self):
        response = self.client.post(reverse('text analysis'), {'textField': 'This is a test sentence'})
        self.assertEqual(3, len(response.context['sentiment']))
        # check that sentiment has 3 keys ('pos', 'neu', 'neg')
        self.assertIn('pos', response.context['sentiment'])
        self.assertIn('neu', response.context['sentiment'])
        self.assertIn('neg', response.context['sentiment'])
        # check that values are floats
        self.assertIsInstance(response.context['sentiment']['pos'], float)
        self.assertIsInstance(response.context['sentiment']['neu'], float)
        self.assertIsInstance(response.context['sentiment']['neg'], float)

    # kwilso24
    def test_text_analysis_output_structure_reviewsRatio(self):
        # should be empty
        response = self.client.post(reverse('text analysis'), {'textField': 'This is a test sentence'})
        self.assertEqual({}, response.context['reviewsRatio'])


class TestBatchAnalysis(TestCase):
    # kwilso24
    def test_batch_analysis_get(self):
        response = self.client.get(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence'})
        self.assertEqual(response.status_code, 200)
        # content should be html
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    # kwilso24
    def test_batch_analysis_post(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    # kwilso24
    def test_batch_analysis_post_fields(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence'})
        self.assertIn('sentiment', response.context)
        self.assertIn('text', response.context)
        self.assertIn('reviewsRatio', response.context)
        self.assertIn('showReviewsRatio', response.context)
        self.assertIn('totalReviews', response.context)
        self.assertIn('texts_orig', response.context)

    # kwilso24
    def test_batch_analysis_output_text(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence'})
        self.assertEqual(['This is a test sentence'], response.context['text'])

    # kwilso24
    def test_batch_analysis_output_structure_text(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence.\nThis is another'})
        # text is split by newline
        self.assertEqual(2, len(response.context['text']))
        self.assertEqual(['This is a test sentence.', 'This is another'], response.context['text'])

    # kwilso24
    def test_batch_analysis_output_structure_sentiment(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence'})
        self.assertEqual(3, len(response.context['sentiment']))
        # check that sentiment has 3 keys ('pos', 'neu', 'neg')
        self.assertIn('pos', response.context['sentiment'])
        self.assertIn('neu', response.context['sentiment'])
        self.assertIn('neg', response.context['sentiment'])
        # check that values are floats
        self.assertIsInstance(response.context['sentiment']['pos'], float)
        self.assertIsInstance(response.context['sentiment']['neu'], float)
        self.assertIsInstance(response.context['sentiment']['neg'], float)

    # kwilso24
    def test_batch_analysis_orig_passed(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence'})
        self.assertEqual('This is a test sentence', response.context['texts_orig'])
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence.\nThis is another'})
        self.assertEqual('This is a test sentence.\nThis is another', response.context['texts_orig'])


    # kwilso24
    def test_batch_analysis_csv_type(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence}', 'download_csv': 'true'})
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="sentiment_analysis_results.csv"')

    # kwilso24
    def test_batch_analysis_csv_parse(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence}', 'download_csv': 'true'})
        # check that csv is not empty
        self.assertTrue(response.content)
        # check that csv has correct headers
        csv_content = response.content.decode('utf-8')
        headers = csv_content.splitlines()[0].split(',')
        expected_headers = ['Index', 'Text', 'Positive', 'Negative', 'Neutral']
        self.assertListEqual(headers, expected_headers)

    # kwilso24
    def test_batch_analysis_csv_data(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence}', 'download_csv': 'true'})
        # check that csv is not empty
        self.assertTrue(response.content)
        # check that csv has correct data
        csv_content = response.content.decode('utf-8')
        # should be 2 lines: header and data
        lines = csv_content.splitlines()
        self.assertEqual(2, len(lines))
        # check that data is correct
        data = lines[1].split(',')
        assert len(data) == 5
        # make sure the first column is an integer
        self.assertIsInstance(int(data[0]), int)
        # make sure the second column is a string
        self.assertIsInstance(data[1], str)
        # make sure the last three columns are floats
        self.assertIsInstance(float(data[2]), float)
        self.assertIsInstance(float(data[3]), float)
        self.assertIsInstance(float(data[4]), float)

    # kwilso24
    def test_batch_analysis_csv_multiple_lines(self):
        response = self.client.post(reverse('batch_text_analysis'), {'batchTextField': 'This is a test sentence.\nThis is another}', 'download_csv': 'true'})
        # check that csv is not empty
        self.assertTrue(response.content)
        # check that csv has correct data
        csv_content = response.content.decode('utf-8')
        # should be 3 lines: header and 2 data lines
        lines = csv_content.splitlines()
        self.assertEqual(3, len(lines))
        # check that data is correct
        for i in range(1, 3):
            data = lines[i].split(',')
            assert len(data) == 5
            # make sure the first column is an integer
            self.assertIsInstance(int(data[0]), int)
            # make sure the second column is a string
            self.assertIsInstance(data[1], str)
            # make sure the last three columns are floats
            self.assertIsInstance(float(data[2]), float)
            self.assertIsInstance(float(data[3]), float)
            self.assertIsInstance(float(data[4]), float)


class LanguageCheck(TestCase):
    # kwilso24
    def test_eng_check(self):
        # Fails: apparently I speak vietnamese
        result = determine_language("This is a test sentence with tons of english-like words")
        self.assertEqual(result, True)

    # kwilso24
    def test_es_check(self):
        result = determine_language("Hola, como estas?")
        self.assertEqual(result, False)


if __name__ == '__main__':
    unittest.main()