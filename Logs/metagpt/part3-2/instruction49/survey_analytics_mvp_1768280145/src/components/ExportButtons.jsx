import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Divider,
  Stack,
} from "@mui/material";
import axios from "axios";

const ExportButtons = () => {
  const [surveys, setSurveys] = useState([]);
  const [selectedSurveyId, setSelectedSurveyId] = useState("");
  const [loadingSurveys, setLoadingSurveys] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Fetch surveys for selection
  useEffect(() => {
    const fetchSurveys = async () => {
      setLoadingSurveys(true);
      setError("");
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("/api/survey/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setSurveys(res.data);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            "Failed to fetch surveys. Please check your authentication."
        );
      } finally {
        setLoadingSurveys(false);
      }
    };
    fetchSurveys();
  }, []);

  // Download file helper
  const downloadFile = async (type) => {
    if (!selectedSurveyId) {
      setMessage("Please select a survey.");
      return;
    }
    setDownloading(true);
    setMessage("");
    setError("");
    try {
      const token = localStorage.getItem("token");
      const url =
        type === "pdf"
          ? `/api/survey/${selectedSurveyId}/report/pdf`
          : `/api/survey/${selectedSurveyId}/report/csv`;
      const res = await axios.get(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        responseType: "blob",
      });
      // Get filename from content-disposition
      let filename = "";
      const disposition = res.headers["content-disposition"];
      if (disposition) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }
      if (!filename) filename = `survey_report.${type}`;
      // Download
      const urlBlob = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = urlBlob;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      setMessage(`Downloaded ${filename} successfully.`);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          `Failed to download ${type.toUpperCase()} report.`
      );
    } finally {
      setDownloading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Export Survey Results
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="survey-select-label">Select Survey</InputLabel>
          <Select
            labelId="survey-select-label"
            value={selectedSurveyId}
            label="Select Survey"
            onChange={(e) => setSelectedSurveyId(e.target.value)}
            disabled={loadingSurveys}
          >
            {surveys.map((survey) => (
              <MenuItem key={survey.id} value={survey.id}>
                {survey.title}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}
        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
          <Button
            variant="contained"
            color="primary"
            disabled={!selectedSurveyId || downloading}
            onClick={() => downloadFile("pdf")}
          >
            {downloading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              "Download PDF"
            )}
          </Button>
          <Button
            variant="contained"
            color="secondary"
            disabled={!selectedSurveyId || downloading}
            onClick={() => downloadFile("csv")}
          >
            {downloading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              "Download CSV"
            )}
          </Button>
        </Stack>
        {message && (
          <Typography color="success.main" sx={{ mt: 2 }}>
            {message}
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default ExportButtons;