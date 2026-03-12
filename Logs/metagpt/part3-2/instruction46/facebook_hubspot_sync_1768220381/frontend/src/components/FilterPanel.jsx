import React from "react";
import { Box, TextField, Button, Grid } from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";

/**
 * FilterPanel component for dashboard.
 * Provides controls for date range, campaign ID, and ad ID filtering.
 * Uses MUI and Tailwind CSS.
 */
const FilterPanel = ({ filters, onChange }) => {
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    onChange({ [name]: value });
  };

  const handleDateChange = (name, value) => {
    onChange({ [name]: value });
  };

  const handleReset = () => {
    onChange({
      since: null,
      until: null,
      campaign_id: "",
      ad_id: "",
    });
  };

  return (
    <Box className="bg-gray-100 rounded-lg p-4 shadow flex flex-col md:flex-row items-center gap-4">
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <DatePicker
              label="Start Date"
              value={filters.since}
              onChange={(date) => handleDateChange("since", date)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  size="small"
                  fullWidth
                  variant="outlined"
                  name="since"
                />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <DatePicker
              label="End Date"
              value={filters.until}
              onChange={(date) => handleDateChange("until", date)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  size="small"
                  fullWidth
                  variant="outlined"
                  name="until"
                />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField
              label="Campaign ID"
              name="campaign_id"
              value={filters.campaign_id}
              onChange={handleInputChange}
              size="small"
              fullWidth
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField
              label="Ad ID"
              name="ad_id"
              value={filters.ad_id}
              onChange={handleInputChange}
              size="small"
              fullWidth
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              variant="outlined"
              color="primary"
              onClick={handleReset}
              className="w-full"
            >
              Reset
            </Button>
          </Grid>
        </Grid>
      </LocalizationProvider>
    </Box>
  );
};

export default FilterPanel;