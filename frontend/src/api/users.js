import client from './client';

export const usersAPI = {
  create: (username, password, role) => {
    return client.post('/users/', {
      username,
      password,
      role,
    });
  },

  list: () => {
    return client.get('/users/');
  },
};
