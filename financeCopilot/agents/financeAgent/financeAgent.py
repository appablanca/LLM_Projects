import os
import requests
import pandas as pd
import yfinance as yf
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import google.generativeai as genai
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")



# Step 1: get current market prices from txt file   
def get_current_market_prices(file_path: str):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]
    return symbols

currentPrices = get_current_market_prices("market_prices_output.txt")


with open("historical_data.json", "r", encoding="utf-8") as file:
    historicalDataJSON = json.load(file)



    
user_profile = {
    "age": 40,
    "risk_tolerance": "low",
    "investment_amount": 100000,
}



# Step 6: Build prompt
limited_historical_data = dict(list(historicalDataJSON)[:3])
limited_current_prices = currentPrices[:3]

prompt = f"""
You are a conservative financial assistant recommending a specific investment portfolio.

User profile:
- Age: {user_profile['age']}
- Risk tolerance: {user_profile['risk_tolerance']}
- Investment amount: {user_profile['investment_amount']} TL
- Investment horizon: 10 years
- User prefers stable, smaller companies and wants to avoid speculative investments.

This is simplified stock data:

Historical data: {limited_historical_data}
Current prices: {limited_current_prices}

Please recommend 2–3 stocks **from this data**, naming the tickers and explaining why they are suitable for a super-low-risk, long-term investor.
At the end give a portfolio suggestion with the following format:
- 50% in [TICKER1]
- 30% in [TICKER2]
- 20% in [TICKER3]
The percentage values should add up to 100%.
The percentage values should be in the range of 0-100.
The percantage can change but the total should be 100.
"""




response = model.generate_content(prompt)
print("💡 Gemini's Recommendation:\n")
print(response.text)