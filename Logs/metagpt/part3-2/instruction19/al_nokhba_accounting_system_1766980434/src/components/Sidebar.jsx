import React from 'react';
import { NavLink } from 'react-router-dom';

function Sidebar() {
  return (
    <div className="d-flex flex-column align-items-center align-items-sm-start px-3 pt-2 text-dark min-vh-100">
      <a
        href="/"
        className="d-flex align-items-center pb-3 mb-md-0 me-md-auto text-dark text-decoration-none"
      >
        <span className="fs-4 fw-bold">Al-Nokhba Accounting</span>
      </a>
      <ul className="nav nav-pills flex-column mb-auto w-100">
        <li className="nav-item">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              'nav-link text-dark' + (isActive ? ' active bg-primary text-white' : '')
            }
            end
          >
            <i className="bi bi-speedometer2 me-2"></i>
            Dashboard
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/general-ledger"
            className={({ isActive }) =>
              'nav-link text-dark' + (isActive ? ' active bg-primary text-white' : '')
            }
          >
            <i className="bi bi-journal-bookmark me-2"></i>
            General Ledger
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/invoices"
            className={({ isActive }) =>
              'nav-link text-dark' + (isActive ? ' active bg-primary text-white' : '')
            }
          >
            <i className="bi bi-receipt me-2"></i>
            Invoices
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/purchases"
            className={({ isActive }) =>
              'nav-link text-dark' + (isActive ? ' active bg-primary text-white' : '')
            }
          >
            <i className="bi bi-cart me-2"></i>
            Purchases
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/inventory"
            className={({ isActive }) =>
              'nav-link text-dark' + (isActive ? ' active bg-primary text-white' : '')
            }
          >
            <i className="bi bi-box-seam me-2"></i>
            Inventory
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/reports"
            className={({ isActive }) =>
              'nav-link text-dark' + (isActive ? ' active bg-primary text-white' : '')
            }
          >
            <i className="bi bi-graph-up me-2"></i>
            Reports
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/users"
            className={({ isActive }) =>
              'nav-link text-dark' + (isActive ? ' active bg-primary text-white' : '')
            }
          >
            <i className="bi bi-people me-2"></i>
            Users
          </NavLink>
        </li>
      </ul>
      <hr className="w-100" />
      <div className="pb-2 w-100 text-center small text-muted">
        &copy; {new Date().getFullYear()} Al-Nokhba for Electronics
      </div>
    </div>
  );
}

export default Sidebar;