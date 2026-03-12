import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import "./index.css";

// Create a MUI theme with Roboto font and light palette
const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#009688",
    },
    background: {
      default: "#f9fafb",
      paper: "#fff",
    },
  },
  typography: {
    fontFamily: [
      "Roboto",
      "ui-sans-serif",
      "system-ui",
      "Arial",
      "sans-serif",
    ].join(","),
  },
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);