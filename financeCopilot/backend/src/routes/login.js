const express = require('express');
const router = express.Router();
const loginController = require("../controllers/login");

/**
 * @swagger
 * tags:
 *   name: login
 *   description: API for handling user login and registration
 */

/**
 * @swagger
 * /login/getLogout:
 *   get:
 *     summary: Logs out the user by destroying the session.
 *     tags:
 *       - login
 *     responses:
 *       200:
 *         description: User logged out successfully.
 *       400:
 *         description: No active session.
 *       500:
 *         description: Internal server error.
 */
router.get("/getLogout", loginController.getLogout);

/**
 * @swagger
 * /login/postLogin:
 *   post:
 *     summary: Logs in the user by validating credentials and creating a session.
 *     tags:
 *       - login
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               email:
 *                 type: string
 *                 description: The user's email.
 *               password:
 *                 type: string
 *                 description: The user's password.
 *               rememberMe:
 *                 type: boolean
 *                 description: Whether to keep the session active for 30 days.
 *     responses:
 *       200:
 *         description: User logged in successfully.
 *       401:
 *         description: Invalid password or user not approved.
 *       404:
 *         description: User not found.
 *       500:
 *         description: Internal server error.
 */
router.post("/postLogin", loginController.postLogin);

/**
 * @swagger
 * /login/postRegister:
 *   post:
 *     summary: Registers a new user.
 *     tags:
 *       - login
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               email:
 *                 type: string
 *                 description: The user's email.
 *               name:
 *                 type: string
 *                 description: The user's first name.
 *               surname:
 *                 type: string
 *                 description: The user's last name.
 *               password:
 *                 type: string
 *                 description: The user's password.
 *     responses:
 *       201:
 *         description: User created successfully.
 *       400:
 *         description: User already exists or missing required fields.
 *       500:
 *         description: Internal server error.
 */
router.post("/postRegister", loginController.postRegister);

module.exports = router;