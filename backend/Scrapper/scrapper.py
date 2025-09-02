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

# Setup Chrome options for better stealth
chrome_options = Options()
chrome_options.add_argument("--headless")  # Re-enabled for production
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.155 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Auto-install and setup ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# URLs
urls = {
    "instagram": "https://www.instagram.com/snuc_cc/",
    "linkedin": "https://www.linkedin.com/company/snuc-coding-club/"
}

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
                "url": url,
                "method": "requests_fallback"
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
                "method": "requests_fallback"
            }
            
    except Exception as e:
        return {"error": f"Requests method failed: {str(e)}"}

# --- Instagram Scraper ---
def scrape_instagram():
    print("Attempting Instagram scraping with Selenium...")
    try:
        driver.get(urls["instagram"])
        time.sleep(3)  # Wait for page to load
        
        # Try multiple selectors for username
        username_selectors = [
            "h1",
            "h2",
            "[data-testid='user-name']",
            "._aacl._aaco._aacw._aacx._aad7._aade",
            "span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.xvs91rp.xo1l8bm.x5n08af.x10wh9bi.x1wdrske.x8viiok.x18hxmgj"
        ]
        
        username = "snuc_cc"  # Default fallback
        for selector in username_selectors:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                username = element.text
                if username and username.strip():
                    break
            except:
                continue
        
        # Try to get followers from page source
        page_source = driver.page_source
        followers = "N/A"
        
        # Multiple patterns to find follower count
        follower_patterns = [
            r'"edge_followed_by":{"count":(\d+)}',
            r'"follower_count":(\d+)',
            r'(\d+(?:,\d+)*)\s*followers?',
            r'(\d+(?:\.\d+)?[KMB]?)\s*followers?'
        ]
        
        for pattern in follower_patterns:
            match = re.search(pattern, page_source, re.IGNORECASE)
            if match:
                followers = match.group(1)
                break
        
        # Get bio from meta description
        bio = "N/A"
        try:
            meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']")
            bio = meta_desc.get_attribute("content")
        except:
            pass
        
        return {
            "platform": "Instagram",
            "username": username,
            "followers": followers,
            "bio": bio,
            "url": urls["instagram"],
            "method": "selenium"
        }
        
    except Exception as e:
        print(f"Instagram Selenium failed: {e}")
        print("Falling back to requests method...")
        return scrape_with_requests(urls["instagram"], "instagram")

# --- LinkedIn Scraper ---
def scrape_linkedin():
    print("Attempting LinkedIn scraping with Selenium...")
    try:
        driver.get(urls["linkedin"])
        time.sleep(5)  # Longer wait for LinkedIn
        
        # Try multiple selectors for company name
        company_selectors = [
            "h1.top-card-layout__title",
            "h1[data-test-id='org-top-card-summary-info-header']",
            ".org-top-card-summary__title h1",
            "h1.org-top-card-summary-info-list__info-item",
            "h1",
            ".top-card-layout__entity-info h1"
        ]
        
        company_name = "SNUC Coding Club"  # Default fallback
        for selector in company_selectors:
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.text and element.text.strip():
                    company_name = element.text.strip()
                    print(f"Found company name: {company_name}")
                    break
            except:
                continue
        
        # Try multiple approaches for follower count
        followers = "N/A"
        
        # Method 1: Look for follower text in various elements
        follower_selectors = [
            ".top-card-layout__first-subline",
            ".org-top-card-summary-info-list__info-item",
            "[data-test-id='org-followers-count']",
            ".follower-count",
            "span:contains('followers')",
            ".top-card-layout__headline"
        ]
        
        for selector in follower_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.lower()
                    if "follower" in text:
                        followers = element.text.strip()
                        print(f"Found followers via CSS: {followers}")
                        break
                if followers != "N/A":
                    break
            except:
                continue
        
        # Method 2: Search in page source for follower patterns
        if followers == "N/A":
            page_source = driver.page_source.lower()
            follower_patterns = [
                r'(\d+(?:,\d+)*)\s*followers?',
                r'(\d+(?:\.\d+)?[kmb]?)\s*followers?',
                r'"followerCount":(\d+)',
                r'follower.*?(\d+(?:,\d+)*)',
                r'(\d+)\s*follower'
            ]
            
            for pattern in follower_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    followers = match.group(1)
                    print(f"Found followers via regex: {followers}")
                    break
        
        # Method 3: Look for any element containing numbers and "follower"
        if followers == "N/A":
            try:
                all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'follower')]")
                for element in all_elements:
                    text = element.text
                    if re.search(r'\d+', text):
                        followers = text.strip()
                        print(f"Found followers via XPath: {followers}")
                        break
            except:
                pass
        
        # Get about/description with multiple methods
        about = "N/A"
        
        # Method 1: Try various about section selectors
        about_selectors = [
            "[data-test-id='org-about-us-org-description'] span",
            ".org-about-us-org-description__text",
            ".about-us-org-description",
            ".org-page-details__definition dd",
            ".top-card-layout__headline",
            ".org-top-card-summary__description"
        ]
        
        for selector in about_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.text and len(element.text.strip()) > 10:  # Ensure it's substantial text
                    about = element.text.strip()
                    print(f"Found about section: {about[:100]}...")
                    break
            except:
                continue
        
        # Method 2: Try to find and click "Show more" buttons
        if about == "N/A" or len(about) < 50:
            try:
                show_more_buttons = driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Show more') or contains(text(), 'See more') or contains(text(), '...more')]")
                for button in show_more_buttons:
                    try:
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(2)
                        
                        # Try to get expanded content
                        for selector in about_selectors:
                            try:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                                if element.text and len(element.text.strip()) > len(about):
                                    about = element.text.strip()
                                    print(f"Found expanded about: {about[:100]}...")
                                    break
                            except:
                                continue
                        break
                    except:
                        continue
            except:
                pass
        
        # Method 3: Look in meta tags
        if about == "N/A":
            try:
                meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']")
                meta_content = meta_desc.get_attribute("content")
                if meta_content and len(meta_content.strip()) > 10:
                    about = meta_content.strip()
                    print(f"Found about in meta: {about[:100]}...")
            except:
                pass
        
        # Print debug info
        print(f"Final results - Company: {company_name}, Followers: {followers}, About length: {len(about)}")
        
        # Clean up followers data - extract just the number
        clean_followers = followers
        if followers != "N/A":
            # Extract number from strings like "Chennai, Tamil Nadu 226 followers"
            follower_match = re.search(r'(\d+(?:,\d+)*)\s*followers?', followers, re.IGNORECASE)
            if follower_match:
                clean_followers = follower_match.group(1)
        
        # Clean up about section
        clean_about = about
        if about and len(about.strip()) > 3 and about != "N/A":
            # If about is too short, try to get more from page
            if len(about.strip()) < 20:
                try:
                    # Look for longer descriptions
                    longer_desc_elements = driver.find_elements(By.XPATH, 
                        "//p[contains(@class, 'description') or contains(@class, 'about')]")
                    for elem in longer_desc_elements:
                        if len(elem.text) > len(about):
                            clean_about = elem.text.strip()
                            break
                except:
                    pass
        
        return {
            "platform": "LinkedIn",
            "company": company_name,
            "followers": clean_followers,
            "about": clean_about,
            "raw_followers_text": followers,  # Keep original for reference
            "url": urls["linkedin"],
            "method": "selenium"
        }
        
    except Exception as e:
        print(f"LinkedIn Selenium failed: {e}")
        print("Falling back to requests method...")
        return scrape_with_requests(urls["linkedin"], "linkedin")

# --- Manual data collection as ultimate fallback ---
def get_manual_data():
    """Provide manually collected data as fallback"""
    return {
        "instagram": {
            "platform": "Instagram",
            "username": "snuc_cc",
            "handle": "@snuc_cc",
            "url": "https://www.instagram.com/snuc_cc/",
            "followers": "Manual data collection needed",
            "bio": "SNUC Coding Club - Programming community at SNU",
            "method": "manual_fallback",
            "note": "Visit the URL to get current follower count and bio"
        },
        "linkedin": {
            "platform": "LinkedIn",
            "company": "SNUC Coding Club",
            "url": "https://www.linkedin.com/company/snuc-coding-club/",
            "followers": "Manual data collection needed",
            "about": "Coding club at SNU focusing on programming excellence",
            "method": "manual_fallback",
            "note": "Visit the URL to get current follower count and description"
        }
    }

# --- Run Scrapers ---
try:
    print("=== SNUC Coding Club Social Media Scraper ===\n")
    
    print("Scraping Instagram...")
    data["instagram"] = scrape_instagram()
    
    print("\nScraping LinkedIn...")
    data["linkedin"] = scrape_linkedin()
    
    # If both failed, provide manual data structure
    if ("error" in data.get("instagram", {}) and 
        "error" in data.get("linkedin", {})):
        print("\nAll automated methods failed. Providing manual data structure...")
        manual_data = get_manual_data()
        data.update(manual_data)

finally:
    driver.quit()

# --- Save and Print Results ---
print("\n" + "="*50)
print("SCRAPED DATA RESULTS")
print("="*50)
print(json.dumps(data, indent=2))

# Save to file
output_file = "social_media_data.json"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Data saved to {output_file}")
except Exception as e:
    print(f"\n❌ Failed to save data: {e}")

# Summary
print(f"\n📊 SUMMARY:")
for platform, info in data.items():
    if isinstance(info, dict):
        method = info.get('method', 'unknown')
        status = "✅ Success" if 'error' not in info else "❌ Failed"
        print(f"  {platform.title()}: {status} (Method: {method})")

print(f"\n🔍 For manual data collection, visit:")
print(f"  Instagram: {urls['instagram']}")
print(f"  LinkedIn: {urls['linkedin']}")
print(f"\n💡 Note: Social media scraping is challenging due to anti-bot measures.")
print(f"Consider using official APIs or manual data collection for accurate results.")