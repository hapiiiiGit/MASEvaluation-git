import React from "react";
import { Box, Typography, Paper, ToggleButtonGroup, ToggleButton } from "@mui/material";
import { Line, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * ChartPanel component for dashboard.
 * Visualizes ad metrics (clicks, conversions, spend) using charts.
 * Uses MUI and Tailwind CSS.
 */
const ChartPanel = ({ metrics }) => {
  const [chartType, setChartType] = React.useState("line");

  // Prepare chart data
  const labels = metrics.map((m) => m.date);
  const clicksData = metrics.map((m) => m.clicks);
  const conversionsData = metrics.map((m) => m.conversions);
  const spendData = metrics.map((m) => m.spend);

  const lineData = {
    labels,
    datasets: [
      {
        label: "Clicks",
        data: clicksData,
        borderColor: "#1976d2",
        backgroundColor: "rgba(25, 118, 210, 0.1)",
        fill: true,
        tension: 0.3,
      },
      {
        label: "Conversions",
        data: conversionsData,
        borderColor: "#43a047",
        backgroundColor: "rgba(67, 160, 71, 0.1)",
        fill: true,
        tension: 0.3,
      },
      {
        label: "Spend ($)",
        data: spendData,
        borderColor: "#fbc02d",
        backgroundColor: "rgba(251, 192, 45, 0.1)",
        fill: true,
        tension: 0.3,
        yAxisID: "y1",
      },
    ],
  };

  const barData = {
    labels,
    datasets: [
      {
        label: "Clicks",
        data: clicksData,
        backgroundColor: "#1976d2",
      },
      {
        label: "Conversions",
        data: conversionsData,
        backgroundColor: "#43a047",
      },
      {
        label: "Spend ($)",
        data: spendData,
        backgroundColor: "#fbc02d",
        yAxisID: "y1",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          font: {
            family: "Roboto, Arial, sans-serif",
          },
        },
      },
      title: {
        display: true,
        text: "Ad Performance Metrics",
        font: {
          size: 18,
          family: "Roboto, Arial, sans-serif",
        },
      },
      tooltip: {
        mode: "index",
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Count",
        },
      },
      y1: {
        beginAtZero: true,
        position: "right",
        title: {
          display: true,
          text: "Spend ($)",
        },
        grid: {
          drawOnChartArea: false,
        },
      },
      x: {
        title: {
          display: true,
          text: "Date",
        },
      },
    },
  };

  return (
    <Paper className="p-6 mb-4 bg-white rounded-lg shadow-md">
      <Box className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
        <Typography variant="h6" className="font-bold text-gray-700 mb-2 md:mb-0">
          Ad Performance Charts
        </Typography>
        <ToggleButtonGroup
          value={chartType}
          exclusive
          onChange={(_, value) => value && setChartType(value)}
          aria-label="chart type"
          size="small"
        >
          <ToggleButton value="line" aria-label="Line Chart">
            Line
          </ToggleButton>
          <ToggleButton value="bar" aria-label="Bar Chart">
            Bar
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>
      <Box className="w-full h-[350px]">
        {metrics.length === 0 ? (
          <Typography variant="body2" color="textSecondary">
            No metrics data available for selected filters.
          </Typography>
        ) : chartType === "line" ? (
          <Line data={lineData} options={options} />
        ) : (
          <Bar data={barData} options={options} />
        )}
      </Box>
    </Paper>
  );
};

export default ChartPanel;