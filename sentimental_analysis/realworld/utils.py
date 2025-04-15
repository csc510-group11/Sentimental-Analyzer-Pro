from google import genai
from realworld.models import SentimentScore
from dotenv import load_dotenv
from google.genai import types

import assemblyai as aai
import tempfile
import os
import json
import logging
import requests

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