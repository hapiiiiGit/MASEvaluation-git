/**
 * Report model for PostgreSQL.
 * Defines schema and methods for reports, including export functionality.
 */

const { v4: uuidv4 } = require('uuid');
const db = require('../utils/db');
const { Parser } = require('json2csv');
const PDFDocument = require('pdfkit');
const stream = require('stream');

class Report {
  constructor({ id, title, data, created_by, created_at }) {
    this.id = id;
    this.title = title;
    this.data = typeof data === 'object' ? data : (data ? JSON.parse(data) : {});
    this.created_by = created_by;
    this.created_at = created_at;
  }

  /**
   * Creates a new report in the database.
   * @param {object} params - { title, data, created_by }
   * @returns {Promise<Report>}
   */
  static async create({ title, data, created_by }) {
    const id = uuidv4();
    const created_at = new Date().toISOString();
    const reportData = {
      id,
      title,
      data: JSON.stringify(data),
      created_by,
      created_at,
    };
    await db.insert('reports', reportData);
    return new Report(reportData);
  }

  /**
   * Finds reports by user_id.
   * @param {string} user_id
   * @param {number} [limit=20]
   * @returns {Promise<Report[]>}
   */
  static async findByUserId(user_id, limit = 20) {
    const sql = `
      SELECT * FROM reports
      WHERE created_by = $1
      ORDER BY created_at DESC
      LIMIT $2
    `;
    const rows = await db.query(sql, [user_id, limit]);
    return rows.map(row => new Report(row));
  }

  /**
   * Finds all reports (admin use).
   * @param {number} [limit=100]
   * @returns {Promise<Report[]>}
   */
  static async findAll(limit = 100) {
    const sql = `
      SELECT * FROM reports
      ORDER BY created_at DESC
      LIMIT $1
    `;
    const rows = await db.query(sql, [limit]);
    return rows.map(row => new Report(row));
  }

  /**
   * Finds a report by id.
   * @param {string} id
   * @returns {Promise<Report|null>}
   */
  static async findById(id) {
    const sql = `
      SELECT * FROM reports
      WHERE id = $1
      LIMIT 1
    `;
    const rows = await db.query(sql, [id]);
    if (rows.length === 0) return null;
    return new Report(rows[0]);
  }

  /**
   * Export the report data in the specified format.
   * @param {string} format - 'csv' or 'pdf'
   * @returns {Promise<Buffer>} - Buffer of the exported file
   */
  async export(format) {
    if (format === 'csv') {
      // Export as CSV
      const parser = new Parser();
      // Data should be an array of objects for CSV, wrap in array if flat object
      const dataArr = Array.isArray(this.data) ? this.data : [this.data];
      const csv = parser.parse(dataArr);
      return Buffer.from(csv, 'utf-8');
    } else if (format === 'pdf') {
      // Export as PDF
      const doc = new PDFDocument();
      const bufferStream = new stream.PassThrough();
      doc.pipe(bufferStream);

      doc.fontSize(18).text(this.title, { align: 'center' });
      doc.moveDown();

      doc.fontSize(12);
      const dataObj = this.data;
      Object.keys(dataObj).forEach(key => {
        doc.text(`${key}: ${dataObj[key]}`);
      });

      doc.end();

      // Collect the PDF buffer
      const chunks = [];
      return new Promise((resolve, reject) => {
        bufferStream.on('data', chunk => chunks.push(chunk));
        bufferStream.on('end', () => resolve(Buffer.concat(chunks)));
        bufferStream.on('error', reject);
      });
    } else {
      throw new Error('Unsupported export format');
    }
  }

  /**
   * Returns a plain object representation of the report.
   */
  toJSON() {
    return {
      id: this.id,
      title: this.title,
      data: this.data,
      created_by: this.created_by,
      created_at: this.created_at,
    };
  }
}

module.exports = Report;