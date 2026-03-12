import React, { useEffect, useState } from 'react';
import axios from 'axios';

function GeneralLedger() {
  const [accounts, setAccounts] = useState([]);
  const [journalEntries, setJournalEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For creating a new journal entry
  const [newEntry, setNewEntry] = useState({
    date: '',
    description: '',
    lines: [],
  });
  const [entryLines, setEntryLines] = useState([
    { account_id: '', debit: '', credit: '' }
  ]);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [accountsRes, journalEntriesRes] = await Promise.all([
          axios.get('/api/general_ledger/accounts/'),
          axios.get('/api/general_ledger/journal_entries/'),
        ]);
        setAccounts(accountsRes.data);
        setJournalEntries(journalEntriesRes.data);
      } catch (err) {
        setError('Failed to load general ledger data.');
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  // Handle new journal entry form changes
  const handleEntryChange = (e) => {
    setNewEntry({ ...newEntry, [e.target.name]: e.target.value });
  };

  const handleLineChange = (idx, e) => {
    const updatedLines = entryLines.map((line, i) =>
      i === idx ? { ...line, [e.target.name]: e.target.value } : line
    );
    setEntryLines(updatedLines);
  };

  const addEntryLine = () => {
    setEntryLines([...entryLines, { account_id: '', debit: '', credit: '' }]);
  };

  const removeEntryLine = (idx) => {
    setEntryLines(entryLines.filter((_, i) => i !== idx));
  };

  const handleCreateEntry = async (e) => {
    e.preventDefault();
    setCreating(true);
    setCreateError(null);

    // Prepare lines for API
    const linesForApi = entryLines.map(line => ({
      account: accounts.find(acc => acc.id === Number(line.account_id)),
      debit: parseFloat(line.debit) || 0,
      credit: parseFloat(line.credit) || 0,
    }));

    try {
      await axios.post('/api/general_ledger/journal_entries/', {
        date: newEntry.date,
        description: newEntry.description,
        lines: linesForApi,
      });
      // Refresh data
      const journalEntriesRes = await axios.get('/api/general_ledger/journal_entries/');
      setJournalEntries(journalEntriesRes.data);
      setNewEntry({ date: '', description: '', lines: [] });
      setEntryLines([{ account_id: '', debit: '', credit: '' }]);
    } catch (err) {
      setCreateError('Failed to create journal entry.');
    }
    setCreating(false);
  };

  return (
    <div>
      <h2 className="mb-4">General Ledger</h2>
      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status" />
          <div>Loading general ledger...</div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <>
          {/* Chart of Accounts */}
          <div className="mb-5">
            <h4>Chart of Accounts</h4>
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Parent</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map(account => (
                  <tr key={account.id}>
                    <td>{account.code}</td>
                    <td>{account.name}</td>
                    <td>{account.type}</td>
                    <td>{account.parent ? accounts.find(a => a.id === account.parent)?.name : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Journal Entry Form */}
          <div className="mb-5">
            <h4>Create Journal Entry</h4>
            <form onSubmit={handleCreateEntry}>
              <div className="row mb-3">
                <div className="col-md-3">
                  <label className="form-label">Date</label>
                  <input
                    type="date"
                    className="form-control"
                    name="date"
                    value={newEntry.date}
                    onChange={handleEntryChange}
                    required
                  />
                </div>
                <div className="col-md-9">
                  <label className="form-label">Description</label>
                  <input
                    type="text"
                    className="form-control"
                    name="description"
                    value={newEntry.description}
                    onChange={handleEntryChange}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="form-label">Entry Lines</label>
                <table className="table table-sm table-bordered">
                  <thead>
                    <tr>
                      <th>Account</th>
                      <th>Debit</th>
                      <th>Credit</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {entryLines.map((line, idx) => (
                      <tr key={idx}>
                        <td>
                          <select
                            className="form-select"
                            name="account_id"
                            value={line.account_id}
                            onChange={e => handleLineChange(idx, e)}
                            required
                          >
                            <option value="">Select Account</option>
                            {accounts.map(account => (
                              <option key={account.id} value={account.id}>
                                {account.code} - {account.name}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td>
                          <input
                            type="number"
                            className="form-control"
                            name="debit"
                            value={line.debit}
                            onChange={e => handleLineChange(idx, e)}
                            min="0"
                            step="0.01"
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            className="form-control"
                            name="credit"
                            value={line.credit}
                            onChange={e => handleLineChange(idx, e)}
                            min="0"
                            step="0.01"
                          />
                        </td>
                        <td>
                          {entryLines.length > 1 && (
                            <button
                              type="button"
                              className="btn btn-sm btn-danger"
                              onClick={() => removeEntryLine(idx)}
                            >
                              &times;
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <button
                  type="button"
                  className="btn btn-sm btn-secondary me-2"
                  onClick={addEntryLine}
                >
                  Add Line
                </button>
              </div>
              {createError && <div className="alert alert-danger mt-2">{createError}</div>}
              <button
                type="submit"
                className="btn btn-primary mt-3"
                disabled={creating}
              >
                {creating ? 'Creating...' : 'Create Journal Entry'}
              </button>
            </form>
          </div>

          {/* Journal Entries List */}
          <div>
            <h4>Journal Entries</h4>
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Created By</th>
                  <th>Lines</th>
                </tr>
              </thead>
              <tbody>
                {journalEntries.map(entry => (
                  <tr key={entry.id}>
                    <td>{entry.date}</td>
                    <td>{entry.description}</td>
                    <td>{entry.created_by}</td>
                    <td>
                      <table className="table table-sm mb-0">
                        <thead>
                          <tr>
                            <th>Account</th>
                            <th>Debit</th>
                            <th>Credit</th>
                          </tr>
                        </thead>
                        <tbody>
                          {entry.lines.map((line, idx) => (
                            <tr key={idx}>
                              <td>
                                {line.account
                                  ? `${line.account.code} - ${line.account.name}`
                                  : ''}
                              </td>
                              <td>{line.debit}</td>
                              <td>{line.credit}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default GeneralLedger;