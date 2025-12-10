import requests
from .base import BaseScraper


class RequestsScraper(BaseScraper):
    """
        Scraper implementation using the `requests` library.

        This class extends BaseScraper and provides an implementation of `_fetch_html()`
        using a persistent `requests.Session` for connection reuse and cookie management.

        Notes:
            - If `base_url` is provided in the parent class, relative URLs will be
              automatically prefixed.
            - All retry, delay, and statistics logic is handled by BaseScraper.

        Attributes:
            session (requests.Session): Persistent HTTP session for efficient requests.
    """

    def __init__(self, *args, **kwargs):
        """
            Initialize a RequestsScraper object.
            Args:
                *args, **kwargs: Passed directly to BaseScraper.__init__
        """
        super().__init__(*args, **kwargs)
        self.session = requests.Session()

    def _fetch(self, url, **kwargs):
        """
            Execute an HTTP GET request using the `requests` library, and returns the HTML content.
                Args:
                url (str): The URL to fetch. Can be relative or absolute.
                **kwargs: Passed directly to `requests.Session.get`

            Returns:
                requests.Response: The HTTP response object.

            Raises:
                requests.RequestException: If the request fails.
        """
        # Prefix base url if necessary
        if self.base_url and not url.startswith("http"):
            url = self.base_url.rstrip("/") + "/" + url.lstrip("/")
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response