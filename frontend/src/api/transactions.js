import client from './client';

export const transactionsAPI = {
  create: (itemId, type, quantity) => {
    return client.post('/transactions/', {
      item_id: itemId,
      type,
      quantity,
    });
  },

  list: () => {
    return client.get('/transactions/');
  },
};
