import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import TwoFactorSettings from './TwoFactorSettings';
import SessionManagement from './SessionManagement';
import AccountDeletion from './AccountDeletion';
import PasswordStrengthIndicator from './PasswordStrengthIndicator';
import ProfilePictureUpload from './ProfilePictureUpload';
import Toast from './Toast';
import './UserProfile.css';

const UserProfile = () => {
  const { user, logout, updateUser, token } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [email, setEmail] = useState(user?.email || '');
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [oldPassword, setOldPassword] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (password && password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    if (password && password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (password && !oldPassword) {
      setError('Veuillez entrer votre mot de passe actuel');
      return;
    }

    const updates = {};
    if (email !== user.email) updates.email = email;
    if (fullName !== user.full_name) updates.full_name = fullName;
    if (password) {
      updates.old_password = oldPassword;
      updates.password = password;
    }

    if (Object.keys(updates).length === 0) {
      setError('Aucune modification détectée');
      return;
    }

    setLoading(true);
    const result = await updateUser(updates);
    setLoading(false);

    if (result.success) {
      setToastMessage('Profil mis à jour avec succès');
      setToastType('success');
      setShowToast(true);
      setIsEditing(false);
      setOldPassword('');
      setPassword('');
      setConfirmPassword('');
      setError('');
    } else {
      setError(result.error || 'Échec de la mise à jour');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEmail(user?.email || '');
    setFullName(user?.full_name || '');
    setOldPassword('');
    setPassword('');
    setConfirmPassword('');
    setError('');
  };

  if (!user) {
    return null;
  }

  const tabs = [
    {
      id: 'profile',
      label: 'Profil',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      )
    },
    {
      id: 'security',
      label: 'Sécurité',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
          <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
        </svg>
      )
    },
    {
      id: 'sessions',
      label: 'Sessions',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2" strokeWidth="2"/>
          <line x1="8" y1="21" x2="16" y2="21" strokeWidth="2" strokeLinecap="round"/>
          <line x1="12" y1="17" x2="12" y2="21" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      )
    },
    {
      id: 'danger',
      label: 'Zone Dangereuse',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
        </svg>
      )
    }
  ];

  return (
    <div className="profile-container-new fade-in-up">
      {/* Toast Notification */}
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

      {/* Page Header */}
      <div className="profile-page-header-new">
        <div className="header-content">
          <div className="header-text">
            <h1 className="page-title-new">Paramètres du Compte</h1>
            <p className="page-subtitle-new">Gérez vos informations et préférences</p>
          </div>
          <button className="btn-logout-header-new" onClick={logout} title="Se déconnecter">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9M16 17L21 12M21 12L16 7M21 12H9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>Se déconnecter</span>
          </button>
        </div>

        {/* User Info Card */}
        <div className="user-info-card">
          <div className="user-avatar">
            {user?.profile_picture ? (
              <img 
                src={`http://localhost:8000/api/profile/picture/${user.profile_picture}`} 
                alt="Profile"
                style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
              />
            ) : (
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </div>
          <div className="user-info-text">
            <h2 className="user-name">{user.username}</h2>
            <p className="user-email">{user.email}</p>
          </div>
          <div className="user-badge">
            <span className={`status-badge ${user.is_active ? 'status-active' : 'status-inactive'}`}>
              <span className="status-dot"></span>
              {user.is_active ? 'Actif' : 'Inactif'}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="tabs-container">
        <div className="tabs-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''} ${tab.id === 'danger' ? 'danger-tab' : ''}`}
              onClick={() => {
                setActiveTab(tab.id);
                setIsEditing(false);
                setError('');
              }}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="tab-panel fade-in">
              {!isEditing ? (
                <div className="profile-view">
                  <div className="section-header">
                    <h3>Informations Personnelles</h3>
                    <button className="btn-edit" onClick={() => setIsEditing(true)}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 2.5C18.8978 2.1022 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.1022 21.5 2.5C21.8978 2.8978 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.1022 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Modifier
                    </button>
                  </div>

                  <div className="info-grid-new">
                    <div className="info-item-new">
                      <label className="info-label-new">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round"/>
                        </svg>
                        Adresse Email
                      </label>
                      <p className="info-value-new">{user.email}</p>
                    </div>

                    <div className="info-item-new">
                      <label className="info-label-new">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        Nom Complet
                      </label>
                      <p className="info-value-new">{user.full_name || 'Non renseigné'}</p>
                    </div>

                    <div className="info-item-new">
                      <label className="info-label-new">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" strokeWidth="2"/>
                          <line x1="16" y1="2" x2="16" y2="6" strokeWidth="2" strokeLinecap="round"/>
                          <line x1="8" y1="2" x2="8" y2="6" strokeWidth="2" strokeLinecap="round"/>
                          <line x1="3" y1="10" x2="21" y2="10" strokeWidth="2" strokeLinecap="round"/>
                        </svg>
                        Membre Depuis
                      </label>
                      <p className="info-value-new">{new Date(user.created_at).toLocaleDateString('fr-FR')}</p>
                    </div>
                  </div>

                  <div className="section-header" style={{ marginTop: '2rem' }}>
                    <h3>Photo de Profil</h3>
                  </div>
                  <ProfilePictureUpload 
                    currentPicture={user.profile_picture}
                    onUploadSuccess={async () => {
                      // Refresh user data from localStorage (already updated by ProfilePictureUpload)
                      const updatedUser = JSON.parse(localStorage.getItem('auth_user'));
                      if (updatedUser) {
                        // Update the user state through AuthContext
                        await updateUser({});
                      }
                      setToastMessage('Photo de profil mise à jour');
                      setToastType('success');
                      setShowToast(true);
                    }}
                  />
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="profile-edit-form">
                  <div className="section-header">
                    <h3>Modifier le Profil</h3>
                  </div>

                  {error && (
                    <div className="alert alert-error">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2"/>
                      </svg>
                      {error}
                    </div>
                  )}

                  <div className="form-group-new">
                    <label htmlFor="email" className="form-label-new">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round"/>
                      </svg>
                      Adresse Email
                    </label>
                    <input
                      id="email"
                      type="email"
                      className="input-new"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={loading}
                      placeholder="votre@email.com"
                    />
                  </div>

                  <div className="form-group-new">
                    <label htmlFor="fullName" className="form-label-new">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Nom Complet
                    </label>
                    <input
                      id="fullName"
                      type="text"
                      className="input-new"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      disabled={loading}
                      placeholder="Votre nom complet"
                    />
                  </div>

                  <div className="divider-new"></div>

                  <h4 className="subsection-title">Changer le Mot de Passe</h4>
                  <p className="subsection-subtitle">Laissez vide si vous ne souhaitez pas modifier</p>

                  <div className="form-group-new">
                    <label htmlFor="oldPassword" className="form-label-new">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
                        <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
                      </svg>
                      Mot de Passe Actuel
                    </label>
                    <input
                      id="oldPassword"
                      type="password"
                      className="input-new"
                      placeholder="Votre mot de passe actuel"
                      value={oldPassword}
                      onChange={(e) => setOldPassword(e.target.value)}
                      disabled={loading}
                    />
                  </div>

                  <div className="form-group-new">
                    <label htmlFor="password" className="form-label-new">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
                        <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
                      </svg>
                      Nouveau Mot de Passe
                    </label>
                    <input
                      id="password"
                      type="password"
                      className="input-new"
                      placeholder="Minimum 8 caractères"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={loading}
                      minLength={8}
                    />
                    <PasswordStrengthIndicator password={password} />
                  </div>

                  {password && (
                    <div className="form-group-new">
                      <label htmlFor="confirmPassword" className="form-label-new">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" strokeWidth="2"/>
                          <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" strokeWidth="2"/>
                        </svg>
                        Confirmer le Mot de Passe
                      </label>
                      <input
                        id="confirmPassword"
                        type="password"
                        className={`input-new ${
                          confirmPassword && password === confirmPassword ? 'password-match' : 
                          confirmPassword && password !== confirmPassword ? 'password-mismatch' : ''
                        }`}
                        placeholder="Retapez votre mot de passe"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        disabled={loading}
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
                  )}

                  <div className="form-actions-new">
                    <button type="button" className="btn-cancel-new" onClick={handleCancel} disabled={loading}>
                      Annuler
                    </button>
                    <button type="submit" className="btn-save-new" disabled={loading}>
                      {loading ? (
                        <>
                          <div className="spinner-new"></div>
                          <span>Enregistrement...</span>
                        </>
                      ) : (
                        <>
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H16L21 8V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            <path d="M17 21V13H7V21M7 3V8H15" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                          Enregistrer
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="tab-panel fade-in">
              <TwoFactorSettings token={token} />
            </div>
          )}

          {/* Sessions Tab */}
          {activeTab === 'sessions' && (
            <div className="tab-panel fade-in">
              <SessionManagement token={token} />
            </div>
          )}

          {/* Danger Zone Tab */}
          {activeTab === 'danger' && (
            <div className="tab-panel fade-in">
              <AccountDeletion />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
