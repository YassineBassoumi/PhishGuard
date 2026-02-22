import './Integrations.css';

function Integrations({ onOpenModal }) {
  const handleConnectClick = () => {
    if (onOpenModal) {
      onOpenModal();
    }
  };

  return (
    <div className="integrations">
      <div className="container">
        <h2 className="integrations-title">
          Connectez vos <span className="integrations-title-highlight">comptes email</span>
        </h2>
        <p className="integrations-subtitle">
              PhishGuard s’intègre aux principaux services de messagerie pour analyser les emails sélectionnés et identifier les menaces de sécurité à l’aide de techniques avancées de détection.        </p>

        <div className="integrations-grid">
          <div className="integration-card">
            <div className="integration-icon-wrapper gmail-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                <path d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L12 9.366l8.073-5.873C21.69 2.28 24 3.434 24 5.457z" fill="#EA4335"/>
              </svg>
            </div>
            <h3 className="integration-name">Gmail</h3>
            <p className="integration-description">
Connectez votre compte Google en un clic.
Analyse intelligente des emails sélectionnés afin de détecter et traiter les menaces potentielles            </p>
            <div className="integration-users">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              2M+ utilisateurs
            </div>
            <button className="integration-btn" onClick={handleConnectClick}>
              Connecter →
            </button>
          </div>

          <div className="integration-card">
            <div className="integration-icon-wrapper outlook-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="18" height="16" rx="2" fill="#0078D4"/>
                <path d="M3 8l9 5 9-5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 className="integration-name">Outlook</h3>
            <p className="integration-description">
Intégration native avec Microsoft 365.
Analyse ciblée des emails sélectionnés pour une protection efficace des comptes personnels et professionnels.            </p>
            <div className="integration-users">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              800K+ utilisateurs
            </div>
            <button className="integration-btn" onClick={handleConnectClick}>
              Connecter →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Integrations;
