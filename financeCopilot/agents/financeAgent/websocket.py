import websocket
import json

API_KEY = "355b0b5039e14dbf87a85a61e7a44715"
URL = f"wss://ws.twelvedata.com/v1/quotes/price?apikey={API_KEY}"

def on_open(ws):
    symbols = input("Enter up to 8 symbols (e.g., AAPL,MSFT,NVDA): ").upper().split(",")
    if len(symbols) > 8:
        print("⚠️ Max 8 symbols allowed")
        ws.close()
        return

    subscribe_msg = {
        "action": "subscribe",
        "params": {
            "symbols": ",".join(symbols)
        }
    }
    ws.send(json.dumps(subscribe_msg))
    print("✅ Subscribed to:", symbols)

def on_message(ws, message):
    data = json.loads(message)
    print(f"{data.get('symbol')}: {data.get('price')}")

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws, *args):
    print("🔌 WebSocket closed")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()