import React from 'react';

function EmailInputField({ index, email, onChange, onPaste, onRemove, disabled, canRemove }) {
  return (
    <div className="email-field-group">
      <div className="email-field-header">
        <span className="email-number">Email {index + 1}</span>
        {canRemove && (
          <button
            className="remove-email-btn"
            onClick={() => onRemove(index)}
            disabled={disabled}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M18 6L6 18M6 6L18 18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}
      </div>
      <textarea
        className="email-textarea"
        placeholder="Collez le contenu de l'email ici..."
        value={email}
        onChange={(e) => onChange(index, e.target.value)}
        onPaste={onPaste}
        data-index={index}
        disabled={disabled}
        rows={4}
      />
    </div>
  );
}

export default EmailInputField;
