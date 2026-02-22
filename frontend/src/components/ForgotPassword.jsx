import { useState } from 'react';
import Toast from './Toast';
import './ForgotPassword.css';

const ForgotPassword = ({ onBack }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email) {
      setToastMessage('Veuillez entrer votre adresse email');
      setToastType('error');
      setShowToast(true);
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/password-reset/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      });

      if (response.ok) {
        setEmailSent(true);
      } else {
        // Even on error, show success message (security best practice)
        setEmailSent(true);
      }
    } catch (error) {
      console.error('Error requesting password reset:', error);
      setToastMessage('Erreur de connexion au serveur');
      setToastType('error');
      setShowToast(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-modal">
      {showToast && (
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setShowToast(false)}
          duration={5000}
        />
      )}

      {!emailSent ? (
        <>
          <div className="forgot-password-header">
            <div className="forgot-password-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h2>Mot de Passe Oublié?</h2>
            <p>Pas de problème, nous vous enverrons un lien de réinitialisation</p>
          </div>

          <form onSubmit={handleSubmit} className="forgot-password-form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Adresse Email
              </label>
              <input
                id="email"
                type="email"
                className="form-input"
                placeholder="votre@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
                autoFocus
              />
            </div>

            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner"></div>
                  <span>Envoi en cours...</span>
                </>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Envoyer le Lien
                </>
              )}
            </button>

            <button type="button" className="btn-back" onClick={onBack} disabled={loading}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M19 12H5M12 19L5 12L12 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Retour à la Connexion
            </button>
          </form>
        </>
      ) : (
        <div className="success-state">
          <div className="success-icon-large">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
            </svg>
          </div>
          <h3>Email Envoyé!</h3>
          <p className="success-description">
            Si un compte existe avec l'adresse <strong>{email}</strong>, 
            vous recevrez un email avec les instructions pour réinitialiser votre mot de passe.
          </p>
          <div className="info-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
              <line x1="12" y1="16" x2="12" y2="12" strokeWidth="2" strokeLinecap="round"/>
              <line x1="12" y1="8" x2="12.01" y2="8" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <div className="info-content">
              <p className="info-title">Vérifiez votre boîte de réception</p>
              <ul className="info-list">
                <li>Le lien est valide pendant 1 heure</li>
                <li>Vérifiez aussi vos spams</li>
                <li>Le lien ne peut être utilisé qu'une seule fois</li>
              </ul>
            </div>
          </div>
          <button className="btn-primary" onClick={onBack}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 12H5M12 19L5 12L12 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Retour à la Connexion
          </button>
        </div>
      )}
    </div>
  );
};

export default ForgotPassword;
