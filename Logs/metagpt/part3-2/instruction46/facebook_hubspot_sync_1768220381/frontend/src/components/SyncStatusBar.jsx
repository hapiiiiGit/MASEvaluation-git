import React, { useState } from "react";
import {
  Box,
  Typography,
  Button,
  Chip,
  CircularProgress,
  Tooltip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import SyncIcon from "@mui/icons-material/Sync";
import SettingsIcon from "@mui/icons-material/Settings";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import AutorenewIcon from "@mui/icons-material/Autorenew";

/**
 * SyncStatusBar component for dashboard.
 * Displays sync status, allows manual sync trigger and interval adjustment.
 * Uses MUI and Tailwind CSS.
 */
const SyncStatusBar = ({
  syncStatus,
  onManualSync,
  onSyncIntervalChange,
  loading,
}) => {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [intervalInput, setIntervalInput] = useState(
    syncStatus?.interval_seconds || 3600
  );
  const [intervalError, setIntervalError] = useState("");

  // Format next run time
  const formatNextRun = (isoString) => {
    if (!isoString) return "N/A";
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  // Status chip
  const getStatusChip = () => {
    if (loading) {
      return (
        <Chip
          icon={<AutorenewIcon className="animate-spin" />}
          label="Syncing..."
          color="info"
          variant="filled"
        />
      );
    }
    if (syncStatus?.running) {
      return (
        <Chip
          icon={<CheckCircleIcon />}
          label="Scheduler Running"
          color="success"
          variant="filled"
        />
      );
    }
    return (
      <Chip
        icon={<ErrorIcon />}
        label="Scheduler Stopped"
        color="error"
        variant="filled"
      />
    );
  };

  // Handle interval change
  const handleIntervalChange = (e) => {
    const value = e.target.value;
    setIntervalInput(value);
    if (value < 60) {
      setIntervalError("Interval must be at least 60 seconds.");
    } else {
      setIntervalError("");
    }
  };

  const handleIntervalSave = () => {
    if (intervalInput >= 60) {
      onSyncIntervalChange(Number(intervalInput));
      setSettingsOpen(false);
    }
  };

  return (
    <Box className="w-full flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 shadow-sm">
      <Box className="flex items-center gap-4">
        <Typography variant="h5" className="font-bold text-gray-800">
          Facebook-HubSpot Sync
        </Typography>
        {getStatusChip()}
        <Tooltip title="Next Scheduled Sync">
          <Chip
            label={`Next: ${formatNextRun(syncStatus?.next_run_time)}`}
            color="primary"
            variant="outlined"
            size="small"
          />
        </Tooltip>
        <Chip
          label={`Interval: ${syncStatus?.interval_seconds || 3600}s`}
          color="default"
          variant="outlined"
          size="small"
        />
      </Box>
      <Box className="flex items-center gap-2">
        <Tooltip title="Manual Sync">
          <span>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SyncIcon />}
              onClick={onManualSync}
              disabled={loading}
              sx={{ textTransform: "none" }}
            >
              Manual Sync
            </Button>
          </span>
        </Tooltip>
        <Tooltip title="Sync Settings">
          <IconButton
            color="secondary"
            onClick={() => setSettingsOpen(true)}
            aria-label="Sync Settings"
          >
            <SettingsIcon />
          </IconButton>
        </Tooltip>
      </Box>
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)}>
        <DialogTitle>Sync Settings</DialogTitle>
        <DialogContent>
          <TextField
            label="Sync Interval (seconds)"
            type="number"
            value={intervalInput}
            onChange={handleIntervalChange}
            error={!!intervalError}
            helperText={intervalError || "Minimum: 60 seconds"}
            fullWidth
            margin="normal"
            inputProps={{ min: 60 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)} color="inherit">
            Cancel
          </Button>
          <Button
            onClick={handleIntervalSave}
            color="primary"
            disabled={!!intervalError || intervalInput < 60}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SyncStatusBar;