import { useState } from 'react';
import './ResultsDisplay.css';

// Simple verdict row used inside the decision-trace panel.
// Shows only a label and a colored verdict (no scores, URLs, or rule names).
const SimpleVerdictRow = ({ icon, label, verdict }) => {
    const map = {
        safe: { color: '#10b981', text: 'Sûr' },
        suspicious: { color: '#f59e0b', text: 'Suspect' },
        dangerous: { color: '#ef4444', text: 'Dangereux' },
    };
    const v = map[verdict] || { color: '#9ca3af', text: verdict || '—' };
    return (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', marginBottom: '0.5rem' }}>
            <span>{icon} {label}</span>
            <strong style={{ color: v.color }}>{v.text}</strong>
        </div>
    );
};

const ResultsDisplay = ({ results, isAnalyzing }) => {
    const [showTrace, setShowTrace] = useState(false);

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
                    label: 'SÛR',
                    className: 'badge-success',
                    icon: (
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M20 6L9 17L4 12" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    ),
                    message: 'Aucune menace détectée',
                    bgColor: 'rgba(16, 185, 129, 0.1)',
                    borderColor: '#10b981'
                };
            case 'suspicious':
                return {
                    label: 'SUSPECT',
                    className: 'badge-warning',
                    icon: (
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    ),
                    message: 'Éléments suspects détectés',
                    bgColor: 'rgba(245, 158, 11, 0.1)',
                    borderColor: '#f59e0b'
                };
            case 'dangerous':
                return {
                    label: 'DANGEREUX',
                    className: 'badge-danger',
                    icon: (
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M18 6L6 18M6 6L18 18" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    ),
                    message: 'Menace de phishing détectée',
                    bgColor: 'rgba(239, 68, 68, 0.1)',
                    borderColor: '#ef4444'
                };
            default:
                return {
                    label: 'INCONNU',
                    className: 'badge-warning',
                    icon: (
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M8.228 9C8.654 7.833 9.776 7 11 7C12.657 7 14 8.343 14 10C14 11.657 12.657 13 11 13V15M11 19H11.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    ),
                    message: 'Résultat non disponible',
                    bgColor: 'rgba(156, 163, 175, 0.1)',
                    borderColor: '#9ca3af'
                };
        }
    };

    const threat = getThreatConfig(results.threatLevel);

    return (
        <div className="results-container scale-in">
            <div className="results-header">
                <h2 className="results-title">Résultats de l'analyse</h2>
            </div>

            <div className="results-grid">
                {/* Main Threat Card */}
                <div className="glass-card threat-card" style={{ 
                    background: threat.bgColor,
                    borderLeft: `4px solid ${threat.borderColor}`
                }}>
                    <div className="threat-content">
                        <div className="threat-icon-wrapper" style={{ color: threat.borderColor }}>
                            {threat.icon}
                        </div>
                        <div className="threat-info">
                            <div className={`threat-badge ${threat.className}`}>
                                {threat.label}
                            </div>
                            <p className="threat-message">{threat.message}</p>
                        </div>
                    </div>
                </div>

                {/* Confidence Score Card */}
                <div className="glass-card confidence-card">
                    <div className="card-header">
                        <h3 className="card-title">Score de confiance</h3>
                        <div className="confidence-percentage">{results.confidence.toFixed(2)}%</div>
                    </div>
                    <div className="progress-bar-modern">
                        <div
                            className="progress-fill-modern"
                            style={{ 
                                width: `${results.confidence}%`,
                                background: results.confidence > 80 
                                    ? 'linear-gradient(90deg, #5b8def, #9b7ee8)' 
                                    : results.confidence > 50 
                                    ? 'linear-gradient(90deg, #f59e0b, #f97316)'
                                    : 'linear-gradient(90deg, #ef4444, #dc2626)'
                            }}
                        ></div>
                    </div>
                </div>
            </div>

            {/* Content Preview */}
            <div className="glass-card content-card">
                <div className="card-header">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M9 12H15M9 16H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17 21Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <h3 className="card-title">Contenu analysé</h3>
                </div>
                <div className="content-box-modern">
                    <code>{results.content}</code>
                </div>
            </div>

            {/* Features and Recommendations Grid */}
            <div className="details-grid">
                {/* Detected Features */}
                {results.features && results.features.length > 0 && (
                    <div className="glass-card features-card">
                        <div className="card-header">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5M12 12H15M12 16H15M9 12H9.01M9 16H9.01" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            <h3 className="card-title">Caractéristiques détectées</h3>
                        </div>
                        <ul className="features-list-modern">
                            {results.features.map((feature, index) => (
                                <li key={index} className="feature-item-modern" style={{ animationDelay: `${index * 0.05}s` }}>
                                    <div className="feature-bullet"></div>
                                    <span>{feature}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Recommendations */}
                {results.recommendations && results.recommendations.length > 0 && (
                    <div className="glass-card recommendations-card">
                        <div className="card-header">
                            {results.threatLevel === 'safe' ? (
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                            ) : (
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M12 9V11M12 15H12.01M5.07183 19H18.9282C20.4678 19 21.4301 17.3333 20.6603 16L13.7321 4C12.9623 2.66667 11.0377 2.66667 10.2679 4L3.33975 16C2.56995 17.3333 3.53223 19 5.07183 19Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                            )}
                            <h3 className="card-title">Recommandations</h3>
                        </div>
                        <ul className="recommendations-list-modern">
                            {results.recommendations.map((rec, index) => (
                                <li key={index} className="recommendation-item-modern" style={{ animationDelay: `${index * 0.05}s` }}>
                                    <div className="recommendation-icon">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M9 5L16 12L9 19" strokeLinecap="round" strokeLinejoin="round"/>
                                        </svg>
                                    </div>
                                    <span>{rec}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Decision Trace - Transparency for the user/auditor */}
            {results.decision_trace && (
                <div className="glass-card" style={{ marginTop: '1.5rem' }}>
                    <button
                        onClick={() => setShowTrace(!showTrace)}
                        style={{
                            display: 'flex', alignItems: 'center', gap: '0.5rem',
                            background: 'transparent', border: 'none', color: 'inherit',
                            cursor: 'pointer', fontSize: '1rem', fontWeight: 600,
                            padding: '0.25rem 0', width: '100%'
                        }}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M9.09 9C9.3251 8.33167 9.78915 7.76811 10.4 7.40913C11.0108 7.05016 11.7289 6.91894 12.4272 7.03871C13.1255 7.15849 13.7588 7.52152 14.2151 8.06353C14.6713 8.60553 14.9211 9.29152 14.92 10C14.92 12 11.92 13 11.92 13M12 17H12.01" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        <span>Détails de la décision IA</span>
                        <span style={{ marginLeft: 'auto', transform: showTrace ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}>▼</span>
                    </button>

                    {showTrace && (
                        <div style={{ marginTop: '1rem', fontSize: '0.875rem' }}>
                            {/* Preprocessing notice */}
                            {results.decision_trace.preprocessed && (
                                <div style={{ marginBottom: '0.5rem', padding: '0.6rem 0.9rem', background: 'rgba(99, 102, 241, 0.08)', borderRadius: '6px', borderLeft: '3px solid #6366f1', fontSize: '0.8rem' }}>
                                    🧹 Email brut détecté — en-têtes et code HTML automatiquement nettoyés avant analyse.
                                </div>
                            )}

                            {/* Text verdict (general only) */}
                            <SimpleVerdictRow icon="📝" label="Analyse du texte" verdict={results.decision_trace.ml_email?.verdict} />

                            {/* URL verdict (general - most severe wins, no individual URLs) */}
                            {(() => {
                                const urls = results.decision_trace.url_models || [];
                                if (urls.length === 0) return null;
                                let overall = 'safe';
                                if (urls.some(u => u.verdict === 'dangerous')) overall = 'dangerous';
                                else if (urls.some(u => u.verdict === 'suspicious')) overall = 'suspicious';
                                return <SimpleVerdictRow icon="🔗" label="Analyse des liens" verdict={overall} />;
                            })()}

                            {/* Override notice in plain language */}
                            {results.decision_trace.ml_overridden && (
                                <div style={{ marginTop: '0.75rem', padding: '0.75rem 1rem', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '6px', borderLeft: '3px solid #f59e0b', fontSize: '0.85rem' }}>
                                    ℹ️ Le verdict final a été ajusté après combinaison des analyses du texte et des liens.
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ResultsDisplay;
