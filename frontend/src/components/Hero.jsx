import React from 'react';
import './Hero.css';

const Hero = () => {
    return (
        <div className="hero" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', width: '100%' }}>
            <div className="hero-content fade-in-up" style={{ textAlign: 'center', maxWidth: '1000px', margin: '0 auto' }}>
                <div className="hero-badge mb-md" style={{ margin: '0 auto 1.5rem' }}>
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                            fill="url(#gradient)" stroke="currentColor" strokeWidth="2" />
                        <defs>
                            <linearGradient id="gradient" x1="2" y1="2" x2="22" y2="21">
                                <stop offset="0%" stopColor="#00d4ff" />
                                <stop offset="100%" stopColor="#a855f7" />
                            </linearGradient>
                        </defs>
                    </svg>
                </div>

                <h1 className="hero-title" style={{ textAlign: 'center' }}>PhishGuard AI</h1>
                <p className="hero-subtitle mb-lg" style={{ textAlign: 'center' }}>
                    Système de détection de phishing par IA
                </p>

                <p className="hero-description mb-xl" style={{ textAlign: 'center', margin: '0 auto 3rem' }}>
                    Détectez les emails et URLs malveillants grâce à l'intelligence artificielle.
                    <br />
                    Analyse en temps réel • NLP avancé • Haute précision
                </p>

                <div className="hero-stats" style={{ display: 'flex', justifyContent: 'center', gap: '3rem', flexWrap: 'wrap', margin: '0 auto' }}>
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
