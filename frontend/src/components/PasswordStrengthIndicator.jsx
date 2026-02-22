import React from 'react';
import './PasswordStrengthIndicator.css';

const PasswordStrengthIndicator = ({ password }) => {
  const calculateStrength = (pwd) => {
    if (!pwd) return { score: 0, label: '', color: '' };

    let score = 0;
    const checks = {
      length: pwd.length >= 8,
      uppercase: /[A-Z]/.test(pwd),
      lowercase: /[a-z]/.test(pwd),
      number: /[0-9]/.test(pwd),
      special: /[^A-Za-z0-9]/.test(pwd),
      longLength: pwd.length >= 12
    };

    // Calculate score
    if (checks.length) score += 20;
    if (checks.uppercase) score += 15;
    if (checks.lowercase) score += 15;
    if (checks.number) score += 15;
    if (checks.special) score += 20;
    if (checks.longLength) score += 15;

    // Determine strength level
    let label = '';
    let color = '';
    
    if (score < 40) {
      label = 'Très faible';
      color = '#ef4444';
    } else if (score < 60) {
      label = 'Faible';
      color = '#f97316';
    } else if (score < 80) {
      label = 'Moyen';
      color = '#f59e0b';
    } else if (score < 95) {
      label = 'Fort';
      color = '#84cc16';
    } else {
      label = 'Très fort';
      color = '#22c55e';
    }

    return { score, label, color, checks };
  };

  const strength = calculateStrength(password);

  if (!password) return null;

  return (
    <div className="password-strength-container">
      <div className="strength-bar-container">
        <div 
          className="strength-bar" 
          style={{ 
            width: `${strength.score}%`,
            backgroundColor: strength.color
          }}
        />
      </div>
      
      <div className="strength-info">
        <span className="strength-label" style={{ color: strength.color }}>
          {strength.label}
        </span>
        <span className="strength-score">{strength.score}%</span>
      </div>

      <div className="password-requirements">
        <div className={`requirement ${strength.checks?.length ? 'met' : ''}`}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            {strength.checks?.length ? (
              <path d="M20 6L9 17L4 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            ) : (
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            )}
          </svg>
          <span>Au moins 8 caractères</span>
        </div>

        <div className={`requirement ${strength.checks?.uppercase ? 'met' : ''}`}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            {strength.checks?.uppercase ? (
              <path d="M20 6L9 17L4 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            ) : (
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            )}
          </svg>
          <span>Une lettre majuscule</span>
        </div>

        <div className={`requirement ${strength.checks?.lowercase ? 'met' : ''}`}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            {strength.checks?.lowercase ? (
              <path d="M20 6L9 17L4 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            ) : (
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            )}
          </svg>
          <span>Une lettre minuscule</span>
        </div>

        <div className={`requirement ${strength.checks?.number ? 'met' : ''}`}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            {strength.checks?.number ? (
              <path d="M20 6L9 17L4 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            ) : (
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            )}
          </svg>
          <span>Un chiffre</span>
        </div>

        <div className={`requirement ${strength.checks?.special ? 'met' : ''}`}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            {strength.checks?.special ? (
              <path d="M20 6L9 17L4 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            ) : (
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            )}
          </svg>
          <span>Un caractère spécial (!@#$%...)</span>
        </div>
      </div>
    </div>
  );
};

export default PasswordStrengthIndicator;
