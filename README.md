# SentiLLyzer

> Next-gen sentiment analyzer, powered by AI that gets you!

[![GitHub Release](https://img.shields.io/github/v/release/csc510-group11/Sentimental-Analyzer-Pro)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/releases)  [![Python](https://img.shields.io/badge/python-latest-brightgreen.svg)](https://www.python.org/)  [![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)  [![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/blob/dev/README.md)  [![GitHub license](https://img.shields.io/github/license/csc510-group11/Sentimental-Analyzer-Pro)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/blob/dev/LICENSE.md)  [![Github Repo size in bytes](https://img.shields.io/github/languages/code-size/csc510-group11/Sentimental-Analyzer-Pro)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro) [![GitHub issues](https://img.shields.io/github/issues/csc510-group11/Sentimental-Analyzer-Pro)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/issues?q=is%3Aopen) [![GitHub closed issues](https://img.shields.io/github/issues-closed/csc510-group11/Sentimental-Analyzer-Pro)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/issues?q=is%3Aissue+is%3Aclosed)  [![Github pull requests](https://img.shields.io/github/issues-pr/csc510-group11/Sentimental-Analyzer-Pro)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/pulls)  [![Github closed pull requests](https://img.shields.io/github/issues-pr-closed/csc510-group11/Sentimental-Analyzer-Pro)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/pulls?q=is%3Apr+is%3Aclosed)  [![github workflow](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/actions/workflows/style_checker.yml/badge.svg)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/actions/workflows/style_checker.yml)  [![github workflow](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/actions/workflows/main.yml/badge.svg)](https://github.com/csc510-group11/Sentimental-Analyzer-Pro/actions/workflows/main.yml)  [![codecov](https://codecov.io/gh/csc510-group11/Sentimental-Analyzer-Pro/graph/badge.svg?token=G314IO3WO7)](https://codecov.io/gh/csc510-group11/Sentimental-Analyzer-Pro) ![GitHub language count](https://img.shields.io/github/languages/count/csc510-group11/Sentimental-Analyzer-Pro) [![DOI](https://zenodo.org/badge/937265974.svg)](https://doi.org/10.5281/zenodo.14938870)

---

Tired of scrolling through endless reviews to figure out if something’s actually good?Whether you're picking a movie, trying a new product, or running your own business— SentiLLyzer has your back. We use cutting-edge LLMs to read the room (or the internet!) across text, audio, video, and images. From product reviews to restaurantrants, we decode the real user sentiment, so you don’t have to. Shoppers get clarity. Businesses get insight. Everyone wins!!!

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation and Setup](#installation-and-setup)
4. [Usage](#usage)
5. [Roadmap and Progress](#roadmap-and-progress)
6. [Team Members](#team-members)
7. [Code of Conduct](#code-of-conduct)
8. [Contribution](#contribution)
9. [License](#license)
10. [Citation](#citation)

---

## Introduction

**SentiLLyzer** is a sentiment analysis platform designed for educational and research purposes as part of a Software Engineering project for CSC 510. Its goal is to provide comprehensive insights by analyzing various data channels—ranging from text, audio, and images to reviews and even video content. With the rapid growth of sentiment analysis research, SentiLLyzer offers a unified solution to capture the emotional tone behind diverse types of user-generated content.

---

## Features

SentiLLyzer can perform sentiment analysis on multiple data types:

| Feature                   | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| **Text Analysis**         | Analyze sentiment from manually entered text.        |
| **Audio Analysis**        | Transcribe and analyze sentiment from audio files.   |
| **Document Analysis**     | Analyze sentiment from uploaded documents (TXT, PDF).|
| **Image Analysis**        | Generate image captions and assess sentiment/emotions.|
| **Video Analysis**        | Transcribe and analyze short video files or YouTube links.|
| **Review Analysis**       | Dedicated review analysis with sub-categories: Product, Movie, Restaurant, Book.|

Additional improvements include:

- **Intelligent Caching:** Reuses processed responses to reduce redundant API calls.
- **Live Data Scraping:** Fetches and analyzes data from various sources to provide real-time insights.
- **Media Previews:** Displays a live preview of the content being analyzed.
- **Content Summary:** Provides a summary of the analyzed content.
- **Modular Design:** Built with Django and Python for easy customization.
- **Docker-Ready:** Containerized deployment ensures seamless portability.
- **CI/CD Pipelines:** Automated builds, tests, and code quality checks for reliable development.

---

## Installation and Setup

Please refer to the [INSTALL.md](INSTALL.md) file for detailed instructions on how to set up SentiLLyzer on your local machine.

---

## Usage

SentiLLyzer supports various analysis modules accessible directly from the homepage. For instance:

- **Text Analysis:** Enter or paste text to get an immediate sentiment report.
- **Document Analysis:** Drag and drop files or select them from your system for analysis. Currently, only TXT and PDF formats are supported. Preview the document before analysis.
- **Audio Analysis:** Drag and drop audio files or select them from your system. The system will transcribe the audio and provide sentiment analysis. You can also record audio directly from your browser. Currently, only MP3 and WAV formats are supported. Preview the audio before analysis.
- **Image Analysis:** Drag and drop image files or select them from your system. The system will generate captions and analyze sentiment/emotions. Currently, only JPG, JPEG, and PNG formats are supported. Preview the image before analysis.
- **Video Analysis:** Drag and drop video files or select them from your system. The system will summarize the video and provide sentiment analysis. You can also enter a YouTube link for analysis. Currently, only MP4 format is supported. Preview the video before analysis.
- **Review Analysis:** Expand the reviews card to access sub-categories (Product, Movie, Restaurant, Book Reviews). Currently, selected platform urls are supported for analysis. For product reviews, you can enter the Etsy product URL. For movie reviews, you can enter the IMDB movie URL. For restaurant reviews, you can enter the Tripadvisor restaurant URL. For book reviews, you can enter the Goodreads book URL. The system will scrape the reviews and provide summary and sentiment analysis. Currently, only English language is supported.

Additionally, the system employs an intelligent caching mechanism to speed up repeated queries.

---

## Roadmap and Progress

### Past Achievements

- Sentiment analysis using spanish_nlp library and spacy.
- Docker-ready deployment.
- Batch analysis for multiple text inputs.
- Implementation of user authentication.

### Current Achievements

- Rich UI improvements for better user interaction.
- Sentiment analysis using Gemini Flash 2.0 LLM.
- Multi-modal analysis (text, document, audio, image, video).
- Review analysis with sub-categories (Product, Movie, Restaurant, Book).
- Intelligent caching for reducing redundant API calls.

### Future Scope

- Multi-language support for sentiment analysis.
- Sentiment trend dashboard for visualizing sentiment over time.
- Offer plug and play modules for easy integration with other applications.

---

## Team Members

- [Md Atiqur Rahman](https://github.com/atiqur-rahman-0041)
- [Nazia Afreen](https://github.com/NaziaAfreen015)
- [Sohom Datta](https://github.com/sohomdatta1)

---

## Code of Conduct

Please adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) in all your interactions with the project.

---

## Contribution

Please refer the [CONTRIBUTING.md](./CONTRIBUTING.md) file for instructions on how to contribute to our repository.

---

## License

This project is licensed under the MIT License - see the [LICENSE.md](./LICENSE.md) file for details.

---

## Citation

Please refer to the [CITATION.md](./CITATION.cff) file for citation details.
