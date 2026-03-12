import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import MetricsPanel from '../components/MetricsPanel';
import ChartPanel from '../components/ChartPanel';
import DataTable from '../components/DataTable';
import ExportButton from '../components/ExportButton';
import { fetchMetrics, fetchReports, subscribeToRealtimeMetrics } from '../utils/api';
import { Metric, Report } from '../utils/types';
import styles from '../styles/globals.module.css';

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let unsubscribe: (() => void) | undefined;

    const loadData = async () => {
      setLoading(true);
      try {
        const [metricsData, reportsData] = await Promise.all([
          fetchMetrics(),
          fetchReports(),
        ]);
        setMetrics(metricsData);
        setReports(reportsData);
      } catch (err) {
        // Handle error (could show notification)
      }
      setLoading(false);
    };

    loadData();

    // Subscribe to real-time metric updates
    unsubscribe = subscribeToRealtimeMetrics((newMetric: Metric) => {
      setMetrics((prev) => [newMetric, ...prev]);
    });

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, []);

  return (
    <div className={styles.dashboardRoot}>
      <Header />
      <div className={styles.dashboardContainer}>
        <Sidebar />
        <main className={styles.dashboardMain}>
          <section className={styles.dashboardSection}>
            <h1>Dashboard</h1>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <>
                <MetricsPanel metrics={metrics} />
                <ChartPanel metrics={metrics} />
                <ExportButton reports={reports} />
                <DataTable reports={reports} />
              </>
            )}
          </section>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;