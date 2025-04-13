import os, sys
import json
from io import StringIO
from google import genai
import subprocess
import shutil
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import speech_recognition as sr
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.template.defaulttags import register
from django.http import HttpResponse
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pydub import AudioSegment
from sentimental_analysis.realworld.scrapers.newsScraper import *
from realworld.utilityFunctions import *
from sentimental_analysis.realworld.scrapers.reddit_scrap import *
from django.contrib.auth.decorators import login_required
from realworld.cache_manager import AnalysisCache
from realworld.cache_manager import AnalysisCache
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

def pdfparser(data):
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

@login_required
def analysis(request):
    return render(request, 'realworld/index.html')

def detailed_analysis(result):
    result_dict = {"pos": 0, "neu": 0, "neg": 0}
    neg_count = 0
    pos_count = 0
    neu_count = 0
    total_count = len(result)

    if isinstance(result, str):
        result = [result]

    # logging.info("running detailed analysis on %s", result)
    for item in result:
        # cleantext = get_clean_text(str(item))
        cleantext = str(item)
        # print(cleantext)
        # logging.info("cleaned text: %s", cleantext)
        sentiment = sentiment_scores(cleantext)
        # logging.info("sentiment: %s", sentiment)
        pos_count += sentiment['pos']
        neu_count += sentiment['neu']
        neg_count += sentiment['neg']
    total = pos_count + neu_count + neg_count
    if(total>0):
        pos_ratio = (pos_count/total)
        neu_ratio = (neu_count/total)
        neg_ratio = (neg_count/total)
        result_dict['pos'] = pos_ratio
        result_dict['neu'] = neu_ratio
        result_dict['neg'] = neg_ratio
    return result_dict

def detailed_analysis_sentence(result):
    sia = SentimentIntensityAnalyzer()
    result_dict = {}
    result_dict['compound'] = sia.polarity_scores(result)['compound']
    return result_dict

def input(request):
    if request.method == 'POST':
        file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(file.name, file)
        pathname = 'sentimental_analysis/media/'
        extension_name = file.name
        extension_name = extension_name[len(extension_name) - 3:]
        path = pathname + file.name
        destination_folder = 'sentimental_analysis/media/document/'
        shutil.copy(path, destination_folder)
        useFile = destination_folder + file.name
        result = {}
        finalText = ''
        if extension_name == 'pdf':
            value = pdfparser(useFile)
            result = detailed_analysis(value)
            finalText = result
        elif extension_name == 'txt':
            text_file = open(useFile, 'r', encoding="utf-8")
            a = ""
            for x in text_file:
                if len(x) > 2:
                    b = x.split()
                    for i in b:
                        a += " " + i
            final_comment = a.split('.')
            text_file.close()
            finalText = final_comment
            result = detailed_analysis(final_comment)
        folder_path = 'sentimental_analysis/media/'
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return render(request, 'realworld/results.html', {'sentiment': result, 'text': finalText, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False})
    else:
        note = "Please Enter the Document you want to analyze"
        return render(request, 'realworld/home.html', {'note': note})

def inputimage(request):
    if request.method == 'POST':
        return
    '''
        file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(file.name, file)
        pathname = 'sentimental_analysis/media/'
        extension_name = file.name
        extension_name = extension_name[len(extension_name) - 3:]
        path = pathname + file.name
        destination_folder = 'sentimental_analysis/media/document/'
        shutil.copy(path, destination_folder)
        useFile = destination_folder + file.name
        image = cv2.imread(useFile)
        detected_emotion = DeepFace.analyze(image)

        emotions_dict = {'happy': 0.0, 'sad': 0.0, 'neutral': 0.0}
        for emotion in detected_emotion:
            emotion_scores = emotion['emotion']
            happy_score = emotion_scores['happy']
            sad_score = emotion_scores['sad']
            neutral_score = emotion_scores['neutral']

            emotions_dict['happy'] += happy_score
            emotions_dict['sad'] += sad_score
            emotions_dict['neutral'] += neutral_score

        total_score = sum(emotions_dict.values())
        if total_score > 0:
            for emotion in emotions_dict:
                emotions_dict[emotion] /= total_score

        print(emotions_dict)
        finalText = max(emotions_dict, key=emotions_dict.get)
        return render(request, 'realworld/resultsimage.html',
                      {'sentiment': emotions_dict, 'text': finalText, 'analyzed_image_path': useFile})
'''

def productanalysis(request):
    if request.method == 'POST':
        blogname = request.POST.get("blogname", "")

        text_file = open(
            "Amazon_Comments_Scrapper/amazon_reviews_scraping/amazon_reviews_scraping/spiders/ProductAnalysis.txt", "w")
        text_file.write(blogname)
        text_file.close()

        spider_path = r'Amazon_Comments_Scrapper/amazon_reviews_scraping/amazon_reviews_scraping/spiders/amazon_review.py'
        output_file = r'Amazon_Comments_Scrapper/amazon_reviews_scraping/amazon_reviews_scraping/spiders/reviews.json'
        command = f"scrapy runspider \"{spider_path}\" -o \"{output_file}\" "
        result = subprocess.run(command, shell=True)

        if result.returncode == 0:
            print("Scrapy spider executed successfully.")
        else:
            print("Error executing Scrapy spider.")

        with open(r'Amazon_Comments_Scrapper/amazon_reviews_scraping/amazon_reviews_scraping/spiders/reviews.json',
                  'r') as json_file:
            json_data = json.load(json_file)
        reviews = []
        reviews2 = {
            "pos": 0,
            "neu": 0,
            "neg": 0,
        }
        for item in json_data:
            reviews.append(item['Review'])
            r = detailed_analysis_sentence(item['Review'])
            if(r != {}):
                st = item['Stars']
                if(st is not None):
                    stars = int(float(st))
                    if(stars != -1):
                        if(stars >= 4):
                            r['compound'] += 0.1
                        elif(stars >= 2):
                           continue
                        else:
                            r['compound'] -= 0.1
                if(r['compound'] > 0.4):
                    reviews2['pos'] += 1
                elif(r['compound'] < -0.4):
                    reviews2['neg'] += 1
                else:
                    reviews2['neu'] +=1
        finalText = reviews
        totalReviews = reviews2['pos'] + reviews2['neu'] + reviews2['neg']
        result = detailed_analysis(reviews)
        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : finalText, 'reviewsRatio': reviews2, 'totalReviews': totalReviews, 'showReviewsRatio': True})

    else:
        note = "Please Enter the product blog link for analysis"
        return render(request, 'realworld/productanalysis.html', {'note': note})


# Text sentiment Analysis - Detect Language and use corresponding model for sentiment score
    """Detects the language of the given text using spaCy."""
    detected_languages = []
    for text in texts:
        try:
            lang = detect(text)
            detected_languages.append(lang)
        except Exception:
            detected_languages.append("unknown")
    # Determine the most common detected language
    return max(set(detected_languages), key=detected_languages.count)

class SentimentScore(BaseModel):
    pos: float
    neu: float
    neg: float

def gemini_sentiment_analysis(text, model="gemini-2.0-flash"):
    """
    Calls the Gemini API to perform sentiment analysis on the provided text.
    
    Args:
        text (str): The input text for sentiment analysis.
        model (str): The Gemini model to use. Default is "gemini-2.0-flash".
        
    Returns:
        dict: A dictionary containing sentiment analysis results, e.g. {'pos': 0.7, 'neu': 0.2, 'neg': 0.1}
    """
    # Construct a prompt specifically designed to extract sentiment analysis scores
    # Customize the prompt as needed based on how Gemini expects instructions.
    prompt = (
        "Perform sentiment analysis on the following text. "
        "Return a JSON object with keys 'pos', 'neu', and 'neg' representing the positive, neutral, and negative sentiment scores respectively:\n\n"
        f"{text}"
    )

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Call the Gemini API using the client
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': SentimentScore,
            },
        )
        # Log the raw response for debugging
        logging.info("Gemini raw response: %s", response.text)
        
        # Assume the response.text is a JSON formatted string
        result = json.loads(response.text)
        
    except Exception as e:
        logging.error("Error during Gemini API call: %s", e)
        # Optionally, define a fallback sentiment result or raise an error
        result = {"pos": 0.0, "neu": 0.0, "neg": 0.0}
    
    return result

def textanalysis(request):
    """Performs sentiment analysis for the single line text"""
    if request.method == 'POST':
        text_data = request.POST.get("textField", "")
        final_comment = text_data.split('.')
        result = {}
        finalText = final_comment

        '''
        logging.info("Text Data: %s", text_data)  # Debugging
        lang = detect_language(final_comment)
        logging.info("Detected Language: %s", lang)  # Debugging

        if detect_language(final_comment) == 'en':
            logging.info("using %s", final_comment)
            result = detailed_analysis(final_comment)
            logging.info("Sentiment Scores: %s", result)  # Debugging
        else:
            sc = classifiers.SpanishClassifier(model_name="sentiment_analysis")
            result_string = ' '.join(final_comment)
            result_classifier = sc.predict(result_string)
            result = {
                'pos': result_classifier.get('positive', 0.0),
                'neu': result_classifier.get('neutral', 0.0),
                'neg': result_classifier.get('negative', 0.0)
            }
        '''
        result = gemini_sentiment_analysis(text_data)
        # logging.info("Sentiment Scores: %s", str(sentiment_scores))  # Debugging
        logging.info("result: %s", result)  # Debugging

        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : finalText, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False,})

    else:
        note = "Enter the Text to be analysed!"
        return render(request, 'realworld/textanalysis.html', {'note': note, 'heatmap_image': image_base64})

def batch_analysis(request):
    logging.info("Batch analysis called! Woah!")
    pass

# End of text sentiment analysis

def scrap_social_media(url):
    return """
        I am so sad today! :(
        I don't know what to do. I feel like crying. :(
        I just want to be happy again. :(
        I miss my friends. :(
        I miss my family. :(
        I miss my life. :(
    """

def fbanalysis(request):
    if request.method == 'POST':
        rquest_url = request.POST.get("blogname", "")

        scrapped_data = scrap_social_media(rquest_url)

        logging.info("scrapped_data: %s", scrapped_data)  # Debugging

        result = gemini_sentiment_analysis(scrapped_data)


        # logging.info("Sentiment Scores: %s", str(sentiment_scores))  # Debugging
        logging.info("result: %s", result)  # Debugging


        return render(request, 'realworld/results.html', {'sentiment': result, 'text': scrapped_data.split("\n"), 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False})

def twitteranalysis(request):
    if request.method == 'POST':
        rquest_url = request.POST.get("blogname", "")

        scrapped_data = scrap_social_media(rquest_url)

        result = gemini_sentiment_analysis(scrapped_data)

        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : scrapped_data.split("\n"), 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False})


def redditanalysis(request):
    if request.method == 'POST':
        rquest_url = request.POST.get("blogname", "")

        scrapped_data = scrap_social_media(rquest_url)

        result = gemini_sentiment_analysis(scrapped_data)

        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : scrapped_data.split("\n"), 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False})


def audioanalysis(request):
    if request.method == 'POST':
        file = request.FILES['audioFile']
        fs = FileSystemStorage()
        fs.save(file.name, file)
        pathname = "sentimental_analysis/media/"
        extension_name = file.name
        extension_name = extension_name[len(extension_name) - 3:]
        path = pathname + file.name
        result = {}
        destination_folder = 'sentimental_analysis/media/audio/'
        shutil.copy(path, destination_folder)
        useFile = destination_folder + file.name
        text = speech_to_text(useFile)
        finalText = text
        result = detailed_analysis(text)

        folder_path = 'sentimental_analysis/media/'
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : finalText, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False})
    else:
        note = "Please Enter the audio file you want to analyze"
        return render(request, 'realworld/audio.html', {'note': note})

def livespeechanalysis(request):
    if request.method == 'POST':
        my_file_handle = open(
            'sentimental_analysis/realworld/recordedAudio.txt')
        audioFile = my_file_handle.read()
        result = {}
        text = speech_to_text(audioFile)

        finalText = text
        result = detailed_analysis(text)
        folder_path = 'sentimental_analysis/media/recordedAudio/'
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : finalText, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False})


@csrf_exempt
def recordaudio(request):
    if request.method == 'POST':
        audio_file = request.FILES['liveaudioFile']
        fs = FileSystemStorage()
        fs.save(audio_file.name, audio_file)
        folder_path = 'sentimental_analysis/media/'
        files = os.listdir(folder_path)

        pathname = "sentimental_analysis/media/"
        extension_name = audio_file.name
        extension_name = extension_name[len(extension_name) - 3:]
        path = pathname + audio_file.name
        audioName = audio_file.name
        destination_folder = 'sentimental_analysis/media/recordedAudio/'
        shutil.copy(path, destination_folder)
        useFile = destination_folder + audioName
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        audio = AudioSegment.from_file(useFile)
        audio = audio.set_sample_width(2)
        audio = audio.set_frame_rate(44100)
        audio = audio.set_channels(1)
        audio.export(useFile, format='wav')

        text_file = open("sentimental_analysis/realworld/recordedAudio.txt", "w")
        text_file.write(useFile)
        text_file.close()
        response = HttpResponse('Success! This is a 200 response.', content_type='text/plain', status=200)
        return response

analysis_cache = AnalysisCache()
def newsanalysis(request):
    if request.method == 'POST':
        topicname = request.POST.get("topicname", "")
        scrapNews(topicname, 10)

        with open(r'sentimental_analysis/realworld/news.json', 'r') as json_file:
            json_data = json.load(json_file)
        news = []
        for item in json_data:
            news.append(item['Summary'])

        cached_sentiment, cached_text = analysis_cache.get_analysis(topicname, news)

        if cached_sentiment and cached_text:
            print('loaded sentiment')
            return render(request, 'realworld/results.html', {
                'sentiment': cached_sentiment,
                'text': cached_text,
                'reviewsRatio': {},
                'totalReviews': 1,
                'showReviewsRatio': False
            })

        finalText = news
        result = detailed_analysis(news)
        print('cached sentiment')
        analysis_cache.set_analysis(topicname, news, result, finalText)

        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : finalText, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False})

    else:
        return render(request, 'realworld/index.html')

def speech_to_text(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)
        return text


def sentiment_analyzer_scores(sentence):
    analyser = SentimentIntensityAnalyzer()
    score = analyser.polarity_scores(sentence)
    print(score)
    return score


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, 0)
