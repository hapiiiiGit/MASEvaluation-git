/**
 * Authentication controller for Express.
 * Handles user registration, login, and logout.
 * Uses User model and JWT utility.
 */

const User = require('../models/User');
const jwtUtil = require('../utils/jwt');

/**
 * Registers a new user.
 * Expects { username, email, password } in req.body.
 * Returns the created user object (excluding password hash).
 */
async function register(req, res) {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required.' });
    }

    // Check if user already exists
    const existingUser = await User.findByUsernameOrEmail(username) || await User.findByUsernameOrEmail(email);
    if (existingUser) {
      return res.status(409).json({ error: 'User with this username or email already exists.' });
    }

    // Create new user
    const user = await User.create({ username, email, password });
    return res.status(201).json({ user: user.toJSON() });
  } catch (err) {
    console.error('Register error:', err);
    return res.status(500).json({ error: 'Failed to register user.' });
  }
}

/**
 * Logs in a user.
 * Expects { usernameOrEmail, password } in req.body.
 * Returns JWT token if successful.
 */
async function login(req, res) {
  try {
    const { usernameOrEmail, password } = req.body;
    if (!usernameOrEmail || !password) {
      return res.status(400).json({ error: 'Username/email and password are required.' });
    }

    // Find user by username or email
    const user = await User.findByUsernameOrEmail(usernameOrEmail);
    if (!user) {
      return res.status(401).json({ error: 'Invalid username/email or password.' });
    }

    // Verify password
    const valid = await user.verify_password(password);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid username/email or password.' });
    }

    // Generate JWT token
    const token = jwtUtil.encode({
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
    });

    return res.status(200).json({ token });
  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ error: 'Failed to login.' });
  }
}

/**
 * Logs out a user.
 * For stateless JWT, this is a client-side operation.
 * Optionally, you can implement token blacklisting here.
 */
function logout(req, res) {
  // For stateless JWT, logout is handled on the client by deleting the token.
  // Optionally, implement token blacklisting if needed.
  return res.status(200).json({ success: true, message: 'Logged out.' });
}

module.exports = {
  register,
  login,
  logout,
};