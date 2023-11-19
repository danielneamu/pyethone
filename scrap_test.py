from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

# Create a Chrome webdriver instance
driver = webdriver.Chrome()

# Open the Reuters search results page
driver.get("https://www.reuters.com/site-search/?query=ASML")

# Wait for the search results to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3[data-testid='Heading']")))

# Get all search results
results = driver.find_elements_by_css_selector("h3[data-testid='Heading']")

# Print the text of each search result
for result in results:
    print(result.text)

# Close the browser window
driver.quit()
