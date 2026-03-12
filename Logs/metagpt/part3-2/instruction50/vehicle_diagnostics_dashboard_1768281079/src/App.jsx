import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from "@mui/material";
import { styled } from "@mui/material/styles";

// Tailwind utility classes can be used alongside MUI components

const DiagnosticsPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginTop: theme.spacing(4),
  boxShadow: theme.shadows[2],
}));

const initialSensorData = {
  rpm: "",
  speed: "",
  coolant_temp: "",
  throttle_pos: "",
  maf: "",
  intake_pressure: "",
  o2_voltage: "",
  fuel_level: "",
  dtc_codes: "",
};

const API_BASE_URL = "http://localhost:8000"; // Update if API runs elsewhere

function App() {
  const [sensorData, setSensorData] = useState(initialSensorData);
  const [diagnostics, setDiagnostics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [modelInfo, setModelInfo] = useState(null);

  // Fetch model info on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/model/info`)
      .then((res) => {
        if (!res.ok) throw new Error("Model info not available");
        return res.json();
      })
      .then((data) => setModelInfo(data))
      .catch(() => setModelInfo(null));
  }, []);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setSensorData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Parse DTC codes from comma-separated string
  const parseDtcCodes = (dtcString) => {
    return dtcString
      .split(",")
      .map((code) => code.trim())
      .filter((code) => code.length > 0);
  };

  // Submit sensor data to API
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setApiError("");
    setDiagnostics(null);

    // Prepare payload
    const payload = {
      ...sensorData,
      rpm: parseFloat(sensorData.rpm),
      speed: parseFloat(sensorData.speed),
      coolant_temp: parseFloat(sensorData.coolant_temp),
      throttle_pos: parseFloat(sensorData.throttle_pos),
      maf: parseFloat(sensorData.maf),
      intake_pressure: parseFloat(sensorData.intake_pressure),
      o2_voltage: parseFloat(sensorData.o2_voltage),
      fuel_level: parseFloat(sensorData.fuel_level),
      dtc_codes: sensorData.dtc_codes
        ? parseDtcCodes(sensorData.dtc_codes)
        : [],
    };

    try {
      const res = await fetch(`${API_BASE_URL}/diagnostics`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "API error");
      }
      const data = await res.json();
      setDiagnostics(data);
    } catch (err) {
      setApiError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" className="min-h-screen py-8">
      <Typography
        variant="h3"
        component="h1"
        gutterBottom
        className="text-center font-bold text-blue-700"
      >
        Vehicle Diagnostics Dashboard
      </Typography>
      <Typography
        variant="subtitle1"
        className="text-center mb-6 text-gray-600"
      >
        Real-time fault detection and anomaly classification powered by AI
      </Typography>

      <DiagnosticsPaper elevation={3}>
        <Typography variant="h6" gutterBottom>
          Input Vehicle Sensor Data
        </Typography>
        <Box component="form" onSubmit={handleSubmit} autoComplete="off">
          <Grid container spacing={2}>
            <Grid item xs={6} sm={4}>
              <TextField
                label="Engine RPM"
                name="rpm"
                type="number"
                required
                fullWidth
                value={sensorData.rpm}
                onChange={handleChange}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField
                label="Speed (km/h)"
                name="speed"
                type="number"
                required
                fullWidth
                value={sensorData.speed}
                onChange={handleChange}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField
                label="Coolant Temp (°C)"
                name="coolant_temp"
                type="number"
                required
                fullWidth
                value={sensorData.coolant_temp}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField
                label="Throttle Position (%)"
                name="throttle_pos"
                type="number"
                required
                fullWidth
                value={sensorData.throttle_pos}
                onChange={handleChange}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField
                label="Mass Air Flow (g/s)"
                name="maf"
                type="number"
                required
                fullWidth
                value={sensorData.maf}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField
                label="Intake Pressure (kPa)"
                name="intake_pressure"
                type="number"
                required
                fullWidth
                value={sensorData.intake_pressure}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField
                label="O2 Sensor Voltage (V)"
                name="o2_voltage"
                type="number"
                required
                fullWidth
                value={sensorData.o2_voltage}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={6} sm={4}>
              <TextField
                label="Fuel Level (%)"
                name="fuel_level"
                type="number"
                required
                fullWidth
                value={sensorData.fuel_level}
                onChange={handleChange}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={12} sm={8}>
              <TextField
                label="DTC Codes (comma separated)"
                name="dtc_codes"
                type="text"
                fullWidth
                value={sensorData.dtc_codes}
                onChange={handleChange}
                placeholder="e.g. P0300,P0420"
              />
            </Grid>
            <Grid item xs={12}>
              <Box className="flex justify-end">
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={loading}
                  size="large"
                  className="bg-blue-600"
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} color="inherit" />
                      &nbsp;Analyzing...
                    </>
                  ) : (
                    "Run Diagnostics"
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
        {apiError && (
          <Box mt={3}>
            <Alert severity="error">{apiError}</Alert>
          </Box>
        )}
      </DiagnosticsPaper>

      <Divider className="my-8" />

      <Paper elevation={2} className="p-6 mt-4 bg-white">
        <Typography variant="h6" gutterBottom>
          Diagnostics Result
        </Typography>
        {!diagnostics && !loading && (
          <Typography color="textSecondary">
            Enter sensor data and run diagnostics to see results here.
          </Typography>
        )}
        {diagnostics && (
          <Box mt={2}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle1" className="font-semibold">
                  Fault Detected:
                </Typography>
                {diagnostics.fault_detected ? (
                  <Chip
                    label="Fault"
                    color="error"
                    className="font-bold"
                    size="medium"
                  />
                ) : (
                  <Chip
                    label="No Fault"
                    color="success"
                    className="font-bold"
                    size="medium"
                  />
                )}
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle1" className="font-semibold">
                  Anomaly Score:
                </Typography>
                <Chip
                  label={diagnostics.anomaly_score.toFixed(3)}
                  color={
                    diagnostics.anomaly_score > 0.7
                      ? "error"
                      : diagnostics.anomaly_score > 0.4
                      ? "warning"
                      : "success"
                  }
                  className="font-bold"
                  size="medium"
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" className="font-semibold">
                  Fault Type:
                </Typography>
                <Typography>
                  {diagnostics.fault_type || "N/A"}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" className="font-semibold">
                  Recommended Action:
                </Typography>
                <Typography>
                  {diagnostics.recommended_action || "N/A"}
                </Typography>
              </Grid>
              {diagnostics.details && diagnostics.details.dtc_codes && (
                <Grid item xs={12}>
                  <Typography variant="subtitle1" className="font-semibold">
                    DTC Codes:
                  </Typography>
                  <Box className="flex flex-wrap gap-2 mt-1">
                    {diagnostics.details.dtc_codes.map((code) => (
                      <Chip key={code} label={code} color="info" />
                    ))}
                  </Box>
                </Grid>
              )}
            </Grid>
          </Box>
        )}
      </Paper>

      <Divider className="my-8" />

      <Paper elevation={1} className="p-4 mt-4 bg-gray-50">
        <Typography variant="h6" gutterBottom>
          Model Information
        </Typography>
        {modelInfo ? (
          <Box>
            <Typography>
              <strong>Name:</strong> {modelInfo.model_name}
            </Typography>
            <Typography>
              <strong>Version:</strong> {modelInfo.version}
            </Typography>
            <Typography>
              <strong>Trained On:</strong> {modelInfo.trained_on}
            </Typography>
            <Typography>
              <strong>Description:</strong> {modelInfo.description}
            </Typography>
            <Typography>
              <strong>Features:</strong>
            </Typography>
            <Box className="flex flex-wrap gap-2 mt-1">
              {modelInfo.features.map((feature) => (
                <Chip key={feature} label={feature} variant="outlined" />
              ))}
            </Box>
          </Box>
        ) : (
          <Typography color="textSecondary">
            Model information is not available.
          </Typography>
        )}
      </Paper>
    </Container>
  );
}

export default App;