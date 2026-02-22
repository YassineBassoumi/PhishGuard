import './HowItWorks.css';

function HowItWorks() {
  return (
    <div className="how-it-works">
      <div className="container">
        <h2 className="how-title">
          Comment ça <span className="how-title-highlight">marche</span> ?
        </h2>
        <p className="how-subtitle">
Quatre étapes simples pour analyser les emails sélectionnés de vos comptes et détecter les tentatives de phishing.        </p>

        <div className="steps-container">
          <div className="step-item">
            <div className="step-header">
              <span className="step-num">01</span>
              <svg className="step-svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <h3 className="step-name">Créez votre compte</h3>
            <p className="step-text">
              Inscription rapide en 30 secondes.Gratuit.
            </p>
          </div>

          <div className="step-item">
            <div className="step-header">
              <span className="step-num">02</span>
              <svg className="step-svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="16" rx="2" />
                <polyline points="3,8 12,13 21,8" />
              </svg>
            </div>
            <h3 className="step-name">Connectez vos emails</h3>
            <p className="step-text">
              Liez Gmail ou Outlook en quelques clics grâce à une authentification sécurisée OAuth.
            </p>
          </div>

          <div className="step-item">
            <div className="step-header">
              <span className="step-num">03</span>
              <svg className="step-svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7" />
                <rect x="14" y="3" width="7" height="7" />
                <rect x="14" y="14" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" />
              </svg>
            </div>
            <h3 className="step-name">Laissez l'IA travailler</h3>
            <p className="step-text">
              Notre système analyse les emails sélectionnés en un simple clic et vous alerte en cas de menace.
            </p>
          </div>

          <div className="step-item">
            <div className="step-header">
              <span className="step-num">04</span>
              <svg className="step-svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <h3 className="step-name">Restez protégé</h3>
            <p className="step-text">
              Consultez vos rapports de sécurité et personnalisez vos préférences de protection.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HowItWorks;
