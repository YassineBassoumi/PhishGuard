import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import PasswordStrengthIndicator from './PasswordStrengthIndicator';
import Toast from './Toast';
import './ResetPassword.css';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');
  const [resetSuccess, setResetSuccess] = useState(false);

  useEffect(() => {
    if (!token) {
      setVerifying(false);
      setTokenValid(false);
      return;
    }

    verifyToken();
  }, [token]);

  const verifyToken = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/password-reset/verify?token=${token}`, {
        method: 'POST'
      });

      if (response.ok) {
        setTokenValid(true);
      } else {
        setTokenValid(false);
        setToastMessage('Le lien de réinitialisation est invalide ou expiré');
        setToastType('error');
        setShowToast(true);
      }
    } catch (error) {
      console.error('Error verifying token:', error);
      setTokenValid(false);
      setToastMessage('Erreur de connexion au serveur');
      setToastType('error');
      setShowToast(true);
    } finally {
      setVerifying(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (password.length < 8) {
      setToastMessage('Le mot de passe doit contenir au moins 8 caractères');
      setToastType('error');
      setShowToast(true);
      return;
    }

    if (password !== confirmPassword) {
      setToastMessage('Les mots de passe ne correspondent pas');
      setToastType('error');
      setShowToast(true);
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/password-reset/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          token: token,
          new_password: password
        })
      });

      if (response.ok) {
        setResetSuccess(true);
        // Don't show toast when showing success modal
        setShowToast(false);

        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/');
        }, 3000);
      } else {
        const data = await response.json();
        setToastMessage(data.detail || 'Échec de la réinitialisation');
        setToastType('error');
        setShowToast(true);
      }
    } catch (error) {
      console.error('Error resetting password:', error);
      setToastMessage('Erreur de connexion au serveur');
      setToastType('error');
      setShowToast(true);
    } finally {
      setLoading(false);
    }
  };

  if (verifying) {
    return (
      <div className="reset-password-container">
        <div className="reset-password-card">
          <div className="loading-state">
            <div className="spinner-large"></div>
            <p>Vérification du lien...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!token || !tokenValid) {
    return (
      <div className="reset-password-container">
        {showToast && (
          <Toast
            message={toastMessage}
            type={toastType}
            onClose={() => setShowToast(false)}
            duration={5000}
          />
        )}
        <div className="reset-password-card">
          <div className="error-state">
            <div className="error-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
              </svg>
            </div>
            <h2>Lien Invalide ou Expiré</h2>
            <p>
              Le lien de réinitialisation que vous avez utilisé est invalide ou a expiré.
              Les liens de réinitialisation sont valides pendant 1 heure seulement.
            </p>
            <button className="btn-primary" onClick={() => navigate('/')}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M19 12H5M12 19L5 12L12 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Retour à la Connexion
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (resetSuccess) {
    return (
      <div className="reset-password-container">
        {showToast && (
          <Toast
            message={toastMessage}
            type={toastType}
            onClose={() => setShowToast(false)}
            duration={5000}
          />
        )}
        <div className="reset-password-card">
          <div className="success-state">
            <div className="success-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
              </svg>
            </div>
            <h2>Mot de Passe Réinitialisé!</h2>
            <p>
              Votre mot de passe a été réinitialisé avec succès.
              Vous allez être redirigé vers la page de connexion...
            </p>
            <div className="redirect-info">
              <div className="spinner-small"></div>
              <span>Redirection en cours...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="reset-password-container">
      {showToast && (
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setShowToast(false)}
          duration={5000}
        />
      )}

      <div className="reset-password-card">
        <div className="reset-password-header">
          <div className="reset-password-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
              <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
            </svg>
          </div>
          <h2>Nouveau Mot de Passe</h2>
          <p>Choisissez un mot de passe sécurisé pour votre compte</p>
        </div>

        <form onSubmit={handleSubmit} className="reset-password-form">
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
                <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
              </svg>
              Nouveau Mot de Passe
            </label>
            <input
              id="password"
              type="password"
              className="form-input"
              placeholder="Minimum 8 caractères"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              required
              minLength={8}
            />
            <PasswordStrengthIndicator password={password} />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
                <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
              </svg>
              Confirmer le Mot de Passe
            </label>
            <input
              id="confirmPassword"
              type="password"
              className={`form-input ${
                confirmPassword && password === confirmPassword ? 'password-match' : 
                confirmPassword && password !== confirmPassword ? 'password-mismatch' : ''
              }`}
              placeholder="Retapez votre mot de passe"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              required
            />
            {confirmPassword && (
              <div className={`password-match-indicator ${password === confirmPassword ? 'match' : 'mismatch'}`}>
                {password === confirmPassword ? (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M20 6L9 17L4 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <span>Les mots de passe correspondent</span>
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M18 6L6 18M6 6L18 18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <span>Les mots de passe ne correspondent pas</span>
                  </>
                )}
              </div>
            )}
          </div>

          <button type="submit" className="btn-submit" disabled={loading || password !== confirmPassword}>
            {loading ? (
              <>
                <div className="spinner"></div>
                <span>Réinitialisation...</span>
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
                </svg>
                Réinitialiser le Mot de Passe
              </>
            )}
          </button>

          <button type="button" className="btn-back" onClick={() => navigate('/')} disabled={loading}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 12H5M12 19L5 12L12 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Retour à la Connexion
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
