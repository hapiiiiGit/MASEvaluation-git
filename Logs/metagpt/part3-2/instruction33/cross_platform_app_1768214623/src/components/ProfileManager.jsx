import React, { useContext, useState, useRef } from "react";
import {
  Box,
  Typography,
  Paper,
  Divider,
  TextField,
  Button,
  Avatar,
  IconButton,
  Tooltip,
  CircularProgress,
} from "@mui/material";
import PhotoCameraIcon from "@mui/icons-material/PhotoCamera";
import { AuthContext } from "../context/AuthContext";

const ProfileManager = () => {
  const { user, updateProfile } = useContext(AuthContext);

  // Local state for form fields
  const [form, setForm] = useState({
    name: user?.name || "",
    email: user?.email || "",
    password: "",
    avatar: user?.avatar || "",
  });
  const [avatarPreview, setAvatarPreview] = useState(user?.avatar || "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  // Handle input changes
  const handleChange = (field) => (event) => {
    setForm((prev) => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  // Handle avatar upload
  const handleAvatarChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setAvatarPreview(e.target.result);
        setForm((prev) => ({
          ...prev,
          avatar: e.target.result,
        }));
      };
      reader.readAsDataURL(file);
    } else {
      setError("Please select a valid image file.");
    }
  };

  // Handle save
  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      // In production, call updateProfile(form)
      setSaving(false);
    } catch (e) {
      setError("Failed to save profile. Please try again.");
      setSaving(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    setForm({
      name: user?.name || "",
      email: user?.email || "",
      password: "",
      avatar: user?.avatar || "",
    });
    setAvatarPreview(user?.avatar || "");
    setError("");
  };

  return (
    <Box
      className="w-full max-w-xl mx-auto py-6 px-4"
      sx={{ bgcolor: "background.default" }}
      aria-label="Profile management page"
    >
      <Typography variant="h4" color="primary" fontWeight={700} gutterBottom>
        Profile Management
      </Typography>
      <Paper elevation={2} className="p-6" sx={{ borderRadius: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Update Your Information
        </Typography>
        <Divider className="mb-4" />
        <Box className="flex flex-col gap-6">
          <Box className="flex items-center gap-4">
            <Avatar
              src={avatarPreview}
              alt={form.name || "User Avatar"}
              sx={{ width: 72, height: 72, bgcolor: "primary.main" }}
            />
            <input
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              ref={fileInputRef}
              onChange={handleAvatarChange}
              aria-label="Upload avatar"
            />
            <Tooltip title="Upload new avatar">
              <IconButton
                color="primary"
                onClick={() => fileInputRef.current && fileInputRef.current.click()}
                aria-label="Upload avatar"
                size="large"
              >
                <PhotoCameraIcon />
              </IconButton>
            </Tooltip>
          </Box>
          <TextField
            label="Name"
            value={form.name}
            onChange={handleChange("name")}
            variant="outlined"
            fullWidth
            autoComplete="name"
            aria-label="Name"
          />
          <TextField
            label="Email"
            value={form.email}
            onChange={handleChange("email")}
            variant="outlined"
            fullWidth
            autoComplete="email"
            aria-label="Email"
            type="email"
          />
          <TextField
            label="Password"
            value={form.password}
            onChange={handleChange("password")}
            variant="outlined"
            fullWidth
            autoComplete="new-password"
            aria-label="Password"
            type="password"
            helperText="Leave blank to keep current password."
          />
          {error && (
            <Typography color="error" variant="body2" className="mb-2">
              {error}
            </Typography>
          )}
          <Box className="flex gap-4 justify-end mt-4">
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleCancel}
              disabled={saving}
              aria-label="Cancel"
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
              disabled={saving}
              aria-label="Save profile"
              startIcon={saving ? <CircularProgress size={20} /> : null}
            >
              {saving ? "Saving..." : "Save"}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default ProfileManager;