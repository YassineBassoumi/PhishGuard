import { useState, useEffect } from 'react';
import Toast from './Toast';
import './SessionManagement.css';

const SessionManagement = ({ token }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  useEffect(() => {
    fetchSessions();
  }, [token]);

  const fetchSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/sessions/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions);
      } else {
        setError('Échec du chargement des sessions');
      }
    } catch (err) {
      console.error('Error fetching sessions:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const [confirmingRevoke, setConfirmingRevoke] = useState(null);

  const revokeSession = async (sessionId) => {
    try {
      const response = await fetch('http://localhost:8000/api/sessions/revoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (response.ok) {
        setToastMessage('Session déconnectée avec succès');
        setToastType('success');
        setShowToast(true);
        setConfirmingRevoke(null);
        fetchSessions();
      } else {
        const error = await response.json();
        setToastMessage(error.detail || 'Échec de la déconnexion');
        setToastType('error');
        setShowToast(true);
      }
    } catch (err) {
      console.error('Error revoking session:', err);
      setToastMessage('Erreur de connexion au serveur');
      setToastType('error');
      setShowToast(true);
    }
  };

  const [confirmingRevokeAll, setConfirmingRevokeAll] = useState(false);

  const revokeAllSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/sessions/revoke-all', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setToastMessage(data.message);
        setToastType('success');
        setShowToast(true);
        setConfirmingRevokeAll(false);
        fetchSessions();
      } else {
        const error = await response.json();
        setToastMessage(error.detail || 'Échec de la déconnexion');
        setToastType('error');
        setShowToast(true);
      }
    } catch (err) {
      console.error('Error revoking all sessions:', err);
      setToastMessage('Erreur de connexion au serveur');
      setToastType('error');
      setShowToast(true);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays}j`;
    
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  if (loading) {
    return (
      <div className="sessions-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="sessions-container">
      {showToast && (
        <div className="toast-container">
          <Toast
            message={toastMessage}
            type={toastType}
            onClose={() => setShowToast(false)}
            duration={3000}
          />
        </div>
      )}

      <div className="sessions-header">
        <div className="sessions-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2" strokeWidth="2"/>
            <line x1="8" y1="21" x2="16" y2="21" strokeWidth="2" strokeLinecap="round"/>
            <line x1="12" y1="17" x2="12" y2="21" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </div>
        <div>
          <h2 className="sessions-title">Gestion des Sessions</h2>
          <p className="sessions-subtitle">
            Gérez les appareils connectés à votre compte
          </p>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
          </svg>
          {error}
        </div>
      )}

      {sessions.length > 0 && (
        <div className="sessions-actions-top">
          <button
            className="btn-revoke-all"
            onClick={() => setConfirmingRevokeAll(true)}
            disabled={sessions.filter(s => !s.is_current).length === 0}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M18 8L6 20M6 8L18 20" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Déconnecter Tous les Autres Appareils
          </button>
        </div>
      )}

      {/* Confirmation Modal for Revoke All */}
      {confirmingRevokeAll && (
        <div className="modal-overlay" onClick={() => setConfirmingRevokeAll(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="modal-icon-warning">
                <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
              </svg>
              <h3>Déconnecter Tous les Appareils?</h3>
              <p>Êtes-vous sûr de vouloir déconnecter tous les autres appareils? Cette action ne peut pas être annulée.</p>
            </div>
            <div className="modal-actions">
              <button className="btn-modal-cancel" onClick={() => setConfirmingRevokeAll(false)}>
                Annuler
              </button>
              <button className="btn-modal-confirm" onClick={revokeAllSessions}>
                Oui, Déconnecter Tout
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="sessions-list">
        {sessions.length === 0 ? (
          <div className="no-sessions">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2" strokeWidth="2"/>
              <line x1="8" y1="21" x2="16" y2="21" strokeWidth="2" strokeLinecap="round"/>
              <line x1="12" y1="17" x2="12" y2="21" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <p>Aucune session active</p>
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              className={`session-card ${session.is_current ? 'current-session' : ''}`}
            >
              <div className="session-icon">
                {session.device_info?.includes('Windows') || session.device_info?.includes('Mac') || session.device_info?.includes('Linux') ? (
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2" strokeWidth="2"/>
                    <line x1="8" y1="21" x2="16" y2="21" strokeWidth="2" strokeLinecap="round"/>
                    <line x1="12" y1="17" x2="12" y2="21" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                ) : (
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="5" y="2" width="14" height="20" rx="2" ry="2" strokeWidth="2"/>
                    <line x1="12" y1="18" x2="12.01" y2="18" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                )}
              </div>

              <div className="session-info">
                <div className="session-device">
                  <h3>{session.device_info || 'Appareil Inconnu'}</h3>
                  {session.is_current && (
                    <span className="current-badge">
                      <span className="badge-dot"></span>
                      Session Actuelle
                    </span>
                  )}
                </div>

                <div className="session-details">
                  <div className="detail-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" strokeWidth="2"/>
                      <circle cx="12" cy="9" r="2.5" strokeWidth="2"/>
                    </svg>
                    <span>{session.ip_address || 'IP inconnue'}</span>
                  </div>

                  <div className="detail-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                      <path d="M12 6V12L16 14" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <span>Dernière activité: {formatDate(session.last_activity)}</span>
                  </div>

                  <div className="detail-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" strokeWidth="2"/>
                      <line x1="16" y1="2" x2="16" y2="6" strokeWidth="2" strokeLinecap="round"/>
                      <line x1="8" y1="2" x2="8" y2="6" strokeWidth="2" strokeLinecap="round"/>
                      <line x1="3" y1="10" x2="21" y2="10" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <span>Connecté le {new Date(session.created_at).toLocaleDateString('fr-FR')}</span>
                  </div>
                </div>
              </div>

              {!session.is_current && (
                <>
                  <button
                    className="btn-revoke-session"
                    onClick={() => setConfirmingRevoke(session.id)}
                    title="Déconnecter cette session"
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M18 8L6 20M6 8L18 20" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  </button>

                  {/* Confirmation Modal for Individual Session */}
                  {confirmingRevoke === session.id && (
                    <div className="modal-overlay" onClick={() => setConfirmingRevoke(null)}>
                      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="modal-icon-warning">
                            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
                          </svg>
                          <h3>Déconnecter cette Session?</h3>
                          <p>Êtes-vous sûr de vouloir déconnecter <strong>{session.device_info || 'cet appareil'}</strong>?</p>
                        </div>
                        <div className="modal-actions">
                          <button className="btn-modal-cancel" onClick={() => setConfirmingRevoke(null)}>
                            Annuler
                          </button>
                          <button className="btn-modal-confirm" onClick={() => revokeSession(session.id)}>
                            Oui, Déconnecter
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          ))
        )}
      </div>

      {sessions.length > 0 && (
        <div className="sessions-info-box">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            <line x1="12" y1="16" x2="12" y2="12" strokeWidth="2" strokeLinecap="round"/>
            <line x1="12" y1="8" x2="12.01" y2="8" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <div>
            <p className="info-title">Conseil de Sécurité</p>
            <p className="info-text">
              Si vous voyez une session que vous ne reconnaissez pas, déconnectez-la immédiatement et changez votre mot de passe.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionManagement;
