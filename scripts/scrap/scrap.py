from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_webdriver():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless Chrome
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Suppress logs
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress logging

    # Initialize the WebDriver
    return webdriver.Chrome(service=ChromeService(), options=chrome_options)

def extract_data(page_content, price_pattern, product_pattern):
    # Extract price
    match = re.search(price_pattern, page_content)
    price = match.group(1) if match else "Price not found"
    
    # Extract product name
    match_product = re.search(product_pattern, page_content)
    product = match_product.group(1) if match_product else "Product not found"
    
    return price, product

def main(url):
    price_pattern = r"EM\.productFullPrice\s*=\s*(\d+\.\d+);"
    product_pattern = r'EM\.product_title\s*=\s*"([^"]+)"'

    with get_webdriver() as driver:
        # Set page load timeout
        driver.set_page_load_timeout(30)
        driver.get(url)
        
        # Use WebDriverWait to wait for a specific element to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "script"))
            )
        except:
            print("Error: Page did not load within the expected time")
            return
        
        # Extract page content
        page_content = driver.page_source
        
    price, product = extract_data(page_content, price_pattern, product_pattern)
    
    print(f"The extracted price is: {price} RON")
    print(f"The extracted product is: {product}")

if __name__ == "__main__":
    # url = "https://www.emag.ro/telefon-mobil-samsung-galaxy-s23-plus-dual-sim-8gb-ram-256gb-5g-phantom-black-sm-s916bzkdeue/pd/DB7R8RMBM/"
    url = "https://www.emag.ro/casti-audio-in-ear-nothing-ear-a-true-wireless-noise-cancelling-bluetooth-alb-a10600064/pd/DPS7TXYBM/?ref=hdr-favorite_products"
    # url = "https://www.emag.ro/casti-audio-in-ear-cmf-buds-by-nothing-wireless-bluetooth-5-3-anc-ip54-voice-assistant-light-grey-a10600057/pd/DG2W2PYBM/"
    main(url)
