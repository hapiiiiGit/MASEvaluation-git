import React, { createContext, useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";

// User model for reference
// {
//   id: string,
//   name: string,
//   email: string,
//   role: string,
//   avatar?: string
// }

export const AuthContext = createContext({
  user: null,
  login: async () => {},
  logout: () => {},
  isAuthenticated: () => false,
  updateProfile: async () => {},
});

export const AuthContextProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // Simulate loading user from localStorage or API on mount
  useEffect(() => {
    const storedUser = localStorage.getItem("cross_platform_app_user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Save user to localStorage on change
  useEffect(() => {
    if (user) {
      localStorage.setItem("cross_platform_app_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("cross_platform_app_user");
    }
  }, [user]);

  // Simulated login function
  const login = useCallback(async (credentials) => {
    // In production, call backend API for authentication
    // Here, simulate login with any credentials
    const fakeUser = {
      id: "1",
      name: credentials.name || "Demo User",
      email: credentials.email || "demo@crossplatform.app",
      role: "user",
      avatar: "",
    };
    setUser(fakeUser);
    return fakeUser;
  }, []);

  // Logout function
  const logout = useCallback(() => {
    setUser(null);
  }, []);

  // Check if authenticated
  const isAuthenticated = useCallback(() => !!user, [user]);

  // Update profile function
  const updateProfile = useCallback(async (profile) => {
    // In production, call backend API to update profile
    setUser((prev) => ({
      ...prev,
      ...profile,
    }));
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

AuthContextProvider.propTypes = {
  children: PropTypes.node.isRequired,
};