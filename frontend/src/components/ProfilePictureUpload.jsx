import React, { useState, useRef } from 'react';
import Toast from './Toast';
import './ProfilePictureUpload.css';

function ProfilePictureUpload({ currentPicture, onUploadSuccess }) {
  const [isUploading, setIsUploading] = useState(false);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [toast, setToast] = useState(null); // { message, type }
  const fileInputRef = useRef(null);

  const showToast = (message, type = 'success') => setToast({ message, type });
  const closeToast = () => setToast(null);

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      showToast('Format invalide. Utilisez JPG, PNG, GIF ou WebP', 'error');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      showToast('Fichier trop volumineux. Maximum 5MB', 'error');
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/api/profile/picture', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Échec du téléchargement');
      }

      const data = await response.json();
      
      // Fetch updated user data
      const authToken = localStorage.getItem('auth_token');
      const userResponse = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        localStorage.setItem('auth_user', JSON.stringify(userData));
        onUploadSuccess(userData.profile_picture);
      } else {
        onUploadSuccess(data.filename);
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteClick = () => {
    setShowConfirmDelete(true);
  };

  const handleConfirmDelete = async () => {
    setShowConfirmDelete(false);
    setIsUploading(true);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/api/profile/picture', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Échec de la suppression');
      }

      // Fetch updated user data
      const authToken = localStorage.getItem('auth_token');
      const userResponse = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        localStorage.setItem('auth_user', JSON.stringify(userData));
      }
      
      onUploadSuccess(null);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="profile-picture-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      
      <div className="upload-actions">
        <button
          className="upload-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
        >
          {isUploading ? 'Téléchargement...' : currentPicture ? 'Changer la photo' : 'Ajouter une photo'}
        </button>
        
        {currentPicture && (
          <button
            className="delete-btn"
            onClick={handleDeleteClick}
            disabled={isUploading}
          >
            Supprimer
          </button>
        )}
      </div>

      <div className="upload-hint">
        JPG, PNG, GIF ou WebP. Max 5MB
      </div>

      {/* Toast notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={closeToast}
          duration={3500}
        />
      )}

      {/* Confirm delete modal */}
      {showConfirmDelete && (
        <div
          className="ppu-modal-overlay"
          onClick={() => setShowConfirmDelete(false)}
        >
          <div
            className="ppu-modal-content"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="ppu-modal-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 6H5H21M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 className="ppu-modal-title">Supprimer la photo de profil ?</h3>
            <p className="ppu-modal-message">
              Cette action est irréversible. Votre avatar sera remplacé par l’image par défaut.
            </p>
            <div className="ppu-modal-actions">
              <button
                type="button"
                className="ppu-btn-cancel"
                onClick={() => setShowConfirmDelete(false)}
                disabled={isUploading}
              >
                Annuler
              </button>
              <button
                type="button"
                className="ppu-btn-confirm"
                onClick={handleConfirmDelete}
                disabled={isUploading}
              >
                Supprimer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProfilePictureUpload;
