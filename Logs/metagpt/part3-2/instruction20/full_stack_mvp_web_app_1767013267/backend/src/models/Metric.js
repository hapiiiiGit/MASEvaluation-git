/**
 * Metric model for PostgreSQL.
 * Defines schema and methods for metrics used in the dashboard.
 */

const { v4: uuidv4 } = require('uuid');
const db = require('../utils/db');

class Metric {
  constructor({ id, name, value, timestamp, user_id }) {
    this.id = id;
    this.name = name;
    this.value = value;
    this.timestamp = timestamp;
    this.user_id = user_id;
  }

  /**
   * Creates a new metric in the database.
   * @param {object} data - { name, value, user_id }
   * @returns {Promise<Metric>}
   */
  static async create({ name, value, user_id }) {
    const id = uuidv4();
    const timestamp = new Date().toISOString();
    const metricData = {
      id,
      name,
      value,
      timestamp,
      user_id,
    };
    await db.insert('metrics', metricData);
    return new Metric(metricData);
  }

  /**
   * Finds metrics by user_id.
   * @param {string} user_id
   * @param {number} [limit=20] - Number of metrics to fetch
   * @returns {Promise<Metric[]>}
   */
  static async findByUserId(user_id, limit = 20) {
    const sql = `
      SELECT * FROM metrics
      WHERE user_id = $1
      ORDER BY timestamp DESC
      LIMIT $2
    `;
    const rows = await db.query(sql, [user_id, limit]);
    return rows.map(row => new Metric(row));
  }

  /**
   * Finds all metrics (admin use).
   * @param {number} [limit=100]
   * @returns {Promise<Metric[]>}
   */
  static async findAll(limit = 100) {
    const sql = `
      SELECT * FROM metrics
      ORDER BY timestamp DESC
      LIMIT $1
    `;
    const rows = await db.query(sql, [limit]);
    return rows.map(row => new Metric(row));
  }

  /**
   * Finds a metric by id.
   * @param {string} id
   * @returns {Promise<Metric|null>}
   */
  static async findById(id) {
    const sql = `
      SELECT * FROM metrics
      WHERE id = $1
      LIMIT 1
    `;
    const rows = await db.query(sql, [id]);
    if (rows.length === 0) return null;
    return new Metric(rows[0]);
  }

  /**
   * Returns a plain object representation of the metric.
   */
  toJSON() {
    return {
      id: this.id,
      name: this.name,
      value: this.value,
      timestamp: this.timestamp,
      user_id: this.user_id,
    };
  }
}

module.exports = Metric;