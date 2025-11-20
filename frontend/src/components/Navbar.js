import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import '../styles/Navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="navbar-brand">
          📦 IMS
        </Link>

        <div className="navbar-links">
          <Link to="/dashboard" className="nav-link">Dashboard</Link>
          <Link to="/items" className="nav-link">Items</Link>
          <Link to="/transactions" className="nav-link">Transactions</Link>
          {user?.role === 'manager' && (
            <>
              <Link to="/users" className="nav-link">Users</Link>
              <Link to="/health" className="nav-link">Health</Link>
            </>
          )}
        </div>

        <div className="navbar-user">
          <span className="user-info">
            {user?.username} ({user?.role})
          </span>
          <button className="btn btn-secondary btn-small" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
