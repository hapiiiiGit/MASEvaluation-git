/**
 * Dashboard controller for Express.
 * Handles fetching metrics and reports for the dashboard.
 * Uses Metric and Report models.
 */

const Metric = require('../models/Metric');
const Report = require('../models/Report');

/**
 * Get metrics for the current user.
 * If the user is an admin, return all metrics.
 * Otherwise, return metrics for the user.
 */
async function get_metrics(req, res) {
  try {
    const { id, role } = req.user;
    let metrics;
    if (role === 'admin') {
      metrics = await Metric.findAll(100);
    } else {
      metrics = await Metric.findByUserId(id, 20);
    }
    return res.status(200).json({ metrics: metrics.map(m => m.toJSON()) });
  } catch (err) {
    console.error('Dashboard get_metrics error:', err);
    return res.status(500).json({ error: 'Failed to fetch metrics.' });
  }
}

/**
 * Get reports for the current user.
 * If the user is an admin, return all reports.
 * Otherwise, return reports created by the user.
 */
async function get_reports(req, res) {
  try {
    const { id, role } = req.user;
    let reports;
    if (role === 'admin') {
      reports = await Report.findAll(50);
    } else {
      reports = await Report.findByUserId(id, 20);
    }
    return res.status(200).json({ reports: reports.map(r => r.toJSON()) });
  } catch (err) {
    console.error('Dashboard get_reports error:', err);
    return res.status(500).json({ error: 'Failed to fetch reports.' });
  }
}

module.exports = {
  get_metrics,
  get_reports,
};