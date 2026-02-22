import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import PasswordStrengthIndicator from './PasswordStrengthIndicator';
import './Login.css';

const Register = ({ onSwitchToLogin }) => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!email.trim() || !username.trim() || !password.trim()) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    setLoading(true);
    const result = await register(email, username, password, fullName);
    setLoading(false);

    if (result.success) {
      setRegistrationSuccess(true);
      setRegisteredEmail(email);
    } else {
      setError(result.error || 'Échec de l\'inscription');
    }
  };

  if (registrationSuccess) {
    return (
      <div className="auth-container fade-in-up">
        <div className="glass-card auth-card">
          <div className="success-registration">
            <div className="success-icon-large">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h2 className="success-title">Vérifiez votre Email!</h2>
            <p className="success-message">
              Un email de vérification a été envoyé à <strong>{registeredEmail}</strong>
            </p>
            <div className="info-box-register">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                <line x1="12" y1="16" x2="12" y2="12" strokeWidth="2" strokeLinecap="round"/>
                <line x1="12" y1="8" x2="12.01" y2="8" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <div>
                <p className="info-title-register">Prochaines étapes:</p>
                <ul className="info-list-register">
                  <li>Vérifiez votre boîte de réception</li>
                  <li>Cliquez sur le lien de vérification</li>
                  <li>Connectez-vous à votre compte</li>
                </ul>
              </div>
            </div>
            <button
              type="button"
              className="btn btn-primary btn-full"
              onClick={onSwitchToLogin}
            >
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

  return (
    <div className="auth-container fade-in-up">
      <div className="glass-card auth-card">
        <div className="auth-header">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="auth-icon">
            <path d="M16 21V19C16 17.9391 15.5786 16.9217 14.8284 16.1716C14.0783 15.4214 13.0609 15 12 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88M12.5 7C12.5 9.20914 10.7091 11 8.5 11C6.29086 11 4.5 9.20914 4.5 7C4.5 4.79086 6.29086 3 8.5 3C10.7091 3 12.5 4.79086 12.5 7Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h2 className="auth-title">Créer un compte</h2>
          <p className="auth-subtitle">Rejoignez PhishGuard pour protéger vos emails</p>
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
            <label htmlFor="email" className="form-label">
              Email <span className="required">*</span>
            </label>
            <input
              id="email"
              type="email"
              className="input"
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Nom d'utilisateur <span className="required">*</span>
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
              minLength={3}
              maxLength={50}
            />
          </div>

          <div className="form-group">
            <label htmlFor="fullName" className="form-label">
              Nom complet
            </label>
            <input
              id="fullName"
              type="text"
              className="input"
              placeholder="John Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={loading}
              autoComplete="name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Mot de passe <span className="required">*</span>
            </label>
            <input
              id="password"
              type="password"
              className="input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
              minLength={8}
            />
            <PasswordStrengthIndicator password={password} />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              Confirmer le mot de passe <span className="required">*</span>
            </label>
            <input
              id="confirmPassword"
              type="password"
              className={`input ${
                confirmPassword && password === confirmPassword ? 'password-match' : 
                confirmPassword && password !== confirmPassword ? 'password-mismatch' : ''
              }`}
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
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

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '3px' }}></div>
                <span>Création...</span>
              </>
            ) : (
              'Créer mon compte'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Déjà un compte ?{' '}
            <button
              type="button"
              className="link-button"
              onClick={onSwitchToLogin}
              disabled={loading}
            >
              Se connecter
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
