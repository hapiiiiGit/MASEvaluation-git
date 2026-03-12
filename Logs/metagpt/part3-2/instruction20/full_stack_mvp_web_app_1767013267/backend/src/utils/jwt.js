/**
 * JWT utility for encoding and decoding authentication tokens.
 * Uses jsonwebtoken library.
 */

const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const JWT_SECRET = process.env.JWT_SECRET || 'supersecretkey';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '2h';

/**
 * Encode a payload into a JWT token.
 * @param {object} payload - The payload to encode (e.g., user info)
 * @returns {string} - JWT token
 */
function encode(payload) {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
}

/**
 * Decode a JWT token and verify its signature.
 * @param {string} token - JWT token
 * @returns {object} - Decoded payload if valid, or null if invalid
 */
function decode(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (err) {
    return null;
  }
}

module.exports = {
  encode,
  decode,
};