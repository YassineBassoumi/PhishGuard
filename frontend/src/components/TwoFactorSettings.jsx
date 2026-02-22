import { useState, useEffect, useCallback } from 'react';
import './TwoFactorSettings.css';

const TwoFactorSettings = ({ token }) => {
  const [status, setStatus] = useState({ enabled: false, backup_codes_remaining: 0 });
  const [loading, setLoading] = useState(true);
  const [setupData, setSetupData] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/2fa/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (err) {
      console.error('Error fetching 2FA status:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const handleSetup = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/2fa/setup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSetupData(data);
        setSuccess('Scannez le code QR avec votre application d\'authentification');
      } else {
        const error = await response.json();
        setError(error.detail || 'Échec de la configuration 2FA');
      }
    } catch (err) {
      console.error('Error setting up 2FA:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const handleEnable = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Veuillez entrer un code à 6 chiffres');
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/2fa/enable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ token: verificationCode })
      });

      if (response.ok) {
        setSuccess('Authentification à deux facteurs activée avec succès!');
        setSetupData(null);
        setVerificationCode('');
        fetchStatus();
      } else {
        const error = await response.json();
        setError(error.detail || 'Code de vérification invalide');
      }
    } catch (err) {
      console.error('Error enabling 2FA:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable = async () => {
    if (!password) {
      setError('Veuillez entrer votre mot de passe');
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/2fa/disable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ password })
      });

      if (response.ok) {
        setSuccess('Authentification à deux facteurs désactivée');
        setPassword('');
        fetchStatus();
      } else {
        const error = await response.json();
        setError(error.detail || 'Mot de passe invalide');
      }
    } catch (err) {
      console.error('Error disabling 2FA:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateBackupCodes = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/2fa/regenerate-backup-codes', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSetupData({ ...setupData, backup_codes: data.backup_codes });
        setShowBackupCodes(true);
        setSuccess('Codes de secours régénérés avec succès');
        fetchStatus();
      } else {
        const error = await response.json();
        setError(error.detail || 'Échec de la régénération des codes');
      }
    } catch (err) {
      console.error('Error regenerating backup codes:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const downloadBackupCodes = () => {
    if (!setupData?.backup_codes) return;

    const text = `PhishGuard - Codes de Secours 2FA\n\n${setupData.backup_codes.join('\n')}\n\nConservez ces codes en lieu sûr. Chaque code ne peut être utilisé qu'une seule fois.`;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'phishguard-backup-codes.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading && !setupData) {
    return (
      <div className="twofa-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="twofa-container">
      <div className="twofa-header">
        <div className="twofa-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
            <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
          </svg>
        </div>
        <div>
          <h2 className="twofa-title">Authentification à Deux Facteurs</h2>
          <p className="twofa-subtitle">
            Ajoutez une couche de sécurité supplémentaire à votre compte
          </p>
        </div>
        <div className="twofa-status-badge">
          <span className={`status-indicator ${status.enabled ? 'active' : 'inactive'}`}>
            <span className="status-dot"></span>
            {status.enabled ? 'Activé' : 'Désactivé'}
          </span>
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

      {success && (
        <div className="alert alert-success">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
          </svg>
          {success}
        </div>
      )}

      {!status.enabled && !setupData && (
        <div className="twofa-section">
          <h3 className="section-title">Pourquoi activer la 2FA?</h3>
          <div className="benefits-grid">
            <div className="benefit-card">
              <div className="benefit-icon">🛡️</div>
              <h4>Sécurité Renforcée</h4>
              <p>Protection supplémentaire contre les accès non autorisés</p>
            </div>
            <div className="benefit-card">
              <div className="benefit-icon">🔐</div>
              <h4>Double Vérification</h4>
              <p>Nécessite votre mot de passe ET votre téléphone</p>
            </div>
            <div className="benefit-card">
              <div className="benefit-icon">📱</div>
              <h4>Codes Temporaires</h4>
              <p>Codes à usage unique générés par votre application</p>
            </div>
          </div>
          <button className="btn-primary-2fa" onClick={handleSetup} disabled={loading}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 4V20M20 12H4" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Activer l'Authentification à Deux Facteurs
          </button>
        </div>
      )}

      {setupData && !status.enabled && (
        <div className="twofa-setup">
          <div className="setup-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Scannez le Code QR</h3>
              <p>Utilisez une application d'authentification comme Google Authenticator ou Authy</p>
              <div className="qr-code-container">
                <img src={setupData.qr_code} alt="QR Code" className="qr-code" />
              </div>
              <details className="manual-entry">
                <summary>Saisie manuelle</summary>
                <div className="secret-code">
                  <code>{setupData.secret}</code>
                  <button
                    onClick={() => navigator.clipboard.writeText(setupData.secret)}
                    className="btn-copy"
                    title="Copier"
                  >
                    📋
                  </button>
                </div>
              </details>
            </div>
          </div>

          <div className="setup-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Entrez le Code de Vérification</h3>
              <p>Saisissez le code à 6 chiffres de votre application</p>
              <input
                type="text"
                className="verification-input"
                placeholder="000000"
                maxLength="6"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
              />
              <button
                className="btn-verify"
                onClick={handleEnable}
                disabled={loading || verificationCode.length !== 6}
              >
                Vérifier et Activer
              </button>
            </div>
          </div>

          <div className="setup-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Sauvegardez vos Codes de Secours</h3>
              <p>Utilisez ces codes si vous perdez l'accès à votre application</p>
              <div className="backup-codes-grid">
                {setupData.backup_codes.map((code, index) => (
                  <div key={index} className="backup-code">{code}</div>
                ))}
              </div>
              <button className="btn-download" onClick={downloadBackupCodes}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Télécharger les Codes
              </button>
            </div>
          </div>
        </div>
      )}

      {status.enabled && (
        <div className="twofa-enabled">
          <div className="enabled-info">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="success-icon">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
            </svg>
            <h3>2FA Activé</h3>
            <p>Votre compte est protégé par l'authentification à deux facteurs</p>
          </div>

          <div className="backup-codes-status">
            <div className="status-item">
              <span className="status-label">Codes de secours restants:</span>
              <span className="status-value">{status.backup_codes_remaining}</span>
            </div>
            {status.backup_codes_remaining < 3 && (
              <div className="warning-message">
                ⚠️ Il vous reste peu de codes de secours. Pensez à les régénérer.
              </div>
            )}
          </div>

          <div className="twofa-actions">
            <button
              className="btn-regenerate"
              onClick={handleRegenerateBackupCodes}
              disabled={loading}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M1 4V10H7M23 20V14H17M20.49 9C19.9828 7.56678 19.1209 6.28536 17.9845 5.27542C16.8482 4.26548 15.4745 3.55976 13.9917 3.22426C12.5089 2.88875 10.9652 2.93434 9.50481 3.35677C8.04437 3.77921 6.71475 4.56471 5.64 5.64L1 10M23 14L18.36 18.36C17.2853 19.4353 15.9556 20.2208 14.4952 20.6432C13.0348 21.0657 11.4911 21.1112 10.0083 20.7757C8.52547 20.4402 7.1518 19.7345 6.01547 18.7246C4.87913 17.7146 4.01717 16.4332 3.51 15" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Régénérer les Codes de Secours
            </button>

            <button
              className="btn-disable"
              onClick={() => setShowBackupCodes(false)}
              disabled={loading}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M18 8L6 20M6 8L18 20" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Désactiver la 2FA
            </button>
          </div>

          {showBackupCodes && setupData?.backup_codes && (
            <div className="new-backup-codes">
              <h4>Nouveaux Codes de Secours</h4>
              <p>Sauvegardez ces codes immédiatement. Les anciens codes ne fonctionnent plus.</p>
              <div className="backup-codes-grid">
                {setupData.backup_codes.map((code, index) => (
                  <div key={index} className="backup-code">{code}</div>
                ))}
              </div>
              <button className="btn-download" onClick={downloadBackupCodes}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Télécharger les Codes
              </button>
            </div>
          )}

          <div className="disable-section">
            <h4>Désactiver l'Authentification à Deux Facteurs</h4>
            <p>Entrez votre mot de passe pour désactiver la 2FA</p>
            <div className="disable-form">
              <input
                type="password"
                className="password-input"
                placeholder="Votre mot de passe"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                className="btn-disable-confirm"
                onClick={handleDisable}
                disabled={loading || !password}
              >
                Désactiver
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TwoFactorSettings;
