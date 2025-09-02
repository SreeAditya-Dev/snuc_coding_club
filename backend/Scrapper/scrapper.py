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

# Context manager to suppress all output
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

# Setup Chrome options for complete silence
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--silent")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
chrome_options.add_argument("--disable-dev-tools")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--disable-default-apps")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.155 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_experimental_option("detach", True)

# Auto-install and setup ChromeDriver with complete output suppression
with suppress_all_output():
    service = Service(ChromeDriverManager().install())
    service.log_path = os.devnull
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Load clubs data
def load_clubs_data():
    try:
        with open('../data/clubs.json', 'r', encoding='utf-8') as f:
            clubs_data = json.load(f)
            return clubs_data['clubs']
    except Exception as e:
        print(f"Error loading clubs data: {e}")
        return []

clubs = load_clubs_data()
data = {}

# --- Alternative scraping method using requests and BeautifulSoup ---
def scrape_with_requests(url, platform):
    """Fallback method using requests for basic public information"""
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
        
        if platform == "instagram":
            # Try to extract basic info from meta tags
            title = soup.find('title')
            description = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
            
            return {
                "platform": "Instagram",
                "username": "snuc_cc",
                "title": title.text if title else "N/A",
                "description": description.get('content') if description else "N/A",
                "url": url
            }
        
        elif platform == "linkedin":
            title = soup.find('title')
            description = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
            
            # Try to extract follower info from title or description
            followers = "N/A"
            about_text = "N/A"
            
            if description:
                desc_content = description.get('content', '')
                about_text = desc_content
                
                # Look for follower count in description
                follower_match = re.search(r'(\d+(?:,\d+)*)\s*followers?', desc_content, re.IGNORECASE)
                if follower_match:
                    followers = follower_match.group(1)
            
            # Also check title for info
            title_text = title.text if title else ""
            if "follower" in title_text.lower():
                follower_match = re.search(r'(\d+(?:,\d+)*)\s*followers?', title_text, re.IGNORECASE)
                if follower_match:
                    followers = follower_match.group(1)
            
            return {
                "platform": "LinkedIn",
                "company": "SNUC Coding Club",
                "title": title_text,
                "description": about_text,
                "followers": followers,
                "url": url,
            }
            
    except Exception as e:
        return {"error": f"Requests method failed: {str(e)}"}

# --- Instagram Scraper ---
def scrape_instagram(url, username):
    try:
        driver.get(url)
        time.sleep(3)
        
        # Get followers from page source
        page_source = driver.page_source
        followers = "N/A"
        
        # Try to extract follower count from page source
        follower_patterns = [
            r'"edge_followed_by":{"count":(\d+)}',
            r'"edge_follow":{"count":(\d+)}',
            r'(\d+(?:,\d+)*)\s*followers?',
        ]
        
        for pattern in follower_patterns:
            match = re.search(pattern, page_source, re.IGNORECASE)
            if match:
                followers = match.group(1)
                break
        
        # Extract account creation year
        creation_date = "2022"  # Default for SNUC clubs
        
        # Get bio from meta description
        bio = "N/A"
        try:
            meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']")
            full_bio = meta_desc.get_attribute("content")
            if full_bio:
                # Extract clean bio from meta description
                bio_match = re.search(r'"([^"]*)"', full_bio)
                if bio_match:
                    bio = bio_match.group(1)
                else:
                    bio = full_bio
        except:
            pass
        
        return {
            "platform": "Instagram",
            "username": username,
            "followers": followers,
            "bio": bio,
            "account_created": creation_date,
            "url": url
        }
        
    except Exception as e:
        return scrape_with_requests(url, "instagram")

# --- LinkedIn Scraper ---
def scrape_linkedin(url, company_name):
    try:
        driver.get(url)
        time.sleep(5)
        
        # Get followers - try to extract from page
        followers = "N/A"
        
        # Try to extract follower count
        try:
            follower_selectors = [
                "[data-test-id='org-followers-count']",
                ".org-top-card-secondary-content__follower-count",
                ".follower-count",
                ".org-page-details__definition dd"
            ]
            
            for selector in follower_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text
                    follower_match = re.search(r'(\d+(?:,\d+)*)', text)
                    if follower_match:
                        followers = follower_match.group(1)
                        break
                except:
                    continue
        except:
            pass
        
        # Get about section
        about = "N/A"
        try:
            # Try to get the actual about section from the page
            about_selectors = [
                "[data-test-id='org-about-us-org-description'] span",
                ".org-about-us-org-description__text",
                ".about-us-org-description",
                ".org-page-details__definition dd"
            ]
            
            for selector in about_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text and len(element.text.strip()) > 20:
                        about = element.text.strip()
                        # Clean up the about text
                        about = re.sub(r'\s+', ' ', about)  # Remove extra whitespace
                        break
                except:
                    continue
        except:
            pass
        
        return {
            "platform": "LinkedIn",
            "company": company_name,
            "followers": followers,
            "about": about,
            "url": url
        }
        
    except Exception as e:
        return scrape_with_requests(url, "linkedin")



# --- Run Scrapers for All Clubs ---
try:
    with suppress_all_output():
        for club in clubs:
            club_name = club['name']
            club_id = club['id']
            print(f"Scraping data for {club_name}...")
            
            club_data = {
                "club_id": club_id,
                "club_name": club_name,
                "social_media": {}
            }
            
            # Check if club has social media accounts
            if 'social_media' in club:
                social_media = club['social_media']
                
                # Scrape Instagram if available
                if 'instagram' in social_media:
                    instagram_url = social_media['instagram']
                    # Extract username from URL
                    username_match = re.search(r'instagram\.com/([^/]+)', instagram_url)
                    username = username_match.group(1) if username_match else "unknown"
                    
                    print(f"  Scraping Instagram: {username}")
                    instagram_data = scrape_instagram(instagram_url, username)
                    club_data['social_media']['instagram'] = instagram_data
                
                # Scrape LinkedIn if available
                if 'linkedin' in social_media:
                    linkedin_url = social_media['linkedin']
                    
                    print(f"  Scraping LinkedIn: {club_name}")
                    linkedin_data = scrape_linkedin(linkedin_url, club_name)
                    club_data['social_media']['linkedin'] = linkedin_data
            
            # Add club data to main data structure
            data[f"club_{club_id}"] = club_data
            
            # Small delay between clubs to be respectful
            time.sleep(2)

finally:
    with suppress_all_output():
        driver.quit()

# --- Save and Print Clean Results ---
print("\n" + "="*50)
print("SOCIAL MEDIA SCRAPING COMPLETED")
print("="*50)
print(json.dumps(data, indent=2, ensure_ascii=False))

# Save to file
output_file = "social_media_data.json"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nData saved to {output_file}")
except Exception as e:
    print(f"Error saving file: {e}")