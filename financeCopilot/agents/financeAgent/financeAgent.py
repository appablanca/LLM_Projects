import os
import json
import requests
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime, timedelta
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

user_profile = {
    "age": 22,
    "risk_tolerance": "high",
    "investment_amount": 100000,
}


def get_current_market_prices(file_path: str):
    symbol_to_price = {}
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if ":" in line and "$" in line:
                try:
                    parts = line.split(":")
                    symbol = parts[0].strip()
                    price = float(parts[1].replace("$", "").strip())
                    symbol_to_price[symbol] = price
                except ValueError:
                    continue  # Geçersiz satırı atla
    return symbol_to_price

current_prices = get_current_market_prices("market_prices_output.txt")


with open("historical_data.json", "r", encoding="utf-8") as file:
    historical_data = json.load(file)

# Step 4: Her hissenin özetini çıkar
def summarize_stock(symbol_data):
    closes = [day["close"] for day in reversed(symbol_data["data"])]
    if len(closes) < 2:
        return None
    return {
        "symbol": symbol_data["symbol"],
        "avg_close": round(sum(closes) / len(closes), 2),
        "min_close": round(min(closes), 2),
        "max_close": round(max(closes), 2),
        "last_close": round(closes[-1], 2),
        "volatility": round(max(closes) - min(closes), 2),
        "growth_pct": round(((closes[-1] - closes[0]) / closes[0]) * 100, 2)
    }

summaries = [summarize_stock(item) for item in historical_data]
summaries = [s for s in summaries if s is not None]


low_risk_candidates = [
    s for s in summaries if s["volatility"] < 35 and s["growth_pct"] > 0
]


selected = sorted(low_risk_candidates, key=lambda x: x["volatility"])[:100]

for s in selected:
    s["today_price"] = current_prices.get(s["symbol"], "N/A")



for s in selected:
    print(f"- {s['symbol']}: Volatility={s['volatility']}, Growth={s['growth_pct']}%, LastClose={s['last_close']}, Today={s['today_price']}")


summary_lines = "\n".join([
    f"""
Ticker: {s['symbol']}
- Avg Close: {s['avg_close']} $
- Growth (1y): {s['growth_pct']} %
- Volatility: {s['volatility']} $
- Last Close: {s['last_close']} $
- Today’s Price: {s['today_price']} $
""" for s in selected
])

prompt = f"""
You are a conservative financial assistant recommending a specific investment portfolio.

User profile:
- Age: {user_profile['age']}
- Risk tolerance: {user_profile['risk_tolerance']}
- Investment amount: {user_profile['investment_amount']} TL
- Investment horizon: 10 years
- User prefers stable, smaller companies and wants to avoid speculative investments.

Below is a summary of 100 low-risk stock candidates:

{summary_lines}

Please recommend 2–3 stocks **from this data**, naming the tickers and explaining why they are suitable for a super-low-risk, long-term investor.
At the end give a portfolio suggestion with the following format:
- 50% in [TICKER1]
- 30% in [TICKER2]
- 20% in [TICKER3]
The percentage values should add up to 100%.
"""

response = model.generate_content(prompt)
print("💡 Gemini's Recommendation:\n")
print(response.text)