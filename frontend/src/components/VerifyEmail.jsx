import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Toast from './Toast';
import './VerifyEmail.css';

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [verifying, setVerifying] = useState(true);
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState('');
  const [resending, setResending] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  useEffect(() => {
    if (!token) {
      setVerifying(false);
      setError('Token de vérification manquant');
      return;
    }

    verifyEmail();
  }, [token]);

  const verifyEmail = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/email-verification/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
      });

      const data = await response.json();

      if (response.ok) {
        setVerified(true);
        setError('');
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/');
        }, 3000);
      } else {
        setError(data.detail || 'Échec de la vérification');
      }
    } catch (error) {
      console.error('Error verifying email:', error);
      setError('Erreur de connexion au serveur');
    } finally {
      setVerifying(false);
    }
  };

  const handleResendEmail = async () => {
    setResending(true);

    try {
      const response = await fetch('http://localhost:8000/api/email-verification/resend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: '' }) // User needs to provide email
      });

      if (response.ok) {
        setToastMessage('Email de vérification renvoyé');
        setToastType('success');
        setShowToast(true);
      } else {
        setToastMessage('Échec de l\'envoi de l\'email');
        setToastType('error');
        setShowToast(true);
      }
    } catch (error) {
      console.error('Error resending email:', error);
      setToastMessage('Erreur de connexion au serveur');
      setToastType('error');
      setShowToast(true);
    } finally {
      setResending(false);
    }
  };

  if (verifying) {
    return (
      <div className="verify-email-container">
        <div className="verify-email-card">
          <div className="loading-state">
            <div className="spinner-large"></div>
            <h2>Vérification en cours...</h2>
            <p>Veuillez patienter pendant que nous vérifions votre email</p>
          </div>
        </div>
      </div>
    );
  }

  if (verified) {
    return (
      <div className="verify-email-container">
        <div className="verify-email-card">
          <div className="success-state">
            <div className="success-icon-animated">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
              </svg>
            </div>
            <h2>Email Vérifié!</h2>
            <p>Votre adresse email a été vérifiée avec succès.</p>
            <p className="redirect-text">Vous pouvez maintenant vous connecter à votre compte.</p>
            <div className="redirect-info">
              <div className="spinner-small"></div>
              <span>Redirection vers la connexion...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="verify-email-container">
      {showToast && (
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setShowToast(false)}
          duration={5000}
        />
      )}

      <div className="verify-email-card">
        <div className="error-state">
          <div className="error-icon">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
              <line x1="12" y1="8" x2="12" y2="12" strokeWidth="2" strokeLinecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <h2>Vérification Échouée</h2>
          <p className="error-message">{error}</p>
          <div className="error-reasons">
            <p className="reasons-title">Raisons possibles:</p>
            <ul>
              <li>Le lien a expiré (valide 24 heures)</li>
              <li>Le lien a déjà été utilisé</li>
              <li>Le lien est invalide</li>
            </ul>
          </div>
          <div className="action-buttons">
            <button className="btn-primary" onClick={() => navigate('/')}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M19 12H5M12 19L5 12L12 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Retour à la Connexion
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;
