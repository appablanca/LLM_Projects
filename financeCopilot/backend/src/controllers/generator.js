const fs = require("fs");
const path = require("path");
const axios = require("axios");
const Stock = require("../models/stockInfo");
// TWELVE_DATA_API_KEY= "39047c1681c8452ba5b4fda546541a10" //femp
// TWELVE_DATA_API_KEY= "8df44756db4c4d379ab253b05fefc6da" //feyzieren
TWELVE_DATA_API_KEY= "355b0b5039e14dbf87a85a61e7a44715" //feyzibattle
// TWELVE_DATA_API_KEY= "13a55b9967904dc6b7dedf185b986648" //20feyzi02

const BASE_URL = "https://api.twelvedata.com/time_series";

exports.fetchAllStocksFromFile = async (req, res) => {
  const symbolsPath = path.join(__dirname, "/sp500_symbols.txt");

  let symbols;
  try {
    const fileData = fs.readFileSync(symbolsPath, "utf8");
    // symbols = fileData.split("\n").map(line => line.trim()).filter(line => line);
    symbols = fileData.split(/\r?\n/).map(line => line.trim()).filter(line => line);

  } catch (err) {
    console.error("Error reading symbols.txt:", err);
    return res.status(500).json({ message: "Failed to read symbol list." });
  }

  const results = [];

  for (const symbol of symbols) {
    try {

        const existingStock = await Stock
            .findOne({ symbol})
            .select("symbol")
            .lean();
        if (existingStock) {
            results.push({ symbol, status: "Already exists" });
            continue;
        }

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
          type: 0, 
          deleted: 0,
        });
      }

      await stockDoc.save();
      console.log(`Data for ${symbol} saved successfully.`);
      results.push({ symbol, status: "Saved", entries: formattedData.length });
    } catch (err) {
      console.error(`Error for symbol ${symbol}:`, err.response?.data || err.message);
      results.push({ symbol, status: "Error", message: err.message });
    }
  }
  console.log("---------------------------");
  return res.status(200).json({message: "Data fetched successfully"});
};


exports.getStockData = async (req, res) => {
  const { symbol } = req.body;

  try {
    const stockData = await Stock.findOne({ symbol, deleted: 0, type: 0 })
      .select("symbol data type deleted")
      .lean();
    if (!stockData) {
      return res.status(404).json({ message: "Stock not found" });
    }
    // Only include non-deleted entries
    const filteredData = (stockData.data || []).filter(entry => entry.deleted === 0);
    const formattedData = filteredData.map((entry) => ({
      date: entry.date,
      open: entry.open,
      high: entry.high,
      low: entry.low,
      close: entry.close,
      volume: entry.volume,
    }));
    return res.status(200).json({
      symbol: stockData.symbol,
      type: stockData.type,
      data: formattedData
    });
  } catch (err) {
    console.error("Error fetching stock data:", err);
    return res.status(500).json({ message: "Failed to fetch stock data" });
  }
};

exports.fetchStockDataFromAPI = async (req, res) => {
  const { symbol } = req.body;

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
      return res.status(404).json({ message: "No data returned" });
    }

    // Format data according to schema (include deleted: 0)
    const formattedData = symbolData.values.map((entry) => ({
      date: new Date(entry.datetime),
      open: parseFloat(entry.open),
      high: parseFloat(entry.high),
      low: parseFloat(entry.low),
      close: parseFloat(entry.close),
      volume: parseFloat(entry.volume),
      deleted: 0,
    }));

    // Upsert stock document according to schema
    let stockDoc = await Stock.findOne({ symbol });
    if (stockDoc) {
      stockDoc.data = formattedData;
      stockDoc.type = 0;
      stockDoc.deleted = 0;
    } else {
      stockDoc = new Stock({
        symbol,
        data: formattedData,
        type: 0,
        deleted: 0,
      });
    }
    await stockDoc.save();

    return res.status(200).json({
      symbol,
      type: stockDoc.type,
      data: formattedData,
    });
  } catch (err) {
    console.error("Error fetching stock data:", err);
    return res.status(500).json({ message: "Failed to fetch stock data" });
  }
};