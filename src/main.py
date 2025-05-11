# In src/main.py
from scrapers.chards_prod import get_all_prices
from scrapers.chards_coins import COINS

if __name__ == "__main__":
    # get_all_prices("logging")
    print (get_all_prices())
    