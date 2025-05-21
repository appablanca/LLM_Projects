import os
import json
import finnhub
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta


class NewsAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.finnhub_api_key = os.getenv("finhub_api_key")

        self.generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        self.role = """
You are a professional financial analyst AI.
You will receive a list of recent stock news articles.
Return a structured JSON with:
- "overview": a concise summary of the overall sentiment and themes,
- "key_trends": recurring themes or topics,
- "market_impacts": effects on stock price or investor perception,
- "opportunities": any favorable developments for investors,
- "risks": potential negative signals or red flags.
After creating the JSON add another field called "URL" and populate with the URL of the news article.
Include top 10 relevant news article URLs in the "URL" field as a list of strings.
The JSON should be formatted as follows:
{
  "overview": "...",
  "key_trends": ["..."],
  "market_impacts": ["..."],
  "opportunities": ["..."],
  "risks": ["..."],
  "URL": ["...", "..."]
}
The JSON should be valid and well-structured.

"""

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=self.generation_config,
            system_instruction=self.role,
        )

        self.finnhub_client = finnhub.Client(api_key=self.finnhub_api_key)

    def fetch_top_news(self, symbol: str, limit: int = 30):
        today = datetime.now()
        last_week = today - timedelta(weeks=1)
        today_fmt = today.strftime("%Y-%m-%d")
        last_week_fmt = last_week.strftime("%Y-%m-%d")

        news = self.finnhub_client.company_news(symbol, _from=last_week_fmt, to=today_fmt)[:limit]
        structured_news = []
        for item in news:
            date = datetime.fromtimestamp(item['datetime']).strftime('%Y-%m-%d')
            structured_news.append({
                "headline": item['headline'],
                "date": date,
                "source": item['source'],
                "summary": item.get("summary", ""),
                "url": item['url']
            })
        return structured_news, last_week_fmt, today_fmt

    def analyze_news(self, symbol: str):
        news_list, start_date, end_date = self.fetch_top_news(symbol)
        company_name = symbol.upper()  # Optionally map to full name if desired

        prompt = f"""
Analyze the following {len(news_list)} news articles for {company_name} from {start_date} to {end_date}.

Return a JSON object with:
{{
  "overview": "...",
  "key_trends": ["..."],
  "market_impacts": ["..."],
  "opportunities": ["..."],
  "risks": ["..."]
}}

News articles:
{json.dumps(news_list, indent=2)}
"""

        response = self.model.generate_content(prompt)

        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            print(f"\n⚠️ Gemini response for {symbol} is not valid JSON:\n")
            print(response.text)
            return None
        
if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    symbol = "KO"  # Example stock symbol
    result = analyzer.analyze_news(symbol)
    