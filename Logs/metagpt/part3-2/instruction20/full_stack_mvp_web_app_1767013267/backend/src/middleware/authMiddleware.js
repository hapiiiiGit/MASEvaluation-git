/**
 * Authentication middleware for Express.
 * Verifies JWT token and attaches user info to the request.
 * Returns 401 if unauthorized.
 */

const jwtUtil = require('../utils/jwt');

/**
 * Express middleware to authenticate requests using JWT.
 * If valid, attaches user info to req.user.
 * If invalid or missing, responds with 401 Unauthorized.
 */
function authMiddleware(req, res, next) {
  // Get token from Authorization header: "Bearer <token>"
  const authHeader = req.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Authorization header missing or malformed' });
  }

  const token = authHeader.split(' ')[1];
  if (!token) {
    return res.status(401).json({ error: 'Token missing' });
  }

  // Decode and verify token
  const decoded = jwtUtil.decode(token);
  if (!decoded) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }

  // Attach user info to request
  req.user = {
    id: decoded.id,
    username: decoded.username,
    email: decoded.email,
    role: decoded.role,
  };

  next();
}

module.exports = authMiddleware;