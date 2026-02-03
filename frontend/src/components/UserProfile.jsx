import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './UserProfile.css';

const UserProfile = () => {
  const { user, logout, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [email, setEmail] = useState(user?.email || '');
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (password && password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    if (password && password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    const updates = {};
    if (email !== user.email) updates.email = email;
    if (fullName !== user.full_name) updates.full_name = fullName;
    if (password) updates.password = password;

    if (Object.keys(updates).length === 0) {
      setError('Aucune modification détectée');
      return;
    }

    setLoading(true);
    const result = await updateUser(updates);
    setLoading(false);

    if (result.success) {
      setSuccess('Profil mis à jour avec succès');
      setIsEditing(false);
      setPassword('');
      setConfirmPassword('');
    } else {
      setError(result.error || 'Échec de la mise à jour');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEmail(user?.email || '');
    setFullName(user?.full_name || '');
    setPassword('');
    setConfirmPassword('');
    setError('');
    setSuccess('');
  };

  if (!user) {
    return null;
  }

  return (
    <div className="profile-container fade-in-up">
      <div className="glass-card profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2 className="profile-title">{user.username}</h2>
          <p className="profile-subtitle">
            Membre depuis {new Date(user.created_at).toLocaleDateString('fr-FR')}
          </p>
        </div>

        {error && (
          <div className="alert alert-error">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {success}
          </div>
        )}

        {!isEditing ? (
          <div className="profile-info">
            <div className="info-item">
              <label className="info-label">Email</label>
              <p className="info-value">{user.email}</p>
            </div>

            <div className="info-item">
              <label className="info-label">Nom complet</label>
              <p className="info-value">{user.full_name || 'Non renseigné'}</p>
            </div>

            <div className="info-item">
              <label className="info-label">Statut</label>
              <p className="info-value">
                <span className={`status-badge ${user.is_active ? 'status-active' : 'status-inactive'}`}>
                  {user.is_active ? 'Actif' : 'Inactif'}
                </span>
              </p>
            </div>

            <div className="profile-actions">
              <button
                className="btn btn-primary"
                onClick={() => setIsEditing(true)}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 2.5C18.8978 2.1022 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.1022 21.5 2.5C21.8978 2.8978 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.1022 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Modifier le profil
              </button>

              <button
                className="btn btn-danger"
                onClick={logout}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9M16 17L21 12M21 12L16 7M21 12H9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Se déconnecter
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email
              </label>
              <input
                id="email"
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
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
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Nouveau mot de passe
              </label>
              <input
                id="password"
                type="password"
                className="input"
                placeholder="Laisser vide pour ne pas changer"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                minLength={6}
              />
              <p className="input-hint">Minimum 6 caractères</p>
            </div>

            {password && (
              <div className="form-group">
                <label htmlFor="confirmPassword" className="form-label">
                  Confirmer le mot de passe
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  className="input"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={loading}
                />
              </div>
            )}

            <div className="form-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleCancel}
                disabled={loading}
              >
                Annuler
              </button>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '3px' }}></div>
                    <span>Enregistrement...</span>
                  </>
                ) : (
                  'Enregistrer'
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default UserProfile;
