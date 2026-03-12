import React, { useState } from 'react';
import { Report } from '../utils/types';
import styles from '../styles/globals.module.css';
import { exportReport } from '../utils/api';

interface ExportButtonProps {
  reports: Report[];
}

const ExportButton: React.FC<ExportButtonProps> = ({ reports }) => {
  const [exporting, setExporting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async (format: 'csv' | 'pdf') => {
    setExporting(true);
    setError(null);
    try {
      if (!reports || reports.length === 0) {
        setError('No reports available to export.');
        setExporting(false);
        return;
      }
      // Export the latest report
      const report = reports[0];
      const fileBlob = await exportReport(report.id, format);
      const url = window.URL.createObjectURL(fileBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${report.title || 'report'}_${new Date(report.created_at).toISOString().slice(0, 19).replace(/[:T]/g, '-')}.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export report.');
    }
    setExporting(false);
  };

  return (
    <div className={styles.exportButtonContainer}>
      <button
        className={styles.exportBtn}
        onClick={() => handleExport('csv')}
        disabled={exporting || !reports || reports.length === 0}
        aria-label="Export as CSV"
      >
        Export CSV
      </button>
      <button
        className={styles.exportBtn}
        onClick={() => handleExport('pdf')}
        disabled={exporting || !reports || reports.length === 0}
        aria-label="Export as PDF"
      >
        Export PDF
      </button>
      {exporting && <span className={styles.exportingText}>Exporting...</span>}
      {error && <span className={styles.exportError}>{error}</span>}
    </div>
  );
};

export default ExportButton;