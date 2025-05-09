import yfinance as yf
import pandas as pd

import yfinance as yf

def get_current_market_prices_fast(file_path: str):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]

    results = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.fast_info.get("last_price") or ticker.info.get("regularMarketPrice")
            if price:
                results.append(f"{symbol}: {price:.2f} $")
            else:
                results.append(f"{symbol}: Price not available")
        except Exception:
            results.append(f"{symbol}: Error retrieving data")

    print(results)
    return results