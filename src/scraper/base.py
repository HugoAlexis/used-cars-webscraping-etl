import time
import random
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """
       Base class for web scrapers.

       This class manages:
       - Request pacing (delays between requests)
       - Retry logic with backoff
       - Basic request statistics
       - URL prefixing via `base_url`

       Subclasses must implement `_fetch_html()` to perform the actual HTTP request
       using any backend (e.g., `requests`, `httpx`, `playwright`, etc.).

       Attributes:
           base_url (str | None): Optional base URL prefixed to all fetch calls.
           delay_range (tuple): Minimum and maximum delay (in seconds) between requests.
           max_retries (int): Maximum number of retries when a request fails.
           retry_backoff (float): Multiplier applied to the retry delay after each failure.
           requests_total (int): Number of requests attempted.
           requests_failed (int): Number of failed requests after all retries.
           requests_success (int): Number of successful requests.
           last_request (float): Timestamp of the previous request.
       """

    def __init__(self, base_url=None, delay_range=(1, 3), max_retries=3, retry_backoff=1.5):
        """
        Initialize a BaseScraper instance.

        Args:
            base_url (str | None): Optional URL prefix for all requests.
            delay_range (tuple[int, int]): (min_delay, max_delay) between requests.
            max_retries (int): Number of retry attempts before marking failure.
            retry_backoff (float): Retry delay multiplier for exponential backoff.
        """
        self.base_url = base_url
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        # Statistics
        self.requests_total = 0
        self.requests_failed = 0
        self.requests_success = 0

        # Request timing
        self.last_request = time.time()

    def _delay(self):
        """
        Sleep to ensure at least `delay_range[0]` seconds have passed
        since the last request, and optionally add random delay up to
        `delay_range[1]`.

        Ensures:
            - No negative delay values are sent to `random.uniform()`.
            - If enough time has passed, no delay is added.
        """
        time_elapsed = time.time() - self.last_request
        if time_elapsed < self.delay_range[0]:
            delay_range = (
                self.delay_range[0] - time_elapsed,
                self.delay_range[1] - time_elapsed
            )
            random_delay = random.uniform(*delay_range)
            time.sleep(random_delay)


    @abstractmethod
    def _fetch(self, url, **kwargs):
        """
        Perform the actual HTTP request.

        Subclasses must implement this method.

        Args:
            url (str): Absolute or relative URL.
            **kwargs: Additional backend-specific parameters.

        Returns:
            Any: The raw response object (HTML string, Response object, etc.).
        """

    def fetch(self, url, **kwargs):
        """
        Fetch HTML content with retry logic, delay enforcement,
        statistics tracking, and optional base_url prefixing.

        Args:
            url (str): Target URL (absolute or relative).
            **kwargs: Passed directly to `_fetch_html()`.

        Returns:
            Any: Response returned by `_fetch_html()`.

        Raises:
            RuntimeError: If all retries fail.
        """
        self._delay()
        self.last_request = time.time()
        self.requests_total += 1

        retries_left = self.max_retries
        delay_backoff = 1

        while retries_left >= 0:
            try:
                response = self._fetch(url, **kwargs)
                self.requests_success += 1
                return response
            except Exception as e:
                if retries_left == 0:
                    self.requests_failed += 1
                    raise RuntimeError(
                        f"Requests permanently failed for {url}: {e}"
                    )
                time.sleep(delay_backoff)
                delay_backoff *= self.retry_backoff
                retries_left -= 1