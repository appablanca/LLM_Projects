import time
import yfinance as yf

def get_latest_prices_serial(file_path: str, output_file: str = "latest_prices.txt"):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]

    results = []

    for symbol in symbols:
        try:
            data = yf.download(
                tickers=symbol,
                period="5d",         # biraz daha uzun alalım ki veri olsun
                interval="1d",
                auto_adjust=False,
                progress=False
            )

            if not data.empty:
                price = data['Close'].dropna().iloc[-1]
                results.append(f"{symbol}: {price:.2f} $")
            else:
                results.append(f"{symbol}: No data available")
        except Exception as e:
            results.append(f"{symbol}: Error ({str(e)})")

    # Dosyaya yaz
    with open(output_file, "w") as f:
        for result in results:
            f.write(result + "\n")

    return results

# Zaman ölçümü
start_time = time.time()
get_latest_prices_serial("sp500_symbols.txt")
end_time = time.time()
print(f"\nExecution Time: {end_time - start_time:.2f} seconds")