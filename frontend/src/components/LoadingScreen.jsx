import React from 'react';

function LoadingScreen() {
  return (
    <div className="app">
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        <div className="spinner" style={{ width: '48px', height: '48px', borderWidth: '4px' }}></div>
        <p style={{ color: 'var(--text-muted)' }}>Chargement...</p>
      </div>
    </div>
  );
}

export default LoadingScreen;
