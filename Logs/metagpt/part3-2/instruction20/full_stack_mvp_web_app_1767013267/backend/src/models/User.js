/**
 * User model for PostgreSQL.
 * Defines user schema and password verification.
 * Uses bcrypt for password hashing.
 */

const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const db = require('../utils/db');

const SALT_ROUNDS = 10;

class User {
  constructor({ id, username, email, password_hash, role, created_at }) {
    this.id = id;
    this.username = username;
    this.email = email;
    this.password_hash = password_hash;
    this.role = role;
    this.created_at = created_at;
  }

  /**
   * Verifies a password against the stored hash.
   * @param {string} password
   * @returns {Promise<boolean>}
   */
  async verify_password(password) {
    return bcrypt.compare(password, this.password_hash);
  }

  /**
   * Creates a new user in the database.
   * @param {object} data - { username, email, password, role }
   * @returns {Promise<User>}
   */
  static async create({ username, email, password, role = 'user' }) {
    const id = uuidv4();
    const password_hash = await bcrypt.hash(password, SALT_ROUNDS);
    const created_at = new Date().toISOString();
    const userData = {
      id,
      username,
      email,
      password_hash,
      role,
      created_at,
    };
    await db.insert('users', userData);
    return new User(userData);
  }

  /**
   * Finds a user by username or email.
   * @param {string} usernameOrEmail
   * @returns {Promise<User|null>}
   */
  static async findByUsernameOrEmail(usernameOrEmail) {
    const sql = `
      SELECT * FROM users
      WHERE username = $1 OR email = $1
      LIMIT 1
    `;
    const rows = await db.query(sql, [usernameOrEmail]);
    if (rows.length === 0) return null;
    return new User(rows[0]);
  }

  /**
   * Finds a user by id.
   * @param {string} id
   * @returns {Promise<User|null>}
   */
  static async findById(id) {
    const sql = `
      SELECT * FROM users
      WHERE id = $1
      LIMIT 1
    `;
    const rows = await db.query(sql, [id]);
    if (rows.length === 0) return null;
    return new User(rows[0]);
  }

  /**
   * Returns a plain object representation of the user (excluding password_hash).
   */
  toJSON() {
    return {
      id: this.id,
      username: this.username,
      email: this.email,
      role: this.role,
      created_at: this.created_at,
    };
  }
}

module.exports = User;