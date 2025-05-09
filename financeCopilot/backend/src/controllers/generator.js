const fs = require("fs");
const path = require("path");
const axios = require("axios");
const Stock = require("../models/stockInfo");

const TWELVE_DATA_API_KEY = process.env.TWELVE_DATA_API_KEY;
const BASE_URL = "https://api.twelvedata.com/time_series";

exports.fetchAllStocksFromFile = async (req, res) => {
  const symbolsPath = path.join(__dirname, "/sp500_symbols.txt");

  let symbols;
  try {
    const fileData = fs.readFileSync(symbolsPath, "utf8");
    symbols = fileData.split("\n").map(line => line.trim()).filter(line => line);
  } catch (err) {
    console.error("Error reading symbols.txt:", err);
    return res.status(500).json({ message: "Failed to read symbol list." });
  }

  const results = [];

  for (const symbol of symbols) {
    try {
      const response = await axios.get(BASE_URL, {
        params: {
          symbol: symbol,
          interval: "1week",
          outputsize: 52,
          apikey: TWELVE_DATA_API_KEY,
        },
      });

      const symbolData = response.data;

      if (!symbolData || !Array.isArray(symbolData.values)) {
        results.push({ symbol, status: "No data returned" });
        continue;
      }

      const formattedData = symbolData.values.map((entry) => ({
        date: new Date(entry.datetime),
        open: parseFloat(entry.open),
        high: parseFloat(entry.high),
        low: parseFloat(entry.low),
        close: parseFloat(entry.close),
        volume: parseFloat(entry.volume),
        deleted: 0,
      }));

      let stockDoc = await Stock.findOne({ symbol });

      if (stockDoc) {
        stockDoc.data.push(...formattedData);
      } else {
        stockDoc = new Stock({
          symbol,
          data: formattedData,
          deleted: 0,
        });
      }

      await stockDoc.save();
      results.push({ symbol, status: "Saved", entries: formattedData.length });
    } catch (err) {
      console.error(`Error for symbol ${symbol}:`, err.response?.data || err.message);
      results.push({ symbol, status: "Error", message: err.message });
    }
  }

  return res.status(200).json({
    message: "Weekly stock data processing completed.",
    summary: results,
  });
};