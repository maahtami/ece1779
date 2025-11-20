import client from './client';

export const healthAPI = {
  /**
   * Get system health metrics including droplet metrics and service logs
   * @param {number} lines - Number of log lines to retrieve (default: 100)
   * @returns {Promise} System metrics response
   */
  getSystemMetrics: (lines = 100) => {
    return client.get('/health/system-metrics', {
      params: { lines }
    });
  },

  /**
   * Get metrics from DigitalOcean droplets
   * @returns {Promise} Droplet metrics response
   */
  getDropletMetrics: () => {
    return client.get('/health/droplet-metrics');
  },

  /**
   * Get logs from a specific Docker service
   * @param {string} serviceName - Name of the service (e.g., 'ims_stack_api')
   * @param {number} lines - Number of log lines to retrieve (default: 100)
   * @returns {Promise} Service logs response
   */
  getServiceLogs: (serviceName, lines = 100) => {
    return client.get(`/health/service-logs/${serviceName}`, {
      params: { lines }
    });
  },
};
