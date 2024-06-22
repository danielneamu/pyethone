import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os
import psutil


# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the chromedriver to the current folder from where the script is running
CHROME_DRIVER_PATH = os.path.join(script_dir, 'chromedriver.exe')

def get_webdriver():
    # Configure Chrome WebDriver
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (without opening browser window)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")  # Suppress logs
    options.add_argument('--disable-logging')
    options.add_argument('--disable-logging-redirect')
    options.add_argument('--disable-extensions')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-logging')
    options.add_argument('--disable-logging-redirect')
    options.add_argument('--log-level=3')  # Suppress logs
    options.add_argument('--silent')

    # Suppress browser console logs
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])

    # Initialize the WebDriver
    service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

# Function to scrape Zacks.com for recommendation rating
def scrape_zacks_recommendation(symbol):
    base_url = 'https://www.zacks.com/stock/quote/'
    url = urljoin(base_url, symbol)
    print(f"Fetching data for symbol: {symbol} from {url}")
    
    driver = get_webdriver()
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for 5 seconds for page to load (adjust as needed)
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rank_view = soup.find('p', class_='rank_view')
        if rank_view:
            # Extract the text and find the rating number
            rank_text = rank_view.get_text(strip=True)
            rating_text = rank_text.split(' ')[0].strip()  # Assuming rank_text is like '3-Hold'
            rating = rating_text.split('-')[0].strip()
            print(f"Found rating {rating} for symbol: {symbol}")
            return rating
        else:
            print(f"Could not find rank_view element for symbol: {symbol}")
            return None
    except Exception as e:
        print(f"Error scraping data for symbol {symbol}: {str(e)}")
        return None
    finally:
        print ("Quitting Chrome driver")
        driver.quit()  # Ensure the WebDriver is quit to release resources
        time.sleep(2)  # Add a small delay to ensure the browser closes properly
        cleanup_chrome_processes()


def cleanup_chrome_processes():
    for proc in psutil.process_iter():
        # Check if process name contains 'chrome' or 'chromedriver'
        if 'chrome' in proc.name().lower() or 'chromedriver' in proc.name().lower():
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass

# Main function to read CSV, scrape ratings, and update CSV
def main(input_csv, output_csv):
    with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Zacks Rating']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            symbol = row['Symbol']
            rating = scrape_zacks_recommendation(symbol)
            row['Zacks Rating'] = rating
            writer.writerow(row)

if __name__ == "__main__":
    input_csv = 'large_cap_stocks.csv'  # Replace with your input CSV file path
    output_csv = 'stocks_with_ratings.csv'  # Replace with your desired output CSV file path
    main(input_csv, output_csv)
