from google import genai
from .schemas import SentimentScore
from dotenv import load_dotenv
from google.genai import types

import os
import json
import logging
import hashlib


load_dotenv()

def gemini_summarize(text):
    """
    Calls the Gemini API to summarize the provided text.
    
    Args:
        text (str): The input text to summarize.
        model (str): The Gemini model to use. Default is "gemini-2.0-flash".
        
    Returns:
        str: The summarized text.
    """
    # Construct a prompt specifically designed for summarization
    prompt = (
        "Summarize the following text in a concise manner:\n\n"
        f"{text}"
    )

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Call the Gemini API using the client
    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL_NAME"),
            contents=prompt,
            config={
                'response_mime_type': 'text/plain',
            },
        )
        
        # Assume the response.text is the summary
        result = response.text.strip()
        
    except Exception as e:
        logging.error("Error during Gemini API call: %s", e)
        # Optionally, define a fallback summary or raise an error
        result = "Error generating summary."
    
    return result

def gemini_sentiment_analysis(text):
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
            model=os.getenv("GEMINI_MODEL_NAME"),
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

def gemini_caption_image(encoded_image):
    """
    Calls the Gemini API to generate a caption for the provided image.
    
    Args:
        encoded_image (str): The base64 encoded image data.
        model (str): The Gemini model to use. Default is "gemini-2.0-flash".
        
    Returns:
        str: The generated caption.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL_NAME"),
        contents=["What is this image?",
                types.Part.from_bytes(data=encoded_image, mime_type="image/jpeg")])

    logging.info("Gemini caption response: %s", response.text)
    # Assuming the response.text is the caption
    caption = response.text.strip()
    return caption

def gemini_transcribe_audio(audio_data):
    """
    Calls the Gemini API to transcribe the provided audio.
    
    Args:
        audio_data (bytes): The binary data of the audio file.
        model (str): The Gemini model to use. Default is "gemini-2.0-flash".
        
    Returns:
        str: The transcribed text.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL_NAME"),
        contents=[
            'Describe this audio clip',
            types.Part.from_bytes(
            data=audio_data,
            mime_type='audio/mp3',
            )
        ]
    )

    return response.text.strip()

def gemini_video_analysis(video_bytes, video_url):
    """
    Calls the Gemini API to analyze the provided video.
    
    Args:
        video_data (bytes): The binary data of the video.
        video_url (str): The URL of the video.
        model (str): The Gemini model to use. Default is "gemini-2.0-flash".
        
    Returns:
        str: The analysis result.
    """
    # Construct a prompt specifically designed for video analysis
    prompt = "Can you summarize this video?"


    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    if video_url:
        contents=types.Content(
            parts=[
                types.Part(text=prompt),
                types.Part(
                    file_data=types.FileData(file_uri=video_url)
                )
            ]
        )
    elif video_bytes:
        contents = types.Content(
            parts=[
            types.Part(text=prompt),
            types.Part(
                inline_data=types.Blob(data=video_bytes.read(), mime_type='video/mp4')
            )
            ]
        )
    else:
        raise ValueError("Either video_bytes or video_url must be provided.")
    
    # Call the Gemini API using the client
    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL_NAME"),
            contents=contents,
        )

        result = response.text.strip()
        
    except Exception as e:
        logging.error("Error during Gemini API call: %s", e)
        # Optionally, define a fallback analysis result or raise an error
        result = "Error generating video analysis."
    
    return result

def get_request_hash(request):
    # Build a basic representation of the request.
    data = {
        'method': request.method,
        'path': request.path,
        'GET': request.GET.dict(),
        'POST': request.POST.dict(),
    }
    # If there are any uploaded files, include their details.
    if request.FILES:
        files_data = {}
        for key, file_obj in request.FILES.items():
            # Reset the file pointer, then read content.
            file_obj.seek(0)
            content = file_obj.read()
            # Calculate a hash of the file content.
            content_hash = hashlib.sha256(content).hexdigest()
            files_data[key] = {
                'name': file_obj.name,
                'size': file_obj.size,
                'content_hash': content_hash,
            }
            # Reset file pointer for further processing later in the view.
            file_obj.seek(0)
        data['FILES'] = files_data
    # Convert the data to a JSON string with sorted keys, and then compute a hash.
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
