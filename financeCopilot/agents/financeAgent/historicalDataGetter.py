import requests
import json

def read_symbols(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def fetch_all_stock_data(symbols):
    url = "http://localhost:8080/generator/getStockData"
    historical_data = []
    missing_symbols = []

    for symbol in symbols:
        try:
            response = requests.post(url, json={"symbol": symbol})
            if response.status_code == 200:
                data = response.json()
                historical_data.append(data)
            else:
                missing_symbols.append(symbol)
        except requests.exceptions.RequestException:
            missing_symbols.append(symbol)

    return historical_data, missing_symbols

IP = ["IP"]
historicalData, missingSymbols = fetch_all_stock_data(IP)

# Save the data to a JSON file named historical_data
with open("historical_data1.json", "w") as f:
    json.dump(historicalData, f, indent=2)
