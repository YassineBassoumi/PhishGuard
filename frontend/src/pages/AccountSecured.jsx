import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Shield, Mail, Lock, AlertTriangle } from 'lucide-react';
import './AccountSecured.css';

const AccountSecured = () => {
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(10);

  useEffect(() => {
    // Countdown timer
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          navigate('/login');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [navigate]);

  return (
    <div className="account-secured-container">
      <div className="account-secured-card">
        {/* Success Icon */}
        <div className="success-icon-wrapper">
          <div className="success-icon-circle">
            <Shield className="shield-icon" size={40} />
          </div>
          <CheckCircle className="check-icon" size={24} />
        </div>

        {/* Main Message */}
        <h1 className="secured-title">Compte sécurisé avec succès !</h1>
        <p className="secured-subtitle">
          Votre compte PhishGuard est maintenant protégé
        </p>

        {/* Actions Taken */}
        <div className="actions-box">
          <h3 className="actions-title">
            <Lock size={18} />
            Actions de sécurité effectuées
          </h3>
          <ul className="actions-list">
            <li>
              <CheckCircle size={16} className="check-small" />
              Toutes les sessions actives ont été fermées
            </li>
            <li>
              <CheckCircle size={16} className="check-small" />
              Un jeton de réinitialisation de mot de passe a été généré
            </li>
            <li>
              <CheckCircle size={16} className="check-small" />
              Une alerte de sécurité a été envoyée à votre adresse email
            </li>
          </ul>
        </div>

        {/* Next Steps */}
        <div className="next-steps-box">
          <h3 className="next-steps-title">
            <Mail size={18} />
            Prochaines étapes
          </h3>
          <p className="next-steps-text">
            Nous vous avons envoyé un lien de réinitialisation de mot de passe par email.
            Consultez votre boîte de réception et suivez les instructions pour définir un nouveau mot de passe.
          </p>
          <div className="email-reminder">
            <AlertTriangle size={16} />
            <span>Pensez à vérifier votre dossier spam si vous ne voyez pas l’email</span>
          </div>
        </div>

        {/* Security Tips */}
        <div className="tips-box">
          <h4 className="tips-title">🔒 Recommandations de sécurité</h4>
          <ul className="tips-list">
            <li>Choisissez un mot de passe fort et unique (12 caractères ou plus)</li>
            <li>Activez l’authentification à deux facteurs (2FA)</li>
            <li>Ne partagez jamais votre mot de passe avec qui que ce soit</li>
          </ul>
        </div>

        {/* Redirect Notice */}
        <div className="redirect-notice">
          <p>
            Redirection vers la page de connexion dans <strong>{countdown}</strong> seconde{countdown > 1 ? 's' : ''}...
          </p>
          <button 
            onClick={() => navigate('/login')} 
            className="login-button"
          >
            Aller à la connexion maintenant
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountSecured;
