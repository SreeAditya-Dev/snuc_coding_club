from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json
import requests
from bs4 import BeautifulSoup
import sys
import os
import logging
import contextlib

# Suppress all warnings and logs completely
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('webdriver_manager').setLevel(logging.CRITICAL)

@contextlib.contextmanager
def suppress_all_output():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def scrape_linkedin_advanced(url, company_name):
    """Advanced LinkedIn scraper with multiple fallback methods"""
    
    # Method 1: Try direct requests first (fastest)
    def try_requests_method():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.155 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract from meta tags
            description = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
            title = soup.find('title')
            
            followers = "N/A"
            about_text = "N/A"
            
            if description:
                desc_content = description.get('content', '')
                
                # Look for follower patterns
                follower_patterns = [
                    r'(\d+(?:,\d+)*)\s*followers?',
                    r'followers?\s*(\d+(?:,\d+)*)',
                    r'(\d+(?:,\d+)*)\s*members?',
                    r'members?\s*(\d+(?:,\d+)*)'
                ]
                
                for pattern in follower_patterns:
                    match = re.search(pattern, desc_content, re.IGNORECASE)
                    if match:
                        followers = match.group(1)
                        break
                
                # Clean up description
                if desc_content and len(desc_content) > 30:
                    # Remove LinkedIn branding
                    about_text = re.sub(r'.*?on LinkedIn.*?[.|:]', '', desc_content)
                    about_text = re.sub(r'Sign up.*$', '', about_text)
                    about_text = re.sub(r'750 million.*?opportunities\.', '', about_text)
                    about_text = about_text.strip()
                    
                    # If it's still generic LinkedIn text, mark as N/A
                    if any(generic in about_text.lower() for generic in ['manage your professional identity', 'build and engage', '750 million']):
                        about_text = "N/A"
            
            # Also check title
            title_text = title.text if title else ""
            if followers == "N/A" and title_text:
                for pattern in [r'(\d+(?:,\d+)*)\s*followers?', r'(\d+(?:,\d+)*)\s*members?']:
                    match = re.search(pattern, title_text, re.IGNORECASE)
                    if match:
                        followers = match.group(1)
                        break
            
            return {
                "platform": "LinkedIn",
                "company": company_name,
                "followers": followers,
                "about": about_text,
                "url": url,
                "method": "requests"
            }
            
        except Exception as e:
            return None
    
    # Method 2: Try Selenium with special techniques
    def try_selenium_method():
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.155 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            with suppress_all_output():
                service = Service(ChromeDriverManager().install())
                service.log_path = os.devnull
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.get(url)
            time.sleep(10)  # Give more time for LinkedIn to load
            
            followers = "N/A"
            about = "N/A"
            
            # Get page source and search for patterns
            page_source = driver.page_source
            
            # Look for follower data in JSON-LD or other structured data
            json_patterns = [
                r'"followerCount[^"]*":\s*(\d+)',
                r'"numberOfEmployees[^"]*":\s*"([^"]*)"',
                r'followers?\D*(\d+(?:,\d+)*)',
                r'(\d+(?:,\d+)*)\D*followers?'
            ]
            
            for pattern in json_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    followers = match.group(1)
                    break
            
            # Look for description in various places
            description_patterns = [
                r'"description":\s*"([^"]{30,})"',
                r'"about":\s*"([^"]{30,})"',
                r'<meta[^>]*property="og:description"[^>]*content="([^"]{30,})"',
                r'<meta[^>]*name="description"[^>]*content="([^"]{30,})"'
            ]
            
            for pattern in description_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE | re.DOTALL)
                if match:
                    desc = match.group(1)
                    # Clean up
                    desc = re.sub(r'\\n', ' ', desc)
                    desc = re.sub(r'\s+', ' ', desc)
                    desc = desc.strip()
                    
                    # Check if it's not generic
                    if len(desc) > 30 and not any(generic in desc.lower() for generic in ['manage your professional identity', '750 million', 'build and engage']):
                        about = desc
                        break
            
            driver.quit()
            
            return {
                "platform": "LinkedIn",
                "company": company_name,
                "followers": followers,
                "about": about,
                "url": url,
                "method": "selenium"
            }
            
        except Exception as e:
            try:
                driver.quit()
            except:
                pass
            return None
    
    # Try methods in order
    print(f"Scraping LinkedIn for {company_name}...")
    
    # Try requests first (faster)
    result = try_requests_method()
    if result and (result["followers"] != "N/A" or result["about"] != "N/A"):
        print(f"  ✓ Success with requests method")
        return result
    
    # If requests didn't work well, try Selenium
    print(f"  → Trying Selenium method...")
    result = try_selenium_method()
    if result:
        print(f"  ✓ Success with Selenium method")
        return result
    
    # If both failed, return basic result
    print(f"  ✗ Both methods failed, returning basic result")
    return {
        "platform": "LinkedIn",
        "company": company_name,
        "followers": "N/A",
        "about": "N/A",
        "url": url,
        "method": "failed"
    }

# Test with SNUC clubs
def main():
    # Load clubs data
    try:
        with open('../data/clubs.json', 'r', encoding='utf-8') as f:
            clubs_data = json.load(f)
            clubs = clubs_data['clubs']
    except Exception as e:
        print(f"Error loading clubs data: {e}")
        return
    
    results = {}
    
    for club in clubs:
        if 'social_media' in club and 'linkedin' in club['social_media']:
            club_name = club['name']
            linkedin_url = club['social_media']['linkedin']
            
            result = scrape_linkedin_advanced(linkedin_url, club_name)
            results[f"club_{club['id']}"] = {
                "club_id": club['id'],
                "club_name": club_name,
                "linkedin_data": result
            }
            
            # Add delay between requests
            time.sleep(3)
    
    # Print results
    print("\n" + "="*50)
    print("LINKEDIN SCRAPING RESULTS")
    print("="*50)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Save to file
    with open('linkedin_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to linkedin_results.json")

if __name__ == "__main__":
    main()
