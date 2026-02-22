import React, { useState, useEffect } from 'react';
import { AdminLayout } from './AdminLayout';
import { Dashboard } from './Dashboard';
import { UsersManagement } from './UsersManagement';
import { BannedUsers } from './BannedUsers';
import { AuditLogs } from './AuditLogs';
import { EmailProviders } from './EmailProviders';
import { UserActivity } from './UserActivity';
import { setAuthToken } from '../../services/adminApi';

export function AdminPanel({ user, token, onLogout, onBackToApp }) {
  const [currentView, setCurrentView] = useState('dashboard');

  useEffect(() => {
    // Set auth token for API calls
    if (token) {
      console.log('Setting auth token in AdminPanel');
      setAuthToken(token);
    }
  }, [token]);

  // Check if user is admin or superadmin
  if (!user || (user.role !== 'ADMIN' && user.role !== 'SUPERADMIN')) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">You don't have permission to access the admin panel.</p>
          <button
            onClick={onBackToApp}
            className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800"
          >
            Back to App
          </button>
        </div>
      </div>
    );
  }

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'users':
        return <UsersManagement />;
      case 'banned':
        return <BannedUsers />;
      case 'audit':
        return <AuditLogs />;
      case 'email-providers':
        return <EmailProviders />;
      case 'activity':
        return <UserActivity />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <AdminLayout
      currentView={currentView}
      onViewChange={setCurrentView}
      user={user}
      onLogout={onLogout}
      onBackToApp={onBackToApp}
    >
      {renderView()}
    </AdminLayout>
  );
}
