import os
import json
from google import genai
from django.shortcuts import render
from django.http import HttpResponse
from realworld.scrapers.newsScraper import *
from realworld.scrapers.reddit_scrap import *
from realworld.models import SentimentScore
from django.contrib.auth.decorators import login_required
import PyPDF2
import base64
import assemblyai as aai
import tempfile
from dotenv import load_dotenv

load_dotenv()

@login_required
def index(request):
    note = "Welcome to the Sentiment Analysis App! Please select an analysis option from the menu."
    return render(request, 'realworld/index.html', {'note': note})

def social_media_analysis(request):
    note = "This is a Social Media Analysis App that uses various models to analyze the sentiment of text, audio, and social media data."
    return render(request, 'realworld/index.html', {'note': note})

def document_analysis(request):
    if request.method == 'POST':
        document_text = None  # This will hold the text from the document

        # Check if a file was uploaded using the field named 'document'
        uploaded_file = request.FILES.get('document')
        if uploaded_file:
            # Enforce 5KB file size limit (5KB = 5120 bytes)
            if uploaded_file.size > 5120:
                return HttpResponse("File size exceeds 5KB limit.", status=400)

            # Determine the file type based on the file extension
            file_ext = uploaded_file.name.split('.')[-1].lower()
            if file_ext == 'txt':
                try:
                    document_text = uploaded_file.read().decode('utf-8')
                except UnicodeDecodeError:
                    return HttpResponse("Error decoding text file.", status=400)
            elif file_ext == 'pdf':
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    document_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            document_text += text
                except Exception as e:
                    return HttpResponse("Error processing PDF file: " + str(e), status=400)
            else:
                return HttpResponse("Unsupported file type. Please upload a TXT or PDF file.", status=400)
        else:
            return HttpResponse("No file uploaded.", status=400)

        if document_text:
            result = gemini_sentiment_analysis(document_text)

            return render(request, 'realworld/results.html', {'sentiment': result, 'text' : document_text, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False,})
        else:
            return HttpResponse("No document content found.", status=400)
    
    else:
        # For GET requests, simply render the document analysis template
        return render(request, 'realworld/document_analysis.html')

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
        text_data = request.POST.get("text", "")

        result = gemini_sentiment_analysis(text_data)

        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : text_data, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False,})
    else:
        note = "Enter the Text to be analysed!"
        return render(request, 'realworld/textanalysis.html', {'note': note})

def generate_emotion_caption(encoded_image):
    # Optional: Customize prompt to ask for emotions
    prompt_instruction = "Describe the scene in the image and include details about any emotions shown."

    headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}
    api_url = os.getenv("HF_IMAGE_CAPTION_API_URL")
    payload = {
        "inputs": encoded_image,
        "options": {"prompt": prompt_instruction}
    }

    response = requests.post(api_url, headers=headers, json=payload)
    results = response.json()

    # Depending on the API response, you might need to adjust how you extract the caption.
    caption = results[0].get("generated_text", "")
    return caption

def image_analysis(request):
    if request.method == "POST":
        # Retrieve the uploaded image from the request
        uploaded_image = request.FILES.get("image")
        if not uploaded_image:
            return HttpResponse("No image file provided.", status=400)
        
        try:
            # Read the image and encode it in Base64
            image_bytes = uploaded_image.read()
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            
            # Pass the Base64 string to the caption generation function.
            # The function should be designed to accept the Base64 data.
            caption = generate_emotion_caption(encoded_image)
        except Exception as e:
            return HttpResponse("Error generating caption: " + str(e), status=500)
        
        # Render the result page with the generated caption.
        if caption.strip() == "":
            return HttpResponse("No caption generated.", status=500)
        
        result = gemini_sentiment_analysis(caption)
        
        return render(request, 'realworld/resultsimage.html', {
            'caption': caption,
            'sentiment': result,
            'encoded_image': "data:image/jpeg;base64," + encoded_image
        })
    
    # For GET requests, simply render the image analysis upload form.
    else:
        return render(request, 'realworld/image_analysis.html')

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

def transcribe_audio(audio_data):
    # Set your AssemblyAI API key.
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    transcriber = aai.Transcriber()

    # Write binary audio data to a temporary file (with .wav extension).
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_data)
        temp_file_path = temp_file.name

    try:
        # Transcribe the audio using the temporary file path.
        transcript = transcriber.transcribe(temp_file_path)
        transcript_text = transcript.text
    except Exception as e:
        # Ensure cleanup in case of an error.
        os.remove(temp_file_path)
        raise e

    # Clean up the temporary file.
    os.remove(temp_file_path)

    return transcript_text

def audio_analysis(request):
    if request.method == 'POST':
        transcribed_text = transcribe_audio(request.FILES.get('audio').read())
        result = gemini_sentiment_analysis(transcribed_text)
        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : transcribed_text, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False})
    else:
        note = "Please Enter the Audio file you want to analyze"
        return render(request, 'realworld/audio_analysis.html', {'note': note})

def newsanalysis(request):
    if request.method == 'POST':
        pass
    else:
        return render(request, 'realworld/index.html')
    