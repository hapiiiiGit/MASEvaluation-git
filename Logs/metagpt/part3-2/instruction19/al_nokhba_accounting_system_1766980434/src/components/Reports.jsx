import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Reports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState(null);

  // For custom report generation
  const [customParams, setCustomParams] = useState({
    type: 'CUSTOM',
    parameters: '',
  });

  useEffect(() => {
    const fetchReports = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get('/api/reports/');
        setReports(res.data);
      } catch (err) {
        setError('Failed to load reports.');
      }
      setLoading(false);
    };
    fetchReports();
  }, []);

  const handleGenerateReport = async (type) => {
    setGenerating(true);
    setGenerateError(null);
    try {
      let res;
      if (type === 'BALANCE_SHEET') {
        res = await axios.get('/api/reports/balance_sheet');
      } else if (type === 'INCOME_STATEMENT') {
        res = await axios.get('/api/reports/income_statement');
      } else if (type === 'CASH_FLOW') {
        res = await axios.get('/api/reports/cash_flow');
      }
      if (res && res.data) {
        setReports([res.data, ...reports]);
      }
    } catch (err) {
      setGenerateError('Failed to generate report.');
    }
    setGenerating(false);
  };

  const handleCustomParamsChange = (e) => {
    setCustomParams({ ...customParams, [e.target.name]: e.target.value });
  };

  const handleGenerateCustomReport = async (e) => {
    e.preventDefault();
    setGenerating(true);
    setGenerateError(null);
    try {
      // Custom report generation endpoint (assume POST to /api/reports/)
      const paramsObj = customParams.parameters
        ? JSON.parse(customParams.parameters)
        : {};
      const res = await axios.post('/api/reports/', {
        type: 'CUSTOM',
        parameters: paramsObj,
      });
      if (res && res.data) {
        setReports([res.data, ...reports]);
      }
    } catch (err) {
      setGenerateError('Failed to generate custom report. Ensure parameters are valid JSON.');
    }
    setGenerating(false);
  };

  return (
    <div>
      <h2 className="mb-4">Financial Reports</h2>
      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status" />
          <div>Loading reports...</div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <>
          {/* Report Generation */}
          <div className="mb-5">
            <h4>Generate Report</h4>
            <div className="d-flex flex-wrap gap-2 mb-3">
              <button
                className="btn btn-outline-primary"
                disabled={generating}
                onClick={() => handleGenerateReport('BALANCE_SHEET')}
              >
                {generating ? 'Generating...' : 'Balance Sheet'}
              </button>
              <button
                className="btn btn-outline-success"
                disabled={generating}
                onClick={() => handleGenerateReport('INCOME_STATEMENT')}
              >
                {generating ? 'Generating...' : 'Income Statement'}
              </button>
              <button
                className="btn btn-outline-warning"
                disabled={generating}
                onClick={() => handleGenerateReport('CASH_FLOW')}
              >
                {generating ? 'Generating...' : 'Cash Flow'}
              </button>
            </div>
            <form onSubmit={handleGenerateCustomReport} className="mb-3">
              <div className="row g-2 align-items-end">
                <div className="col-md-8">
                  <label className="form-label">Custom Report Parameters (JSON)</label>
                  <input
                    type="text"
                    className="form-control"
                    name="parameters"
                    value={customParams.parameters}
                    onChange={handleCustomParamsChange}
                    placeholder='e.g. {"date_from":"2024-01-01","date_to":"2024-06-30"}'
                  />
                </div>
                <div className="col-md-4">
                  <button
                    type="submit"
                    className="btn btn-outline-dark w-100"
                    disabled={generating}
                  >
                    {generating ? 'Generating...' : 'Generate Custom Report'}
                  </button>
                </div>
              </div>
            </form>
            {generateError && <div className="alert alert-danger mt-2">{generateError}</div>}
          </div>

          {/* Reports List */}
          <div>
            <h4>Reports History</h4>
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th>Type</th>
                  <th>Parameters</th>
                  <th>Generated By</th>
                  <th>Generated At</th>
                  <th>Data</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td>{report.type.replace('_', ' ')}</td>
                    <td>
                      <pre className="mb-0 small">
                        {report.parameters ? JSON.stringify(report.parameters, null, 2) : '-'}
                      </pre>
                    </td>
                    <td>
                      {report.generated_by
                        ? report.generated_by.username
                        : '-'}
                    </td>
                    <td>{report.generated_at ? new Date(report.generated_at).toLocaleString() : '-'}</td>
                    <td>
                      <pre className="mb-0 small">
                        {report.data ? JSON.stringify(report.data, null, 2) : '-'}
                      </pre>
                    </td>
                  </tr>
                ))}
                {reports.length === 0 && (
                  <tr>
                    <td colSpan={5} className="text-center text-muted">
                      No reports generated yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default Reports;