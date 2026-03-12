import React, { useState, useEffect } from "react";
import Dashboard from "./components/Dashboard.jsx";
import FilterPanel from "./components/FilterPanel.jsx";
import DataTable from "./components/DataTable.jsx";
import ChartPanel from "./components/ChartPanel.jsx";
import SegmentationSidebar from "./components/SegmentationSidebar.jsx";
import SyncStatusBar from "./components/SyncStatusBar.jsx";
import ExportButton from "./components/ExportButton.jsx";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import "./styles/tailwind.css";
import api from "./api/api.js";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
    background: {
      default: "#f9fafb",
    },
  },
  typography: {
    fontFamily: "Roboto, Arial, sans-serif",
  },
});

function App() {
  // State for filters, metrics, contacts, deals, sync status, and segmentation
  const [filters, setFilters] = useState({
    since: null,
    until: null,
    campaign_id: "",
    ad_id: "",
  });
  const [metrics, setMetrics] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [deals, setDeals] = useState([]);
  const [syncStatus, setSyncStatus] = useState({});
  const [segmentation, setSegmentation] = useState({
    facebook_id: "",
    email: "",
    contact_id: "",
    stage: "",
  });
  const [loading, setLoading] = useState(false);

  // Fetch metrics, contacts, deals, and sync status
  const fetchAllData = async () => {
    setLoading(true);
    try {
      const metricsRes = await api.getMetrics(filters);
      setMetrics(metricsRes);

      const contactsRes = await api.getContacts({
        facebook_id: segmentation.facebook_id,
        email: segmentation.email,
      });
      setContacts(contactsRes);

      const dealsRes = await api.getDeals({
        contact_id: segmentation.contact_id,
        stage: segmentation.stage,
      });
      setDeals(dealsRes);

      const syncStatusRes = await api.getSyncStatus();
      setSyncStatus(syncStatusRes);
    } catch (err) {
      // Handle error (could use a notification system)
      console.error("Error fetching dashboard data:", err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchAllData();
    // eslint-disable-next-line
  }, [filters, segmentation]);

  // Handlers for filter and segmentation changes
  const handleFilterChange = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleSegmentationChange = (newSegmentation) => {
    setSegmentation((prev) => ({ ...prev, ...newSegmentation }));
  };

  // Manual sync trigger
  const handleManualSync = async () => {
    setLoading(true);
    try {
      await api.triggerManualSync();
      await fetchAllData();
    } catch (err) {
      console.error("Manual sync failed:", err);
    }
    setLoading(false);
  };

  // Sync interval adjustment
  const handleSyncIntervalChange = async (intervalSeconds) => {
    try {
      await api.setSyncInterval(intervalSeconds);
      await fetchAllData();
    } catch (err) {
      console.error("Failed to set sync interval:", err);
    }
  };

  // Export data handler
  const handleExport = (type) => {
    let data = [];
    if (type === "metrics") data = metrics;
    else if (type === "contacts") data = contacts;
    else if (type === "deals") data = deals;

    const csvRows = [];
    if (data.length > 0) {
      const headers = Object.keys(data[0]);
      csvRows.push(headers.join(","));
      data.forEach((row) => {
        csvRows.push(headers.map((h) => `"${row[h]}"`).join(","));
      });
      const csvContent = csvRows.join("\n");
      const blob = new Blob([csvContent], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${type}_export_${Date.now()}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="min-h-screen flex flex-col bg-gray-50">
        {/* Top Navigation: Sync Status, Manual Trigger, Settings */}
        <SyncStatusBar
          syncStatus={syncStatus}
          onManualSync={handleManualSync}
          onSyncIntervalChange={handleSyncIntervalChange}
          loading={loading}
        />

        <div className="flex flex-1">
          {/* Sidebar: Segmentation, Export */}
          <SegmentationSidebar
            segmentation={segmentation}
            onChange={handleSegmentationChange}
            onExport={handleExport}
          />

          {/* Main Panel */}
          <main className="flex-1 p-6">
            <Dashboard>
              <div className="mb-4">
                <FilterPanel filters={filters} onChange={handleFilterChange} />
              </div>
              <div className="mb-6">
                <ChartPanel metrics={metrics} />
              </div>
              <div className="mb-6">
                <DataTable
                  metrics={metrics}
                  contacts={contacts}
                  deals={deals}
                  loading={loading}
                />
              </div>
              <ExportButton onExport={handleExport} />
            </Dashboard>
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;