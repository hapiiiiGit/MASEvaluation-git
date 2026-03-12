/**
 * Authentication utility for the dashboard.
 * Handles login, registration, logout, and JWT token management.
 * Uses TypeScript and fetch API.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:4000/api';

// Store JWT token in localStorage
function setToken(token: string) {
  localStorage.setItem('token', token);
}

// Retrieve JWT token from localStorage
export function getToken(): string | null {
  return localStorage.getItem('token');
}

// Remove JWT token from localStorage
export function clearToken() {
  localStorage.removeItem('token');
}

// Register a new user
export async function register(username: string, email: string, password: string): Promise<{ success: boolean; message?: string }> {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    return { success: false, message: error.message || 'Registration failed' };
  }

  return { success: true };
}

// Login user and store JWT token
export async function login(usernameOrEmail: string, password: string): Promise<{ success: boolean; token?: string; message?: string }> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ usernameOrEmail, password }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    return { success: false, message: error.message || 'Login failed' };
  }

  const data = await res.json();
  if (data.token) {
    setToken(data.token);
    return { success: true, token: data.token };
  }
  return { success: false, message: 'No token received' };
}

// Logout user (clear token)
export function logout() {
  clearToken();
}

// Check if user is authenticated
export function isAuthenticated(): boolean {
  return !!getToken();
}

// Decode JWT payload (without verifying signature, for client-side use only)
export function getUserFromToken(): { id: string; username: string; email: string; role: string } | null {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    return {
      id: decoded.id,
      username: decoded.username,
      email: decoded.email,
      role: decoded.role,
    };
  } catch {
    return null;
  }
}