import React from "react";
import PropTypes from "prop-types";
import { useNavigate, useLocation } from "react-router-dom";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import HomeIcon from "@mui/icons-material/Home";
import SettingsIcon from "@mui/icons-material/Settings";
import NotificationsIcon from "@mui/icons-material/Notifications";
import PersonIcon from "@mui/icons-material/Person";
import AccessibilityNewIcon from "@mui/icons-material/AccessibilityNew";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import Box from "@mui/material/Box";

/**
 * Sidebar navigation component for desktop.
 * Uses MUI Drawer and List for navigation, styled with Tailwind CSS.
 * Responsive and accessible, with navigation items and icons.
 */
const iconMap = {
  Home: <HomeIcon />,
  Settings: <SettingsIcon />,
  Notifications: <NotificationsIcon />,
  Profile: <PersonIcon />,
  Accessibility: <AccessibilityNewIcon />,
};

const drawerWidth = 240;

const Sidebar = ({ open, navItems, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <>
      {/* Sidebar toggle button for accessibility */}
      <Box
        className="fixed top-4 left-4 z-50"
        sx={{ display: { xs: "none", md: "block" } }}
      >
        <IconButton
          aria-label={open ? "Close sidebar" : "Open sidebar"}
          onClick={onToggle}
          size="large"
        >
          <MenuIcon />
        </IconButton>
      </Box>
      <Drawer
        variant="persistent"
        anchor="left"
        open={open}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            backgroundColor: "#f5f5f5",
            color: "#1976d2",
            borderRight: "1px solid #e0e0e0",
          },
          display: { xs: "none", md: "block" },
        }}
        PaperProps={{
          className: "pt-8 pb-4",
          elevation: 3,
        }}
        aria-label="Sidebar navigation"
      >
        <List>
          {navItems.map((item) => (
            <ListItemButton
              key={item.label}
              selected={location.pathname === item.route}
              onClick={() => navigate(item.route)}
              sx={{
                "&.Mui-selected": {
                  backgroundColor: "#e3f2fd",
                  color: "#1976d2",
                  fontWeight: 600,
                },
                borderRadius: "0.5rem",
                margin: "0.25rem 0.5rem",
                minHeight: 48,
              }}
              aria-label={item.label}
            >
              <ListItemIcon sx={{ color: "#1976d2" }}>
                {iconMap[item.label] || <HomeIcon />}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: "1rem",
                  fontWeight: location.pathname === item.route ? 600 : 400,
                }}
              />
            </ListItemButton>
          ))}
        </List>
      </Drawer>
      {/* Sidebar overlay for when open */}
      {open && (
        <Box
          className="fixed inset-0 bg-black bg-opacity-20 z-40"
          onClick={onToggle}
          sx={{ display: { xs: "none", md: "block" } }}
          aria-label="Close sidebar overlay"
        />
      )}
    </>
  );
};

Sidebar.propTypes = {
  open: PropTypes.bool.isRequired,
  navItems: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      route: PropTypes.string.isRequired,
    })
  ).isRequired,
  onToggle: PropTypes.func.isRequired,
};

export default Sidebar;