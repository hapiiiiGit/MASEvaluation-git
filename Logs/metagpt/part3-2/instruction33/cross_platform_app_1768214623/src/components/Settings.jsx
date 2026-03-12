import React, { useContext, useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Divider,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Switch,
  Select,
  MenuItem,
  Button,
  TextField,
} from "@mui/material";
import { ThemeContext } from "../context/ThemeContext";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

// Supported languages
const languages = [
  { code: "en", label: "English" },
  { code: "es", label: "Español" },
];

// Accessibility options
const accessibilityOptions = [
  { key: "highContrast", label: "High Contrast Mode" },
  { key: "largeText", label: "Large Text" },
  { key: "screenReader", label: "Screen Reader Support" },
];

const Settings = () => {
  const { theme, setTheme } = useContext(ThemeContext);
  const { user, logout } = useContext(AuthContext);
  const [language, setLanguage] = useState("en");
  const [accessibility, setAccessibility] = useState({
    highContrast: false,
    largeText: false,
    screenReader: false,
  });
  const [profile, setProfile] = useState({
    name: user?.name || "",
    email: user?.email || "",
  });
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  // Handle theme change
  const handleThemeChange = (event) => {
    setTheme(event.target.value);
  };

  // Handle language change
  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
  };

  // Handle accessibility option change
  const handleAccessibilityChange = (key) => (event) => {
    setAccessibility((prev) => ({
      ...prev,
      [key]: event.target.checked,
    }));
  };

  // Handle profile change
  const handleProfileChange = (field) => (event) => {
    setProfile((prev) => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  // Simulate save settings
  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      // In production, call API to save settings
    }, 1000);
  };

  return (
    <Box
      className="w-full max-w-2xl mx-auto py-6 px-4"
      sx={{ bgcolor: "background.default" }}
      aria-label="Settings page"
    >
      <Typography variant="h4" color="primary" fontWeight={700} gutterBottom>
        Settings
      </Typography>
      <Paper elevation={2} className="p-6 mb-6" sx={{ borderRadius: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Profile
        </Typography>
        <Divider className="mb-4" />
        <Box className="flex flex-col gap-4">
          <TextField
            label="Name"
            value={profile.name}
            onChange={handleProfileChange("name")}
            variant="outlined"
            fullWidth
            autoComplete="name"
            aria-label="Name"
          />
          <TextField
            label="Email"
            value={profile.email}
            onChange={handleProfileChange("email")}
            variant="outlined"
            fullWidth
            autoComplete="email"
            aria-label="Email"
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSave}
            disabled={saving}
            sx={{ alignSelf: "flex-start" }}
            aria-label="Save profile"
          >
            {saving ? "Saving..." : "Save Profile"}
          </Button>
        </Box>
      </Paper>

      <Paper elevation={2} className="p-6 mb-6" sx={{ borderRadius: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Theme
        </Typography>
        <Divider className="mb-4" />
        <FormControl component="fieldset">
          <FormLabel component="legend">Select Theme</FormLabel>
          <RadioGroup
            row
            value={theme}
            onChange={handleThemeChange}
            aria-label="Theme selection"
          >
            <FormControlLabel
              value="light"
              control={<Radio />}
              label="Light"
            />
            <FormControlLabel
              value="dark"
              control={<Radio />}
              label="Dark"
            />
            <FormControlLabel
              value="system"
              control={<Radio />}
              label="System"
            />
          </RadioGroup>
        </FormControl>
      </Paper>

      <Paper elevation={2} className="p-6 mb-6" sx={{ borderRadius: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Language
        </Typography>
        <Divider className="mb-4" />
        <FormControl fullWidth>
          <FormLabel>Select Language</FormLabel>
          <Select
            value={language}
            onChange={handleLanguageChange}
            aria-label="Language selection"
          >
            {languages.map((lang) => (
              <MenuItem key={lang.code} value={lang.code}>
                {lang.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Paper>

      <Paper elevation={2} className="p-6 mb-6" sx={{ borderRadius: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Accessibility
        </Typography>
        <Divider className="mb-4" />
        <Box className="flex flex-col gap-3">
          {accessibilityOptions.map((option) => (
            <FormControlLabel
              key={option.key}
              control={
                <Switch
                  checked={accessibility[option.key]}
                  onChange={handleAccessibilityChange(option.key)}
                  color="primary"
                  aria-label={option.label}
                />
              }
              label={option.label}
            />
          ))}
        </Box>
      </Paper>

      <Box className="flex justify-between items-center mt-8">
        <Button
          variant="outlined"
          color="secondary"
          onClick={() => {
            logout();
            navigate("/");
          }}
          aria-label="Logout"
        >
          Logout
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          disabled={saving}
          aria-label="Save all settings"
        >
          {saving ? "Saving..." : "Save All Settings"}
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;