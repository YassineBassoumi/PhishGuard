import React, { useEffect, useState } from 'react';
import './WelcomeRedirect.css';

const WelcomeRedirect = ({ provider, onClose }) => {
  const [countdown, setCountdown] = useState(3);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const providerName = provider.charAt(0).toUpperCase() + provider.slice(1);
  
  const providerIcons = {
    gmail: (
      <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
      </svg>
    ),
    outlook: (
      <svg width="48" height="48" viewBox="0 0 64 64" fill="none">
        <rect width="64" height="64" rx="8" fill="#0078D4"/>
        <circle cx="32" cy="32" r="18" fill="white"/>
        <circle cx="32" cy="32" r="12" fill="#0078D4"/>
        <circle cx="32" cy="32" r="6" fill="white"/>
      </svg>
    )
  };

  return (
    <div className="welcome-redirect-overlay">
      <div className="welcome-redirect-modal">
        <div className="welcome-icon-container">
          <div className="welcome-icon-bg">
            {providerIcons[provider] || providerIcons.gmail}
          </div>
          <div className="welcome-checkmark">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 6L9 17L4 12" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </div>

        <h2 className="welcome-title">Bienvenue sur PhishGuard! 🎉</h2>
        
        <p className="welcome-message">
          Nous avons détecté que vous utilisez <strong>{providerName}</strong>.
        </p>

        <div className="welcome-info-box">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            <path d="M12 16V12M12 8H12.01" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <p>
            Vous allez être redirigé vers {providerName} pour connecter votre compte en toute sécurité.
          </p>
        </div>

        <div className="welcome-countdown">
          <div className="countdown-circle">
            <svg className="countdown-svg" viewBox="0 0 100 100">
              <circle
                className="countdown-bg"
                cx="50"
                cy="50"
                r="45"
              />
              <circle
                className="countdown-progress"
                cx="50"
                cy="50"
                r="45"
                style={{
                  strokeDashoffset: `${283 - (283 * (3 - countdown)) / 3}`
                }}
              />
            </svg>
            <span className="countdown-number">{countdown}</span>
          </div>
          <p className="countdown-text">Redirection dans {countdown} seconde{countdown !== 1 ? 's' : ''}...</p>
        </div>

        <div className="welcome-features">
          <div className="feature-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
            </svg>
            <span>Analyse automatique des emails</span>
          </div>
          <div className="feature-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 15V3M12 15L8 11M12 15L16 11M2 17L2.621 19.485C2.72915 19.9177 2.97882 20.3018 3.33033 20.5763C3.68184 20.8508 4.11501 20.9999 4.561 21H19.439C19.885 20.9999 20.3182 20.8508 20.6697 20.5763C21.0212 20.3018 21.2708 19.9177 21.379 19.485L22 17" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>Protection en temps réel</span>
          </div>
          <div className="feature-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
              <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
            </svg>
            <span>Vos données restent privées</span>
          </div>
        </div>

        {onClose && (
          <button className="welcome-skip-btn" onClick={onClose}>
            Passer cette étape
          </button>
        )}
      </div>
    </div>
  );
};

export default WelcomeRedirect;
