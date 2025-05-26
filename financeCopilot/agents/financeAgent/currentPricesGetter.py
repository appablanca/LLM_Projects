from flask import Flask, jsonify
import time
import yfinance as yf
import asyncio
import httpx

app = Flask(__name__)
FINNHUB_API_KEY = "d0mpdvhr01qi78ngcl50d0mpdvhr01qi78ngcl5g"

def get_current_market_prices_fast(file_path: str):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]

    data = yf.download(
        tickers=" ".join(symbols),
        period="1d",
        interval="1m",  
        group_by="ticker",
        # threads=True,
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

async def fetch_quote(session, symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = await session.get(url, timeout=5.0)
        response.raise_for_status()
        data = response.json()
        price = data.get("c")
        return f"{symbol}: {price:.2f} $" if price else f"{symbol}: Price not available"
    except Exception:
        return f"{symbol}: Price not available"

async def get_current_market_prices_finnhub_async(file_path: str):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]

    async with httpx.AsyncClient() as client:
        tasks = [fetch_quote(client, symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

@app.route("/market-prices", methods=["GET"])
def fetch_market_prices():
    start = time.time()
    prices = get_current_market_prices_fast("sp500_symbols.txt")
    elapsed = time.time() - start

    with open("market_prices_output.txt", "w") as f:
        for p in prices:
            f.write(p + "\n")
        f.write(f"\nExecution Time: {elapsed:.2f} seconds\n")

    return jsonify({"status": "success", "method": "yfinance", "execution_time": elapsed}), 200

@app.route("/market-prices-finnhub", methods=["GET"])
def fetch_market_prices_finnhub():
    start = time.time()
    prices = asyncio.run(get_current_market_prices_finnhub_async("sp500_symbols.txt"))
    elapsed = time.time() - start

    with open("market_prices_finnhub_output.txt", "w") as f:
        for p in prices:
            f.write(p + "\n")
        f.write(f"\nExecution Time: {elapsed:.2f} seconds\n")

    return jsonify({"status": "success", "method": "finnhub-async", "execution_time": elapsed}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5050)