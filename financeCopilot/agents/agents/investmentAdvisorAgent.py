from agents.baseAgent import Agent
import os,json,httpx
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")


investmentAdvisorAgentRole = f"""
You are a highly cautious financial advisor specializing. Your primary goal is to protect capital while offering modest, steady growth.

Your responsibilities:
1. Analyze the provided stock data and identify 2 to 3 ticker symbols that are suitable for a **super low-risk**, long-term investment strategy.
2. Justify each recommendation with a clear explanation based on available metrics (e.g., stability, dividend history, market dominance, or industry resilience).
3. Focus on conservative investment principles: prioritize blue-chip stocks, low volatility, and consistent performance over time.
4. Analyze the user's profile to ensure the recommendations align with their risk tolerance and investment goals.
5. [Short Reason] = Use current price and historical data to provide a brief explanation of why the stock is a good fit for a risk-averse strategy.
Output format:
- First, list the recommended stocks with brief explanations.
- Then, provide a portfolio allocation suggestion using the following structure:

Portfolio Suggestion:
- 50% in [TICKER1] - [Short reason]
- 30% in [TICKER2] - [Short reason]
- 20% in [TICKER3] - [Short reason]

Ensure the total adds up to 100% and the recommendations strictly reflect a risk-averse strategy.

# Language:
•⁠  Use the same language as the user. 
"""




class InvestmentAdvisorAgent(Agent):
    
    def __init__(self, name, role):
        super().__init__(name, role)

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
                        continue 
        return symbol_to_price
    
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
        
    async def fetch_user_data(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BACKEND_URL}/userPanel/getFields?userId=6818ee0c6507de8196c00a55")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching user data: {e}")
                return {}    
        
        
    def give_summary_lines(self):
        # Step 1: Get the current market prices
        current_prices = self.get_current_market_prices("../financeAgent/market_prices_output.txt") #uzantı değişcek
        
        # Step 2: Load historical data
        with open("../financeAgent/historical_data.json", "r", encoding="utf-8") as file:
            historical_data = json.load(file)
        
        # Step 3: Summarize each stock
        summaries = [self.summarize_stock(item) for item in historical_data]
        summaries = [s for s in summaries if s is not None]
        
        # Step 4: Filter low-risk candidates
        low_risk_candidates = [
            s for s in summaries if s["volatility"] < 35 and s["growth_pct"] > 0
        ]
        
        # Step 5: Select top candidates
        selected = sorted(low_risk_candidates, key=lambda x: x["volatility"])[:100]
        
        # Step 6: Add today's price to each candidate
        for s in selected:
            s["today_price"] = current_prices.get(s["symbol"], "N/A")
            
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
        
        return summary_lines
            
    def get_financal_advise(self, user_message):
        # Step 1: Get the current market prices
        summery_lines = self.give_summary_lines()
        # Step 2: Get user data
        user_data = self.fetch_user_data()
        # Step 3: Create the prompt
        self.model.generate_content(user_message + "User profile: " + json.dumps(user_data) + "Below is a summary of 100 low-risk stock candidates: " +summery_lines)        