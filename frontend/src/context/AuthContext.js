import React from 'react';
import './Auth.css';

/**
 * Auth Context Hook
 * Manages authentication state and JWT tokens
 */
export const AuthContext = React.createContext();

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = React.useState(null);
  const [token, setToken] = React.useState(localStorage.getItem('token'));
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('user');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, [token]);

  const value = {
    user,
    token,
    loading,
    setUser,
    setToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
