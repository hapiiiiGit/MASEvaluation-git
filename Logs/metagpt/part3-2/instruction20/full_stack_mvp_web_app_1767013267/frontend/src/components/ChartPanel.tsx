import React from 'react';
import { Metric } from '../utils/types';
import styles from '../styles/globals.module.css';

// Import a chart library (e.g., Chart.js via react-chartjs-2)
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ChartPanelProps {
  metrics: Metric[];
}

const ChartPanel: React.FC<ChartPanelProps> = ({ metrics }) => {
  // Prepare data for the chart
  // Group metrics by name, and plot the latest 20 points for each metric type
  const metricNames = Array.from(new Set(metrics.map((m) => m.name)));
  const chartDataSets = metricNames.map((name, idx) => {
    const colorPalette = [
      'rgba(75,192,192,1)',
      'rgba(255,99,132,1)',
      'rgba(54,162,235,1)',
      'rgba(255,206,86,1)',
      'rgba(153,102,255,1)',
      'rgba(255,159,64,1)',
    ];
    const filtered = metrics
      .filter((m) => m.name === name)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .slice(-20);

    return {
      label: name,
      data: filtered.map((m) => m.value),
      fill: false,
      borderColor: colorPalette[idx % colorPalette.length],
      backgroundColor: colorPalette[idx % colorPalette.length],
      tension: 0.2,
    };
  });

  // X-axis labels: timestamps of the latest 20 points (assuming all metrics have similar timestamps)
  const latestMetrics = metrics
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    .slice(-20);
  const labels = latestMetrics.map((m) =>
    new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  );

  const data = {
    labels,
    datasets: chartDataSets,
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Metrics Over Time',
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Time',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Value',
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <section className={styles.chartPanel}>
      <h2 className={styles.chartPanelTitle}>Metrics Chart</h2>
      {metrics.length === 0 ? (
        <div className={styles.chartPanelEmpty}>No metrics data available for chart.</div>
      ) : (
        <div className={styles.chartPanelChart}>
          <Line data={data} options={options} />
        </div>
      )}
    </section>
  );
};

export default ChartPanel;