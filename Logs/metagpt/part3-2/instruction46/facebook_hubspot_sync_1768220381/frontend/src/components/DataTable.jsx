import React from "react";
import { Box, Typography, CircularProgress } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

/**
 * DataTable component for dashboard.
 * Displays ad metrics, contacts, and deals in a table.
 * Supports filtering, sorting, and loading state.
 * Uses MUI DataGrid and Tailwind CSS.
 */
const DataTable = ({ metrics, contacts, deals, loading }) => {
  // Prepare rows and columns for ad metrics
  const metricColumns = [
    { field: "campaign_id", headerName: "Campaign ID", width: 130 },
    { field: "ad_id", headerName: "Ad ID", width: 130 },
    { field: "date", headerName: "Date", width: 120 },
    { field: "clicks", headerName: "Clicks", type: "number", width: 100 },
    { field: "impressions", headerName: "Impressions", type: "number", width: 120 },
    { field: "spend", headerName: "Spend ($)", type: "number", width: 110 },
    { field: "conversions", headerName: "Conversions", type: "number", width: 120 },
  ];

  const metricRows = metrics.map((m, idx) => ({
    id: idx,
    campaign_id: m.campaign_id,
    ad_id: m.ad_id,
    date: m.date,
    clicks: m.clicks,
    impressions: m.impressions,
    spend: m.spend,
    conversions: m.conversions,
  }));

  // Prepare rows and columns for contacts
  const contactColumns = [
    { field: "id", headerName: "Contact ID", width: 120 },
    { field: "email", headerName: "Email", width: 200 },
    { field: "name", headerName: "Name", width: 180 },
    { field: "facebook_id", headerName: "Facebook ID", width: 130 },
  ];

  const contactRows = contacts.map((c, idx) => ({
    id: c.id ?? idx,
    email: c.email,
    name: c.name,
    facebook_id: c.facebook_id,
  }));

  // Prepare rows and columns for deals
  const dealColumns = [
    { field: "id", headerName: "Deal ID", width: 120 },
    { field: "contact_id", headerName: "Contact ID", width: 120 },
    { field: "amount", headerName: "Amount ($)", type: "number", width: 120 },
    { field: "stage", headerName: "Stage", width: 140 },
  ];

  const dealRows = deals.map((d, idx) => ({
    id: d.id ?? idx,
    contact_id: d.contact_id,
    amount: d.amount,
    stage: d.stage,
  }));

  return (
    <Box className="bg-white rounded-lg shadow p-4">
      <Typography variant="h6" className="mb-2 font-bold text-gray-700">
        Ad Metrics
      </Typography>
      <div style={{ height: 320, width: "100%" }} className="mb-8">
        {loading ? (
          <Box className="flex items-center justify-center h-full">
            <CircularProgress />
          </Box>
        ) : (
          <DataGrid
            rows={metricRows}
            columns={metricColumns}
            pageSize={5}
            rowsPerPageOptions={[5, 10, 20]}
            autoHeight
            disableSelectionOnClick
            sx={{
              backgroundColor: "#f9fafb",
              borderRadius: 2,
              fontFamily: "Roboto, Arial, sans-serif",
            }}
          />
        )}
      </div>

      <Typography variant="h6" className="mb-2 font-bold text-gray-700">
        Contacts
      </Typography>
      <div style={{ height: 240, width: "100%" }} className="mb-8">
        {loading ? (
          <Box className="flex items-center justify-center h-full">
            <CircularProgress />
          </Box>
        ) : (
          <DataGrid
            rows={contactRows}
            columns={contactColumns}
            pageSize={5}
            rowsPerPageOptions={[5, 10]}
            autoHeight
            disableSelectionOnClick
            sx={{
              backgroundColor: "#f9fafb",
              borderRadius: 2,
              fontFamily: "Roboto, Arial, sans-serif",
            }}
          />
        )}
      </div>

      <Typography variant="h6" className="mb-2 font-bold text-gray-700">
        Deals
      </Typography>
      <div style={{ height: 240, width: "100%" }}>
        {loading ? (
          <Box className="flex items-center justify-center h-full">
            <CircularProgress />
          </Box>
        ) : (
          <DataGrid
            rows={dealRows}
            columns={dealColumns}
            pageSize={5}
            rowsPerPageOptions={[5, 10]}
            autoHeight
            disableSelectionOnClick
            sx={{
              backgroundColor: "#f9fafb",
              borderRadius: 2,
              fontFamily: "Roboto, Arial, sans-serif",
            }}
          />
        )}
      </div>
    </Box>
  );
};

export default DataTable;