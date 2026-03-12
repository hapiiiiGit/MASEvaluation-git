import React, { useState, useContext } from "react";
import {
  Box,
  Typography,
  Paper,
  Divider,
  FormControlLabel,
  Switch,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from "@mui/material";
import ContrastIcon from "@mui/icons-material/Contrast";
import FormatSizeIcon from "@mui/icons-material/FormatSize";
import RecordVoiceOverIcon from "@mui/icons-material/RecordVoiceOver";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { ThemeContext } from "../context/ThemeContext";

const accessibilityFeatures = [
  {
    key: "highContrast",
    label: "High Contrast Mode",
    description: "Improves visibility for users with low vision.",
    icon: <ContrastIcon color="primary" />,
  },
  {
    key: "largeText",
    label: "Large Text",
    description: "Increases font size for better readability.",
    icon: <FormatSizeIcon color="primary" />,
  },
  {
    key: "screenReader",
    label: "Screen Reader Support",
    description: "Optimizes app for screen readers.",
    icon: <RecordVoiceOverIcon color="primary" />,
  },
];

const AccessibilityOptions = () => {
  const { theme, setTheme } = useContext(ThemeContext);
  const [options, setOptions] = useState({
    highContrast: false,
    largeText: false,
    screenReader: false,
  });
  const [saving, setSaving] = useState(false);

  // Handle toggle change
  const handleToggle = (key) => (event) => {
    setOptions((prev) => ({
      ...prev,
      [key]: event.target.checked,
    }));
    // Optionally, update theme for high contrast
    if (key === "highContrast") {
      setTheme(event.target.checked ? "highContrast" : "light");
    }
  };

  // Simulate save
  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      // In production, save accessibility options to backend or context
    }, 1000);
  };

  return (
    <Box
      className="w-full max-w-xl mx-auto py-6 px-4"
      sx={{ bgcolor: "background.default" }}
      aria-label="Accessibility options page"
    >
      <Typography variant="h4" color="primary" fontWeight={700} gutterBottom>
        Accessibility Options
      </Typography>
      <Paper elevation={2} className="p-6 mb-6" sx={{ borderRadius: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Customize Accessibility
        </Typography>
        <Divider className="mb-4" />
        <Box className="flex flex-col gap-3">
          {accessibilityFeatures.map((feature) => (
            <FormControlLabel
              key={feature.key}
              control={
                <Switch
                  checked={options[feature.key]}
                  onChange={handleToggle(feature.key)}
                  color="primary"
                  aria-label={feature.label}
                />
              }
              label={
                <Box className="flex items-center gap-2">
                  {feature.icon}
                  <Typography variant="body1">{feature.label}</Typography>
                </Box>
              }
            />
          ))}
        </Box>
        <Box className="flex justify-end mt-6">
          <Button
            variant="contained"
            color="primary"
            onClick={handleSave}
            disabled={saving}
            aria-label="Save accessibility settings"
            startIcon={saving ? <CheckCircleIcon /> : null}
          >
            {saving ? "Saving..." : "Save Settings"}
          </Button>
        </Box>
      </Paper>
      <Paper elevation={1} className="p-4" sx={{ borderRadius: 3 }}>
        <Typography variant="subtitle1" color="secondary" fontWeight={500} gutterBottom>
          Accessibility Features Summary
        </Typography>
        <List>
          {accessibilityFeatures.map((feature) => (
            <ListItem key={feature.key} disableGutters>
              <ListItemIcon>{feature.icon}</ListItemIcon>
              <ListItemText
                primary={feature.label}
                secondary={feature.description}
                primaryTypographyProps={{ fontWeight: 600 }}
              />
              {options[feature.key] && (
                <Tooltip title="Enabled">
                  <CheckCircleIcon color="success" />
                </Tooltip>
              )}
            </ListItem>
          ))}
        </List>
        <Divider className="my-2" />
        <Typography variant="body2" color="text.secondary">
          This app is designed to meet WCAG 2.1 AA accessibility standards. Use these options to tailor your experience for maximum comfort and usability.
        </Typography>
      </Paper>
    </Box>
  );
};

export default AccessibilityOptions;