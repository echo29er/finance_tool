from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

def scrape_chards_sovereign_price(url):
    try:
        # Set up headless Chrome browser
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the page
        driver.get(url)
        
        # Wait for the page to load completely
        time.sleep(3)  # Simple wait
        
        # Print the entire page source for debugging
        print("Page loaded. Looking for price elements...")
        
        # Try various selectors to find the price
        price_element = None
        selectors_to_try = [
            "td.tw-py-2\\.5.tw-px-4",
            "div.tw-bg-neutral-200 td",
            "td:contains(£)",
            ".price",
            "td.price",
            "span.price"
        ]
        
        for selector in selectors_to_try:
            try:
                print(f"Trying selector: {selector}")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text
                    print(f"Found element with text: '{text}'")
                    if '£' in text:
                        price_element = element
                        break
                if price_element:
                    break
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        if price_element:
            price_text = price_element.text
            print(f"Found price element with text: '{price_text}'")
            
            # Extract the price using regex
            price_match = re.search(r'£(\d+[\.,]\d+)', price_text)
            if price_match:
                price = float(price_match.group(1).replace(',', '.'))
                print(f"Extracted price: £{price}")
                return price
            else:
                print(f"Could not extract price from text: '{price_text}'")
        else:
            # Last resort: get all text and look for pound signs
            body_text = driver.find_element(By.TAG_NAME, "body").text
            price_matches = re.findall(r'£(\d+[\.,]\d+)', body_text)
            if price_matches:
                # Get the first match or the one that looks most like a sovereign price
                print(f"Found potential prices in body: {price_matches}")
                prices = [float(p.replace(',', '.')) for p in price_matches]
                # Sovereign price is likely between £500 and £700
                sovereign_prices = [p for p in prices if 500 <= p <= 700]
                if sovereign_prices:
                    price = sovereign_prices[0]
                    print(f"Selected likely sovereign price: £{price}")
                    return price
                else:
                    return prices[0]
        
        return None
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        try:
            driver.quit()
        except:
            pass

# Example usage
if __name__ == "__main__":
    url = "https://www.chards.co.uk/2025-uk-full-gold-sovereign-coin/2952"
    price = scrape_chards_sovereign_price(url)
    
    if price:
        print(f"The current price is: £{price}")
    else:
        print("Could not find the price")