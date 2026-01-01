"""
SCRYFALL REQUESTS
"""

import json
import os
from typing import Callable, Optional, Any
from src import settings as cfg
import requests
from backoff import on_exception, expo
from PIL import Image
from ratelimit import RateLimitDecorator, sleep_and_retry
from requests import RequestException, Timeout

# RateLimiter objects with calls per period (seconds)
scryfall_rate_limit = RateLimitDecorator(calls=20, period=2.0)
mtgp_rate_limit = RateLimitDecorator(calls=10, period=2.0)

# Default timeout for all network requests (in seconds)
TIMEOUT = 10

"""
DECORATORS
"""


def handle_final_exception(fail_response: Optional[Any]) -> Callable:
    """
    Decorator to handle any exception and return appropriate failure value.
    @param fail_response: Return value if Exception occurs.
    @return: Return value of the function, or fail_response.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Final exception catch
            try:
                return func(*args, **kwargs)
            except (RequestException, json.JSONDecodeError):
                # All requests failed
                return fail_response

        return wrapper

    return decorator


def handle_scryfall_request(fail_response: Optional[Any] = None) -> Callable:
    """
    Decorator to handle all Scryfall request failure cases, and return appropriate failure value.
    @param fail_response: The value to return if request failed entirely.
    @return: Requested data if successful, fail_response if not.
    """

    def decorator(func):
        @sleep_and_retry
        @scryfall_rate_limit
        @on_exception(expo, RequestException, max_tries=3, max_time=10)
        @handle_final_exception(fail_response)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def handle_mtgp_request(fail_response: Optional[Any] = None) -> Callable:
    """
    Decorator to handle all Scryfall request failure cases, and return appropriate failure value.
    @param fail_response: The value to return if request failed entirely.
    @return: Requested data if successful, fail_response if not.
    """

    def decorator(func):
        @sleep_and_retry
        @mtgp_rate_limit
        @on_exception(expo, RequestException, max_tries=3, max_time=10)
        @handle_final_exception(fail_response)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


"""
SCRYFALL REQUESTS
"""


@handle_scryfall_request({})
def get_data_url(url: str, params: Optional[dict[str, str]] = None) -> dict:
    """
    Get JSON data from any valid API URL.
    @param url: Valid API URL, such as Scryfall.
    @param params: Params to pass to an API endpoint.
    @return: JSON data returned.
    """
    with requests.get(url, params=(params or {}), timeout=TIMEOUT) as response:
        if response.status_code == 200:
            return response.json() or {}
        return {}


@handle_scryfall_request({})
def get_scryfall_set(code: str) -> dict:
    """
    Lookup Set data on Scryfall using /sets/code API.
    @note: https://scryfall.com/docs/api/sets/code
    @param code: MTG set code, ex: MH2
    @return: Set data as dict.
    """
    with requests.get(
        f"https://api.scryfall.com/sets/{code}", timeout=TIMEOUT
    ) as response:
        if response.status_code == 200:
            data = response.json() or {}
            return data if data.get("object") == "set" else {}
        return {}


@handle_scryfall_request({})
def get_scryfall_card_named(name: str, code: str) -> dict:
    """
    Lookup Card data on Scryfall using /cards/named API.
    @note: https://scryfall.com/docs/api/cards/named
    @param name: Name of the card.
    @param code: Set code of the card.
    @return: Card data as dict.
    """
    with requests.get(
        f"https://api.scryfall.com/cards/named",
        params={"fuzzy": name, "set": code},
        timeout=TIMEOUT,
    ) as response:
        if response.status_code == 200:
            data = response.json() or {}
            return data if data.get("object", "error") != "error" else {}
        return {}


@handle_scryfall_request({})
def get_scryfall_card_numbered(code: str, number: str) -> dict:
    """
    Lookup Card data on Scryfall using /cards/code/number API.
    @note: https://scryfall.com/docs/api/cards/collector
    @param code: Set code of the card.
    @param number: Collector number of the card.
    @return: Card data as dict.
    """
    with requests.get(
        f"https://api.scryfall.com/cards/{code}/{number}", timeout=TIMEOUT
    ) as response:
        if response.status_code == 200:
            data = response.json() or {}
            return data if data.get("object", "error") != "error" else {}
        return {}


@handle_scryfall_request(False)
def get_scryfall_image(url: str, path: str):
    """
    Download an image file from Scryfall.
    @param url: Url to the image.
    @param path: Path to save the image.
    @return: True if successful, False if failed.
    """
    with requests.get(url, timeout=TIMEOUT) as response:
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            return True
        return False


"""
MTGP REQUESTS
"""


@handle_mtgp_request(False)
def get_mtgp_image(url: str, path: str):
    """
    Download an image file from MTG Pics.
    @param url: Url to the image.
    @param path: Path to save the image.
    @return: True if successful, False if failed.
    """
    with requests.get(url, timeout=TIMEOUT) as response:
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)

            # Import only locally to avoid circular dependencies
            from src.core import log_debug, log_size_warning

            # Check file size in kilobytes
            file_size_kb = int(round(os.path.getsize(path) / 1024, 0))

            # Check image dimensions
            try:
                with Image.open(path) as img:
                    width, height = img.size
                    if (
                        width < cfg.card_width_warning_limit
                        or height < cfg.card_height_warning_limit
                    ):
                        # Python ternary: value_if_true if condition else value_if_false
                        log_size_warning(
                            os.path.basename(path),
                            file_size_kb,
                            width,
                            height,
                            action="MTGP",
                        )
            except Exception as e:
                log_debug(
                    f"Image saved: {os.path.basename(path)} | "
                    f"Dimensions: Error reading image ({e})"
                )

            return True
        return False


@handle_mtgp_request(None)
def get_mtgp_page(url: str) -> Optional[bytes]:
    with requests.get(url, timeout=TIMEOUT) as response:
        if response.status_code == 200:
            if "Wrong ref or number." not in response.text:
                if "No card found." not in response.text:
                    return response.content
        return None


"""
UTILITY FUNCTIONS
"""


def get_cards_paged(
    url: str,
    params: Optional[dict[str, str]] = None,
    keys: Optional[list[str]] = None,
    has_more: str = "has_more",
    next_page: str = "next_page",
) -> list[dict]:
    """
    Grab paginated card list from JSON API such as Scryfall.
    @param url: Either the API endpoint or full URL.
    @param params: Optional parameters to pass to API endpoint.
    @param keys: Sequence of keys to find card list in data.
    @param has_more: The key to check for additional pages.
    @param next_page: The key that links the next page of results.
    """
    # If keys not provided, use 'data'
    if not keys:
        keys = ["data"]

    # Create initial list from first request
    res = get_data_url(url, params=params) or {}
    cards = res.copy()
    for k in keys:
        cards = cards.get(k, {})
    if not isinstance(cards, list):
        return []

    # Add additional pages if any exist
    while res.get(has_more) and res.get(next_page):
        res = get_data_url(res[next_page]) or {}
        page = res.copy()
        for k in keys:
            page = page.get(k, {})
        if not isinstance(page, list):
            page = []
        cards.extend(page)
    return cards


def get_scryfall_card_search(params: dict) -> list[dict]:
    """
    Lookup Card data on Scryfall using /cards/search API.
    @note: https://scryfall.com/docs/api/cards/search
    @param params: Search parameters to find the card.
    @return: Card data as dict.
    """
    data = get_cards_paged("https://api.scryfall.com/cards/search", params=params)
    return data or []
