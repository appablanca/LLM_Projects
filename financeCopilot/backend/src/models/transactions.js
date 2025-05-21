const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  amount: {
    type: String,
    required: true
  },
  date: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  flow: {
    type: String,
    enum: ['spending', 'income'],
    required: true
  },
  spendingCategory: {
    type: String,
    required: true
  },
  embeddings:{
    type: Object,
    default: {}
  }
});

const categorySpendingSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  categoryTotals: {
    bill_payment: String,
    clothing_cosmetics: String,
    entertainment: String,
    food_drinks: String,
    groceries: String,
    other: String,
    transportation: String
  },
  cardLimit: {
    remaining_card_limit: String,
    total_card_limit: String
  },
  date: {
    type: Date,
    default: Date.now
  }
});

const Transaction = mongoose.model('Transaction', transactionSchema);
const CategorySpending = mongoose.model('CategorySpending', categorySpendingSchema);

module.exports = {
  Transaction,
  CategorySpending
}; 