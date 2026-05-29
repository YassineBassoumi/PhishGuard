import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: always inject the latest token from localStorage.
// This avoids race conditions where API calls fire before setAuthToken runs
// (e.g. child useEffect runs before parent useEffect).
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Kept for backward compatibility (no-op when interceptor is present)
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// User Management
export const adminApi = {
  // Users
  getUsers: (skip = 0, limit = 100) => 
    api.get(`/admin/users?skip=${skip}&limit=${limit}`),
  
  getUser: (userId) => 
    api.get(`/admin/users/${userId}`),
  
  updateUserRole: (userId, role) => 
    api.put(`/admin/users/${userId}/role`, { role }),
  
  deleteUser: (userId) => 
    api.delete(`/admin/users/${userId}`),
  
  banUser: (userId, reason) => 
    api.post(`/admin/users/${userId}/ban`, { reason }),
  
  unbanUser: (userId) => 
    api.post(`/admin/users/${userId}/unban`),
  
  getBannedUsers: (skip = 0, limit = 100) => 
    api.get(`/admin/banned-users?skip=${skip}&limit=${limit}`),
  
  // User Activity
  getUserActivity: (userId) => 
    api.get(`/admin/users/${userId}/activity`),
  
  // Statistics
  getStats: () => 
    api.get('/admin/stats'),
  
  // Audit Logs
  getAuditLogs: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.action) queryParams.append('action', params.action);
    if (params.actor_id) queryParams.append('actor_id', params.actor_id);
    if (params.target_user_id) queryParams.append('target_user_id', params.target_user_id);
    
    return api.get(`/admin/audit-logs?${queryParams.toString()}`);
  },
  
  getAuditActions: () => 
    api.get('/admin/audit-logs/actions'),
  
  getAuditStats: () => 
    api.get('/admin/audit-logs/stats'),
  
  // Email Providers
  getEmailConnections: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.provider) queryParams.append('provider', params.provider);
    if (params.user_id) queryParams.append('user_id', params.user_id);
    
    return api.get(`/admin/email-providers/connections?${queryParams.toString()}`);
  },
  
  getEmailProviderStats: () => 
    api.get('/admin/email-providers/stats'),
  
  revokeEmailConnection: (connectionId) => 
    api.delete(`/admin/email-providers/connections/${connectionId}`),
  
  getUserEmailConnections: (userId) => 
    api.get(`/admin/email-providers/users/${userId}/connections`),
};

export default api;
