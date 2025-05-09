import aiohttp
import asyncio
import time

YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="

async def fetch_price_batch(session, batch):
    url = YAHOO_QUOTE_URL + ",".join(batch)
    try:
        async with session.get(url) as resp:
            json_data = await resp.json()
            results = []
            for quote in json_data["quoteResponse"]["result"]:
                symbol = quote.get("symbol")
                price = quote.get("regularMarketPrice")
                if symbol and price is not None:
                    results.append(f"{symbol}: {price:.2f} $")
                else:
                    results.append(f"{symbol or 'Unknown'}: Price not available")
            return results
    except Exception as e:
        return [f"{symbol}: Error ({str(e)})" for symbol in batch]

async def get_latest_prices_async(file_path: str, batch_size=10):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]

    batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price_batch(session, batch) for batch in batches]
        all_results = await asyncio.gather(*tasks)
        for result in all_results:
            results.extend(result)

    return results

# Wrapper to run the async function
def run_fetch_prices(file_path: str, batch_size=10):
    start_time = time.time()
    results = asyncio.run(get_latest_prices_async(file_path, batch_size))
    end_time = time.time()

    for r in results:
        print(r)
    print(f"\nExecution Time: {end_time - start_time:.2f} seconds")

# Run the code
run_fetch_prices("sp500_symbols.txt", batch_size=10)
