import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import { CssBaseline, AppBar, Toolbar, Typography, Button, Container } from "@mui/material";
import SurveyBuilder from "./components/SurveyBuilder";
import SurveyAnalytics from "./components/SurveyAnalytics";
import ExportButtons from "./components/ExportButtons";

function App() {
  return (
    <Router>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Survey Analytics MVP
          </Typography>
          <Button color="inherit" component={Link} to="/builder">
            Survey Builder
          </Button>
          <Button color="inherit" component={Link} to="/analytics">
            Analytics
          </Button>
          <Button color="inherit" component={Link} to="/export">
            Export
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<Navigate to="/builder" />} />
          <Route path="/builder" element={<SurveyBuilder />} />
          <Route path="/analytics" element={<SurveyAnalytics />} />
          <Route path="/export" element={<ExportButtons />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;