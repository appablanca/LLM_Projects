import React, { useEffect, useState, useContext, useRef } from "react";
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  useTheme,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { getUserStocks, getStockQuote } from "../../util/api";
import { tokens } from "../../theme";
import { WebSocketContext } from "../../context/WebSocketContext";

const Invesment = () => {
  const [trackedStocks, setTrackedStocks] = useState([]);
  const livePricesRef = useRef({});
  const priceFlashMap = useRef({});
  const previousClosesRef = useRef({});
  const [, forceUpdate] = useState(0);
  const { ws, connected } = useContext(WebSocketContext);
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  useEffect(() => {
    fetchTrackedStocks();
  }, []);

  const fetchTrackedStocks = async () => {
    try {
      const response = await getUserStocks();
      setTrackedStocks((response || []).map(item => item.content));
      // Populate previous close prices for each symbol
      for (const symbol of (response || []).map(item => item.content)) {
        try {

          const quote = await getStockQuote(symbol);
          console.log("Fetched quote for", symbol, quote);
          previousClosesRef.current[symbol] = quote?.pc;
        } catch (err) {
          console.error("Failed to fetch quote for", symbol, err);
        }
      }
    } catch (error) {
      console.error("Failed to fetch tracked stocks:", error);
    }
  };
  const getFormattedPriceDisplay = (symbol) => {
    const current = livePricesRef.current[symbol];
    const prev = previousClosesRef.current[symbol];
    if (current === undefined || prev === undefined) return "Fiyat bekleniyor...";

    const diff = current - prev;
    const pct = ((diff / prev) * 100).toFixed(2);
    const prefix = diff > 0 ? "▲" : diff < 0 ? "▼" : "—";
    const color = diff > 0 ? colors.greenAccent[300] : diff < 0 ? colors.redAccent[300] : colors.grey[300];

    const flash = priceFlashMap.current[symbol];
    const flashColor =
      flash?.visible && flash.direction === "up"
        ? "rgba(0, 255, 0, 0.5)"
        : flash?.visible && flash.direction === "down"
        ? "rgba(255, 0, 0, 0.5)"
        : "transparent";

    return (
      <>
        <Typography
          variant="h6"
          sx={{
            color: colors.grey[100],
            fontWeight: "bold",
            transition: "background-color 0.3s",
            backgroundColor: flashColor,
            borderRadius: "4px",
            px: 0.5,
          }}
        >
          ${current.toFixed(2)}
        </Typography>
        <Typography variant="body2" sx={{ color }}>
          {prefix} {Math.abs(pct)}% ({diff >= 0 ? "+" : ""}${Math.abs(diff).toFixed(2)})
        </Typography>
      </>
    );
  };

  useEffect(() => {
    if (connected && trackedStocks.length > 0 && ws) {
      ws.send(JSON.stringify({ type: "subscribe", symbols: trackedStocks }));
    }
  }, [connected, trackedStocks]);

  useEffect(() => {
    if (!ws) return;
    const handleMessage = (event) => {
      try {
        const updates = JSON.parse(event.data);
        console.log("WebSocket message received:", updates);
        const latestPrices = {};
        updates.forEach((entry) => {
          if (entry.s && entry.p !== undefined) {
            const prev = livePricesRef.current[entry.s];
            latestPrices[entry.s] = entry.p;

            if (prev !== undefined && prev !== entry.p) {
              const direction = entry.p > prev ? "up" : "down";
              let flashCount = 0;
              const flashInterval = setInterval(() => {
                flashCount += 1;
                priceFlashMap.current[entry.s] = { direction, visible: flashCount % 2 === 1 };
                forceUpdate((n) => n + 1);
                if (flashCount >= 6) {
                  clearInterval(flashInterval);
                  priceFlashMap.current[entry.s] = null;
                  forceUpdate((n) => n + 1);
                }
              }, 500);
            }
          }
        });
        livePricesRef.current = { ...livePricesRef.current, ...latestPrices };
        forceUpdate((n) => n + 1);
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };
    ws.addEventListener("message", handleMessage);
    return () => {
      ws.removeEventListener("message", handleMessage);
    };
  }, [ws]);


  return (
    <Box m="20px">
      <Typography variant="h4" gutterBottom sx={{ color: colors.grey[800] }}>
        Tracked Stocks
      </Typography>
      {trackedStocks.length === 0 ? (
        <Typography sx={{ color: colors.grey[300] }}>
          No tracked stocks found.
        </Typography>
      ) : (
        <List>
          {trackedStocks.map((symbol) => (
            <ListItem
              sx={{
                backgroundColor: colors.primary[700],
                borderRadius: 2,
                mb: 2,
                p: 2,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
              }}
              key={symbol}
            >
              <Box>
                <Typography variant="subtitle2" sx={{ color: colors.greenAccent[400], fontWeight: 600 }}>
                  {symbol}
                </Typography>
                {getFormattedPriceDisplay(symbol)}
              </Box>
              <IconButton edge="end">
                <DeleteIcon sx={{ color: colors.redAccent[400] }} />
              </IconButton>
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
};

export default Invesment;