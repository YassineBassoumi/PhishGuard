import './FeaturesSection.css';

function FeaturesSection() {
  return (
    <section id="fonctionnalites" className="features-section-new">
      <div className="container">
        <div className="features-header-new">
          <h2 className="features-main-title">
            Une protection <span className="text-gradient">complète</span>
          </h2>
          <p className="features-main-subtitle"> 
           Des outils avancés pour analyser les emails et URLs sélectionnés et détecter les attaques de phishing avant qu'elles ne causent des dommages.
          </p>
        </div>

        <div className="features-grid-new">
          <div className="feature-card-new fade-in-up">
            <div className="feature-icon-new">🤖</div>
            <h3 className="feature-title-new">Détection par IA</h3>
            <p className="feature-desc-new">
              Algorithmes de machine learning avancés avec une précision de 95%+ pour identifier les menaces de phishing.
            </p>
          </div>

          <div className="feature-card-new fade-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="feature-icon-new">📧</div>
            <h3 className="feature-title-new">Analyse d'Emails</h3>
            <p className="feature-desc-new">
              Analysez les emails sélectionnés afin de détecter les tentatives de phishing, les liens suspects et les pièces jointes dangereuses.
            </p>
          </div>

          <div className="feature-card-new fade-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="feature-icon-new">🔗</div>
            <h3 className="feature-title-new">Vérification d'URLs</h3>
            <p className="feature-desc-new">
              Analysez les URLs pour détecter les sites de phishing à l’aide de techniques avancées de détection.
            </p>
          </div>

          <div className="feature-card-new fade-in-up" style={{ animationDelay: '0.3s' }}>
            <div className="feature-icon-new">📊</div>
            <h3 className="feature-title-new">Analyse en Masse</h3>
            <p className="feature-desc-new">
              Traitez jusqu'à 50 emails ou URLs simultanément avec suivi de progression en temps réel.
            </p>
          </div>

          <div className="feature-card-new fade-in-up" style={{ animationDelay: '0.4s' }}>
            <div className="feature-icon-new">📈</div>
            <h3 className="feature-title-new">Tableau de Bord</h3>
            <p className="feature-desc-new">
              Visualisez vos statistiques, la distribution des menaces et l'historique de vos analyses.
            </p>
          </div>

          <div className="feature-card-new fade-in-up" style={{ animationDelay: '0.5s' }}>
            <div className="feature-icon-new">🔐</div>
            <h3 className="feature-title-new">Sécurité Renforcée</h3>
            <p className="feature-desc-new">
              Authentification JWT, chiffrement bcrypt et isolation complète des données utilisateur.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;
