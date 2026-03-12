import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import GeneralLedger from './components/GeneralLedger';
import Invoices from './components/Invoices';
import Purchases from './components/Purchases';
import Inventory from './components/Inventory';
import Reports from './components/Reports';
import Users from './components/Users';

import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <Router>
      <div className="container-fluid">
        <div className="row flex-nowrap">
          {/* Sidebar Navigation */}
          <div className="col-auto col-md-3 col-xl-2 px-sm-2 px-0 bg-light min-vh-100 border-end">
            <Sidebar />
          </div>
          {/* Main Content */}
          <div className="col py-3">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/general-ledger/*" element={<GeneralLedger />} />
              <Route path="/invoices/*" element={<Invoices />} />
              <Route path="/purchases/*" element={<Purchases />} />
              <Route path="/inventory/*" element={<Inventory />} />
              <Route path="/reports/*" element={<Reports />} />
              <Route path="/users/*" element={<Users />} />
              {/* 404 fallback */}
              <Route path="*" element={
                <div className="text-center mt-5">
                  <h2>404 - Page Not Found</h2>
                  <p>The page you are looking for does not exist.</p>
                </div>
              } />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;