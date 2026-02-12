import React from 'react';

function ProgressBar({ progress }) {
  return (
    <div className="progress-section">
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="progress-text">
        Analyse en cours... {progress}%
      </p>
    </div>
  );
}

export default ProgressBar;
