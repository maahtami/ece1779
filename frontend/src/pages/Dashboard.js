import React from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

function Dashboard() {
  const { user } = useAuthStore();

  return (
    <div className="container">
      <div className="page">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Welcome back, {user?.username}!</p>

        <div className="grid">
          <Link to="/items" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s' }}>
              <div className="card-title">📦 Inventory Items</div>
              <p>Manage all inventory items - create, read, update, delete items</p>
            </div>
          </Link>

          <Link to="/transactions" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s' }}>
              <div className="card-title">📊 Transactions</div>
              <p>Record and track stock movements (in/out)</p>
            </div>
          </Link>

          {user?.role === 'manager' && (
            <Link to="/users" style={{ textDecoration: 'none' }}>
              <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s' }}>
                <div className="card-title">👥 User Management</div>
                <p>Create and manage staff accounts</p>
              </div>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
