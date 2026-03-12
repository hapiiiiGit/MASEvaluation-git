/**
 * Report controller for Express.
 * Handles report generation and export functionality.
 * Uses Report model.
 */

const Report = require('../models/Report');
const Metric = require('../models/Metric');

/**
 * Generate a new report based on provided parameters.
 * Expects { title, params } in req.body.
 * params can include filters for metrics (e.g., metric name, date range).
 * Returns the created report object.
 */
async function generate_report(req, res) {
  try {
    const { title, params } = req.body;
    const { id: userId } = req.user;

    if (!title) {
      return res.status(400).json({ error: 'Report title is required.' });
    }

    // Fetch metrics based on params (e.g., filter by name, date range)
    let metrics = [];
    if (params && params.metricName) {
      // Optionally filter by metric name
      const sql = `
        SELECT * FROM metrics
        WHERE user_id = $1 AND name = $2
        ORDER BY timestamp DESC
        LIMIT 50
      `;
      metrics = await Metric.findByUserId(userId, 50);
      metrics = metrics.filter(m => m.name === params.metricName);
    } else {
      metrics = await Metric.findByUserId(userId, 50);
    }

    // Optionally filter by date range
    if (params && params.startDate && params.endDate) {
      const start = new Date(params.startDate);
      const end = new Date(params.endDate);
      metrics = metrics.filter(m => {
        const ts = new Date(m.timestamp);
        return ts >= start && ts <= end;
      });
    }

    // Prepare report data (aggregate or list metrics)
    const reportData = {
      totalMetrics: metrics.length,
      metrics: metrics.map(m => m.toJSON()),
      generatedAt: new Date().toISOString(),
      ...(params || {}),
    };

    // Create and save the report
    const report = await Report.create({
      title,
      data: reportData,
      created_by: userId,
    });

    return res.status(201).json({ report: report.toJSON() });
  } catch (err) {
    console.error('Report generate_report error:', err);
    return res.status(500).json({ error: 'Failed to generate report.' });
  }
}

/**
 * Export a report in the specified format (CSV or PDF).
 * GET /api/report/export/:reportId?format=csv|pdf
 * Returns the exported file as a download.
 */
async function export_report(req, res) {
  try {
    const { reportId } = req.params;
    const { format } = req.query;

    if (!reportId || !format || !['csv', 'pdf'].includes(format)) {
      return res.status(400).json({ error: 'Invalid reportId or format.' });
    }

    // Find the report
    const report = await Report.findById(reportId);
    if (!report) {
      return res.status(404).json({ error: 'Report not found.' });
    }

    // Only allow the creator or admin to export
    if (
      req.user.role !== 'admin' &&
      report.created_by !== req.user.id
    ) {
      return res.status(403).json({ error: 'Forbidden.' });
    }

    // Export the report
    const fileBuffer = await report.export(format);
    const fileName = `${report.title.replace(/\s+/g, '_')}_${report.id}.${format}`;

    if (format === 'csv') {
      res.setHeader('Content-Type', 'text/csv');
    } else if (format === 'pdf') {
      res.setHeader('Content-Type', 'application/pdf');
    }
    res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
    res.status(200).send(fileBuffer);
  } catch (err) {
    console.error('Report export_report error:', err);
    return res.status(500).json({ error: 'Failed to export report.' });
  }
}

module.exports = {
  generate_report,
  export_report,
};