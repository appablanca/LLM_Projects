const express = require('express');
const router = express.Router();
const transactionsController  = require('../controllers/transactions');

/**
 * @swagger
 * tags:
 *   name: Transactions
 *   description: Transaction and spending data management
 * 
 * components:
 *   schemas:
 *     Transaction:
 *       type: object
 *       required:
 *         - amount
 *         - date
 *         - description
 *         - flow
 *         - spending_category
 *       properties:
 *         amount:
 *           type: string
 *           example: "195,00 TL"
 *           description: Transaction amount in Turkish Lira
 *         date:
 *           type: string
 *           example: "07.05.2025"
 *           description: Transaction date in DD.MM.YYYY format
 *         description:
 *           type: string
 *           example: "SATIŞ-517040*7261-PAPARA/PAPARA/ADAL G"
 *           description: Transaction description
 *         flow:
 *           type: string
 *           enum: [spending, income]
 *           example: "spending"
 *           description: Transaction type
 *         spending_category:
 *           type: string
 *           example: "other"
 *           description: Category of the spending
 * 
 *     CategoryTotals:
 *       type: object
 *       properties:
 *         bill_payment:
 *           type: string
 *           example: "1.722,20 TL"
 *         clothing_cosmetics:
 *           type: string
 *           example: "201,06 TL"
 *         entertainment:
 *           type: string
 *           example: "280,00 TL"
 *         food_drinks:
 *           type: string
 *           example: "2.843,00 TL"
 *         groceries:
 *           type: string
 *           example: "489,90 TL"
 *         other:
 *           type: string
 *           example: "2.238,89 TL"
 *         transportation:
 *           type: string
 *           example: "1.347,50 TL"
 * 
 *     CardLimit:
 *       type: object
 *       properties:
 *         remaining_card_limit:
 *           type: string
 *           example: "5.000,00 TL"
 *           nullable: true
 *         total_card_limit:
 *           type: string
 *           example: "10.000,00 TL"
 *           nullable: true
 * 
 *     SaveTransactionsRequest:
 *       type: object
 *       required:
 *         - transactions
 *         - category_totals
 *         - card_limit
 *       properties:
 *         transactions:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/Transaction'
 *         category_totals:
 *           $ref: '#/components/schemas/CategoryTotals'
 *         card_limit:
 *           $ref: '#/components/schemas/CardLimit'
 * 
 *     SaveTransactionsResponse:
 *       type: object
 *       properties:
 *         success:
 *           type: boolean
 *           example: true
 *         message:
 *           type: string
 *           example: "Transactions and spending data saved successfully"
 * 
 *     GetTransactionsResponse:
 *       type: object
 *       properties:
 *         success:
 *           type: boolean
 *           example: true
 *         data:
 *           type: object
 *           properties:
 *             category_totals:
 *               $ref: '#/components/schemas/CategoryTotals'
 *             card_limit:
 *               $ref: '#/components/schemas/CardLimit'
 *             transactions:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Transaction'
 */

/**
 * @swagger
 * /transactions/saveTransactionsAndSpending:
 *   post:
 *     tags: [Transactions]
 *     summary: Save transactions and spending data
 *     description: Save user transactions and category spending data
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/SaveTransactionsRequest'
 *     responses:
 *       200:
 *         description: Successfully saved transactions and spending data
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/SaveTransactionsResponse'
 *       401:
 *         description: User not authenticated
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: false
 *                 message:
 *                   type: string
 *                   example: "User not authenticated"
 *       500:
 *         description: Server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: false
 *                 message:
 *                   type: string
 *                   example: "Error saving transactions and spending data"
 *                 error:
 *                   type: string
 *                   example: "Error message details"
 */
router.post('/saveTransactionsAndSpending', transactionsController.saveTransactionsAndSpending);

/**
 * @swagger
 * /transactions/getTransactionsAndSpending:
 *   get:
 *     tags: [Transactions]
 *     parameters:
 *       - in: query
 *         name: userId
 *         schema:
 *           type: string
 *     summary: Get transactions and spending data
 *     description: Retrieve user's transactions and category spending data
 *     responses:
 *       200:
 *         description: Successfully retrieved transactions and spending data
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/GetTransactionsResponse'
 *       401:
 *         description: User not authenticated
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: false
 *                 message:
 *                   type: string
 *                   example: "User not authenticated"
 *       500:
 *         description: Server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: false
 *                 message:
 *                   type: string
 *                   example: "Error fetching transactions and spending data"
 *                 error:
 *                   type: string
 *                   example: "Error message details"
 */
router.get('/getTransactionsAndSpending', transactionsController.getTransactionsAndSpending);

module.exports = router; 