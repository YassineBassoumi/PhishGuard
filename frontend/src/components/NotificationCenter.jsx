import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Bell, X, Check, AlertTriangle, Shield, Mail, Lock, Info, Trash2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import './NotificationCenter.css';

const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);
  const { token } = useAuth();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch notifications
  const fetchNotifications = useCallback(async () => {
    if (!token) return;

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/notifications/recent', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Poll for new notifications every 60 seconds (increased from 30 to reduce server load)
  useEffect(() => {
    if (token) {
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 60000); // 60 seconds
      return () => clearInterval(interval);
    }
  }, [token, fetchNotifications]);

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setNotifications(notifications.map(n => 
          n.id === notificationId ? { ...n, is_read: true } : n
        ));
        setUnreadCount(Math.max(0, unreadCount - 1));
      }
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/notifications/mark-all-read', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setNotifications(notifications.map(n => ({ ...n, is_read: true })));
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  // Delete all notifications for the current user
  const clearAll = async () => {
    if (!window.confirm('Supprimer toutes les notifications ? Cette action est irréversible.')) {
      return;
    }
    try {
      const response = await fetch('http://localhost:8000/api/notifications', {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        setNotifications([]);
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Failed to clear notifications:', error);
    }
  };

  // Get icon based on notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'dangerous_email_alert':
        return <AlertTriangle className="notif-icon danger" size={20} />;
      case 'new_login_alert':
        return <Shield className="notif-icon warning" size={20} />;
      case 'password_changed_alert':
        return <Lock className="notif-icon success" size={20} />;
      case 'two_factor_changed_alert':
        return <Shield className="notif-icon info" size={20} />;
      default:
        return <Info className="notif-icon info" size={20} />;
    }
  };

  // Format time ago
  const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="notification-center" ref={dropdownRef}>
      {/* Bell Icon with Badge */}
      <button 
        className="notification-bell"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notifications"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="notification-badge">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="notification-dropdown">
          {/* Header */}
          <div className="notification-header">
            <h3>Notifications</h3>
            <div className="notification-header-actions">
              {unreadCount > 0 && (
                <button
                  className="mark-all-read"
                  onClick={markAllAsRead}
                >
                  <Check size={16} />
                  Mark all read
                </button>
              )}
              {notifications.length > 0 && (
                <button
                  className="clear-all"
                  onClick={clearAll}
                  title="Supprimer toutes les notifications"
                >
                  <Trash2 size={16} />
                  Clear all
                </button>
              )}
            </div>
          </div>

          {/* Notifications List */}
          <div className="notification-list">
            {loading ? (
              <div className="notification-loading">
                <div className="spinner"></div>
                <p>Loading notifications...</p>
              </div>
            ) : notifications.length === 0 ? (
              <div className="notification-empty">
                <Bell size={48} className="empty-icon" />
                <p>No notifications yet</p>
                <span>You're all caught up!</span>
              </div>
            ) : (
              notifications.map((notification) => (
                <div 
                  key={notification.id}
                  className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                  onClick={() => !notification.is_read && markAsRead(notification.id)}
                >
                  {getNotificationIcon(notification.notification_type)}
                  
                  <div className="notification-content">
                    <div className="notification-title">
                      {notification.subject}
                    </div>
                    <div className="notification-time">
                      {timeAgo(notification.sent_at)}
                    </div>
                  </div>

                  {!notification.is_read && (
                    <div className="unread-dot"></div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="notification-footer">
              <a href="/notifications" className="view-all-link">
                View all notifications
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
