import React, { useState, useRef } from 'react';
import './ProfilePictureUpload.css';

function ProfilePictureUpload({ currentPicture, onUploadSuccess }) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Format invalide. Utilisez JPG, PNG, GIF ou WebP');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Fichier trop volumineux. Maximum 5MB');
      return;
    }

    setError('');
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
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Supprimer votre photo de profil?')) return;

    setIsUploading(true);
    setError('');

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
      setError(err.message);
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
            onClick={handleDelete}
            disabled={isUploading}
          >
            Supprimer
          </button>
        )}
      </div>

      {error && <div className="upload-error">{error}</div>}
      
      <div className="upload-hint">
        JPG, PNG, GIF ou WebP. Max 5MB
      </div>
    </div>
  );
}

export default ProfilePictureUpload;
