import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Purchases() {
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [inventoryItems, setInventoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For creating a new purchase order
  const [newPO, setNewPO] = useState({
    number: '',
    supplier_id: '',
    date: '',
    status: 'DRAFT',
    lines: [],
  });
  const [poLines, setPOLines] = useState([
    { item_id: '', quantity: '', unit_price: '' }
  ]);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [poRes, suppliersRes, itemsRes] = await Promise.all([
          axios.get('/api/purchases/orders/'),
          axios.get('/api/purchases/suppliers/'),
          axios.get('/api/inventory/items/'),
        ]);
        setPurchaseOrders(poRes.data);
        setSuppliers(suppliersRes.data);
        setInventoryItems(itemsRes.data);
      } catch (err) {
        setError('Failed to load purchases data.');
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  // Handle new purchase order form changes
  const handlePOChange = (e) => {
    setNewPO({ ...newPO, [e.target.name]: e.target.value });
  };

  const handleLineChange = (idx, e) => {
    const updatedLines = poLines.map((line, i) =>
      i === idx ? { ...line, [e.target.name]: e.target.value } : line
    );
    setPOLines(updatedLines);
  };

  const addPOLine = () => {
    setPOLines([...poLines, { item_id: '', quantity: '', unit_price: '' }]);
  };

  const removePOLine = (idx) => {
    setPOLines(poLines.filter((_, i) => i !== idx));
  };

  const handleCreatePO = async (e) => {
    e.preventDefault();
    setCreating(true);
    setCreateError(null);

    // Prepare lines for API
    const linesForApi = poLines.map(line => ({
      item: inventoryItems.find(item => item.id === Number(line.item_id)),
      quantity: parseInt(line.quantity, 10) || 0,
      unit_price: parseFloat(line.unit_price) || 0,
    }));

    try {
      await axios.post('/api/purchases/orders/', {
        number: newPO.number,
        supplier: suppliers.find(sup => sup.id === Number(newPO.supplier_id)),
        date: newPO.date,
        status: newPO.status,
        lines: linesForApi,
      });
      // Refresh purchase orders
      const poRes = await axios.get('/api/purchases/orders/');
      setPurchaseOrders(poRes.data);
      setNewPO({
        number: '',
        supplier_id: '',
        date: '',
        status: 'DRAFT',
        lines: [],
      });
      setPOLines([{ item_id: '', quantity: '', unit_price: '' }]);
    } catch (err) {
      setCreateError('Failed to create purchase order.');
    }
    setCreating(false);
  };

  return (
    <div>
      <h2 className="mb-4">Purchases</h2>
      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status" />
          <div>Loading purchases...</div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <>
          {/* Purchase Order Creation Form */}
          <div className="mb-5">
            <h4>Create Purchase Order</h4>
            <form onSubmit={handleCreatePO}>
              <div className="row mb-3">
                <div className="col-md-3">
                  <label className="form-label">PO Number</label>
                  <input
                    type="text"
                    className="form-control"
                    name="number"
                    value={newPO.number}
                    onChange={handlePOChange}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Supplier</label>
                  <select
                    className="form-select"
                    name="supplier_id"
                    value={newPO.supplier_id}
                    onChange={handlePOChange}
                    required
                  >
                    <option value="">Select Supplier</option>
                    {suppliers.map(supplier => (
                      <option key={supplier.id} value={supplier.id}>
                        {supplier.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-3">
                  <label className="form-label">Date</label>
                  <input
                    type="date"
                    className="form-control"
                    name="date"
                    value={newPO.date}
                    onChange={handlePOChange}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Status</label>
                  <select
                    className="form-select"
                    name="status"
                    value={newPO.status}
                    onChange={handlePOChange}
                  >
                    <option value="DRAFT">Draft</option>
                    <option value="ORDERED">Ordered</option>
                    <option value="RECEIVED">Received</option>
                    <option value="CANCELLED">Cancelled</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="form-label">Order Lines</label>
                <table className="table table-sm table-bordered">
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Quantity</th>
                      <th>Unit Price</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {poLines.map((line, idx) => (
                      <tr key={idx}>
                        <td>
                          <select
                            className="form-select"
                            name="item_id"
                            value={line.item_id}
                            onChange={e => handleLineChange(idx, e)}
                            required
                          >
                            <option value="">Select Item</option>
                            {inventoryItems.map(item => (
                              <option key={item.id} value={item.id}>
                                {item.sku} - {item.name}
                              </option>
                            ))}
                          </select>
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
                          {poLines.length > 1 && (
                            <button
                              type="button"
                              className="btn btn-sm btn-danger"
                              onClick={() => removePOLine(idx)}
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
                  onClick={addPOLine}
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
                {creating ? 'Creating...' : 'Create Purchase Order'}
              </button>
            </form>
          </div>

          {/* Purchase Orders List */}
          <div>
            <h4>Purchase Orders List</h4>
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th>Number</th>
                  <th>Supplier</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Total</th>
                  <th>Created By</th>
                  <th>Lines</th>
                </tr>
              </thead>
              <tbody>
                {purchaseOrders.map(po => (
                  <tr key={po.id}>
                    <td>{po.number}</td>
                    <td>{po.supplier ? po.supplier.name : ''}</td>
                    <td>{po.date}</td>
                    <td>{po.status}</td>
                    <td>{po.total}</td>
                    <td>{po.created_by}</td>
                    <td>
                      <table className="table table-sm mb-0">
                        <thead>
                          <tr>
                            <th>Item</th>
                            <th>Quantity</th>
                            <th>Unit Price</th>
                            <th>Total</th>
                          </tr>
                        </thead>
                        <tbody>
                          {po.lines.map((line, idx) => (
                            <tr key={idx}>
                              <td>
                                {line.item
                                  ? `${line.item.sku} - ${line.item.name}`
                                  : ''}
                              </td>
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

export default Purchases;