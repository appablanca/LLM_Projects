import React, { createContext, useRef, useEffect, useState } from "react";

export const WebSocketContext = createContext(null);

const WS_URL = "ws://localhost:8081";

export const WebSocketProvider = ({ children }) => {
  const ws = useRef(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!ws.current) {
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        console.log("WebSocket connected");
        setConnected(true);
      };

      ws.current.onclose = () => {
        console.log("WebSocket disconnected");
        setConnected(false);
      };

      ws.current.onerror = (err) => {
        console.error("WebSocket error:", err);
      };
    }

    return () => {
      // Bağlantı asla kapanmasın, yorumlu bırak:
      // ws.current?.close();
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ ws: ws.current, connected }}>
      {children}
    </WebSocketContext.Provider>
  );
};