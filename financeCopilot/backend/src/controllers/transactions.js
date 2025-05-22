const { Transaction, CategorySpending } = require('../models/transactions');
const User = require("../models/users");
const axios = require("axios");

exports.saveTransactionsAndSpending = async (req, res) => {
  try {
    // Check if user is authenticated
    if (!req.session.user || !req.session.user.id) {
      return res.status(401).json({
        success: false,
        message: 'User not authenticated'
      });
    }

    const userId = req.session.user.id;

    // Verify user exists
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const { transactions, category_totals, card_limit } = req.body;

    // Validate request body
    if (!transactions || !Array.isArray(transactions) || transactions.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid transactions data'
      });
    }

    if (!category_totals || typeof category_totals !== 'object') {
      return res.status(400).json({
        success: false,
        message: 'Invalid category totals data'
      });
    }

    // Check for duplicate transactions
    const existingTransactions = await Transaction.find({
      userId,
      $or: transactions.map(transaction => ({
        amount: transaction.amount,
        date: transaction.date,
        description: transaction.description
      }))
    });

    // Create a map of existing transactions for quick lookup
    const existingTransactionMap = new Map(
      existingTransactions.map(t => [
        `${t.amount}-${t.date}-${t.description}`,
        t
      ])
    );

    // Filter out duplicate transactions
    const newTransactions = transactions.filter(transaction => {
      const key = `${transaction.amount}-${transaction.date}-${transaction.description}`;
      return !existingTransactionMap.has(key);
    });

    if (newTransactions.length === 0) {
      return res.status(200).json({
        success: true,
        message: 'No new transactions to save',
        skipped: transactions.length
      });
    }

    // Save new transactions
    const transactionPromises = newTransactions.map(async (transaction) => {
      try {
        const response = await axios.post("http://localhost:5001/embeddings", {
          text: `${transaction.description} | ${transaction.amount} | ${transaction.flow}`
        });
        console.log(response)

        const embedding = response.data?.embeddings || [];

        return new Transaction({
          userId,
          amount: transaction.amount,
          date: transaction.date,
          description: transaction.description,
          flow: transaction.flow,
          spendingCategory: transaction.spending_category,
          embeddings: embedding // Save it in MongoDB
        }).save();

      } catch (err) {
        console.error("Embedding generation failed for transaction:", transaction.description, err.message);
        // Save transaction without embedding if it fails
        return new Transaction({
          userId,
          amount: transaction.amount,
          date: transaction.date,
          description: transaction.description,
          flow: transaction.flow,
          spendingCategory: transaction.spending_category,
          embeddings: [] // Empty fallback
        }).save();
      }
    });

    // Save category spending
    const categorySpending = new CategorySpending({
      userId,
      categoryTotals: category_totals,
      cardLimit: card_limit
    });

    // Execute all database operations
    await Promise.all([...transactionPromises, categorySpending.save()]);

    res.status(200).json({
      success: true,
      message: 'Transactions and spending data saved successfully',
      saved: newTransactions.length,
      skipped: transactions.length - newTransactions.length
    });

  } catch (error) {
    console.error('Error saving transactions and spending:', error);
    res.status(500).json({
      success: false,
      message: 'Error saving transactions and spending data',
      error: error.message
    });
  }
};

exports.getTransactionsAndSpending = async (req, res) => {
  try {
    let userId = req.query.userId;
    // Check if user is authenticated
    // If userId is not provided in the query, use the session userId
    if (!userId) {
      if (!req.session || !req.session.user) {
        return res.status(401).json({
          success: false,
          message: 'User not authenticated'
        });
      }
      userId = req.session.user.id;
    }
    
    // Verify user exists
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Get latest category spending
    const latestSpending = await CategorySpending.findOne({ userId })
      .sort({ date: -1 })
      .lean();

    // Get all transactions
    const transactions = await Transaction.find({ userId })
      .sort({ date: -1 })
      .lean();

    res.status(200).json({
      success: true,
      data: {
        category_totals: latestSpending?.categoryTotals || {},
        card_limit: latestSpending?.cardLimit || {},
        transactions: transactions || []
      }
    });

  } catch (error) {
    console.error('Error fetching transactions and spending:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching transactions and spending data',
      error: error.message
    });
  }
};