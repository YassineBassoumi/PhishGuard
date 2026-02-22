import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Toast from './Toast';
import './AccountDeletion.css';

const AccountDeletion = () => {
  const { token, logout } = useAuth();
  const [showDeleteSection, setShowDeleteSection] = useState(false);
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');
  const [showFinalConfirmation, setShowFinalConfirmation] = useState(false);

  const handleDeleteAccount = async () => {
    setError('');
    setShowFinalConfirmation(false);

    // Validation
    if (!password) {
      setError('Veuillez entrer votre mot de passe');
      return;
    }

    if (confirmation !== 'DELETE MY ACCOUNT') {
      setError('Veuillez taper exactement "DELETE MY ACCOUNT" pour confirmer');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          password: password,
          confirmation: confirmation
        })
      });

      if (response.ok || response.status === 204) {
        setToastMessage('Compte supprimé avec succès');
        setToastType('success');
        setShowToast(true);
        
        // Logout after 2 seconds
        setTimeout(() => {
          logout();
        }, 2000);
      } else {
        const data = await response.json();
        setError(data.detail || 'Échec de la suppression du compte');
      }
    } catch (err) {
      console.error('Error deleting account:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setPassword('');
    setConfirmation('');
    setError('');
    setShowDeleteSection(false);
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
        <div className="deletion-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
          </svg>
        </div>
        <div>
          <h2 className="deletion-title">Zone Dangereuse</h2>
          <p className="deletion-subtitle">
            Actions irréversibles concernant votre compte
          </p>
        </div>
      </div>

      {!showDeleteSection ? (
        <div className="deletion-warning-box">
          <div className="warning-content">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
            </svg>
            <div>
              <h3>Supprimer Définitivement le Compte</h3>
              <p>
                Une fois supprimé, votre compte ne peut pas être récupéré. Toutes vos données seront définitivement effacées.
              </p>
              <ul className="deletion-consequences">
                <li>Toutes vos analyses seront supprimées</li>
                <li>Vos connexions email seront révoquées</li>
                <li>Toutes vos sessions seront fermées</li>
                <li>Vos paramètres 2FA seront perdus</li>
                <li>Cette action est irréversible</li>
              </ul>
            </div>
          </div>
          <button
            className="btn-show-delete"
            onClick={() => setShowDeleteSection(true)}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 6H5H21M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Je Veux Supprimer Mon Compte
          </button>
        </div>
      ) : (
        <div className="deletion-form-section">
          <div className="deletion-steps">
            <div className="step-indicator">
              <div className="step-number">1</div>
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
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>Confirmation de Suppression</h4>
                <p>Tapez exactement <strong>"DELETE MY ACCOUNT"</strong> pour confirmer</p>
                <input
                  type="text"
                  className={`deletion-input ${
                    confirmation && confirmation === 'DELETE MY ACCOUNT' ? 'input-valid' : 
                    confirmation ? 'input-invalid' : ''
                  }`}
                  placeholder="DELETE MY ACCOUNT"
                  value={confirmation}
                  onChange={(e) => setConfirmation(e.target.value)}
                  disabled={loading}
                />
                {confirmation && confirmation !== 'DELETE MY ACCOUNT' && (
                  <p className="input-hint error">
                    ❌ Le texte ne correspond pas exactement
                  </p>
                )}
                {confirmation === 'DELETE MY ACCOUNT' && (
                  <p className="input-hint success">
                    ✓ Confirmation correcte
                  </p>
                )}
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
              className="btn-confirm-delete"
              onClick={() => setShowFinalConfirmation(true)}
              disabled={loading || !password || confirmation !== 'DELETE MY ACCOUNT'}
            >
              {loading ? (
                <>
                  <div className="spinner"></div>
                  <span>Suppression...</span>
                </>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M3 6H5H21M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  Supprimer Définitivement Mon Compte
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Final Confirmation Modal */}
      {showFinalConfirmation && (
        <div className="modal-overlay" onClick={() => setShowFinalConfirmation(false)}>
          <div className="modal-content modal-danger" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="modal-icon-danger">
                <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
              </svg>
              <h3>Dernière Confirmation</h3>
              <p>
                Êtes-vous absolument certain de vouloir supprimer votre compte?
                <br />
                <strong>Cette action est définitive et irréversible.</strong>
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
                className="btn-modal-danger" 
                onClick={handleDeleteAccount}
                disabled={loading}
              >
                {loading ? 'Suppression...' : 'Oui, Supprimer Définitivement'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AccountDeletion;
