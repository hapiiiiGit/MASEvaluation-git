/**
 * Report routes for Express.
 * Connects /generate and /export endpoints to the reportController.
 */

const express = require('express');
const router = express.Router();
const reportController = require('../controllers/reportController');

// POST /api/report/generate
router.post('/generate', reportController.generate_report);

// GET /api/report/export/:reportId
router.get('/export/:reportId', reportController.export_report);

module.exports = router;