import React from 'react';
import EmailInputField from './EmailInputField';
import ProgressBar from './ProgressBar';

function BulkAnalysisForm({ 
  emails, 
  onEmailChange, 
  onPaste, 
  onAddEmail, 
  onRemoveEmail, 
  onAnalyze, 
  onClear, 
  isAnalyzing, 
  progress,
  initialEmails 
}) {
  const validEmailCount = emails.filter(e => e.trim()).length;

  return (
    <div className="glass-card">
      <h2 className="bulk-analysis-title">Analyse en Masse</h2>
      <p className="form-description">
        Analysez jusqu'à 50 emails simultanément. Collez plusieurs emails séparés par des lignes vides.
        {initialEmails && initialEmails.length > 0 && (
          <span className="gmail-import-notice">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 11L12 14L22 4M21 12V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H16" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {initialEmails.length} email{initialEmails.length > 1 ? 's' : ''} importé{initialEmails.length > 1 ? 's' : ''} depuis Gmail
          </span>
        )}
      </p>

      <div className="email-fields">
        {emails.map((email, index) => (
          <EmailInputField
            key={index}
            index={index}
            email={email}
            onChange={onEmailChange}
            onPaste={onPaste}
            onRemove={onRemoveEmail}
            disabled={isAnalyzing}
            canRemove={emails.length > 1}
          />
        ))}
      </div>

      {emails.length < 50 && (
        <button
          className="btn btn-secondary add-email-btn"
          onClick={onAddEmail}
          disabled={isAnalyzing}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 5V19M5 12H19" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Ajouter un Email
        </button>
      )}

      {isAnalyzing && <ProgressBar progress={progress} />}

      <div className="form-actions">
        <button
          className="btn btn-secondary"
          onClick={onClear}
          disabled={isAnalyzing}
        >
          Effacer Tout
        </button>
        <button
          className="btn btn-primary"
          onClick={onAnalyze}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <>
              <div className="spinner"></div>
              <span>Analyse en cours...</span>
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span>Analyser {validEmailCount} Email(s)</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default BulkAnalysisForm;
