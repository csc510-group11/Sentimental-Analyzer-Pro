# Use the official lightweight Python 3.10 image
FROM python:latest

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl unzip wget gnupg2 \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chromium
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/bin/chromedriver

# ENV CHROME_DRIVER_VERSION=134.0.0.0 

# # # Install Chrome 114 manually
# # RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb && \
# #     apt install -y ./google-chrome-stable_114.0.5735.90-1_amd64.deb && \
# #     rm google-chrome-stable_114.0.5735.90-1_amd64.deb

# # # Install the latest ChromeDriver compatible with the installed Chrome version
# # RUN wget -q https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip && \
# #     unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
# #     rm chromedriver_linux64.zip

# # # Set ChromeDriver path
# # ENV PATH="/usr/local/bin:$PATH"


# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose port 8000 for the Django development server
EXPOSE 8000

# Run Django migrations and then start the Django development server.
# Note: Adjust the manage.py path if necessary.
CMD ["bash", "-c", "python sentimental_analysis/manage.py makemigrations && python sentimental_analysis/manage.py migrate && python sentimental_analysis/manage.py runserver 0.0.0.0:8000"]
