from agents.baseAgent import Agent
import os
import json
import httpx
from dotenv import load_dotenv
import numpy as np  # ensure numpy is imported at the top
import google.generativeai as genai
from financeAgent.newsGetter import NewsAnalyzer
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")

investmentAdvisorAgentRole = f"""
You are a highly experienced financial advisor from Wall Street.
Your goal is to provide personalized investment advice based on the user's profile and current market data.

You are provided with:
- The user's investment profile (e.g., age, income, goals, housing, marital status, investment preferences)
- Summarized data for 10 stock candidates, including:
  • Average closing price
  • Growth percentage over the past year
  • Volatility
  • Last close price
  • Today’s price
  • News-based insights (overview, trends, opportunities, risks)

Your responsibilities:
1. Analyze the user's investment profile and align your recommendations with their risk tolerance, financial goals, and investment horizon.
2. Select 2 to 3 stocks from the list that best match the user's profile.
3. Justify each selection using specific metrics and news insights (e.g., low volatility, strong growth, relevant opportunities).
4. While makeing detailed analysis of each stock, refer to the spesfic news and metrics provided in the summary. 
5. Don't hold back on the details; provide a comprehensive analysis of each stock.
6. Construct a simple portfolio allocation that reflects the selected stocks and fits the user's profile.
7. Populate the URLs field with the URLs that come to you.
8. Give explanations for each ticker.
Output format:
Respond ONLY in valid JSON. Do not include any explanations outside the JSON.

Use this structure:
{{
  "recommendations": [
    {{
      "ticker": "TICKER1",
      "detailed_analysis": "detailed analysis of TICKER1 referansing news and metrics",
      "volatility": 12.3,
      "growth_pct": 8.5
    }},
  ],
  "portfolio_allocation": {{
    "TICKER1": "50%",
    "TICKER2": "30%",
    "TICKER3": "20%"
  }},
  {{
    "URLs": [
        "https://example.com/news1",
        "https://example.com/news2"
        ]
  }}
}}

Guidelines:
- Make sure the total portfolio allocation adds up to 100%.
- Adapt to the user's language automatically.
- Justify recommendations with data-driven reasoning.
- Max URL count: 5.
- DONT ever miss recommendations about the stocks.
"""

class InvestmentAdvisorAgent(Agent):
    def __init__(self, name, role):
        super().__init__(name="Investment Advice Agent", role=investmentAdvisorAgentRole)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            },
            system_instruction=self.role,
        )
        self.news_analyzer = NewsAnalyzer()

    def get_current_market_prices(self, file_path: str):
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
                        continue
        return symbol_to_price

    def calculate_annualized_volatility(self,closes):
        if len(closes) < 2:
            return 0.0
        returns = np.log(np.array(closes[1:]) / np.array(closes[:-1]))
        daily_volatility = np.std(returns, ddof=1)
        return round(daily_volatility * np.sqrt(252), 2)
    
    def summarize_stock(self, symbol_data):
        closes = [day["close"] for day in reversed(symbol_data["data"])]
        if len(closes) < 2:
            return None
        return {
            "symbol": symbol_data["symbol"],
            "avg_close": round(sum(closes) / len(closes), 2),
            "min_close": round(min(closes), 2),
            "max_close": round(max(closes), 2),
            "last_close": round(closes[-1], 2),
            "volatility": self.calculate_annualized_volatility(closes),
            "growth_pct": round(((closes[-1] - closes[0]) / closes[0]) * 100, 2),
        }

    def give_summary_lines(self):
        # Step 1: Get the current market prices
        current_prices = self.get_current_market_prices("./agents/financeAgent/market_prices_output.txt")

        # Step 2: Load historical data
        with open("./agents/financeAgent/historical_data.json", "r", encoding="utf-8") as file:
            stock_data = json.load(file)

        # Step 3: Summarize each stock
        low_risk_candidates= []
        for s in stock_data:
            if(s["volatility"] < 35 and s["growth_pct"] > 0):
                low_risk_candidates.append(s)



        # Step 5: Select top 10 by lowest volatility
        selected = sorted(low_risk_candidates, key=lambda x: x["volatility"])[:10]

        # Step 6: Attach current price and news analysis
        summary_lines = ""

        for s in selected:
            symbol = s["symbol"]
            s["today_price"] = current_prices.get(symbol, "N/A")

            try:
                news_summary = self.news_analyzer.analyze_news(symbol)
            except Exception as e:
                print(f"⚠️ News analysis failed for {symbol}: {e}")
                news_summary = {
                    "overview": "Unavailable",
                    "key_trends": [],
                    "market_impacts": [],
                    "opportunities": [],
                    "risks": [],
                    "URL": []
                }

            s["news_summary"] = news_summary

            summary_lines += f"""
Ticker: {symbol}
- Avg Close: {s['avg_close']} $
- Growth (1y): {s['growth_pct']} %
- Volatility: {s['volatility']} $
- Today's Price: {s['today_price']} $

📊 News Summary:
Overview: {news_summary.get("overview", "N/A")}
Key Trends: {", ".join(news_summary.get("key_trends", []))}
Market Impacts: {", ".join(news_summary.get("market_impacts", []))}
Opportunities: {", ".join(news_summary.get("opportunities", []))}
Risks: {", ".join(news_summary.get("risks", []))}
News URL: {", ".join(news_summary.get("URL", []))}

---------------------------------------------------------
"""

        return summary_lines

    async def get_financal_advise(self, user_message,user):
        userS = json.loads(user)
        summery_lines = self.give_summary_lines()
        print(user)
        prompt = (
            user_message
            + "\nUser profile: "
            + json.dumps(userS)
            + "\nBelow is a summary of 10 low-risk stock candidates with recent news analysis:\n"
            + summery_lines
        )

        print(prompt)
        response = self.generate_response(prompt)
        return json.loads(response)