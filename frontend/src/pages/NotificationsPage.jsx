import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Bell, Check, Trash2, Filter, AlertTriangle, Shield, Lock, Info, Mail } from 'lucide-react';
import './NotificationsPage.css';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, unread, read
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { token } = useAuth();

  // Fetch notifications
  const fetchNotifications = async () => {
    if (!token) return;

    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/notifications/all?page=${page}&per_page=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setTotalPages(data.total_pages || 1);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [token, page]);

  // Filter notifications
  const filteredNotifications = notifications.filter(notif => {
    if (filter === 'unread') return !notif.is_read;
    if (filter === 'read') return notif.is_read;
    return true;
  });

  // Mark as read
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
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  // Delete notification
  const deleteNotification = async (notificationId) => {
    if (!confirm('Delete this notification?')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setNotifications(notifications.filter(n => n.id !== notificationId));
      }
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  // Get icon based on notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'dangerous_email_alert':
        return <AlertTriangle className="notif-page-icon danger" size={24} />;
      case 'new_login_alert':
        return <Shield className="notif-page-icon warning" size={24} />;
      case 'password_changed_alert':
        return <Lock className="notif-page-icon success" size={24} />;
      case 'two_factor_changed_alert':
        return <Shield className="notif-page-icon info" size={24} />;
      default:
        return <Info className="notif-page-icon info" size={24} />;
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get notification type label
  const getTypeLabel = (type) => {
    switch (type) {
      case 'dangerous_email_alert':
        return 'Email Dangereux';
      case 'new_login_alert':
        return 'Nouvelle Connexion';
      case 'password_changed_alert':
        return 'Mot de Passe Modifié';
      case 'two_factor_changed_alert':
        return '2FA Modifié';
      default:
        return 'Notification';
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="notifications-page">
      {/* Header */}
      <div className="notifications-page-header">
        <div className="header-left">
          <Bell size={32} className="page-icon" />
          <div>
            <h1>Notifications</h1>
            <p>{unreadCount} non lue{unreadCount !== 1 ? 's' : ''}</p>
          </div>
        </div>
        <div className="header-actions">
          {unreadCount > 0 && (
            <button onClick={markAllAsRead} className="mark-all-btn">
              <Check size={18} />
              Tout marquer comme lu
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="notifications-filters">
        <button 
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          Toutes ({notifications.length})
        </button>
        <button 
          className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
          onClick={() => setFilter('unread')}
        >
          Non lues ({unreadCount})
        </button>
        <button 
          className={`filter-btn ${filter === 'read' ? 'active' : ''}`}
          onClick={() => setFilter('read')}
        >
          Lues ({notifications.length - unreadCount})
        </button>
      </div>

      {/* Notifications List */}
      <div className="notifications-page-list">
        {loading ? (
          <div className="loading-state">
            <div className="spinner-large"></div>
            <p>Chargement des notifications...</p>
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div className="empty-state">
            <Bell size={64} className="empty-icon" />
            <h3>Aucune notification</h3>
            <p>
              {filter === 'unread' && 'Vous avez tout lu!'}
              {filter === 'read' && 'Aucune notification lue'}
              {filter === 'all' && 'Vous n\'avez pas encore de notifications'}
            </p>
          </div>
        ) : (
          filteredNotifications.map((notification) => (
            <div 
              key={notification.id}
              className={`notification-page-item ${!notification.is_read ? 'unread' : ''}`}
            >
              <div className="notif-icon-wrapper">
                {getNotificationIcon(notification.notification_type)}
              </div>

              <div className="notif-content">
                <div className="notif-header">
                  <span className="notif-type-badge">
                    {getTypeLabel(notification.notification_type)}
                  </span>
                  <span className="notif-date">
                    {formatDate(notification.sent_at)}
                  </span>
                </div>
                <h3 className="notif-subject">{notification.subject}</h3>
                {notification.status === 'failed' && (
                  <p className="notif-error">
                    ⚠️ Échec de l'envoi: {notification.error_message}
                  </p>
                )}
              </div>

              <div className="notif-actions">
                {!notification.is_read && (
                  <button 
                    onClick={() => markAsRead(notification.id)}
                    className="action-btn"
                    title="Marquer comme lu"
                  >
                    <Check size={18} />
                  </button>
                )}
                <button 
                  onClick={() => deleteNotification(notification.id)}
                  className="action-btn delete"
                  title="Supprimer"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="notifications-pagination">
          <button 
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="pagination-btn"
          >
            Précédent
          </button>
          <span className="pagination-info">
            Page {page} sur {totalPages}
          </span>
          <button 
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="pagination-btn"
          >
            Suivant
          </button>
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;
