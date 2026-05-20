import { useState } from 'react';
import './Login.css';

const Login = ({ onSwitchToRegister, onSwitchToForgotPassword }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [show2FA, setShow2FA] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showReactivateModal, setShowReactivateModal] = useState(false);
  const [reactivating, setReactivating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username.trim() || !password.trim()) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    if (show2FA && !twoFactorCode.trim()) {
      setError('Veuillez entrer le code d\'authentification');
      return;
    }

    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      // Add 2FA code if provided
      if (twoFactorCode) {
        formData.append('scope', twoFactorCode);
      }

      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      });

      // Check if 2FA is required
      if (response.status === 403) {
        const errorData = await response.json();
        
        // Check if account is deactivated - offer reactivation
        if (errorData.detail === 'ACCOUNT_DEACTIVATED' || response.headers.get('X-Reactivation-Required') === 'true') {
          setShowReactivateModal(true);
          setLoading(false);
          return;
        }
        
        // Check if it's email verification issue
        if (errorData.detail && errorData.detail.includes('Email non vérifié')) {
          setError('Votre email n\'est pas vérifié. Veuillez vérifier votre boîte de réception.');
          setLoading(false);
          return;
        }
        
        // Check if it's a 2FA requirement
        if (errorData.detail === '2FA code required' || response.headers.get('X-2FA-Required') === 'true') {
          setShow2FA(true);
          setError('Veuillez entrer votre code d\'authentification à deux facteurs');
          setLoading(false);
          return;
        }
        
        // Other 403 errors (banned, etc.)
        setError(errorData.detail || 'Accès refusé');
        setLoading(false);
        return;
      }

      if (!response.ok) {
        const error = await response.json();
        setError(error.detail || 'Échec de la connexion');
        setLoading(false);
        return;
      }

      const data = await response.json();
      
      // Store token and user
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(data.user));
      
      // Store first login info for redirect
      if (data.is_first_login && data.suggested_provider) {
        localStorage.setItem('first_login_provider', data.suggested_provider);
        localStorage.setItem('is_first_login', 'true');
      }
      
      // Trigger login in auth context (reload page or update state)
      window.location.reload();
      
    } catch (error) {
      console.error('Login error:', error);
      setError('Erreur de connexion au serveur');
      setLoading(false);
    }
  };

  const handleReactivate = async () => {
    setReactivating(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      if (twoFactorCode) {
        formData.append('scope', twoFactorCode);
      }

      const response = await fetch('http://localhost:8000/api/auth/reactivate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      });

      if (response.status === 403) {
        const errorData = await response.json();
        if (errorData.detail === '2FA code required' || response.headers.get('X-2FA-Required') === 'true') {
          setShowReactivateModal(false);
          setShow2FA(true);
          setError('Veuillez entrer votre code 2FA pour réactiver votre compte');
          setReactivating(false);
          return;
        }
        setError(errorData.detail || 'Réactivation refusée');
        setShowReactivateModal(false);
        setReactivating(false);
        return;
      }

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || 'Échec de la réactivation');
        setShowReactivateModal(false);
        setReactivating(false);
        return;
      }

      const data = await response.json();
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(data.user));
      window.location.reload();
    } catch (err) {
      console.error('Reactivation error:', err);
      setError('Erreur de connexion au serveur');
      setShowReactivateModal(false);
      setReactivating(false);
    }
  };

  const handleCancelReactivate = () => {
    setShowReactivateModal(false);
    setError('Votre compte est désactivé.');
  };

  return (
    <div className="auth-container fade-in-up">
      <div className="glass-card auth-card">
        <div className="auth-header">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="auth-icon">
            <path d="M12 15V17M6 21H18C19.1046 21 20 20.1046 20 19V13C20 11.8954 19.1046 11 18 11H6C4.89543 11 4 11.8954 4 13V19C4 20.1046 4.89543 21 6 21ZM16 11V7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7V11H16Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h2 className="auth-title">Connexion</h2>
          <p className="auth-subtitle">Connectez-vous à votre compte PhishGuard</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Nom d'utilisateur
            </label>
            <input
              id="username"
              type="text"
              className="input"
              placeholder="johndoe"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Mot de passe
            </label>
            <input
              id="password"
              type="password"
              className="input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="current-password"
            />
            <div className="forgot-password-link">
              <button
                type="button"
                className="link-button-small"
                onClick={onSwitchToForgotPassword}
                disabled={loading}
              >
                Mot de passe oublié?
              </button>
            </div>
          </div>

          {show2FA && (
            <div className="form-group">
              <label htmlFor="twoFactorCode" className="form-label">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{ display: 'inline', marginRight: '0.5rem' }}>
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
                  <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
                </svg>
                Code d'authentification à deux facteurs
              </label>
              <input
                id="twoFactorCode"
                type="text"
                className="input"
                placeholder="000000"
                maxLength="9"
                value={twoFactorCode}
                onChange={(e) => setTwoFactorCode(e.target.value.replace(/[^A-Z0-9-]/gi, ''))}
                disabled={loading}
                autoComplete="one-time-code"
                style={{ letterSpacing: '0.3rem', textAlign: 'center', fontWeight: '600' }}
              />
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                Entrez le code à 6 chiffres de votre app, ou un code de secours (XXXX-XXXX)
              </p>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '3px' }}></div>
                <span>Connexion...</span>
              </>
            ) : (
              'Se connecter'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Pas encore de compte ?{' '}
            <button
              type="button"
              className="link-button"
              onClick={() => {
                console.log('Switching to register...');
                if (onSwitchToRegister) {
                  onSwitchToRegister();
                } else {
                  console.error('onSwitchToRegister is not defined');
                }
              }}
              disabled={loading}
            >
              Créer un compte
            </button>
          </p>
        </div>
      </div>

      {/* Reactivation Modal */}
      {showReactivateModal && (
        <div className="modal-overlay" onClick={() => !reactivating && handleCancelReactivate()}>
          <div
            className="modal-content modal-danger modal-deactivate"
            onClick={(e) => e.stopPropagation()}
            style={{ maxWidth: 500 }}
          >
            <div className="modal-header">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="modal-icon-danger modal-icon-deactivate">
                <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64M12 2v10" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <h3>Compte désactivé</h3>
              <p>
                Votre compte est actuellement désactivé.
                <br />
                <strong>Souhaitez-vous le réactiver et vous connecter ?</strong>
              </p>
            </div>
            <div className="modal-actions">
              <button
                className="btn-modal-cancel"
                onClick={handleCancelReactivate}
                disabled={reactivating}
              >
                Non, annuler
              </button>
              <button
                className="btn-modal-danger btn-modal-deactivate"
                onClick={handleReactivate}
                disabled={reactivating}
              >
                {reactivating ? 'Réactivation...' : 'Oui, réactiver mon compte'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
