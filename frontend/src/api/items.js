import client from './client';

export const itemsAPI = {
  create: (itemData) => {
    return client.post('/items/', itemData);
  },

  list: () => {
    return client.get('/items/');
  },

  get: (itemId) => {
    return client.get(`/items/${itemId}`);
  },

  update: (itemId, itemData) => {
    return client.put(`/items/${itemId}`, itemData);
  },

  delete: (itemId) => {
    return client.delete(`/items/${itemId}`);
  },
};
