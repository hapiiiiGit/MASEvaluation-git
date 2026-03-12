import React from 'react';
import { Report } from '../utils/types';
import styles from '../styles/globals.module.css';

interface DataTableProps {
  reports: Report[];
}

const DataTable: React.FC<DataTableProps> = ({ reports }) => {
  if (!reports || reports.length === 0) {
    return (
      <section className={styles.dataTableSection}>
        <h2 className={styles.dataTableTitle}>Reports</h2>
        <div className={styles.dataTableEmpty}>No reports available.</div>
      </section>
    );
  }

  // Assume each report's data is a flat object with string/number values
  // We'll display the latest report in detail, and a summary table for all reports
  const latestReport = reports[0];
  const reportKeys = latestReport && latestReport.data
    ? Object.keys(latestReport.data)
    : [];

  return (
    <section className={styles.dataTableSection}>
      <h2 className={styles.dataTableTitle}>Reports</h2>
      <div className={styles.dataTableWrapper}>
        <table className={styles.dataTable}>
          <thead>
            <tr>
              <th>Title</th>
              <th>Created By</th>
              <th>Created At</th>
              {reportKeys.map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr key={report.id}>
                <td>{report.title}</td>
                <td>{report.created_by}</td>
                <td>
                  {new Date(report.created_at).toLocaleString()}
                </td>
                {reportKeys.map((key) => (
                  <td key={key}>
                    {report.data && report.data[key] !== undefined
                      ? String(report.data[key])
                      : '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default DataTable;