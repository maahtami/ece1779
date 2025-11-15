import client from './client';

export const authAPI = {
  register: (username, password) => {
    return client.post('/auth/register', {
      username,
      password,
    });
  },

  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
};
