import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os
import psutil
from datetime import datetime

# Construct the path to the chromedriver
CHROME_DRIVER_PATH = '/usr/bin/chromedriver'

def get_webdriver():
    # Configure Chrome WebDriver
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")  # Suppress logs
    options.add_argument('--disable-logging')
    options.add_argument('--disable-extensions')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-notifications')

    # Suppress browser console logs
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])

    # Initialize the WebDriver
    service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

def scrape_zacks_recommendation(symbol):
    base_url = 'https://www.zacks.com/stock/quote/'
    url = urljoin(base_url, symbol)
    
    driver = get_webdriver()
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for 5 seconds for page to load
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rank_view = soup.find('p', class_='rank_view')
        if rank_view:
            rank_text = rank_view.get_text(strip=True)
            rating_text = rank_text.split(' ')[0].strip()
            rating = rating_text.split('-')[0].strip()
            return rating
        else:
            return None
    except Exception as e:
        return None
    finally:
        driver.quit()
        time.sleep(2)
        cleanup_chrome_processes()

def cleanup_chrome_processes():
    for proc in psutil.process_iter():
        if 'chrome' in proc.name().lower() or 'chromedriver' in proc.name().lower():
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass

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
    start_time = datetime.now()
    print(f"Script started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    today_date = datetime.now().strftime('%Y-%m-%d')
    input_csv = '/var/www/html/pyethone/scripts/stocks/scrap/large_cap_stocks2.csv'
    output_csv = f'/var/www/html/pyethone/scripts/stocks/scrap/stocks_with_rating_{today_date}.csv'
    
    main(input_csv, output_csv)
    
    end_time = datetime.now()
    print(f"Script to scrap Zacks executed in {(end_time - start_time).total_seconds():.2f} seconds at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("------------")
