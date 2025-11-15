import React, { useState, useEffect } from 'react';
import { itemsAPI } from '../api/items';
import { useWebSocket } from '../hooks/useWebSocket';

function Items() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [success, setSuccess] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [notifications, setNotifications] = useState([]);

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        sku: '',
        quantity: 0,
        low_stock_threshold: 5,
        price: 0.0,
    });

    // WebSocket for real-time updates
    useWebSocket((message) => {
        console.log('📦 Items component received message:', message);
        if (message.type === 'item_created' || message.type === 'item_updated') {
            console.log('🔄 Refreshing items...');
            fetchItems();
        } else if (message.type === 'item_deleted') {
            console.log('🗑️ Item deleted, updating list...');
            setItems(items => items.filter(item => item.id !== message.data.id));
        } else if (message.type === 'low_stock_alert') {
            //alert(message.data.message);
            setNotifications(prev => [...prev, message.data]);
        }
    });

    useEffect(() => {
        fetchItems();
    }, []);

    const fetchItems = async () => {
        try {
            setLoading(true);
            const response = await itemsAPI.list();
            setItems(response.data);
            setError('');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch items');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: ['quantity', 'low_stock_threshold'].includes(name) ? parseInt(value) :
                name === 'price' ? parseFloat(value) : value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingId) {
                await itemsAPI.update(editingId, formData);
                setSuccess('Item updated successfully!');
            } else {
                await itemsAPI.create(formData);
                setSuccess('Item created successfully!');
            }
            resetForm();
            fetchItems();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to save item');
        }
    };

    const handleEdit = (item) => {
        setFormData(item);
        setEditingId(item.id);
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this item?')) {
            try {
                await itemsAPI.delete(id);
                setSuccess('Item deleted successfully!');
                fetchItems();
                setTimeout(() => setSuccess(''), 3000);
            } catch (err) {
                setError(err.response?.data?.detail || 'Failed to delete item');
            }
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            description: '',
            sku: '',
            quantity: 0,
            low_stock_threshold: 5,
            price: 0.0,
        });
        setEditingId(null);
        setShowForm(false);
    };

    return (
        <div className="container">
            <div className="page">
                {/* Notifications container */}
                {notifications.map((note, idx) => (
                    <div
                        key={idx}
                        style={{
                            backgroundColor: '#ff9800',
                            color: '#000',
                            padding: '20px 30px',
                            fontSize: '18px',
                            fontWeight: 'bold',
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '15px',
                            wordBreak: 'break-word',
                        }}
                    >
                        <div style={{ flex: 1, paddingRight: '10px' }}>
                            ⚠️ <strong>Low stock alert:</strong> {note.name} (SKU: {note.sku}) – Quantity: {note.quantity}
                        </div>

                        <button
                            onClick={() =>
                                setNotifications((prev) => prev.filter((_, i) => i !== idx))
                            }
                            style={{
                                backgroundColor: '#c62828',
                                color: '#fff',
                                border: 'none',
                                borderRadius: '8px',
                                padding: '10px 18px',
                                cursor: 'pointer',
                                whiteSpace: 'nowrap',   
                                fontSize: '16px',
                                fontWeight: 'bold',
                                flexShrink: 0,          
                                minWidth: '110px',      
                                textAlign: 'center',
                            }}
                        >
                            Dismiss
                        </button>
                    </div>
                ))}


                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h1 className="page-title">Inventory Items</h1>
                    <button
                        className="btn btn-primary"
                        onClick={() => {
                            if (showForm) resetForm();
                            else setShowForm(true);
                        }}
                    >
                        {showForm ? 'Cancel' : '+ Create Item'}
                    </button>
                </div>

                {error && <div className="alert alert-error">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}

                {showForm && (
                    <div className="card">
                        <div className="card-title">{editingId ? 'Edit Item' : 'Create New Item'}</div>
                        <form onSubmit={handleSubmit} className="form">
                            <div className="form-group">
                                <label className="form-label">Item Name *</label>
                                <input
                                    type="text"
                                    name="name"
                                    className="form-input"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">SKU *</label>
                                <input
                                    type="text"
                                    name="sku"
                                    className="form-input"
                                    value={formData.sku}
                                    onChange={handleInputChange}
                                    required
                                    disabled={editingId ? true : false}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Description</label>
                                <input
                                    type="text"
                                    name="description"
                                    className="form-input"
                                    value={formData.description}
                                    onChange={handleInputChange}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Quantity</label>
                                <input
                                    type="number"
                                    name="quantity"
                                    className="form-input"
                                    value={formData.quantity}
                                    onChange={handleInputChange}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Price</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="price"
                                    className="form-input"
                                    value={formData.price}
                                    onChange={handleInputChange}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Low Stock Threshold</label>
                                <input
                                    type="number"
                                    name="low_stock_threshold"
                                    className="form-input"
                                    value={formData.low_stock_threshold}
                                    onChange={handleInputChange}
                                />
                            </div>

                            <button type="submit" className="btn btn-primary">
                                {editingId ? 'Update Item' : 'Create Item'}
                            </button>
                        </form>
                    </div>
                )}

                {loading ? (
                    <div className="loading">
                        <div className="spinner"></div>
                        Loading items...
                    </div>
                ) : items.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px 20px', color: '#666' }}>
                        No items yet. Create one to get started!
                    </div>
                ) : (
                    <table className="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>SKU</th>
                                <th>Quantity</th>
                                <th>Price</th>
                                <th>Threshold</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items.map((item) => (
                                <tr key={item.id} style={{ backgroundColor: item.quantity <= item.low_stock_threshold ? '#fff3e0' : 'transparent' }}>
                                    <td>{item.id}</td>
                                    <td>{item.name}</td>
                                    <td>{item.sku}</td>
                                    <td>{item.quantity}</td>
                                    <td>${item.price.toFixed(2)}</td>
                                    <td>{item.low_stock_threshold}</td>
                                    <td>
                                        <div className="table-actions">
                                            <button
                                                className="btn btn-secondary btn-small"
                                                onClick={() => handleEdit(item)}
                                            >
                                                Edit
                                            </button>
                                            <button
                                                className="btn btn-danger btn-small"
                                                onClick={() => handleDelete(item.id)}
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

export default Items;
