const express = require('express');
const router = express.Router();
const multer = require('multer');
const copilotController = require('../controllers/copilot');
const swaggerJSDoc = require('swagger-jsdoc');

/**
 * @swagger
 * components:
 *   schemas:
 *     ChatResponse:
 *       type: object
 *       properties:
 *         success:
 *           type: boolean
 *           description: Indicates if the request was successful
 *         response:
 *           type: object
 *           description: The response data from the copilot
 *         message:
 *           type: string
 *           description: Error message if success is false
 *         error:
 *           type: string
 *           description: Detailed error information if an exception occurred
 * 
 *     ChatRequest:
 *       type: object
 *       properties:
 *         message:
 *           type: string
 *           description: The message to send to the copilot
 * 
 * /copilot/chat:
 *   post:
 *     summary: Send a message or file to the Finance Copilot
 *     description: |
 *       This endpoint allows you to:
 *       - Send a text message to the Finance Copilot
 *       - Upload a PDF file for expense analysis
 *       - Send both a message and a file
 *     tags:
 *       - Finance Copilot
 *     requestBody:
 *       required: true
 *       content:
 *         multipart/form-data:
 *           schema:
 *             type: object
 *             properties:
 *               message:
 *                 type: string
 *                 description: The message to send to the copilot
 *               file:
 *                 type: string
 *                 format: binary
 *                 description: PDF file for expense analysis
 *     responses:
 *       200:
 *         description: Successful response from the copilot
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ChatResponse'
 *       400:
 *         description: Bad request - missing required parameters
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
 *                   example: Message or file is required
 *       500:
 *         description: Internal server error
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
 *                   example: Failed to communicate with Finance Copilot
 *                 error:
 *                   type: string
 *                   example: Detailed error message
 */

const upload = multer();

router.post('/chat', upload.single('file'), copilotController.sendMessageToCopilot);

/**
 * @swagger
 * components:
 *   schemas:
 *     BudgetPlanResponse:
 *       type: object
 *       properties:
 *         success:
 *           type: boolean
 *           description: Indicates if the request was successful
 *         response:
 *           type: object
 *           description: The response data from the copilot
 *         message:
 *           type: string
 *           description: Error message if success is false
 *         error:
 *           type: string
 *           description: Detailed error information if an exception occurred
 * 
 * /copilot/budget-plan:
 *   post:
 *     summary: Get a budget plan from the Finance Copilot
 *     description: |
 *       This endpoint allows you to:
 *       - Get a budget plan based on your financial data
 *     tags:
 *       - Finance Copilot
 *     responses:
 *       200:
 *         description: Successful response from the copilot
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/BudgetPlanResponse'
 *       400:
 *         description: Bad request - missing required parameters
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
 *                   example: Message or file is required
 *       500:
 *         description: Internal server error
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
 *                   example: Failed to communicate with Finance Copilot
 *                 error:
 *                   type: string
 *                   example: Detailed error message
 */

router.post('/budget-plan', copilotController.getBudgetPlan);
module.exports = router;
