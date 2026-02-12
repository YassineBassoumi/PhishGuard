import { useEffect } from 'react';
import Login from './Login';
import Register from './Register';
import './AuthModal.css';

function AuthModal({ isOpen, onClose, authView, onSwitchAuth }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="auth-modal-close" onClick={onClose}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
        
        {authView === 'login' ? (
          <Login onSwitchToRegister={() => onSwitchAuth('register')} />
        ) : (
          <Register onSwitchToLogin={() => onSwitchAuth('login')} />
        )}
      </div>
    </div>
  );
}

export default AuthModal;
