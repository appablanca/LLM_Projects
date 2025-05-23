const WebSocket = require("ws");

const finnhubUrl = "wss://ws.finnhub.io?token=d0o8kghr01qu2361497gd0o8kghr01qu23614980";
const server = new WebSocket.Server({ port: 8081 });

// Shared Finnhub WebSocket connection
const finnhubSocket = new WebSocket(finnhubUrl);

const clients = new Set();
const subscribedSymbols = new Set();

finnhubSocket.on("open", () => {
  console.log("Connected to Finnhub WebSocket");
});

finnhubSocket.on("message", (data) => {
  try {
    const json = JSON.parse(data);
    if (Array.isArray(json.data)) {
      for (const client of clients) {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(json.data));
        }
      }
    }
  } catch (e) {
    console.error("Error parsing message from Finnhub:", e);
  }
});

finnhubSocket.on("error", (err) => {
  console.error("Finnhub WebSocket error:", err.message);
});

server.on("connection", (clientSocket) => {
  console.log("Frontend WebSocket connected");
  clients.add(clientSocket);

  clientSocket.on("message", (msg) => {
    try {
      const { type, symbols } = JSON.parse(msg);
      if (type === "subscribe" && Array.isArray(symbols)) {
        symbols.forEach((symbol) => {
          if (!subscribedSymbols.has(symbol)) {
            subscribedSymbols.add(symbol);
            finnhubSocket.send(JSON.stringify({ type: "subscribe", symbol }));
          }
        });
      }
    } catch (e) {
      console.error("Error parsing message from frontend:", e);
    }
  });

  clientSocket.on("close", () => {
    clients.delete(clientSocket);
  });

  clientSocket.on("error", () => {
    clients.delete(clientSocket);
  });
});

module.exports = { server };