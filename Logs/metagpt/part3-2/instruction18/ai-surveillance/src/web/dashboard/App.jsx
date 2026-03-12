import React, { useEffect, useState } from "react";
import AlertList from "./components/AlertList";
import VideoFeed from "./components/VideoFeed";
import "./styles.css";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

function App() {
  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState({ alert_count: 0, uptime_seconds: 0 });
  const [error, setError] = useState(null);

  // Fetch alerts periodically
  useEffect(() => {
    let isMounted = true;
    const fetchAlerts = async () => {
      try {
        const res = await fetch(`${API_BASE}/alerts`);
        if (!res.ok) throw new Error("Failed to fetch alerts");
        const data = await res.json();
        if (isMounted) setAlerts(data);
      } catch (err) {
        if (isMounted) setError("Error fetching alerts");
      }
    };
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Fetch metrics periodically
  useEffect(() => {
    let isMounted = true;
    const fetchMetrics = async () => {
      try {
        const res = await fetch(`${API_BASE}/metrics`);
        if (!res.ok) throw new Error("Failed to fetch metrics");
        const data = await res.json();
        if (isMounted) setMetrics(data);
      } catch (err) {
        if (isMounted) setError("Error fetching metrics");
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Format uptime in human-readable form
  const formatUptime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h}h ${m}m ${s}s`;
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>AI Surveillance Dashboard</h1>
      </header>
      <main className="dashboard-main">
        <section className="dashboard-section video-section">
          <h2>Live Video Feed</h2>
          <VideoFeed src={`${API_BASE}/video_feed`} />
        </section>
        <section className="dashboard-section alerts-section">
          <h2>Alerts</h2>
          {error && <div className="error">{error}</div>}
          <AlertList alerts={alerts} />
        </section>
        <section className="dashboard-section metrics-section">
          <h2>System Metrics</h2>
          <ul>
            <li>
              <strong>Total Alerts:</strong> {metrics.alert_count}
            </li>
            <li>
              <strong>Uptime:</strong> {formatUptime(metrics.uptime_seconds)}
            </li>
          </ul>
        </section>
      </main>
      <footer className="dashboard-footer">
        &copy; {new Date().getFullYear()} AI Surveillance System
      </footer>
    </div>
  );
}

export default App;