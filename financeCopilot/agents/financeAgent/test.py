import time
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

def chunk_list(lst, size):
    """Split list into chunks of given size."""
    return [lst[i:i + size] for i in range(0, len(lst), size)]

def get_latest_prices_batched(file_path: str, batch_size=10, max_workers=10):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]

    results = []

    def fetch_batch_price(batch):
        try:
            data = yf.download(
                tickers=" ".join(batch),
                period="1d",
                interval="1m",
                auto_adjust=False,
                progress=False,
                threads=False
            )
            output = []
            for symbol in batch:
                try:
                    price = data['Close'][symbol].dropna().iloc[-1]
                    output.append(f"{symbol}: {price:.2f} $")
                except Exception:
                    output.append(f"{symbol}: Price not available")
            return output
        except Exception as e:
            return [f"{symbol}: Error ({str(e)})" for symbol in batch]

    batches = chunk_list(symbols, batch_size)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_batch_price, batch): batch for batch in batches}
        for future in as_completed(futures):
            results.extend(future.result())

    return results

# Measure execution time
start_time = time.time()
get_latest_prices_batched("sp500_symbols.txt", batch_size=10, max_workers=10)
end_time = time.time()



print(f"\nExecution Time: {end_time - start_time:.2f} seconds")
