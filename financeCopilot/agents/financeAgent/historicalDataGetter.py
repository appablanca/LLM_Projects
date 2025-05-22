import requests
import json

def fetch_all_stock_data():
    url = "http://localhost:8080/generator/getAllStocks"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []

if __name__ == "__main__":
    stock_data = fetch_all_stock_data()

    with open("historical_data.json", "w") as f:
        json.dump(stock_data, f, indent=2)

    print(f"✅ Saved {len(stock_data)} stocks to historical_data.json")