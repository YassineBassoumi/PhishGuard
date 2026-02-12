import './Hero.css';
import Logo from './Logo';

const Hero = () => {
    return (
        <div className="hero">
            <div className="hero-content fade-in-up">
                <div className="hero-badge mb-md">
                    <Logo size={64} showText={false} />
                </div>

                <h1 className="hero-title">
                    Phish<span className="hero-title-guard">Guard</span>
                </h1>
                
                <p className="hero-subtitle mb-lg">
                    Plateforme intelligente dédiée à la détection des attaques de phishing
                </p>

                <p className="hero-description mb-xl">
                    Détectez les emails et URLs malveillants à l’aide de l’intelligence artificielle.
                     PhishGuard s’appuie sur des techniques avancées de traitement du langage naturel et de Machine Learning pour analyser les contenus sélectionnés et identifier les menaces en ligne, tout en protégeant les utilisateurs contre les tentatives de fraude.<br/>
                    Analyse à la demande . NLP avancé . Haute précision
                </p>

                <div className="hero-stats">
                    <div className="stat-item scale-in">
                        <div className="stat-value">99.2%</div>
                        <div className="stat-label">Précision</div>
                    </div>
                    <div className="stat-item scale-in" style={{ animationDelay: '0.1s' }}>
                        <div className="stat-value">&lt;2s</div>
                        <div className="stat-label">Temps d'analyse</div>
                    </div>
                    <div className="stat-item scale-in" style={{ animationDelay: '0.2s' }}>
                        <div className="stat-value">24/7</div>
                        <div className="stat-label">Protection</div>
                    </div>
                </div>
            </div>

            {/* Floating elements */}
            <div className="floating-element" style={{ top: '20%', left: '10%' }}></div>
            <div className="floating-element" style={{ top: '60%', right: '15%' }}></div>
            <div className="floating-element" style={{ bottom: '25%', left: '20%' }}></div>
        </div>
    );
};

export default Hero;
