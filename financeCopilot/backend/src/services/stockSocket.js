const WebSocket = require('ws');

function startWebSocketClient() {
  const socket = new WebSocket('wss://ws.finnhub.io?token=d0mpdvhr01qi78ngcl50d0mpdvhr01qi78ngcl5g');

  socket.on('open', () => {
    console.log('WebSocket connected');
    socket.send(JSON.stringify({ type: 'subscribe', symbol: 'AAPL' }));
    socket.send(JSON.stringify({ type: 'subscribe', symbol: 'AMZN' }));
    socket.send(JSON.stringify({ type: 'subscribe', symbol: 'KO' }));
  });

  socket.on('message', (data) => {
  try {
    const json = JSON.parse(data.toString()); // Convert buffer to JSON
    const entries = json.data;

    if (Array.isArray(entries)) {
      entries.forEach(entry => {
        const symbol = entry.s;
        const price = entry.p;
        console.log(`Symbol: ${symbol}, Price: ${price}`);
      });
    }
  } catch (err) {
    console.error('Failed to parse WebSocket message:', err);
  }
});

  socket.on('error', (err) => {
    console.error('WebSocket error:', err);
  });

  socket.on('close', () => {
    console.log('WebSocket closed. Reconnecting...');
    setTimeout(startWebSocketClient, 5000); // Optional: auto-reconnect
  });
}

module.exports = { startWebSocketClient };
