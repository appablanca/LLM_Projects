from agents.baseAgent import Agent
import os


investmentAdvisorAgentRole = f"""


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
        closes = [day["close"] for day in symbol_data["data"]]
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