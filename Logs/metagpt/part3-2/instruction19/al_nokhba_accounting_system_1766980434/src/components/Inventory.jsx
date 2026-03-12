import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Inventory() {
  const [items, setItems] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For creating a new inventory item
  const [newItem, setNewItem] = useState({
    sku: '',
    name: '',
    quantity: '',
    unit_cost: '',
    reorder_level: '',
    supplier_id: '',
  });
  const [creatingItem, setCreatingItem] = useState(false);
  const [createItemError, setCreateItemError] = useState(null);

  // For creating a new inventory adjustment
  const [adjustment, setAdjustment] = useState({
    item_id: '',
    quantity_change: '',
    reason: '',
  });
  const [creatingAdjustment, setCreatingAdjustment] = useState(false);
  const [createAdjustmentError, setCreateAdjustmentError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [itemsRes, suppliersRes] = await Promise.all([
          axios.get('/api/inventory/items/'),
          axios.get('/api/purchases/suppliers/'),
        ]);
        setItems(itemsRes.data);
        setSuppliers(suppliersRes.data);
      } catch (err) {
        setError('Failed to load inventory data.');
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  // Handle new item form changes
  const handleItemChange = (e) => {
    setNewItem({ ...newItem, [e.target.name]: e.target.value });
  };

  const handleCreateItem = async (e) => {
    e.preventDefault();
    setCreatingItem(true);
    setCreateItemError(null);

    try {
      await axios.post('/api/inventory/items/', {
        sku: newItem.sku,
        name: newItem.name,
        quantity: parseInt(newItem.quantity, 10) || 0,
        unit_cost: parseFloat(newItem.unit_cost) || 0,
        reorder_level: parseInt(newItem.reorder_level, 10) || 0,
        supplier_id: newItem.supplier_id ? parseInt(newItem.supplier_id, 10) : null,
      });
      // Refresh items
      const itemsRes = await axios.get('/api/inventory/items/');
      setItems(itemsRes.data);
      setNewItem({
        sku: '',
        name: '',
        quantity: '',
        unit_cost: '',
        reorder_level: '',
        supplier_id: '',
      });
    } catch (err) {
      setCreateItemError('Failed to create inventory item.');
    }
    setCreatingItem(false);
  };

  // Handle adjustment form changes
  const handleAdjustmentChange = (e) => {
    setAdjustment({ ...adjustment, [e.target.name]: e.target.value });
  };

  const handleCreateAdjustment = async (e) => {
    e.preventDefault();
    setCreatingAdjustment(true);
    setCreateAdjustmentError(null);

    try {
      await axios.post('/api/inventory/adjustments/', {
        item_id: adjustment.item_id ? parseInt(adjustment.item_id, 10) : null,
        quantity_change: parseInt(adjustment.quantity_change, 10) || 0,
        reason: adjustment.reason,
      });
      // Refresh items
      const itemsRes = await axios.get('/api/inventory/items/');
      setItems(itemsRes.data);
      setAdjustment({
        item_id: '',
        quantity_change: '',
        reason: '',
      });
    } catch (err) {
      setCreateAdjustmentError('Failed to create inventory adjustment.');
    }
    setCreatingAdjustment(false);
  };

  return (
    <div>
      <h2 className="mb-4">Inventory</h2>
      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status" />
          <div>Loading inventory...</div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <>
          {/* Inventory Item Creation Form */}
          <div className="mb-5">
            <h4>Create Inventory Item</h4>
            <form onSubmit={handleCreateItem}>
              <div className="row mb-3">
                <div className="col-md-2">
                  <label className="form-label">SKU</label>
                  <input
                    type="text"
                    className="form-control"
                    name="sku"
                    value={newItem.sku}
                    onChange={handleItemChange}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Name</label>
                  <input
                    type="text"
                    className="form-control"
                    name="name"
                    value={newItem.name}
                    onChange={handleItemChange}
                    required
                  />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Quantity</label>
                  <input
                    type="number"
                    className="form-control"
                    name="quantity"
                    value={newItem.quantity}
                    onChange={handleItemChange}
                    min="0"
                    required
                  />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Unit Cost</label>
                  <input
                    type="number"
                    className="form-control"
                    name="unit_cost"
                    value={newItem.unit_cost}
                    onChange={handleItemChange}
                    min="0"
                    step="0.01"
                    required
                  />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Reorder Level</label>
                  <input
                    type="number"
                    className="form-control"
                    name="reorder_level"
                    value={newItem.reorder_level}
                    onChange={handleItemChange}
                    min="0"
                    required
                  />
                </div>
                <div className="col-md-1">
                  <label className="form-label">Supplier</label>
                  <select
                    className="form-select"
                    name="supplier_id"
                    value={newItem.supplier_id}
                    onChange={handleItemChange}
                  >
                    <option value="">None</option>
                    {suppliers.map(supplier => (
                      <option key={supplier.id} value={supplier.id}>
                        {supplier.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              {createItemError && <div className="alert alert-danger mt-2">{createItemError}</div>}
              <button
                type="submit"
                className="btn btn-primary mt-3"
                disabled={creatingItem}
              >
                {creatingItem ? 'Creating...' : 'Create Item'}
              </button>
            </form>
          </div>

          {/* Inventory Adjustment Form */}
          <div className="mb-5">
            <h4>Inventory Adjustment</h4>
            <form onSubmit={handleCreateAdjustment}>
              <div className="row mb-3">
                <div className="col-md-4">
                  <label className="form-label">Item</label>
                  <select
                    className="form-select"
                    name="item_id"
                    value={adjustment.item_id}
                    onChange={handleAdjustmentChange}
                    required
                  >
                    <option value="">Select Item</option>
                    {items.map(item => (
                      <option key={item.id} value={item.id}>
                        {item.sku} - {item.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-3">
                  <label className="form-label">Quantity Change</label>
                  <input
                    type="number"
                    className="form-control"
                    name="quantity_change"
                    value={adjustment.quantity_change}
                    onChange={handleAdjustmentChange}
                    required
                  />
                </div>
                <div className="col-md-5">
                  <label className="form-label">Reason</label>
                  <input
                    type="text"
                    className="form-control"
                    name="reason"
                    value={adjustment.reason}
                    onChange={handleAdjustmentChange}
                    required
                  />
                </div>
              </div>
              {createAdjustmentError && <div className="alert alert-danger mt-2">{createAdjustmentError}</div>}
              <button
                type="submit"
                className="btn btn-warning mt-3"
                disabled={creatingAdjustment}
              >
                {creatingAdjustment ? 'Adjusting...' : 'Create Adjustment'}
              </button>
            </form>
          </div>

          {/* Inventory Items List */}
          <div>
            <h4>Inventory Items</h4>
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th>SKU</th>
                  <th>Name</th>
                  <th>Quantity</th>
                  <th>Unit Cost</th>
                  <th>Reorder Level</th>
                  <th>Supplier</th>
                  <th>Below Reorder?</th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id}>
                    <td>{item.sku}</td>
                    <td>{item.name}</td>
                    <td>{item.quantity}</td>
                    <td>{item.unit_cost}</td>
                    <td>{item.reorder_level}</td>
                    <td>{item.supplier ? item.supplier.name : '-'}</td>
                    <td>
                      {item.quantity <= item.reorder_level ? (
                        <span className="badge bg-danger">Yes</span>
                      ) : (
                        <span className="badge bg-success">No</span>
                      )}
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

export default Inventory;