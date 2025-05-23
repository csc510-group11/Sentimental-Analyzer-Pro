from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .scrapers.scraper import scrape_reviews
from .utils import *
from .decorators import cache_response
import pypdf
import base64
from dotenv import load_dotenv


load_dotenv()

@login_required
def index(request):
    return render(request, 'realworld/index.html')

@login_required
@cache_response
def document_analysis(request):
    if request.method == 'POST':
        document_text = None  # This will hold the text from the document

        # Check if a file was uploaded using the field named 'document'
        uploaded_file = request.FILES.get('document')
        if uploaded_file:
            # Enforce 5MB file size limit (5MB = 5 * 1024 * 1024 = 5242880 bytes)
            if uploaded_file.size > 5242880:
                return HttpResponse("File size exceeds 5MB limit.", status=400)


            # Determine the file type based on the file extension
            file_ext = uploaded_file.name.split('.')[-1].lower()
            if file_ext == 'txt':
                try:
                    document_text = uploaded_file.read().decode('utf-8')
                except UnicodeDecodeError:
                    return HttpResponse("Error decoding text file.", status=400)
            elif file_ext == 'pdf':
                try:
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    document_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            document_text += text
                except Exception as e:
                    return HttpResponse("Error processing PDF file: " + str(e), status=406)
            else:
                return HttpResponse("Unsupported file type. Please upload a TXT or PDF file.", status=400)
        else:
            return HttpResponse("No file uploaded.", status=400)

        if document_text:
            try:
                summary = gemini_summarize(document_text)
                result = gemini_sentiment_analysis(document_text)
            except Exception as e:
                return HttpResponse("Error during analysis: " + str(e), status=500)

            return render(request, 'realworld/results.html', {'sentiment': result, 'summary' : summary})
        else:
            return HttpResponse("No document content found.", status=401)
    
    else:
        # For GET requests, simply render the document analysis template
        return render(request, 'realworld/document_analysis.html')

@login_required
@cache_response
def text_analysis(request):
    """Performs sentiment analysis for the single line text"""
    if request.method == 'POST':
        text_data = request.POST.get("text", "")

        result = gemini_sentiment_analysis(text_data)

        return render(request, 'realworld/results.html', {'sentiment': result, 'text' : text_data, 'reviewsRatio': {}, 'totalReviews': 1, 'showReviewsRatio': False,})
    else:
        return render(request, 'realworld/text_analysis.html')

@login_required
@cache_response
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
            caption = gemini_caption_image(encoded_image)
        except Exception as e:
            return HttpResponse("Error generating caption: " + str(e), status=500)
        
        # Render the result page with the generated caption.
        if caption.strip() == "":
            return HttpResponse("No caption generated.", status=500)
        
        result = gemini_sentiment_analysis(caption)
        
        return render(request, 'realworld/results.html', {
            'caption': caption,
            'sentiment': result,
            'encoded_image': "data:image/jpeg;base64," + encoded_image
        })
    
    # For GET requests, simply render the image analysis upload form.
    else:
        return render(request, 'realworld/image_analysis.html')

@login_required
@cache_response
def audio_analysis(request):
    if request.method == 'POST':
        transcribed_text = gemini_transcribe_audio(request.FILES.get('audio').read())
        result = gemini_sentiment_analysis(transcribed_text)
        return render(request, 'realworld/results.html', {'sentiment': result, 'summary' : transcribed_text})
    else:
        return render(request, 'realworld/audio_analysis.html')  
    
@login_required
@cache_response
def video_analysis(request):
    if request.method == 'POST':
        video_url = None
        video_bytes = request.FILES.get('video_bytes')
        if not video_bytes:
            video_url = request.POST.get("youtube_link", "")
            if not video_url:
                return HttpResponse("No video file or URL provided.", status=400)

        video_summary = gemini_video_analysis(video_bytes, video_url)
        if not video_summary:
            return HttpResponse("No summary found.", status=400)
        result = gemini_sentiment_analysis(video_summary)
        return render(request, 'realworld/results.html', {'sentiment': result, 'summary' : video_summary})
    else:
        return render(request, 'realworld/video_analysis.html')

@login_required
@cache_response
def book_review(request):
    if request.method == 'POST':
        book_url = request.POST.get("review_url", "")

        book_review_text = scrape_reviews(book_url, category="book")
        book_review_text = scrape_reviews(book_url, category="book")
        if not book_review_text:
            return HttpResponse("No reviews found.", status=400)
        
        review_summary = gemini_summarize(book_review_text)
        result = gemini_sentiment_analysis(book_review_text)
        return render(request, 'realworld/results.html', {'sentiment': result, 'summary' : review_summary})
    else:
        return render(request, 'realworld/book_review.html')
    
@login_required
@cache_response
def movie_review(request):
    if request.method == 'POST':
        movie_url = request.POST.get("review_url", "")

        movie_review_text = scrape_reviews(movie_url, category="movie")
        if not movie_review_text:
            return HttpResponse("No reviews found.", status=400)
        
        review_summary = gemini_summarize(movie_review_text)
        result = gemini_sentiment_analysis(movie_review_text)
        return render(request, 'realworld/results.html', {'sentiment': result, 'summary' : review_summary})
    else:
        return render(request, 'realworld/movie_review.html')
    
@login_required
@cache_response
def product_review(request):
    if request.method == 'POST':
        product_url = request.POST.get("review_url", "")

        product_review_text = scrape_reviews(product_url, category="product")
        product_review_text = scrape_reviews(product_url, category="product")
        if not product_review_text:
            return HttpResponse("No reviews found.", status=400)
        
        review_summary = gemini_summarize(product_review_text)
        result = gemini_sentiment_analysis(product_review_text)
        return render(request, 'realworld/results.html', {'sentiment': result, 'summary' : review_summary})
    else:
        return render(request, 'realworld/product_review.html')
    
@login_required
@cache_response
def restaurant_review(request):
    if request.method == 'POST':
        restaurant_url = request.POST.get("review_url", "")

        restaurant_review_text = scrape_reviews(restaurant_url, category="restaurant")
        logging.info(f"Restaurant review text: {restaurant_review_text}")
        if not restaurant_review_text:
            return HttpResponse("No reviews found.", status=400)
        
        review_summary = gemini_summarize(restaurant_review_text)
        result = gemini_sentiment_analysis(restaurant_review_text)
        return render(request, 'realworld/results.html', {'sentiment': result, 'summary' : review_summary})
    else:
        return render(request, 'realworld/restaurant_review.html')
    