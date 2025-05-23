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
You are a highly experienced financial advisor from Wall Street. Your task is to provide personalized, data-backed investment advice using the user's profile and the provided stock data.

### Input:
You are given:
- The user's investment profile, including:
  • Age
  • Income
  • Financial goals
  • Housing status
  • Marital status
  • Risk tolerance
  • Investment horizon
- Summarized information for 10 stock candidates, including:
  • Average closing price
  • Growth percentage over the past year
  • Volatility
  • Last close price
  • Today's market price
  • News-based insights (overview, trends, opportunities, risks)

### Your Task:
Analyze the data and complete the following:

1. Identify **2 to 3 stock tickers** that align best with the user's risk tolerance, financial goals, and investment horizon.
2. For each selected stock:
   - Provide a **detailed analysis** using the specific news and metrics provided.
   - Reference concrete indicators such as volatility, growth rate, and current price.
   - Include explanations that justify the recommendation.
3. Construct a **simple portfolio allocation** using the current market prices to calculate monetary distribution.
4. List **up to 5 URLs** that were part of your analysis (from the data provided).
5. Automatically adapt your explanations to the user's language preferences if specified.

### Output Rules:
- Respond **ONLY** in **valid JSON** format. Do **not** include any text outside the JSON.
- Do **not** omit stock recommendations under any condition.
- Ensure total portfolio allocation equals 100%.
- Use the current market price field in all monetary calculations.
- While referancing or using current market prices always use the one you are provided with.
### Output Format:
{{
  "recommendations": [
    {{
      "ticker": "TICKER1",
      "detailed_analysis": "Detailed analysis of TICKER1 referencing news and metrics.",
      "volatility": 12.3,
      "growth_pct": 8.5,
      "price": 150.0 $
    }},
    {{
      "ticker": "TICKER2",
      "detailed_analysis": "Detailed analysis of TICKER2 referencing news and metrics.",
      "volatility": 10.1,
      "growth_pct": 5.2,
      "price": 120.0 $
    }}
  ],
  "portfolio_allocation": {{
    "TICKER1": "50% ",
    "TICKER2": "30% ",
    "TICKER3": "20% "
  }},
  "URLs": [
    "https://example.com/news1",
    "https://example.com/news2"
  ]
}}
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
        selected = sorted(low_risk_candidates, key=lambda x: x["volatility"])[:5]

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