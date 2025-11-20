import React, { useState, useEffect } from 'react';
import { healthAPI } from '../api/health';
import '../styles/SystemHealth.css';

function SystemHealth() {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedService, setSelectedService] = useState(null);
    const [serviceLogs, setServiceLogs] = useState(null);
    const [refreshInterval, setRefreshInterval] = useState(60); // seconds
    const [lastUpdated, setLastUpdated] = useState(null);

    // Fetch system metrics
    const fetchMetrics = async () => {
        try {
            setLoading(true);
            // Fetching up to 50 lines of logs by default
            const response = await healthAPI.getSystemMetrics(50);
            setMetrics(response.data);
            setLastUpdated(new Date().toLocaleTimeString());
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch metrics');
            console.error('Error fetching metrics:', err);
        } finally {
            setLoading(false);
        }
    };

    // Fetch logs for selected service
    const fetchServiceLogs = async (serviceName) => {
        try {
            const response = await healthAPI.getServiceLogs(serviceName, 100);
            setServiceLogs(response.data);
            setSelectedService(serviceName);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch service logs');
            console.error('Error fetching logs:', err);
        }
    };

    // Initial fetch
    useEffect(() => {
        fetchMetrics();
    }, []);

    // Set up polling interval
    useEffect(() => {
        const interval = setInterval(fetchMetrics, refreshInterval * 1000);
        return () => clearInterval(interval);
    }, [refreshInterval]);

    // Utility function to format bytes (not strictly needed now, but kept)
    const formatBytes = (bytes) => {
        if (bytes === null || bytes === undefined) return 'N/A';
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    // Get status color for Droplet Status
    const getStatusColor = (status) => {
        switch (status) {
            case 'active':
                return '#27ae60';
            case 'new':
                return '#3498db';
            default:
                return '#e74c3c';
        }
    };

    // Get color for utilization metrics (CPU, Memory, Disk) based on percentage
    const getUtilizationColor = (usage) => {
        if (usage === null || usage === undefined) return '#95a5a6'; // Gray for N/A
        if (usage < 50) return '#27ae60'; // Green: Low
        if (usage < 80) return '#f39c12'; // Yellow: Medium/Warning
        return '#e74c3c'; // Red: High/Critical
    };

    return (
        <div className="container">
            <div className="health-page">
                <div className="health-header">
                    <h1 className="page-title">System Health Dashboard</h1>
                    <p className="page-subtitle">Monitor DigitalOcean droplets and service health</p>

                    <div className="health-controls">
                        <div className="control-group">
                            <label>Auto-refresh interval:</label>
                            <select
                                value={refreshInterval}
                                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                                className="select-control"
                            >
                                <option value={30}>30 seconds</option>
                                <option value={60}>60 seconds</option>
                            </select>
                        </div>
                        <button
                            onClick={fetchMetrics}
                            className="btn btn-primary"
                            disabled={loading}
                        >
                            {loading ? '⟳ Refreshing...' : '⟳ Refresh Now'}
                        </button>
                        {lastUpdated && (
                            <span className="last-updated">
                                Last updated: {lastUpdated}
                            </span>
                        )}
                    </div>
                </div>

                {error && (
                    <div className="alert alert-error">
                        <strong>Error:</strong> {error}
                    </div>
                )}

                {loading && !metrics && (
                    <div className="alert alert-info">
                        Loading system metrics...
                    </div>
                )}

                {metrics && (
                    <>
                        {/* Droplet Metrics Section */}
                        <section className="metrics-section">
                            <h2 className="section-title">Droplet Metrics</h2>

                            {metrics.droplets && metrics.droplets.length > 0 ? (
                                <div className="droplets-grid">
                                    {metrics.droplets.map((droplet) => {
                                        // Calculate memory in GB for display
                                        const totalMemoryGB = droplet.memory_mb ? (droplet.memory_mb / 1024).toFixed(1) : 'N/A';

                                        return (
                                            <div key={droplet.droplet_id} className="droplet-card">
                                                <div className="card-header">
                                                    <h3>{droplet.name}</h3>
                                                    <span
                                                        className="status-badge"
                                                        style={{ backgroundColor: getStatusColor(droplet.status) }}
                                                    >
                                                        {droplet.status}
                                                    </span>
                                                </div>

                                                <div className="metrics-grid">
                                                    {/* 1. CPU Usage */}
                                                    <div className="metric-box">
                                                        <div className="metric-label">CPU Usage</div>
                                                        <div
                                                            className="metric-value"
                                                            style={{ color: getUtilizationColor(droplet.cpu_usage) }}
                                                        >
                                                            {droplet.cpu_usage !== null
                                                                ? `${Math.round(droplet.cpu_usage)}%`
                                                                : 'N/A'}
                                                        </div>
                                                        {droplet.vcpus && (
                                                            <div className="metric-subtext">{droplet.vcpus} vCPU(s)</div>
                                                        )}
                                                    </div>

                                                    {/* 2. Memory Utilization */}
                                                    <div className="metric-box">
                                                        <div className="metric-label">Memory</div>
                                                        <div className="metric-value"
                                                            style={{ color: getUtilizationColor(droplet.memory_usage) }}
                                                        >
                                                            {droplet.memory_usage !== null
                                                                ? `${Math.round(droplet.memory_usage)}%`
                                                                : 'N/A'}
                                                        </div>
                                                        {totalMemoryGB && (
                                                            <div className="metric-subtext">{totalMemoryGB} GB</div>
                                                        )}
                                                    </div>

                                                    {/* 3. Disk Utilization */}
                                                    <div className="metric-box">
                                                        <div className="metric-label">Disk</div>
                                                        {/* Main value: Total Disk Size */}
                                                        <div className="metric-value"
                                                            style={{ color: getUtilizationColor(droplet.disk_usage) }}
                                                        >
                                                            {droplet.disk_usage !== null
                                                                ? `${Math.round(droplet.disk_usage)}%`
                                                                : 'N/A'}                
                                                        </div>
                                                        {droplet.disk_gb && (
                                                            <div className="metric-subtext">{droplet.disk_gb} GB</div>
                                                        )}
                                                    </div>

                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div className="alert alert-warning">
                                    No droplet metrics available. Configure DIGITALOCEAN_TOKEN and DIGITALOCEAN_DROPLET_IDS in environment variables.
                                </div>
                            )}
                        </section>

                        {/* Docker Services Section */}
                        <section className="services-section">
                            <h2 className="section-title">Docker Services</h2>

                            <div className="services-container">
                                <div className="services-list">
                                    {metrics.services && metrics.services.map((service) => (
                                        <button
                                            key={service}
                                            className={`service-btn ${selectedService === service ? 'active' : ''}`}
                                            onClick={() => fetchServiceLogs(service)}
                                        >
                                            {service}
                                        </button>
                                    ))}
                                </div>

                                {selectedService && serviceLogs && (
                                    <div className="logs-viewer">
                                        <div className="logs-header">
                                            <h3>Logs: {serviceLogs.service}</h3>
                                            <span className="logs-meta">
                                                {serviceLogs.log_lines} lines • {new Date(serviceLogs.timestamp).toLocaleTimeString()}
                                            </span>
                                        </div>
                                        <div className="logs-content">
                                            {serviceLogs.logs && serviceLogs.logs.length > 0 ? (
                                                <pre>{serviceLogs.logs.join('\n')}</pre>
                                            ) : (
                                                <div className="no-logs">No logs available</div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {!selectedService && (
                                    <div className="logs-viewer empty">
                                        <div className="no-logs">
                                            Select a service to view logs
                                        </div>
                                    </div>
                                )}
                            </div>
                        </section>

                    </>
                )}
            </div>
        </div >
    );
}

export default SystemHealth;