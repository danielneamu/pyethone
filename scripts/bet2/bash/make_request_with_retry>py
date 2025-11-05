def make_request_with_retry(url, max_retries=MAX_RETRIES):

  """Make HTTP request with exponential backoff retry"""
   for attempt in range(max_retries):
        try:
            headers = get_random_headers()
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (attempt + 1) * 60
                print(f"    ⚠️  Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.response.status_code == 403:
                wait_time = 30 + (attempt * 15)
                print(f"    ⚠️  Forbidden (403). Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.response.status_code in [500, 502, 503, 504]:
                wait_time = 10 + (attempt * 5)
                print(
                    f"    ⚠️  Server error ({e.response.status_code}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"    ✗ HTTP Error {e.response.status_code}: {e}")
                raise
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Request error: {e}. Retrying...")
            time.sleep(10)
    raise Exception(f"Failed after {max_retries} retries for {url}")
