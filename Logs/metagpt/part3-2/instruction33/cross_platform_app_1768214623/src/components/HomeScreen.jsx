import React from "react";
import { useMediaQuery, Box, Typography, Grid, Card, CardContent, CardActionArea } from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";
import SettingsIcon from "@mui/icons-material/Settings";
import NotificationsIcon from "@mui/icons-material/Notifications";
import PersonIcon from "@mui/icons-material/Person";
import AccessibilityNewIcon from "@mui/icons-material/AccessibilityNew";
import { useNavigate } from "react-router-dom";

/**
 * Main home screen content for the cross-platform app.
 * Responsive, accessible, and adaptive for desktop and mobile.
 * Includes welcome message, feature cards, and accessibility highlights.
 */
const features = [
  {
    label: "Settings",
    description: "Manage your preferences and profile.",
    icon: <SettingsIcon fontSize="large" color="primary" />,
    route: "/settings",
  },
  {
    label: "Notifications",
    description: "View your latest notifications.",
    icon: <NotificationsIcon fontSize="large" color="primary" />,
    route: "/notifications",
  },
  {
    label: "Profile",
    description: "Access and update your profile.",
    icon: <PersonIcon fontSize="large" color="primary" />,
    route: "/profile",
  },
  {
    label: "Accessibility",
    description: "Customize accessibility options.",
    icon: <AccessibilityNewIcon fontSize="large" color="primary" />,
    route: "/accessibility",
  },
];

const HomeScreen = () => {
  const isMobile = useMediaQuery("(max-width:900px)");
  const navigate = useNavigate();

  return (
    <Box
      className="w-full h-full flex flex-col items-center justify-start"
      sx={{
        px: isMobile ? 2 : 6,
        py: isMobile ? 2 : 4,
        minHeight: "80vh",
        width: "100%",
        bgcolor: "background.default",
      }}
      aria-label="Home screen"
    >
      <Box
        className="flex items-center gap-2 mb-6"
        sx={{
          width: "100%",
          justifyContent: isMobile ? "center" : "flex-start",
        }}
      >
        <HomeIcon color="primary" fontSize="large" />
        <Typography
          variant={isMobile ? "h5" : "h4"}
          component="h1"
          fontWeight={700}
          color="primary"
        >
          Welcome to Cross Platform App
        </Typography>
      </Box>
      <Typography
        variant="body1"
        className="mb-8 text-gray-700"
        sx={{ textAlign: isMobile ? "center" : "left", maxWidth: 600 }}
      >
        Seamlessly access your features across Windows, macOS, ChromeOS, Android, and iOS. Enjoy a unified, intuitive, and accessible experience on any device.
      </Typography>
      <Grid
        container
        spacing={isMobile ? 2 : 4}
        justifyContent={isMobile ? "center" : "flex-start"}
        alignItems="stretch"
        sx={{ maxWidth: 900 }}
      >
        {features.map((feature) => (
          <Grid item xs={12} sm={6} md={3} key={feature.label}>
            <Card
              className="shadow-md hover:shadow-lg transition-shadow"
              sx={{
                borderRadius: 3,
                bgcolor: "background.paper",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
              tabIndex={0}
              aria-label={`Go to ${feature.label}`}
            >
              <CardActionArea
                onClick={() => navigate(feature.route)}
                sx={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  py: 3,
                }}
              >
                {feature.icon}
                <Typography
                  variant="h6"
                  fontWeight={600}
                  color="primary"
                  className="mt-2"
                >
                  {feature.label}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  className="mt-1 text-center"
                  sx={{ px: 1 }}
                >
                  {feature.description}
                </Typography>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Box
        className="mt-10 w-full flex flex-col items-center"
        sx={{ maxWidth: 600 }}
      >
        <Typography
          variant="subtitle1"
          color="secondary"
          fontWeight={500}
          className="mb-2"
        >
          Accessibility Highlights
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ textAlign: "center" }}
        >
          This app is designed to meet WCAG 2.1 AA accessibility standards. Use keyboard navigation, screen reader support, and customizable accessibility options for an inclusive experience.
        </Typography>
      </Box>
    </Box>
  );
};

export default HomeScreen;