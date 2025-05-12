"""
Python-only solution using cloudscraper to extract Atkinsons spot prices.
This handles JavaScript-rendered content without browser dependencies.
"""

import cloudscraper
import re
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_scraper')

def extract_spot_prices():
    """Extract gold and silver spot prices from Atkinsons website using cloudscraper."""
    
    # Initialize result dictionary
    result = {
        "timestamp": datetime.now().isoformat(),
        "prices": {},
        "success": False,
        "error": None
    }
    
    try:
        # Create a scraper instance
        logger.info("Creating scraper instance...")
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=10
        )
        
        # Get the webpage
        logger.info("Fetching the Atkinsons website...")
        response = scraper.get('https://www.atkinsonsbullion.com/')
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch page: Status code {response.status_code}")
            result["error"] = f"HTTP Error: {response.status_code}"
            return result
            
        # Parse HTML with BeautifulSoup
        logger.info("Parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # First try - WebSocket URL extraction (for dynamic data)
        logger.info("Looking for WebSocket URLs in script tags...")
        script_tags = soup.find_all('script')
        websocket_url = None
        api_endpoint = None
        
        for script in script_tags:
            script_text = script.string if script.string else ""
            if "wss://" in script_text and "prices" in script_text.lower():
                websocket_matches = re.findall(r'(wss://[^"\']+)', script_text)
                if websocket_matches:
                    websocket_url = websocket_matches[0]
                    logger.info(f"Found WebSocket URL: {websocket_url}")
            
            # Look for API endpoints related to prices
            if "/api/" in script_text and "price" in script_text.lower():
                api_matches = re.findall(r'(/api/[^"\']+price[^"\']*)', script_text)
                if api_matches:
                    api_endpoint = api_matches[0]
                    logger.info(f"Found API endpoint: {api_endpoint}")
        
        # If we found an API endpoint, try to fetch from it
        if api_endpoint:
            logger.info(f"Trying API endpoint: {api_endpoint}")
            api_url = f"https://www.atkinsonsbullion.com{api_endpoint}"
            try:
                api_response = scraper.get(api_url)
                if api_response.status_code == 200:
                    try:
                        api_data = api_response.json()
                        logger.info(f"API response: {api_data}")
                        # Extract prices from API response - structure depends on actual API
                        # You'll need to adapt this based on the actual response format
                        if isinstance(api_data, dict) and "prices" in api_data:
                            for metal, price in api_data["prices"].items():
                                if "gold" in metal.lower() and "oz" in metal.lower():
                                    result["prices"]["XAU"] = float(price)
                                elif "silver" in metal.lower() and "oz" in metal.lower():
                                    result["prices"]["XAG"] = float(price)
                                elif "gold" in metal.lower() and "gram" in metal.lower():
                                    result["prices"]["XAU_GRAM"] = float(price)
                                elif "silver" in metal.lower() and "gram" in metal.lower():
                                    result["prices"]["XAG_GRAM"] = float(price)
                    except json.JSONDecodeError:
                        logger.warning("API response is not valid JSON")
            except Exception as e:
                logger.warning(f"API request failed: {str(e)}")
        
        # If API approach didn't work, fall back to HTML parsing
        if not result["prices"]:
            logger.info("API approach didn't work, falling back to HTML parsing...")
            
            # Try direct parsing approach - repeatedly fetch page until prices are loaded
            max_attempts = 3
            for attempt in range(max_attempts):
                logger.info(f"Attempt {attempt+1}/{max_attempts} to fetch prices...")
                
                # Refetch the page - sometimes the first load doesn't have prices
                if attempt > 0:
                    response = scraper.get('https://www.atkinsonsbullion.com/')
                    soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for spot price table
                table = soup.find('table', attrs={'data-lp': 'spotPrice'})
                
                if not table:
                    logger.warning("Price table not found")
                    time.sleep(2)
                    continue
                    
                # Helper function to extract price
                def get_price_from_cell(cell_selector, row_idx=None, col_idx=None):
                    try:
                        # First try with CSS selector
                        cell = table.select_one(cell_selector)
                        
                        # If that fails, try by row and column index
                        if not cell and row_idx is not None and col_idx is not None:
                            rows = table.find_all('tr')
                            if len(rows) > row_idx:
                                row = rows[row_idx]
                                cells = row.find_all('td')
                                if len(cells) > col_idx:
                                    cell = cells[col_idx]
                        
                        if not cell:
                            return None
                            
                        price_text = cell.get_text().strip()
                        logger.info(f"Found price text: '{price_text}'")
                        
                        # Check for £ symbol
                        if '£' in price_text:
                            match = re.search(r'£([0-9,.]+)', price_text)
                            if match:
                                return float(match.group(1).replace(',', ''))
                        return None
                    except Exception as e:
                        logger.warning(f"Error extracting price from {cell_selector}: {e}")
                        return None
                
                # Try to extract all four prices
                gold_toz = get_price_from_cell('td.js-lp-gold-toz', 1, 0)
                silver_toz = get_price_from_cell('td.js-lp-silver-toz', 2, 0)
                gold_gram = get_price_from_cell('td.js-lp-gold-grams', 1, 1)
                silver_gram = get_price_from_cell('td.js-lp-silver-grams', 2, 1)
                
                # Add any prices we found
                if gold_toz:
                    result["prices"]["XAU"] = gold_toz
                if silver_toz:
                    result["prices"]["XAG"] = silver_toz
                if gold_gram:
                    result["prices"]["XAU_GRAM"] = gold_gram
                if silver_gram:
                    result["prices"]["XAG_GRAM"] = silver_gram
                    
                # If we found at least some prices, we can stop
                if result["prices"]:
                    break
                    
                # Wait before retrying
                time.sleep(3)
        
        # Set success flag
        result["success"] = len(result["prices"]) > 0
        
        # Print the results
        for metal, price in result["prices"].items():
            logger.info(f"{metal}: £{price}")
        
        return result
            
    except Exception as e:
        # Handle exceptions
        error_message = str(e)
        logger.error(f"Error: {error_message}")
        result["error"] = error_message
        return result

if __name__ == "__main__":
    try:
        # Extract the prices
        result = extract_spot_prices()
        
        # Save results to a file
        with open("spot_prices.json", "w") as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Results saved to spot_prices.json")
        
        # Exit with appropriate code
        exit(0 if result["success"] else 1)
    except Exception as e:
        logger.critical(f"Critical error in main: {e}")
        exit(1)