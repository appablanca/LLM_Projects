const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const stockEntrySchema = new Schema({
  date: {
    type: Date,
    required: true,
  },
  open: {
    type: Number,
    required: true,
  },
  high: {
    type: Number,
    required: true,
  },
  low: {
    type: Number,
    required: true,
  },
  close: {
    type: Number,
    required: true,
  },
  volume: {
    type: Number,
    required: true,
  },
  deleted: {
    type: Number,
    default: 0,
    required: true,
  },
});

const stockInfoSchema = new Schema({
  symbol: {
    type: String,
    required: true,
  },
  data: {
    type: [stockEntrySchema],
    default: [],
  },
  type: {
    type: Number, // 0 for stock, 1 for crypto
    required: true,
  },
  volatility: {
    type: Number,
    default: 0,
  },
  growth_pct: {
    type: Number,
    default: 0,
  },
  avg_close: {
    type: Number,
    default: 0,
  },
  min_close: {
    type: Number,
    default: 0,
  },
  max_close: {
    type: Number,
    default: 0,
  },
  deleted: {
    type: Number,
    default: 0,
    required: true,
  },
});

module.exports = mongoose.model("stockInfo", stockInfoSchema);