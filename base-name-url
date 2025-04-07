from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import csv

# Configuration
BASE_URL = "https://www.yellowpages.com.au"
SEARCH_URL = "https://www.yellowpages.com.au/search/listings?clue=home+renovations"
OUTPUT_FILE = "aus-reno.csv"
MAX_PAGES = 100
DELAY = random.uniform(5, 15)
HEADLESS = True  # Recommended for stability

def setup_driver():
    """Configure fresh Chrome instance for each page"""
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument('--headless=new')
    
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90,115)}.0.{random.randint(1000,9999)}.{random.randint(100,999)} Safari/537.36")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_page(driver, page_num):
    """Scrape a single page and return listings"""
    try:
        url = f"{SEARCH_URL}&pageNumber={page_num}" if page_num > 1 else SEARCH_URL
        driver.get(url)
        
        # Wait for listings
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.MuiGrid-container'))
        )
        
        listings = []
        cards = driver.find_elements(By.CSS_SELECTOR, 'div.MuiPaper-root')
        
        for card in cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, 'h3.MuiTypography-h3').text.strip()
                url = card.find_element(By.CSS_SELECTOR, 'a.MuiTypography-root').get_attribute('href')
                if name and url:
                    listings.append((name, url))
            except:
                continue
                
        return listings
        
    except Exception as e:
        print(f"Error scraping page {page_num}: {str(e)[:100]}...")
        return []

def save_listings(listings, writer):
    """Save listings to CSV and print progress"""
    for name, url in listings:
        writer.writerow([name, url])
        print(f"Found: {name[:50]}... | URL: {url[:50]}...")

def main():
    """Main scraping process with page-by-page handling"""
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Business Name', 'Business URL'])
        
        for page_num in range(1, MAX_PAGES + 1):
            print(f"\nStarting page {page_num}...")
            
            # Fresh browser instance for each page
            driver = setup_driver()
            try:
                listings = scrape_page(driver, page_num)
                
                if not listings:
                    print(f"No listings found on page {page_num}. Stopping.")
                    break
                
                save_listings(listings, writer)
                print(f"Page {page_num} completed with {len(listings)} listings")
                
            finally:
                driver.quit()
                time.sleep(DELAY)  # Delay between pages
            
            # Random longer break every few pages
            if page_num % 5 == 0:
                long_delay = random.uniform(30, 60)
                print(f"Extended delay: {long_delay:.1f} seconds...")
                time.sleep(long_delay)

if __name__ == "__main__":
    print("Starting scraper (safe mode)...")
    start_time = time.time()
    main()
    print(f"\nScraping completed in {(time.time()-start_time)/60:.1f} minutes")
    print(f"Results saved to {OUTPUT_FILE}")
