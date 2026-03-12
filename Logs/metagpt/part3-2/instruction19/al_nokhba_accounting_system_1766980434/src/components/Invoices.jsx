import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For creating a new invoice
  const [newInvoice, setNewInvoice] = useState({
    number: '',
    customer: '',
    date: '',
    due_date: '',
    status: 'DRAFT',
    lines: [],
  });
  const [invoiceLines, setInvoiceLines] = useState([
    { description: '', quantity: '', unit_price: '' }
  ]);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState(null);

  useEffect(() => {
    const fetchInvoices = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get('/api/invoices/');
        setInvoices(res.data);
      } catch (err) {
        setError('Failed to load invoices.');
      }
      setLoading(false);
    };
    fetchInvoices();
  }, []);

  // Handle new invoice form changes
  const handleInvoiceChange = (e) => {
    setNewInvoice({ ...newInvoice, [e.target.name]: e.target.value });
  };

  const handleLineChange = (idx, e) => {
    const updatedLines = invoiceLines.map((line, i) =>
      i === idx ? { ...line, [e.target.name]: e.target.value } : line
    );
    setInvoiceLines(updatedLines);
  };

  const addInvoiceLine = () => {
    setInvoiceLines([...invoiceLines, { description: '', quantity: '', unit_price: '' }]);
  };

  const removeInvoiceLine = (idx) => {
    setInvoiceLines(invoiceLines.filter((_, i) => i !== idx));
  };

  const handleCreateInvoice = async (e) => {
    e.preventDefault();
    setCreating(true);
    setCreateError(null);

    // Prepare lines for API
    const linesForApi = invoiceLines.map(line => ({
      description: line.description,
      quantity: parseInt(line.quantity, 10) || 0,
      unit_price: parseFloat(line.unit_price) || 0,
    }));

    try {
      await axios.post('/api/invoices/', {
        number: newInvoice.number,
        customer: newInvoice.customer,
        date: newInvoice.date,
        due_date: newInvoice.due_date,
        status: newInvoice.status,
        lines: linesForApi,
      });
      // Refresh invoices
      const res = await axios.get('/api/invoices/');
      setInvoices(res.data);
      setNewInvoice({
        number: '',
        customer: '',
        date: '',
        due_date: '',
        status: 'DRAFT',
        lines: [],
      });
      setInvoiceLines([{ description: '', quantity: '', unit_price: '' }]);
    } catch (err) {
      setCreateError('Failed to create invoice.');
    }
    setCreating(false);
  };

  return (
    <div>
      <h2 className="mb-4">Invoices</h2>
      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status" />
          <div>Loading invoices...</div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <>
          {/* Invoice Creation Form */}
          <div className="mb-5">
            <h4>Create Invoice</h4>
            <form onSubmit={handleCreateInvoice}>
              <div className="row mb-3">
                <div className="col-md-3">
                  <label className="form-label">Invoice Number</label>
                  <input
                    type="text"
                    className="form-control"
                    name="number"
                    value={newInvoice.number}
                    onChange={handleInvoiceChange}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Customer</label>
                  <input
                    type="text"
                    className="form-control"
                    name="customer"
                    value={newInvoice.customer}
                    onChange={handleInvoiceChange}
                    required
                  />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Date</label>
                  <input
                    type="date"
                    className="form-control"
                    name="date"
                    value={newInvoice.date}
                    onChange={handleInvoiceChange}
                    required
                  />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Due Date</label>
                  <input
                    type="date"
                    className="form-control"
                    name="due_date"
                    value={newInvoice.due_date}
                    onChange={handleInvoiceChange}
                    required
                  />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Status</label>
                  <select
                    className="form-select"
                    name="status"
                    value={newInvoice.status}
                    onChange={handleInvoiceChange}
                  >
                    <option value="DRAFT">Draft</option>
                    <option value="SENT">Sent</option>
                    <option value="PAID">Paid</option>
                    <option value="OVERDUE">Overdue</option>
                    <option value="CANCELLED">Cancelled</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="form-label">Invoice Lines</label>
                <table className="table table-sm table-bordered">
                  <thead>
                    <tr>
                      <th>Description</th>
                      <th>Quantity</th>
                      <th>Unit Price</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoiceLines.map((line, idx) => (
                      <tr key={idx}>
                        <td>
                          <input
                            type="text"
                            className="form-control"
                            name="description"
                            value={line.description}
                            onChange={e => handleLineChange(idx, e)}
                            required
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            className="form-control"
                            name="quantity"
                            value={line.quantity}
                            onChange={e => handleLineChange(idx, e)}
                            min="1"
                            required
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            className="form-control"
                            name="unit_price"
                            value={line.unit_price}
                            onChange={e => handleLineChange(idx, e)}
                            min="0"
                            step="0.01"
                            required
                          />
                        </td>
                        <td>
                          {invoiceLines.length > 1 && (
                            <button
                              type="button"
                              className="btn btn-sm btn-danger"
                              onClick={() => removeInvoiceLine(idx)}
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
                  onClick={addInvoiceLine}
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
                {creating ? 'Creating...' : 'Create Invoice'}
              </button>
            </form>
          </div>

          {/* Invoices List */}
          <div>
            <h4>Invoices List</h4>
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th>Number</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th>Total</th>
                  <th>Created By</th>
                  <th>Lines</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map(invoice => (
                  <tr key={invoice.id}>
                    <td>{invoice.number}</td>
                    <td>{invoice.customer}</td>
                    <td>{invoice.date}</td>
                    <td>{invoice.due_date}</td>
                    <td>{invoice.status}</td>
                    <td>{invoice.total}</td>
                    <td>{invoice.created_by}</td>
                    <td>
                      <table className="table table-sm mb-0">
                        <thead>
                          <tr>
                            <th>Description</th>
                            <th>Quantity</th>
                            <th>Unit Price</th>
                            <th>Total</th>
                          </tr>
                        </thead>
                        <tbody>
                          {invoice.lines.map((line, idx) => (
                            <tr key={idx}>
                              <td>{line.description}</td>
                              <td>{line.quantity}</td>
                              <td>{line.unit_price}</td>
                              <td>{line.total}</td>
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

export default Invoices;