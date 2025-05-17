const express = require('express');
const router = express.Router();
const generatorController = require('../controllers/generator');


router.get("/fetchAllStocksFromFile", generatorController.fetchAllStocksFromFile);

/**
 * @swagger
 * /generator/getStockData:
 *   post:
 *     summary: Get stock data by symbol
 *     tags: [Generator]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               symbol:
 *                 type: string
 *             required:
 *               - symbol
 *     responses:
 *       200:
 *         description: Stock data retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 symbol:
 *                   type: string
 *                 data:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       date:
 *                         type: string
 *                         format: date
 *                       open:
 *                         type: number
 *                       high:
 *                         type: number
 *                       low:
 *                         type: number
 *                       close:
 *                         type: number
 *                       volume:
 *                         type: number
 *       404:
 *         description: Stock not found
 *       500:
 *         description: Failed to fetch stock data
 */
router.post("/getStockData", generatorController.getStockData);

module.exports = router;