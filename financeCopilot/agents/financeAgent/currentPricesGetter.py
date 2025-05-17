from flask import Flask, jsonify
import time
import yfinance as yf

app = Flask(__name__)

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

@app.route("/market-prices", methods=["GET"])
def fetch_market_prices():
    start = time.time()
    prices = get_current_market_prices_fast("sp500_symbols.txt")
    elapsed = time.time() - start

    output_file = "market_prices_output.txt"
    with open(output_file, "w") as f:
        for p in prices:
            f.write(p + "\n")
        f.write(f"\nExecution Time: {elapsed:.2f} seconds\n")

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5050)