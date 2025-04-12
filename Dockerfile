# Use the official lightweight Python 3.10 image
FROM python:3.10-slim

# Install system dependencies including ffmpeg and build tools (g++ is part of build-essential)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Download necessary NLTK data packages
RUN python -c "import nltk; [nltk.download(pkg) for pkg in ['punkt','stopwords','averaged_perceptron_tagger']]"

# Expose port 8000 for the Django development server
EXPOSE 8000

# Run Django migrations and then start the Django development server.
# Note: Adjust the manage.py path if necessary.
CMD ["bash", "-c", "python sentimental_analysis/manage.py makemigrations && python sentimental_analysis/manage.py migrate && python sentimental_analysis/manage.py runserver 0.0.0.0:8000"]
