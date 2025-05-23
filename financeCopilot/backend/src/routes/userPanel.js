const express = require("express");
const router = express.Router();
const userPanelController = require("../controllers/userPanel"); 


/**
 * @swagger
 * tags:
 *   - name: userPanel
 *     description: API for handling user panel operations
 */
/**
 * @swagger
 * /userPanel/doSurvey:
 *    post:
 *     summary: Append survey field data to user's `fields` array
 *     tags: [userPanel]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - surveyData
 *             properties:
 *               surveyData:
 *                 type: array
 *                 description: List of field objects to append to the user
 *                 items:
 *                   type: object
 *                   required:
 *                     - name
 *                     - description
 *                   properties:
 *                     name:
 *                       type: string
 *                       description: Field name
 *                       example: "Housing"
 *                     content:
 *                       type: string
 *                       description: Field content
 *                       example: "1000"
 *                     deleted:
 *                       type: number
 *                       description: Flag to indicate soft-deletion (0 or 1)
 *                       enum: [0, 1]
 *                       default: 0
 *                       example: 0
 *     responses:
 *       200:
 *         description: Survey data successfully appended to the user
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Survey data imported successfully
 *                 addedFields:
 *                   type: integer
 *                   example: 2
 *       400:
 *         description: Invalid format (surveyData not an array)
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Invalid survey data format. Expected an array.
 *       404:
 *         description: User not found
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: User not found
 *       500:
 *         description: Internal server error
 */
router.post("/doSurvey", userPanelController.doSurvey);

/**
 * @swagger
 * /userPanel/editSurvey:
 *  post:
 *     summary: Edit survey field data for a user
 *     tags: [userPanel]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - surveyData
 *             properties:
 *               surveyData:
 *                 type: array
 *                 description: List of field objects to append to the user
 *                 items:
 *                   type: object
 *                   required:
 *                     - name
 *                     - description
 *                   properties:
 *                     name:
 *                       type: string
 *                       description: Field name
 *                       example: "Housing"
 *                     content:
 *                       type: string
 *                       description: Field content
 *                       example: "1000"
 *                     deleted:
 *                       type: number
 *                       description: Flag to indicate soft-deletion (0 or 1)
 *                       enum: [0, 1]
 *                       default: 0
 *                       example: 0
 *     responses:
 *       200:
 *         description: Survey data successfully appended to the user
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Survey data imported successfully
 *                 addedFields:
 *                   type: integer
 *                   example: 2
 *       400:
 *         description: Invalid format (surveyData not an array)
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Invalid survey data format. Expected an array.
 *       404:
 *         description: User not found
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: User not found
 *       500:
 *         description: Internal server error
 */
router.post("/editSurvey", userPanelController.editSurvey);
/**
 * 
 * @swagger
 * /userPanel/getFields:
 *   get:
 *     summary: Get all fields for a user
 *     tags: [userPanel]
 *     parameters:
 *       - in: query
 *         name: userId
 *         schema:
 *           type: string
 *         description: Optional user ID to fetch fields for. If not provided, uses authenticated user's session.
 *     responses:
 *       200:
 *         description: Successfully retrieved user fields
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 *                 properties:
 *                   name:
 *                     type: string
 *                     example: "Housing"
 *                   content:
 *                     type: string
 *                     example: "1000"
 *                   deleted:
 *                     type: number
 *                     example: 0
 *       401:
 *         description: Unauthorized - User session not found (when no userId provided)
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: User session not found
 *       404:
 *         description: User not found
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: User not found
 *       500:
 *         description: Internal server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Internal server error
 */
router.get("/getFields", userPanelController.getFields);
/**
 * @swagger
 * /userPanel/invest:
 *   post:
 *     summary: Save stock symbols as investment fields for the user
 *     tags: [userPanel]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - userId
 *               - investData
 *             properties:
 *               userId:
 *                 type: string
 *                 description: ID of the user to whom investments will be added
 *                 example: "6632d3bda7e874f69a33b2c1"
 *               investData:
 *                 type: array
 *                 description: Array of stock symbols to add as investment fields
 *                 items:
 *                   type: string
 *                   example: "AAPL"
 *     responses:
 *       200:
 *         description: Investments saved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Investments saved successfully
 *       400:
 *         description: Invalid request data
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Invalid request data
 *       404:
 *         description: User not found
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: User not found
 *       500:
 *         description: Internal server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: Internal server error
 */
router.post("/invest", userPanelController.invest);
module.exports = router;
