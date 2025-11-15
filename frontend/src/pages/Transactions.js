import React, { useState, useEffect } from 'react';
import { itemsAPI } from '../api/items';
import { transactionsAPI } from '../api/transactions';
import { useWebSocket } from '../hooks/useWebSocket';

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    item_id: '',
    type: 'in',
    quantity: 1,
  });

  // WebSocket for real-time transaction updates
  useWebSocket((message) => {
    if (message.type === 'transaction_created') {
      fetchData();
    }
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [txResponse, itemsResponse] = await Promise.all([
        transactionsAPI.list(),
        itemsAPI.list(),
      ]);
      setTransactions(txResponse.data);
      setItems(itemsResponse.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'quantity' || name === 'item_id' ? parseInt(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await transactionsAPI.create(formData.item_id, formData.type, formData.quantity);
      setSuccess(`Stock ${formData.type === 'in' ? 'added' : 'removed'} successfully!`);
      setFormData({ item_id: '', type: 'in', quantity: 1 });
      setShowForm(false);
      fetchData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create transaction');
    }
  };

  const getItemName = (itemId) => {
    const item = items.find((i) => i.id === itemId);
    return item ? item.name : `Item #${itemId}`;
  };

  return (
    <div className="container">
      <div className="page">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 className="page-title">Stock Transactions</h1>
          <button
            className="btn btn-primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : '+ New Transaction'}
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {showForm && (
          <div className="card">
            <div className="card-title">Record Stock Movement</div>
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label className="form-label">Item *</label>
                <select
                  name="item_id"
                  className="form-select"
                  value={formData.item_id}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select an item</option>
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name} (SKU: {item.sku})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Transaction Type *</label>
                <select
                  name="type"
                  className="form-select"
                  value={formData.type}
                  onChange={handleInputChange}
                >
                  <option value="in">Stock In (Add)</option>
                  <option value="out">Stock Out (Remove)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Quantity *</label>
                <input
                  type="number"
                  min="1"
                  name="quantity"
                  className="form-input"
                  value={formData.quantity}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary">
                Record Transaction
              </button>
            </form>
          </div>
        )}

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            Loading transactions...
          </div>
        ) : transactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: '#666' }}>
            No transactions yet. Record one to get started!
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Item</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>User ID</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id}>
                  <td>{tx.id}</td>
                  <td>{getItemName(tx.item_id)}</td>
                  <td>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: tx.type === 'in' ? '#e8f5e9' : '#ffebee',
                      color: tx.type === 'in' ? '#2e7d32' : '#c62828',
                      fontWeight: '500',
                    }}>
                      {tx.type === 'in' ? '📥 In' : '📤 Out'}
                    </span>
                  </td>
                  <td>{tx.quantity}</td>
                  <td>{tx.user_id}</td>
                  <td>{new Date(tx.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Transactions;
