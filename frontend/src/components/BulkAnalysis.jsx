import React, { useState } from 'react';
import './BulkAnalysis.css';
import { useAuth } from '../contexts/AuthContext';

const BulkAnalysis = ({ initialEmails = null }) => {
    const { token } = useAuth();
    const [emails, setEmails] = useState(['', '', '']);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [results, setResults] = useState(null);
    const [progress, setProgress] = useState(0);

    // Load initial emails if provided (from Gmail multi-select)
    React.useEffect(() => {
        if (initialEmails && initialEmails.length > 0) {
            setEmails(initialEmails);
        }
    }, [initialEmails]);

    const handleEmailChange = (index, value) => {
        const newEmails = [...emails];
        newEmails[index] = value;
        setEmails(newEmails);
    };

    const addEmailField = () => {
        if (emails.length < 50) {
            setEmails([...emails, '']);
        }
    };

    const removeEmailField = (index) => {
        if (emails.length > 1) {
            const newEmails = emails.filter((_, i) => i !== index);
            setEmails(newEmails);
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        const pastedText = e.clipboardData.getData('text');
        const lines = pastedText.split('\n\n').filter(line => line.trim());
        
        if (lines.length > 1) {
            // Multiple emails pasted
            const newEmails = lines.slice(0, 50); // Max 50
            setEmails(newEmails);
        } else {
            // Single email, paste normally
            const index = parseInt(e.target.dataset.index);
            handleEmailChange(index, pastedText);
        }
    };

    const handleAnalyze = async () => {
        // Filter out empty emails
        const validEmails = emails.filter(email => email.trim());
        
        if (validEmails.length === 0) {
            alert('Veuillez entrer au moins un email à analyser');
            return;
        }

        setIsAnalyzing(true);
        setProgress(0);
        setResults(null);

        try {
            // Simulate progress (since we don't have real-time updates)
            const progressInterval = setInterval(() => {
                setProgress(prev => Math.min(prev + 10, 90));
            }, 200);

            const response = await fetch('http://localhost:8000/api/analyze-bulk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ emails: validEmails })
            });

            clearInterval(progressInterval);
            setProgress(100);

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            setResults(data);
        } catch (error) {
            console.error('Bulk analysis failed:', error);
            alert('Erreur lors de l\'analyse: ' + error.message);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleClear = () => {
        setEmails(['', '', '']);
        setResults(null);
        setProgress(0);
    };

    const getThreatColor = (threatLevel) => {
        switch (threatLevel) {
            case 'safe': return '#10b981';
            case 'suspicious': return '#f59e0b';
            case 'dangerous': return '#ef4444';
            default: return '#6b7280';
        }
    };

    const getThreatIcon = (threatLevel) => {
        switch (threatLevel) {
            case 'safe': return '✓';
            case 'suspicious': return '⚠';
            case 'dangerous': return '✕';
            default: return '?';
        }
    };

    return (
        <div className="bulk-analysis-container fade-in-up">
            {!results ? (
                <div className="glass-card">
                    <h2 className="form-title mb-lg">Analyse en Masse</h2>
                    <p className="form-description">
                        Analysez jusqu'à 50 emails simultanément. Collez plusieurs emails séparés par des lignes vides.
                        {initialEmails && initialEmails.length > 0 && (
                            <span className="gmail-import-notice">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M9 11L12 14L22 4M21 12V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H16" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                                {initialEmails.length} email{initialEmails.length > 1 ? 's' : ''} importé{initialEmails.length > 1 ? 's' : ''} depuis Gmail
                            </span>
                        )}
                    </p>

                    <div className="email-fields">
                        {emails.map((email, index) => (
                            <div key={index} className="email-field-group">
                                <div className="email-field-header">
                                    <span className="email-number">Email {index + 1}</span>
                                    {emails.length > 1 && (
                                        <button
                                            className="remove-email-btn"
                                            onClick={() => removeEmailField(index)}
                                            disabled={isAnalyzing}
                                        >
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                                <path d="M18 6L6 18M6 6L18 18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                            </svg>
                                        </button>
                                    )}
                                </div>
                                <textarea
                                    className="email-textarea"
                                    placeholder="Collez le contenu de l'email ici..."
                                    value={email}
                                    onChange={(e) => handleEmailChange(index, e.target.value)}
                                    onPaste={handlePaste}
                                    data-index={index}
                                    disabled={isAnalyzing}
                                    rows={4}
                                />
                            </div>
                        ))}
                    </div>

                    {emails.length < 50 && (
                        <button
                            className="btn btn-secondary add-email-btn"
                            onClick={addEmailField}
                            disabled={isAnalyzing}
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M12 5V19M5 12H19" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            Ajouter un Email
                        </button>
                    )}

                    {isAnalyzing && (
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
                    )}

                    <div className="form-actions">
                        <button
                            className="btn btn-secondary"
                            onClick={handleClear}
                            disabled={isAnalyzing}
                        >
                            Effacer Tout
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={handleAnalyze}
                            disabled={isAnalyzing}
                        >
                            {isAnalyzing ? (
                                <>
                                    <div className="spinner"></div>
                                    <span>Analyse en cours...</span>
                                </>
                            ) : (
                                <>
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeWidth="2" strokeLinecap="round" />
                                    </svg>
                                    <span>Analyser {emails.filter(e => e.trim()).length} Email(s)</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            ) : (
                <div className="results-container">
                    {/* Summary Card */}
                    <div className="glass-card summary-card">
                        <div className="summary-header">
                            <h2 className="form-title">Résumé de l'Analyse</h2>
                            <button className="btn btn-secondary btn-sm" onClick={handleClear}>
                                Nouvelle Analyse
                            </button>
                        </div>

                        <div className="summary-stats">
                            <div className="summary-stat">
                                <div className="stat-value">{results.total}</div>
                                <div className="stat-label">Emails Analysés</div>
                            </div>
                            <div className="summary-stat safe">
                                <div className="stat-value">{results.summary.safe}</div>
                                <div className="stat-label">Sûrs</div>
                            </div>
                            <div className="summary-stat suspicious">
                                <div className="stat-value">{results.summary.suspicious}</div>
                                <div className="stat-label">Suspects</div>
                            </div>
                            <div className="summary-stat dangerous">
                                <div className="stat-value">{results.summary.dangerous}</div>
                                <div className="stat-label">Dangereux</div>
                            </div>
                        </div>

                        <div className="summary-details">
                            <div className="detail-item">
                                <span className="detail-label">Menaces Détectées:</span>
                                <span className="detail-value">{results.summary.threats_detected}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Confiance Moyenne:</span>
                                <span className="detail-value">{results.summary.average_confidence}%</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Temps de Traitement:</span>
                                <span className="detail-value">{results.processing_time}s</span>
                            </div>
                        </div>
                    </div>

                    {/* Individual Results */}
                    <div className="glass-card results-list-card">
                        <h3 className="results-title">Résultats Détaillés</h3>
                        <div className="results-list">
                            {results.results.map((result) => (
                                <div 
                                    key={result.index} 
                                    className="result-item"
                                    style={{ borderLeftColor: getThreatColor(result.threat_level) }}
                                >
                                    <div className="result-header">
                                        <div className="result-number">
                                            <span 
                                                className="threat-icon"
                                                style={{ 
                                                    background: getThreatColor(result.threat_level),
                                                    color: 'white'
                                                }}
                                            >
                                                {getThreatIcon(result.threat_level)}
                                            </span>
                                            <span>Email {result.index + 1}</span>
                                        </div>
                                        <span 
                                            className="threat-badge"
                                            style={{ 
                                                background: `${getThreatColor(result.threat_level)}20`,
                                                color: getThreatColor(result.threat_level)
                                            }}
                                        >
                                            {result.threat_level}
                                        </span>
                                    </div>

                                    <div className="result-content">
                                        <p className="content-preview">{result.content_preview}</p>
                                        
                                        <div className="confidence-bar">
                                            <span className="confidence-label">Confiance: {result.confidence.toFixed(1)}%</span>
                                            <div className="confidence-progress">
                                                <div 
                                                    className="confidence-fill"
                                                    style={{ 
                                                        width: `${result.confidence}%`,
                                                        background: getThreatColor(result.threat_level)
                                                    }}
                                                ></div>
                                            </div>
                                        </div>

                                        {result.features.length > 0 && (
                                            <div className="features-section">
                                                <strong>Indicateurs:</strong>
                                                <ul className="features-list">
                                                    {result.features.slice(0, 3).map((feature, i) => (
                                                        <li key={i}>{feature}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BulkAnalysis;
