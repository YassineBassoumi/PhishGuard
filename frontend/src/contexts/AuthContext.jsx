/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load token from localStorage on mount and validate it
  useEffect(() => {
    const validateToken = async () => {
      const storedToken = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('auth_user');
      
      if (storedToken && storedUser) {
        try {
          // Validate token by calling /me endpoint
          const response = await fetch('http://localhost:8000/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${storedToken}`
            }
          });
          
          if (response.ok) {
            // Token is valid
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
          } else {
            // Token is invalid, clear it
            console.log('Stored token is invalid, clearing...');
            localStorage.removeItem('auth_token');
            localStorage.removeItem('auth_user');
          }
        } catch (err) {
          console.error('Failed to validate token:', err);
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }
      
      setLoading(false);
    };
    
    validateToken();
  }, []);

  const login = async (username, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Store token and user
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(data.user));
      
      // Store first login info for redirect
      if (data.is_first_login && data.suggested_provider) {
        localStorage.setItem('first_login_provider', data.suggested_provider);
      }
      
      setToken(data.access_token);
      setUser(data.user);
      
      return { success: true, isFirstLogin: data.is_first_login, suggestedProvider: data.suggested_provider };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message };
    }
  };

  const register = async (email, username, password) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          username,
          password
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      const data = await response.json();
      
      // Registration successful - email verification required
      // Don't store token or user, just return success
      return { success: true, data };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    // Get current user to clean up their credentials
    const currentUser = user;
    
    // Remove auth data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    
    // Remove user-specific provider credentials
    if (currentUser) {
      const userId = currentUser.id || currentUser.username;
      const providers = ['gmail', 'outlook'];
      
      providers.forEach(provider => {
        localStorage.removeItem(`${provider}_credentials_${userId}`);
      });
      
      // Also remove old non-user-specific credentials (for cleanup)
      localStorage.removeItem('gmail_credentials');
    }
    
    setToken(null);
    setUser(null);
  };

  const updateUser = async (updates) => {
    try {
      // If updates is empty, just fetch fresh user data
      if (Object.keys(updates).length === 0) {
        const response = await fetch('http://localhost:8000/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }
        
        const data = await response.json();
        localStorage.setItem('auth_user', JSON.stringify(data));
        setUser(data);
        return { success: true };
      }
      
      const response = await fetch('http://localhost:8000/api/auth/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Update failed');
      }

      const data = await response.json();
      
      // Update stored user
      localStorage.setItem('auth_user', JSON.stringify(data));
      setUser(data);
      
      return { success: true };
    } catch (error) {
      console.error('Update error:', error);
      return { success: false, error: error.message };
    }
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    register,
    logout,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
