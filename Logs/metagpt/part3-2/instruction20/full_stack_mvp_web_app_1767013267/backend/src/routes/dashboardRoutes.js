/**
 * Dashboard routes for Express.
 * Connects /metrics and /reports endpoints to the dashboardController.
 */

const express = require('express');
const router = express.Router();
const dashboardController = require('../controllers/dashboardController');

// GET /api/dashboard/metrics
router.get('/metrics', dashboardController.get_metrics);

// GET /api/dashboard/reports
router.get('/reports', dashboardController.get_reports);

module.exports = router;