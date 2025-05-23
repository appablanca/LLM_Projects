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

/**
 * @swagger
 * /generator/resolveNewsUrl:
 *   get:
 *     summary: Resolve the final URL after following redirects
 *     tags: [Generator]
 *     parameters:
 *       - in: query
 *         name: url
 *         schema:
 *           type: string
 *         required: true
 *         description: The URL to resolve
 *     responses:
 *       200:
 *         description: Successfully resolved the final URL
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 finalUrl:
 *                   type: string
 *       400:
 *         description: Invalid URL provided
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 message:
 *                   type: string
 *       500:
 *         description: Failed to resolve the URL
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 message:
 *                   type: string
 */
router.post("/getStockData", generatorController.getStockData);

router.get("/createExtraMetadata", generatorController.createExtraMetadata);

router.get("/getAllStocks", generatorController.getAllStocks);

router.get("/resolveNewsUrl", generatorController.resolveNewsUrl);

module.exports = router;