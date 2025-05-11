# In src/main.py
import logging
from scrapers.chards_prod import update_price
from scrapers.chards_coins import COINS

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test each coin
    for coin_id in COINS:
        price, coin_name = update_price(coin_id)
        if price:
            print(f"The current {coin_name} price is: £{price}")
        else:
            print(f"Could not find the price for {coin_name}")