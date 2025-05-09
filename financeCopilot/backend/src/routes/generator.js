const express = require('express');
const router = express.Router();
const generatorController = require('../controllers/generator');


router.get("/fetchAllStocksFromFile", generatorController.fetchAllStocksFromFile);



module.exports = router;