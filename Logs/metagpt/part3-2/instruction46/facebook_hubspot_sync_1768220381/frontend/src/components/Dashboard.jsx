import React from "react";
import { Container, Paper } from "@mui/material";

/**
 * Dashboard layout wrapper.
 * Uses MUI Container and Paper for structure, and Tailwind CSS for responsive styling.
 * Renders children components inside the main dashboard panel.
 */
const Dashboard = ({ children }) => {
  return (
    <Container maxWidth="xl" className="py-6">
      <Paper
        elevation={3}
        className="p-6 bg-white rounded-lg shadow-md min-h-[600px] flex flex-col"
        sx={{
          backgroundColor: "#fff",
          borderRadius: 2,
          boxShadow: 3,
        }}
      >
        {children}
      </Paper>
    </Container>
  );
};

export default Dashboard;