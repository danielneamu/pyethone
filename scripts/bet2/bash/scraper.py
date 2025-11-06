"""
Playwright-based scraper for FBRef
Handles all HTTP requests and HTML fetching with anti-blocking measures
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import random

# Configuration
REQUEST_DELAY = 8
MAX_RETRIES = 3
TIMEOUT = 60000  # 60 seconds
PAGE_LOAD_TIMEOUT = 60000  # 60 seconds


class FBRefScraper:
    """Manages Playwright browser instance and page fetching"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        """Start browser on context entry"""
        self.playwright = sync_playwright().start()

        # Launch browser with stealth settings
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        # Create context with realistic settings
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )

        # Set extra headers
        self.context.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        self.page = self.context.new_page()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up browser on context exit"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def fetch_page(self, url, max_retries=MAX_RETRIES):
        """
        Fetch page HTML with retry logic
        Returns HTML string or raises exception after max retries
        """
        for attempt in range(max_retries):
            try:
                print(f"      Fetching: {url}")

                # Navigate to page with longer timeout
                response = self.page.goto(
                    url, timeout=PAGE_LOAD_TIMEOUT, wait_until='networkidle')

                # Check for 403/429
                if response.status == 403:
                    wait_time = (2 ** attempt) * 60
                    print(
                        f"      ⚠️  403 Forbidden. Waiting {wait_time}s (attempt {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue

                if response.status == 429:
                    wait_time = (2 ** attempt) * 60
                    print(
                        f"      ⚠️  429 Rate limited. Waiting {wait_time}s (attempt {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue

                # Success - wait for table to load (with longer timeout)
                try:
                    self.page.wait_for_selector('table', timeout=20000)
                except:
                    pass  # Continue even if table selector times out

                # Add random delay to appear human
                time.sleep(REQUEST_DELAY + random.uniform(1, 3))

                return self.page.content()

            except PlaywrightTimeout:
                print(
                    f"      ⚠️  Timeout on attempt {attempt+1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(5)

            except Exception as e:
                print(f"      ⚠️  Error: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(5)

        raise Exception(f"Failed to fetch {url} after {max_retries} retries")


def create_scraper():
    """Factory function to create scraper instance"""
    return FBRefScraper()
