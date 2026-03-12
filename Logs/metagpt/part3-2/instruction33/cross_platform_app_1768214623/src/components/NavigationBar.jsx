import React, { useState } from "react";
import PropTypes from "prop-types";
import { useNavigate, useLocation } from "react-router-dom";
import BottomNavigation from "@mui/material/BottomNavigation";
import BottomNavigationAction from "@mui/material/BottomNavigationAction";
import HomeIcon from "@mui/icons-material/Home";
import SettingsIcon from "@mui/icons-material/Settings";
import NotificationsIcon from "@mui/icons-material/Notifications";
import PersonIcon from "@mui/icons-material/Person";
import AccessibilityNewIcon from "@mui/icons-material/AccessibilityNew";
import Paper from "@mui/material/Paper";

/**
 * NavigationBar component for mobile devices.
 * Renders a bottom navigation bar with icons and routes.
 * Uses MUI for accessibility and Tailwind CSS for styling.
 */
const iconMap = {
  Home: <HomeIcon />,
  Settings: <SettingsIcon />,
  Notifications: <NotificationsIcon />,
  Profile: <PersonIcon />,
  Accessibility: <AccessibilityNewIcon />,
};

const NavigationBar = ({ navItems }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Find the current route index
  const currentRouteIndex = navItems.findIndex(
    (item) => item.route === location.pathname
  );
  const [value, setValue] = useState(
    currentRouteIndex !== -1 ? currentRouteIndex : 0
  );

  const handleChange = (event, newValue) => {
    setValue(newValue);
    navigate(navItems[newValue].route);
  };

  return (
    <Paper
      elevation={3}
      className="fixed bottom-0 left-0 right-0 z-50"
      sx={{
        borderRadius: 0,
        bgcolor: "background.paper",
      }}
      role="navigation"
      aria-label="Bottom navigation"
    >
      <BottomNavigation
        showLabels
        value={value}
        onChange={handleChange}
        sx={{
          bgcolor: "background.paper",
        }}
      >
        {navItems.map((item, idx) => (
          <BottomNavigationAction
            key={item.label}
            label={item.label}
            icon={iconMap[item.label] || <HomeIcon />}
            sx={{
              "&.Mui-selected": {
                color: "primary.main",
              },
              minWidth: 0,
              maxWidth: "100%",
              fontSize: "0.875rem",
            }}
            aria-label={item.label}
          />
        ))}
      </BottomNavigation>
    </Paper>
  );
};

NavigationBar.propTypes = {
  navItems: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      route: PropTypes.string.isRequired,
    })
  ).isRequired,
};

export default NavigationBar;