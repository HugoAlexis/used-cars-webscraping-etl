import time
import pytest
import requests
from unittest.mock import patch

from src.scraper.requests_scraper import RequestsScraper


# --------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------

@pytest.fixture
def scraper():
    """Basic scraper fixture"""
    return RequestsScraper(base_url="https://example.com", delay_range=(0, .5))

@pytest.fixture
def requests_mock_success(requests_mock):
    """Mock GET returning 200 OK."""
    requests_mock.get("https://example.com/test", text="ok")
    return requests_mock



# --------------------------------------------------------------------
# Base functionality
# --------------------------------------------------------------------
def test_initialization(scraper):
    assert scraper.base_url == "https://example.com"
    assert scraper.delay_range == (0, 0.5)
    assert scraper.requests_total == 0
    assert scraper.requests_failed == 0
    assert scraper.requests_success == 0


def test_fetch_success(scraper, requests_mock_success):
    response = scraper.fetch("/test")

    assert response.text == "ok"
    assert scraper.requests_total == 1
    assert scraper.requests_failed == 0
    assert scraper.requests_success == 1


def test_url_prefixing(scraper, requests_mock):
    requests_mock.get("https://example.com/path", text="prefixed")

    response = scraper.fetch("path")
    assert response.text == "prefixed"


# --------------------------------------------------------------------
# Retry logic
# --------------------------------------------------------------------

def test_retry_and_success(scraper, requests_mock):
    """
    First request fails, second succeeds.
    """
    requests_mock.get(
        "https://example.com/retry",
        [
            {'status_code': 500},     # fail 1
            {'text': 'ok'}            # success
        ]
    )

    scraper.max_retries = 2
    scraper.retry_backoff = 0  # avoid waiting in tests

    response = scraper.fetch("/retry")

    assert response.text == "ok"
    assert scraper.requests_total == 1
    assert scraper.requests_success == 1
    assert scraper.requests_failed == 0


def test_retry_failure(scraper, requests_mock):
    """
    All requests fail → raise RuntimeError
    """
    requests_mock.get(
        "https://example.com/fail",
        [{'status_code': 500}] * 3
    )

    scraper.max_retries = 2
    scraper.retry_backoff = 0

    with pytest.raises(RuntimeError):
        scraper.fetch("/fail")

    assert scraper.requests_total == 1
    assert scraper.requests_success == 0
    assert scraper.requests_failed == 1


# --------------------------------------------------------------------
# Delay system
# --------------------------------------------------------------------


def test_delay_called(scraper, requests_mock_success):
    """
    Ensures that the delay method is executed.
    """
    scraper.delay_range = (0.1, 0.3)

    with patch("time.sleep") as sleep_mock:
        scraper.fetch("/test")
        sleep_mock.assert_called_once()



def test_delay_called(scraper, requests_mock_success):
    """
    Ensures that the delay method is executed.
    """
    scraper.delay_range = (0.1, 0.3)

    with patch("time.sleep") as sleep_mock:
        scraper.fetch("/test")
        sleep_mock.assert_called_once()


# --------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------

def test_response_raises_for_status(scraper, requests_mock):
    """
    If response.raise_for_status() fails, it propagates to retry logic.
    """
    requests_mock.get("https://example.com/error", status_code=404)

    scraper.max_retries = 0

    with pytest.raises(RuntimeError):
        scraper.fetch("/error")



# --------------------------------------------------------------------
# _fetch_html behavior
# --------------------------------------------------------------------

def test_fetch_html_returns_response_object(scraper, requests_mock_success):
    response = scraper.fetch("/test")
    assert isinstance(response, requests.Response)