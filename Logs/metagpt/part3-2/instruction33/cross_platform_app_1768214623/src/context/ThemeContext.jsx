import React, { createContext, useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";

// ThemeContext provides theme state and setter for the app.
// Supports "light", "dark", "system", and "highContrast" modes.

export const ThemeContext = createContext({
  theme: "light",
  setTheme: () => {},
});

export const ThemeContextProvider = ({ children }) => {
  // Default theme is "light"
  const [theme, setThemeState] = useState(() => {
    // Try to load from localStorage, fallback to "light"
    return localStorage.getItem("cross_platform_app_theme") || "light";
  });

  // Save theme to localStorage on change
  useEffect(() => {
    localStorage.setItem("cross_platform_app_theme", theme);
    // Optionally, apply theme to <body> for high contrast/large text
    if (theme === "highContrast") {
      document.body.classList.add("high-contrast");
    } else {
      document.body.classList.remove("high-contrast");
    }
    if (theme === "largeText") {
      document.body.classList.add("large-text");
    } else {
      document.body.classList.remove("large-text");
    }
  }, [theme]);

  // Optionally, support system theme
  useEffect(() => {
    if (theme === "system") {
      const mq = window.matchMedia("(prefers-color-scheme: dark)");
      const handleChange = (e) => {
        setThemeState(e.matches ? "dark" : "light");
      };
      mq.addEventListener("change", handleChange);
      setThemeState(mq.matches ? "dark" : "light");
      return () => {
        mq.removeEventListener("change", handleChange);
      };
    }
  }, [theme]);

  // Setter function
  const setTheme = useCallback((newTheme) => {
    setThemeState(newTheme);
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

ThemeContextProvider.propTypes = {
  children: PropTypes.node.isRequired,
};