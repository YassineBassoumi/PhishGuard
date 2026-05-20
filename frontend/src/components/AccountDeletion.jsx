import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Toast from './Toast';
import './AccountDeletion.css';

const AccountDeletion = () => {
  const { token, logout } = useAuth();
  const [showDeactivateSection, setShowDeactivateSection] = useState(false);
  const [password, setPassword] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');
  const [showFinalConfirmation, setShowFinalConfirmation] = useState(false);

  const handleDeactivateAccount = async () => {
    setError('');
    setShowFinalConfirmation(false);

    // Validation
    if (!password) {
      setError('Veuillez entrer votre mot de passe');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/me/deactivate', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          password: password,
          reason: reason || null
        })
      });

      if (response.ok) {
        setToastMessage('Compte d\u00e9sactiv\u00e9 avec succ\u00e8s');
        setToastType('success');
        setShowToast(true);
        
        // Logout after 2 seconds
        setTimeout(() => {
          logout();
        }, 2000);
      } else {
        const data = await response.json();
        setError(data.detail || '\u00c9chec de la d\u00e9sactivation du compte');
      }
    } catch (err) {
      console.error('Error deactivating account:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setPassword('');
    setReason('');
    setError('');
    setShowDeactivateSection(false);
    setShowFinalConfirmation(false);
  };

  return (
    <div className="account-deletion-container">
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

      <div className="deletion-header">
        <div className="deletion-icon deactivation-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64M12 2v10" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </div>
        <div>
          <h2 className="deletion-title">Désactivation du Compte</h2>
          <p className="deletion-subtitle">
            Désactivez temporairement votre compte
          </p>
        </div>
      </div>

      {!showDeactivateSection ? (
        <div className="deletion-warning-box deactivation-warning-box">
          <div className="warning-content">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
            </svg>
            <div>
              <h3>Désactiver Votre Compte</h3>
              <p>
                La désactivation rendra votre compte inaccessible. Vos données seront conservées et un administrateur pourra réactiver votre compte si nécessaire.
              </p>
              <ul className="deletion-consequences deactivation-consequences">
                <li>Vous ne pourrez plus vous connecter</li>
                <li>Toutes vos sessions actives seront fermées</li>
                <li>Vos données et analyses seront conservées</li>
                <li>Un administrateur peut réactiver votre compte</li>
              </ul>
            </div>
          </div>
          <button
            className="btn-show-delete btn-show-deactivate"
            onClick={() => setShowDeactivateSection(true)}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64M12 2v10" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Je Souhaite Désactiver Mon Compte
          </button>
        </div>
      ) : (
        <div className="deletion-form-section deactivation-form-section">
          <div className="deletion-steps">
            <div className="step-indicator">
              <div className="step-number deactivation-step-number">1</div>
              <div className="step-content">
                <h4>Vérification du Mot de Passe</h4>
                <p>Entrez votre mot de passe actuel pour confirmer votre identité</p>
                <input
                  type="password"
                  className="deletion-input"
                  placeholder="Votre mot de passe"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="step-indicator">
              <div className="step-number deactivation-step-number">2</div>
              <div className="step-content">
                <h4>Raison (optionnel)</h4>
                <p>Dites-nous pourquoi vous souhaitez désactiver votre compte</p>
                <textarea
                  className="deletion-input deactivation-textarea"
                  placeholder="Ex: Je souhaite faire une pause..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  disabled={loading}
                  rows={3}
                  maxLength={500}
                />
                <p className="input-hint" style={{ textAlign: 'right', color: '#a0aec0' }}>
                  {reason.length}/500
                </p>
              </div>
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

          <div className="deletion-actions">
            <button
              className="btn-cancel-delete"
              onClick={resetForm}
              disabled={loading}
            >
              Annuler
            </button>
            <button
              className="btn-confirm-delete btn-confirm-deactivate"
              onClick={() => setShowFinalConfirmation(true)}
              disabled={loading || !password}
            >
              {loading ? (
                <>
                  <div className="spinner"></div>
                  <span>Désactivation...</span>
                </>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64M12 2v10" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  Désactiver Mon Compte
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Final Confirmation Modal */}
      {showFinalConfirmation && (
        <div className="modal-overlay" onClick={() => setShowFinalConfirmation(false)}>
          <div className="modal-content modal-danger modal-deactivate" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="modal-icon-danger modal-icon-deactivate">
                <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64M12 2v10" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <h3>Confirmer la Désactivation</h3>
              <p>
                Êtes-vous sûr de vouloir désactiver votre compte ?
                <br />
                <strong>Vous serez déconnecté et ne pourrez plus accéder à votre compte.</strong>
              </p>
            </div>
            <div className="modal-actions">
              <button 
                className="btn-modal-cancel" 
                onClick={() => setShowFinalConfirmation(false)}
                disabled={loading}
              >
                Non, Annuler
              </button>
              <button 
                className="btn-modal-danger btn-modal-deactivate" 
                onClick={handleDeactivateAccount}
                disabled={loading}
              >
                {loading ? 'Désactivation...' : 'Oui, Désactiver Mon Compte'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AccountDeletion;
