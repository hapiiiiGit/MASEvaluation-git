/**
 * Database utility for connecting to PostgreSQL and executing queries.
 * Uses node-postgres (pg) library.
 */

const { Pool } = require('pg');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

// Create a new PostgreSQL connection pool
const pool = new Pool({
  host: process.env.PGHOST || 'localhost',
  port: process.env.PGPORT ? parseInt(process.env.PGPORT, 10) : 5432,
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || '',
  database: process.env.PGDATABASE || 'full_stack_mvp_db',
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

/**
 * Connect to the database (test connection).
 * Returns a promise that resolves if connection is successful.
 */
async function connect() {
  try {
    const client = await pool.connect();
    await client.query('SELECT 1');
    client.release();
    console.log('✅ Connected to PostgreSQL');
  } catch (err) {
    console.error('❌ PostgreSQL connection error:', err);
    throw err;
  }
}

/**
 * Execute a SQL query with optional parameters.
 * Returns a promise that resolves to the result rows.
 * @param {string} sql - SQL query string
 * @param {Array} params - Query parameters
 * @returns {Promise<Array>}
 */
async function query(sql, params = []) {
  const client = await pool.connect();
  try {
    const res = await client.query(sql, params);
    return res.rows;
  } finally {
    client.release();
  }
}

/**
 * Insert a row into a table.
 * @param {string} table - Table name
 * @param {object} data - Key-value pairs for columns
 * @returns {Promise<boolean>}
 */
async function insert(table, data) {
  const keys = Object.keys(data);
  const values = Object.values(data);
  const placeholders = keys.map((_, i) => `$${i + 1}`).join(', ');
  const sql = `INSERT INTO ${table} (${keys.join(', ')}) VALUES (${placeholders}) RETURNING *`;
  const rows = await query(sql, values);
  return rows.length > 0;
}

/**
 * Update a row in a table by id.
 * @param {string} table - Table name
 * @param {string} id - UUID of the row
 * @param {object} data - Key-value pairs for columns to update
 * @returns {Promise<boolean>}
 */
async function update(table, id, data) {
  const keys = Object.keys(data);
  const values = Object.values(data);
  const setClause = keys.map((key, i) => `${key} = $${i + 1}`).join(', ');
  const sql = `UPDATE ${table} SET ${setClause} WHERE id = $${keys.length + 1} RETURNING *`;
  const rows = await query(sql, [...values, id]);
  return rows.length > 0;
}

/**
 * Delete a row from a table by id.
 * @param {string} table - Table name
 * @param {string} id - UUID of the row
 * @returns {Promise<boolean>}
 */
async function deleteRow(table, id) {
  const sql = `DELETE FROM ${table} WHERE id = $1 RETURNING *`;
  const rows = await query(sql, [id]);
  return rows.length > 0;
}

module.exports = {
  connect,
  query,
  insert,
  update,
  delete: deleteRow,
  pool, // Export pool for transactions if needed
};