import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Divider,
} from "@mui/material";
import axios from "axios";
import { Radar } from "react-chartjs-2";
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend, CategoryScale, LinearScale } from "chart.js";
import { Heatmap } from "chartjs-chart-heatmap";
import { Chart } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale
);

// Register heatmap chart type
ChartJS.register(Heatmap);

const SurveyAnalytics = () => {
  const [surveys, setSurveys] = useState([]);
  const [selectedSurveyId, setSelectedSurveyId] = useState("");
  const [radarData, setRadarData] = useState(null);
  const [heatmapData, setHeatmapData] = useState(null);
  const [loadingSurveys, setLoadingSurveys] = useState(false);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [error, setError] = useState("");

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

  // Fetch analytics data when survey is selected
  useEffect(() => {
    if (!selectedSurveyId) {
      setRadarData(null);
      setHeatmapData(null);
      return;
    }
    const fetchAnalytics = async () => {
      setLoadingAnalytics(true);
      setError("");
      try {
        const token = localStorage.getItem("token");
        // Radar chart data
        const radarRes = await axios.get(
          `/api/survey/${selectedSurveyId}/analytics/radar`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setRadarData(radarRes.data);

        // Heatmap data
        const heatmapRes = await axios.get(
          `/api/survey/${selectedSurveyId}/analytics/heatmap`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setHeatmapData(heatmapRes.data);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            "Failed to fetch analytics data. Please check your authentication."
        );
        setRadarData(null);
        setHeatmapData(null);
      } finally {
        setLoadingAnalytics(false);
      }
    };
    fetchAnalytics();
  }, [selectedSurveyId]);

  // Prepare radar chart data for Chart.js
  const getRadarChartData = () => {
    if (!radarData) return null;
    return {
      labels: radarData.labels,
      datasets: radarData.datasets.map((ds) => ({
        ...ds,
        fill: true,
      })),
    };
  };

  // Prepare heatmap chart data for Chart.js
  const getHeatmapChartData = () => {
    if (!heatmapData || !heatmapData.x_labels.length || !heatmapData.y_labels.length) return null;
    // Chart.js heatmap expects data as {x, y, v}
    const dataPoints = [];
    for (let i = 0; i < heatmapData.y_labels.length; i++) {
      for (let j = 0; j < heatmapData.x_labels.length; j++) {
        dataPoints.push({
          x: heatmapData.x_labels[j],
          y: heatmapData.y_labels[i],
          v: heatmapData.data[i][j],
        });
      }
    }
    return {
      datasets: [
        {
          label: "Responses Heatmap",
          data: dataPoints,
          backgroundColor: (ctx) => {
            // Color scale based on value
            const value = ctx.dataset.data[ctx.dataIndex]?.v || 0;
            if (value === 0) return "#f0f0f0";
            if (value < 2) return "#b3c6ff";
            if (value < 5) return "#6699ff";
            return "#0033cc";
          },
          borderWidth: 1,
        },
      ],
    };
  };

  const heatmapOptions = {
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: function (context) {
            const { x, y, v } = context.raw;
            return `Q: ${x}, Option: ${y}, Count: ${v}`;
          },
        },
      },
    },
    scales: {
      x: {
        type: "category",
        labels: heatmapData?.x_labels || [],
        title: { display: true, text: "Questions" },
      },
      y: {
        type: "category",
        labels: heatmapData?.y_labels || [],
        title: { display: true, text: "Options" },
      },
    },
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Survey Analytics
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
        {loadingAnalytics && (
          <Box sx={{ display: "flex", justifyContent: "center", my: 4 }}>
            <CircularProgress />
          </Box>
        )}
        {!loadingAnalytics && selectedSurveyId && (
          <>
            <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
              Radar Chart (Average Scores)
            </Typography>
            {radarData && radarData.labels.length ? (
              <Radar
                data={getRadarChartData()}
                options={{
                  responsive: true,
                  plugins: {
                    legend: { position: "top" },
                  },
                  scales: {
                    r: {
                      beginAtZero: true,
                      min: 0,
                      max: 5,
                    },
                  },
                }}
                style={{ maxHeight: 400 }}
              />
            ) : (
              <Typography variant="body2" color="textSecondary">
                No radar chart data available for this survey.
              </Typography>
            )}
            <Divider sx={{ my: 3 }} />
            <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
              Heatmap (Response Frequency)
            </Typography>
            {heatmapData && heatmapData.x_labels.length && heatmapData.y_labels.length ? (
              <Chart
                type="heatmap"
                data={getHeatmapChartData()}
                options={heatmapOptions}
                style={{ maxHeight: 400 }}
              />
            ) : (
              <Typography variant="body2" color="textSecondary">
                No heatmap data available for this survey.
              </Typography>
            )}
          </>
        )}
      </Paper>
    </Container>
  );
};

export default SurveyAnalytics;