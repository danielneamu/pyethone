"""
HTTP Client with retry logic and anti-blocking measures
For FBRef scraping with proper session management
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

MAX_RETRIES = 5
REQUEST_TIMEOUT = 30


def get_session_with_retries():
    """Create a requests session with retry strategy"""
    session = requests.Session()

    retry_strategy = Retry(
        total=MAX_RETRIES,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        backoff_factor=2
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def get_headers():
    """Get proper browser headers to avoid 403"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://fbref.com/',
        'DNT': '1',
        'Cache-Control': 'max-age=0'
    }


def make_request_with_retry(url, max_retries=MAX_RETRIES):
    """Make HTTP request with session, retry strategy, and proper headers"""

    session = get_session_with_retries()
    headers = get_headers()

    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=headers,
                                   timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if status_code == 429:
                wait_time = (2 ** attempt) * 60
                print(
                    f"    ⚠️  Rate limited (429). Waiting {wait_time}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)

            elif status_code == 403:
                wait_time = (2 ** attempt) * 60
                print(
                    f"    ⚠️  Forbidden (403). Waiting {wait_time}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)

            elif status_code in [500, 502, 503, 504]:
                wait_time = 10 + (attempt * 5)
                print(
                    f"    ⚠️  Server error ({status_code}). Waiting {wait_time}s...")
                time.sleep(wait_time)

            else:
                print(f"    ✗ HTTP Error {status_code}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(5)

        except requests.exceptions.Timeout:
            print(f"    ⚠️  Timeout. Retrying...")
            if attempt == max_retries - 1:
                raise
            time.sleep(5)

        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Request error: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(5)

    raise Exception(f"Failed after {max_retries} retries for {url}")
