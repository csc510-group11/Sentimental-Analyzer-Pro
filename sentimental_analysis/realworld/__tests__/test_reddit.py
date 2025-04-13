import pytest
from unittest.mock import patch, MagicMock
from sentimental_analysis.realworld.scrapers.reddit_scrap import *
from realworld.views import *

@pytest.fixture
def mock_reddit_post():
    return {
        "title": "Sample Reddit Post Title",
        "body": "Sample body of the Reddit post.",
        "comments": [
            "Great post!", "I disagree with this.", "Neutral comment here.",
            "Amazing!", "Terrible post.", "What is this?",
            "Could have been better.", "Very informative!", "I love this!", "Not helpful."
        ]
    }

@pytest.fixture
def sentiment_data():
    return [
        "This is a great day!", "I hate everything.", "This is okay.",
        "Wonderful!", "Awful experience.", "It's alright.",
        "Absolutely love it!", "Terrible decision.", "Not bad.", "Could be better."
    ]

# Test fetch_reddit_post
@patch('realworld.reddit_scrap.praw.Reddit')
def test_fetch_reddit_post(mock_reddit, mock_reddit_post):
    mock_submission = MagicMock()
    mock_submission.title = mock_reddit_post["title"]
    mock_submission.selftext = mock_reddit_post["body"]
    mock_submission.comments.list.return_value = [MagicMock(body=comment) for comment in mock_reddit_post["comments"]]
    mock_reddit.return_value.submission.return_value = mock_submission

    result = fetch_reddit_post("https://www.reddit.com/r/test/comments/test_id")
    assert result == mock_reddit_post

# Test reddit_sentiment_score
def test_sentiment_all_positive():
    data = ["Great!", "Awesome!", "Wonderful!"]
    result = reddit_sentiment_score(data)
    assert result["pos"] == 100
    assert result["neg"] == 0
    assert result["neu"] == 0

def test_sentiment_all_negative():
    data = ["Terrible!", "Awful!", "Horrible!"]
    result = reddit_sentiment_score(data)
    assert result["pos"] == 0
    assert result["neg"] == 100
    assert result["neu"] == 0

def test_sentiment_empty():
    result = reddit_sentiment_score([])
    assert result["pos"] == 0
    assert result["neg"] == 0
    assert result["neu"] == 0

# Test edge cases
def test_sentiment_score_special_characters():
    data = ["!!!", "@@@", "###"]
    result = reddit_sentiment_score(data)
    assert result["pos"] == 0
    assert result["neg"] == 0
    assert result["neu"] == 100

def test_sentiment_score_mixed_language():
    data = ["Good job!", "Terrible!", "Muy bien!"]
    result = reddit_sentiment_score(data)
    assert result["pos"] > 0
    assert result["neg"] > 0

def test_sentiment_score_long_text():
    data = ["This is a very long text with neutral sentiments. " * 50]
    result = reddit_sentiment_score(data)
    assert result["neu"] == 100

# Test invalid inputs
def test_sentiment_score_non_string_input():
    data = [123, None, False]
    result = reddit_sentiment_score([str(item) for item in data])
    assert result["neu"] == 100

@patch('realworld.reddit_scrap.praw.Reddit')
def test_fetch_reddit_post_api_failure(mock_reddit):
    mock_reddit.return_value.submission.side_effect = Exception("API failure")
    with pytest.raises(Exception, match="API failure"):
        fetch_reddit_post("https://www.reddit.com/r/test/comments/test_id")

@patch('realworld.reddit_scrap.praw.Reddit')
def test_fetch_reddit_post_no_comments(mock_reddit):
    mock_submission = MagicMock()
    mock_submission.title = "Sample Title"
    mock_submission.selftext = "Sample Body"
    mock_submission.comments.list.return_value = []
    mock_reddit.return_value.submission.return_value = mock_submission

    result = fetch_reddit_post("https://www.reddit.com/r/test/comments/test_id")
    assert result["comments"] == []

def test_sentiment_score_empty_string():
    data = [""]
    result = reddit_sentiment_score(data)
    assert result["neu"] == 100

def test_sentiment_score_unicode_characters():
    data = ["😊", "😡", "😐"]
    result = reddit_sentiment_score(data)
    assert result["neu"] == 100
