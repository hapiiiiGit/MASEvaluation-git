import React, { useState, useEffect } from "react";
import { useMediaQuery } from "@mui/material";
import { ThemeProvider, useTheme } from "@mui/material/styles";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";
import NavigationBar from "./components/NavigationBar";
import Sidebar from "./components/Sidebar";
import HomeScreen from "./components/HomeScreen";
import Settings from "./components/Settings";
import NotificationCenter from "./components/NotificationCenter";
import ProfileManager from "./components/ProfileManager";
import AccessibilityOptions from "./components/AccessibilityOptions";
import { AuthContextProvider } from "./context/AuthContext";
import { ThemeContextProvider } from "./context/ThemeContext";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import "./assets/styles/tailwind.css";

const App = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const theme = useTheme();
  // Responsive: mobile if width < 900px
  const isMobile = useMediaQuery("(max-width:900px)");

  // Accessibility: focus outline for keyboard users
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Tab") {
        document.body.classList.add("focus-outline");
      }
    };
    const handleMouseDown = () => {
      document.body.classList.remove("focus-outline");
    };
    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("mousedown", handleMouseDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("mousedown", handleMouseDown);
    };
  }, []);

  // Navigation items
  const navItems = [
    { label: "Home", route: "/" },
    { label: "Settings", route: "/settings" },
    { label: "Notifications", route: "/notifications" },
    { label: "Profile", route: "/profile" },
    { label: "Accessibility", route: "/accessibility" },
  ];

  return (
    <AuthContextProvider>
      <ThemeContextProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <Box className="min-h-screen flex bg-gray-50 text-gray-900 font-roboto">
              {/* Sidebar for desktop, NavigationBar for mobile */}
              {!isMobile ? (
                <Sidebar
                  open={sidebarOpen}
                  navItems={navItems}
                  onToggle={() => setSidebarOpen((open) => !open)}
                />
              ) : (
                <NavigationBar navItems={navItems} />
              )}
              {/* Main content area */}
              <Box
                component="main"
                className={`flex-1 p-4 transition-all duration-300 ${
                  sidebarOpen && !isMobile ? "ml-64" : ""
                }`}
                aria-label="Main content"
              >
                <Routes>
                  <Route path="/" element={<HomeScreen />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/notifications" element={<NotificationCenter />} />
                  <Route path="/profile" element={<ProfileManager />} />
                  <Route path="/accessibility" element={<AccessibilityOptions />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Box>
            </Box>
          </Router>
        </ThemeProvider>
      </ThemeContextProvider>
    </AuthContextProvider>
  );
};

export default App;