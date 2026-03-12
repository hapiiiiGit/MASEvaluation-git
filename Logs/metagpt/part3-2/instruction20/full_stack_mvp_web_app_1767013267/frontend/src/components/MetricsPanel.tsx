import React from 'react';
import { Metric } from '../utils/types';
import styles from '../styles/globals.module.css';

interface MetricsPanelProps {
  metrics: Metric[];
}

const MetricsPanel: React.FC<MetricsPanelProps> = ({ metrics }) => {
  // Display the latest 4 key metrics in summary cards
  const latestMetrics = metrics.slice(0, 4);

  return (
    <section className={styles.metricsPanel}>
      <h2 className={styles.metricsPanelTitle}>Key Metrics</h2>
      <div className={styles.metricsGrid}>
        {latestMetrics.length === 0 ? (
          <div className={styles.metricsEmpty}>No metrics available.</div>
        ) : (
          latestMetrics.map((metric) => (
            <div key={metric.id} className={styles.metricCard}>
              <div className={styles.metricName}>{metric.name}</div>
              <div className={styles.metricValue}>{metric.value}</div>
              <div className={styles.metricTimestamp}>
                {new Date(metric.timestamp).toLocaleString()}
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
};

export default MetricsPanel;