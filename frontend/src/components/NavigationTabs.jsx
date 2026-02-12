import React from 'react';

function NavigationTabs({ viewMode, onViewChange, hasConnectedProviders }) {
  return (
    <div className="view-tabs">
      <button 
        className={`view-tab ${viewMode === 'manual' ? 'active' : ''}`}
        onClick={() => onViewChange('manual')}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeWidth="2" strokeLinecap="round" />
        </svg>
        Analyser
      </button>
      <button 
        className={`view-tab ${viewMode === 'bulk' ? 'active' : ''}`}
        onClick={() => onViewChange('bulk')}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9 12H15M9 16H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17 21Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Analyse en Masse
      </button>
      <button 
        className={`view-tab ${viewMode === 'dashboard' ? 'active' : ''}`}
        onClick={() => onViewChange('dashboard')}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 13H11V3H3V13ZM3 21H11V15H3V21ZM13 21H21V11H13V21ZM13 3V9H21V3H13Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Tableau de Bord
      </button>
      {hasConnectedProviders && (
        <button 
          className={`view-tab ${viewMode === 'email' ? 'active' : ''}`}
          onClick={() => onViewChange('email')}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round" />
          </svg>
          Email
        </button>
      )}
      <button 
        className={`view-tab ${viewMode === 'profile' ? 'active' : ''}`}
        onClick={() => onViewChange('profile')}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Profil
      </button>
    </div>
  );
}

export default NavigationTabs;
