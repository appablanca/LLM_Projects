import os
import requests
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime, timedelta
import google.generativeai as genai
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

TWELVE_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BASE_URL = "https://api.twelvedata.com/time_series"
STOCK_LIST_URL = "https://api.twelvedata.com/stocks"


def get_current_market_prices_fast(file_path: str):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]

    data = yf.download(
        tickers=" ".join(symbols),
        period="1d",
        interval="1m",  
        group_by="ticker",
        threads=True,
        progress=False
    )

    results = []
    for symbol in symbols:
        try:
            last_price = data[symbol]["Close"].dropna().iloc[-1]
            results.append(f"{symbol}: {last_price:.2f} $")
        except Exception:
            results.append(f"{symbol}: Price not available")

    return results



def fetch_stock_history(symbol):
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    params = {
        "symbol": symbol,
        "interval": "1mo",
        "start_date": start_date,
        "end_date": end_date,
        "apikey": TWELVE_API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        return []
    return response.json().get("values", [])


user_profile = {
    "age": 40,
    "risk_tolerance": "low",
    "investment_amount": 100000,
}


stock_data = {symbol: fetch_stock_history(symbol) for symbol in stock_symbols}

# Step 6: Build prompt
prompt = f"""
You are a conservative financial assistant recommending a specific investment portfolio.

User profile:
- Age: {user_profile['age']}
- Risk tolerance: {user_profile['risk_tolerance']}
- Investment amount: {user_profile['investment_amount']} TL
- Investment horizon: 10 years
- User prefers stable, smaller companies and wants to avoid speculative investments.

Below is 6-month historical daily price data for {len(stock_data)} stocks.

Please recommend 2–3 stocks **from this data**, specifically naming the tickers and explaining why they're suitable for a super-low-risk, long-term investor. Use the price trend if possible.

Stock price data:
"""

for symbol, values in stock_data.items():
    if not values:
        continue
    prompt += f"\nStock: {symbol}\n"
    prompt += "\n".join([f"{v['datetime']}: {v['close']} USD" for v in values[:5]])  # Limit to recent 5 for brevity

prompt += "\n\nReturn a specific stock recommendation portfolio for this user profile."


print("\n" + "=" * 40 + " PROMPT TO GEMINI " + "=" * 40)
print(prompt)
print("=" * 100 + "\n")


response = model.generate_content(prompt)
print("💡 Gemini's Recommendation:\n")
print(response.text)