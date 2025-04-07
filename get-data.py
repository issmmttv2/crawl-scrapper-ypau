import csv
import time
import random
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (TimeoutException, 
                                     NoSuchElementException,
                                     WebDriverException)

INPUT_FILE = ''
OUTPUT_FILE = 'final.csv'
DELAY = random.uniform(1,3)
MAX_RETRIES = 2
HEADLESS = False
PROXY = None
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

def setup_driver():
    """Driver setup with temporary profile path return"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_argument("--start-maximized")
    
    if PROXY:
        chrome_options.add_argument(f'--proxy-server={PROXY}')
    
    if HEADLESS:
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
    
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    temp_profile = f"temp_profile_{random.randint(1000,9999)}"
    profile_path = os.path.join(os.getcwd(), temp_profile)
    chrome_options.add_argument(f"user-data-dir={profile_path}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(15)
    return driver, profile_path

def cleanup_profile(profile_path):
    """Remove temporary profile directory"""
    try:
        if os.path.exists(profile_path):
            shutil.rmtree(profile_path, ignore_errors=True)
    except Exception as e:
        print(f"Warning: Could not clean up profile {profile_path}: {str(e)[:100]}")

def extract_email_from_page(driver):
    """HTML structure"""
    try:
        # find email using the specific contact-email class
        email_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.contact-email[data-email]'))
        )
        return email_element.get_attribute('data-email')
    except TimeoutException:
        pass
    
    try:
        # Fallback to href mailto extraction
        email_element = driver.find_element(By.CSS_SELECTOR, 'a[href^="mailto:"]')
        email = email_element.get_attribute('href')
        if email:
            return email.replace('mailto:', '').split('?')[0].strip()
    except NoSuchElementException:
        pass
    
    return None

def get_email(driver, url):
    if not url or url.lower() in ["not found", "none"]:
        return "Invalid URL"
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"\nAttempt {attempt + 1} for {url[:50]}...")
            time.sleep(random.uniform(1, 3))
            driver.get(url)
            
            # Minimal scrolling to trigger potential lazy-loading
            for _ in range(random.randint(1, 2)):
                scroll_px = random.randint(300, 800)
                driver.execute_script(f"window.scrollBy(0, {scroll_px});")
                time.sleep(random.uniform(0.3, 1.5))
            
            # Extract email directly from page
            email = extract_email_from_page(driver)
            if email:
                return email
            
            return "Not found"
            
        except WebDriverException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)[:100]}...")
            if "blocked" in str(e).lower() or attempt == MAX_RETRIES - 1:
                return "Blocked"
            
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice(USER_AGENTS)
            })
            time.sleep(DELAY * (attempt + 1))
            
        except Exception as e:
            print(f"Unexpected error: {str(e)[:100]}...")
            return "Error"

def process_emails():
    """Main processing function"""
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        businesses = list(reader)
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header + ['Email'])
        
        for i, row in enumerate(businesses, 1):
            if len(row) < 2:
                continue
                
            name, url = row[0], row[1]
            print(f"\nProcessing {i}/{len(businesses)}: {name[:50]}...")
            
            driver, profile_path = setup_driver()
            try:
                email = get_email(driver, url)
                writer.writerow(row + [email])
                print(f"Result: {email}")
                
                current_delay = random.uniform(DELAY, DELAY * 1.5)
                if i % 3 == 0:
                    current_delay *= 2
                print(f"Waiting {current_delay:.1f} seconds...")
                time.sleep(current_delay)
                
            finally:
                driver.quit()
                cleanup_profile(profile_path)
    
    print("\nEmail collection complete!")

if __name__ == "__main__":
    print("Starting email extractor...")
    process_emails()
