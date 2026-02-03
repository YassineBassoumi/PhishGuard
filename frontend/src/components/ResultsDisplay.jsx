import React from 'react';
import './ResultsDisplay.css';

const ResultsDisplay = ({ results, isAnalyzing }) => {
    if (isAnalyzing) {
        return (
            <div className="results-container fade-in">
                <div className="glass-card">
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <h3>Analyse en cours...</h3>
                        <p>Notre IA analyse le contenu pour détecter les menaces potentielles</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!results) {
        return null;
    }

    const getThreatConfig = (level) => {
        switch (level) {
            case 'safe':
                return {
                    label: 'Sûr',
                    className: 'badge-success',
                    icon: '✓',
                    message: 'Aucune menace détectée'
                };
            case 'suspicious':
                return {
                    label: 'Suspect',
                    className: 'badge-warning',
                    icon: '⚠',
                    message: 'Éléments suspects détectés'
                };
            case 'dangerous':
                return {
                    label: 'Dangereux',
                    className: 'badge-danger',
                    icon: '✕',
                    message: 'Menace de phishing détectée'
                };
            default:
                return {
                    label: 'Inconnu',
                    className: 'badge-warning',
                    icon: '?',
                    message: 'Résultat non disponible'
                };
        }
    };

    const threat = getThreatConfig(results.threatLevel);

    return (
        <div className="results-container scale-in">
            <div className="glass-card">
                <h2 className="results-title mb-lg">Résultats de l'analyse</h2>

                {/* Threat Level */}
                <div className="threat-indicator mb-lg">
                    <div className={`badge ${threat.className}`}>
                        <span className="badge-icon">{threat.icon}</span>
                        <span>{threat.label}</span>
                    </div>
                    <p className="threat-message">{threat.message}</p>
                </div>

                {/* Confidence Score */}
                <div className="confidence-section mb-lg">
                    <div className="confidence-header">
                        <span className="confidence-label">Score de confiance</span>
                        <span className="confidence-value">{results.confidence}%</span>
                    </div>
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${results.confidence}%` }}
                        ></div>
                    </div>
                </div>

                {/* Analyzed Content Preview */}
                <div className="content-preview mb-lg">
                    <h3 className="section-title">Contenu analysé</h3>
                    <div className="content-box">
                        <code>{results.content}</code>
                    </div>
                </div>

                {/* Detected Features */}
                {results.features && results.features.length > 0 && (
                    <div className="features-section mb-lg">
                        <h3 className="section-title">Caractéristiques détectées</h3>
                        <ul className="features-list">
                            {results.features.map((feature, index) => (
                                <li key={index} className="feature-item" style={{ animationDelay: `${index * 0.1}s` }}>
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <circle cx="12" cy="12" r="10" strokeWidth="2" />
                                        <path d="M12 6V12L16 14" strokeWidth="2" strokeLinecap="round" />
                                    </svg>
                                    <span>{feature}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Recommendations */}
                {results.recommendations && results.recommendations.length > 0 && (
                    <div className="recommendations-section">
                        <h3 className="section-title">Recommandations</h3>
                        <ul className="recommendations-list">
                            {results.recommendations.map((rec, index) => (
                                <li key={index} className="recommendation-item" style={{ animationDelay: `${index * 0.1}s` }}>
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M9 5L16 12L9 19" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    <span>{rec}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResultsDisplay;
