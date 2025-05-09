import pandas as pd

def save_sp500_symbols_to_file(filename="sp500_symbols.txt"):
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    symbols = df['Symbol'].tolist()

    # Optional: clean up symbols like 'BRK.B' to 'BRK-B' for API compatibility
    cleaned_symbols = [s.replace('.', '-') for s in symbols]

    with open(filename, "w") as f:
        for symbol in cleaned_symbols:
            f.write(symbol + "\n")

    print(f"✅ Saved {len(cleaned_symbols)} S&P 500 symbols to {filename}")

save_sp500_symbols_to_file()