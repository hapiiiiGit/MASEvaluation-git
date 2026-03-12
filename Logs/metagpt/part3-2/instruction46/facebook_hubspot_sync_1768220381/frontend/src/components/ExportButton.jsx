import React from "react";
import { Button, Menu, MenuItem, ListItemIcon, ListItemText } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";

/**
 * ExportButton component for dashboard.
 * Provides a button to export metrics, contacts, or deals as CSV.
 * Uses MUI and Tailwind CSS.
 *
 * Props:
 * - onExport: function(type) => void, where type is "metrics", "contacts", or "deals"
 */
const ExportButton = ({ onExport }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleOpenMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
  };

  const handleExport = (type) => {
    if (onExport) {
      onExport(type);
    }
    handleCloseMenu();
  };

  return (
    <div className="flex justify-end">
      <Button
        variant="outlined"
        color="primary"
        startIcon={<DownloadIcon />}
        onClick={handleOpenMenu}
        sx={{ textTransform: "none" }}
      >
        Export Data
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleCloseMenu}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
      >
        <MenuItem onClick={() => handleExport("metrics")}>
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Export Metrics" />
        </MenuItem>
        <MenuItem onClick={() => handleExport("contacts")}>
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Export Contacts" />
        </MenuItem>
        <MenuItem onClick={() => handleExport("deals")}>
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Export Deals" />
        </MenuItem>
      </Menu>
    </div>
  );
};

export default ExportButton;