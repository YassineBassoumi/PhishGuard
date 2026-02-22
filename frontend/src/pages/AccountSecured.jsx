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
        <h1 className="secured-title">Account Secured Successfully!</h1>
        <p className="secured-subtitle">
          Your PhishGuard account has been protected
        </p>

        {/* Actions Taken */}
        <div className="actions-box">
          <h3 className="actions-title">
            <Lock size={18} />
            Security Actions Completed
          </h3>
          <ul className="actions-list">
            <li>
              <CheckCircle size={16} className="check-small" />
              All active sessions have been terminated
            </li>
            <li>
              <CheckCircle size={16} className="check-small" />
              Password reset token generated
            </li>
            <li>
              <CheckCircle size={16} className="check-small" />
              Security alert sent to your email
            </li>
          </ul>
        </div>

        {/* Next Steps */}
        <div className="next-steps-box">
          <h3 className="next-steps-title">
            <Mail size={18} />
            Next Steps
          </h3>
          <p className="next-steps-text">
            We've sent a password reset link to your email address. 
            Please check your inbox and follow the instructions to set a new password.
          </p>
          <div className="email-reminder">
            <AlertTriangle size={16} />
            <span>Check your spam folder if you don't see the email</span>
          </div>
        </div>

        {/* Security Tips */}
        <div className="tips-box">
          <h4 className="tips-title">🔒 Security Recommendations</h4>
          <ul className="tips-list">
            <li>Choose a strong, unique password (12+ characters)</li>
            <li>Enable Two-Factor Authentication (2FA)</li>
            <li>Never share your password with anyone</li>
          </ul>
        </div>

        {/* Redirect Notice */}
        <div className="redirect-notice">
          <p>
            Redirecting to login page in <strong>{countdown}</strong> seconds...
          </p>
          <button 
            onClick={() => navigate('/login')} 
            className="login-button"
          >
            Go to Login Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountSecured;
