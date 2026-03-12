import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState({
    accounts: 0,
    invoices: 0,
    purchases: 0,
    inventory: 0,
    users: 0,
    reports: 0,
    loading: true,
    error: null,
  });

  useEffect(() => {
    // Fetch dashboard stats from backend API
    const fetchStats = async () => {
      try {
        // You may need to adjust the API URLs according to your backend routing
        const [
          accountsRes,
          invoicesRes,
          purchasesRes,
          inventoryRes,
          usersRes,
          reportsRes,
        ] = await Promise.all([
          axios.get('/api/general_ledger/accounts/'),
          axios.get('/api/invoices/'),
          axios.get('/api/purchases/orders/'),
          axios.get('/api/inventory/items/'),
          axios.get('/api/users/'),
          axios.get('/api/reports/'),
        ]);
        setStats({
          accounts: accountsRes.data.length,
          invoices: invoicesRes.data.length,
          purchases: purchasesRes.data.length,
          inventory: inventoryRes.data.length,
          users: usersRes.data.length,
          reports: reportsRes.data.length,
          loading: false,
          error: null,
        });
      } catch (error) {
        setStats((prev) => ({
          ...prev,
          loading: false,
          error: 'Failed to load dashboard stats.',
        }));
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <h2 className="mb-4">Dashboard</h2>
      {stats.loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status" />
          <div>Loading dashboard...</div>
        </div>
      ) : stats.error ? (
        <div className="alert alert-danger">{stats.error}</div>
      ) : (
        <div className="row g-4">
          <div className="col-md-4">
            <div className="card shadow-sm border-primary">
              <div className="card-body">
                <h5 className="card-title">Accounts</h5>
                <p className="card-text display-5 fw-bold">{stats.accounts}</p>
                <p className="card-text text-muted">Total Chart of Accounts</p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card shadow-sm border-success">
              <div className="card-body">
                <h5 className="card-title">Invoices</h5>
                <p className="card-text display-5 fw-bold">{stats.invoices}</p>
                <p className="card-text text-muted">Total Invoices</p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card shadow-sm border-warning">
              <div className="card-body">
                <h5 className="card-title">Purchases</h5>
                <p className="card-text display-5 fw-bold">{stats.purchases}</p>
                <p className="card-text text-muted">Total Purchase Orders</p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card shadow-sm border-info">
              <div className="card-body">
                <h5 className="card-title">Inventory Items</h5>
                <p className="card-text display-5 fw-bold">{stats.inventory}</p>
                <p className="card-text text-muted">Total Inventory Items</p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card shadow-sm border-secondary">
              <div className="card-body">
                <h5 className="card-title">Users</h5>
                <p className="card-text display-5 fw-bold">{stats.users}</p>
                <p className="card-text text-muted">Total System Users</p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card shadow-sm border-dark">
              <div className="card-body">
                <h5 className="card-title">Reports</h5>
                <p className="card-text display-5 fw-bold">{stats.reports}</p>
                <p className="card-text text-muted">Financial Reports Generated</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;