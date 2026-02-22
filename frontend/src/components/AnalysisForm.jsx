import { useState, useEffect } from 'react';
import './AnalysisForm.css';

const AnalysisForm = ({ onAnalyze, isAnalyzing, onSwitchToGmail, token }) => {
    const [activeTab, setActiveTab] = useState('url');
    const [emailContent, setEmailContent] = useState('');
    const [urlContent, setUrlContent] = useState('');
    
    // URL-specific indicators
    const [urlIndicators, setUrlIndicators] = useState({
        https: { status: 'waiting', label: 'Vérification SSL', message: '' },
        domain: { status: 'waiting', label: 'Analyse du Domaine', message: '' },
        keywords: { status: 'waiting', label: 'Mots-clés Suspects', message: '' },
        structure: { status: 'waiting', label: 'Structure URL', message: '' }
    });
    
    // Email-specific indicators
    const [emailIndicators, setEmailIndicators] = useState({
        phishingKeywords: { status: 'waiting', label: 'Mots-clés de Phishing', message: '' },
        urgencyLanguage: { status: 'waiting', label: 'Langage Urgent', message: '' },
        suspiciousLinks: { status: 'waiting', label: 'Liens Suspects', message: '' },
        credentialRequest: { status: 'waiting', label: 'Demande de Données', message: '' }
    });
    
    const [isProgressiveAnalyzing, setIsProgressiveAnalyzing] = useState(false);
    
    // Get current indicators based on active tab
    const liveIndicators = activeTab === 'url' ? urlIndicators : emailIndicators;

    // Real-time progressive analysis for URLs
    const performProgressiveAnalysis = async (url) => {
        if (!url || url.trim().length < 10) {
            // Reset URL indicators if URL is too short
            setUrlIndicators({
                https: { status: 'waiting', label: 'Vérification SSL', message: '' },
                domain: { status: 'waiting', label: 'Analyse du Domaine', message: '' },
                keywords: { status: 'waiting', label: 'Mots-clés Suspects', message: '' },
                structure: { status: 'waiting', label: 'Structure URL', message: '' }
            });
            return;
        }

        setIsProgressiveAnalyzing(true);

        try {
            // Call progressive analysis endpoint
            const response = await fetch('http://localhost:8000/api/analyze-progressive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                throw new Error('Progressive analysis failed');
            }

            const data = await response.json();

            // Update URL indicators with real backend results
            if (data.indicators) {
                setUrlIndicators({
                    https: data.indicators.https || urlIndicators.https,
                    domain: data.indicators.domain || urlIndicators.domain,
                    keywords: data.indicators.keywords || urlIndicators.keywords,
                    structure: data.indicators.structure || urlIndicators.structure
                });
            }
        } catch (error) {
            console.error('Progressive analysis error:', error);
        } finally {
            setIsProgressiveAnalyzing(false);
        }
    };
    
    // Real-time progressive analysis for Emails
    const performEmailAnalysis = async (content) => {
        if (!content || content.trim().length < 20) {
            // Reset email indicators if content is too short
            setEmailIndicators({
                phishingKeywords: { status: 'waiting', label: 'Mots-clés de Phishing', message: '' },
                urgencyLanguage: { status: 'waiting', label: 'Langage Urgent', message: '' },
                suspiciousLinks: { status: 'waiting', label: 'Liens Suspects', message: '' },
                credentialRequest: { status: 'waiting', label: 'Demande de Données', message: '' }
            });
            return;
        }

        setIsProgressiveAnalyzing(true);

        try {
            const contentLower = content.toLowerCase();
            
            // Check for phishing keywords
            const phishingKeywords = ['verify', 'urgent', 'suspended', 'locked', 'confirm', 'click here', 'account', 'password', 'update', 'expire'];
            const foundKeywords = phishingKeywords.filter(kw => contentLower.includes(kw));
            
            setEmailIndicators(prev => ({
                ...prev,
                phishingKeywords: {
                    status: foundKeywords.length === 0 ? 'safe' : foundKeywords.length <= 2 ? 'warning' : 'danger',
                    label: 'Mots-clés de Phishing',
                    message: foundKeywords.length === 0 ? 'Aucun mot-clé suspect' : `${foundKeywords.length} mot(s)-clé(s) trouvé(s)`
                }
            }));
            
            // Check for urgency language
            const urgencyWords = ['urgent', 'immediate', 'act now', 'expire', 'suspended', 'limited time'];
            const foundUrgency = urgencyWords.filter(word => contentLower.includes(word));
            
            setEmailIndicators(prev => ({
                ...prev,
                urgencyLanguage: {
                    status: foundUrgency.length === 0 ? 'safe' : foundUrgency.length === 1 ? 'warning' : 'danger',
                    label: 'Langage Urgent',
                    message: foundUrgency.length === 0 ? 'Pas de langage urgent' : `${foundUrgency.length} expression(s) urgente(s)`
                }
            }));
            
            // Check for suspicious links
            const urlPattern = /https?:\/\/[^\s]+/gi;
            const urls = content.match(urlPattern) || [];
            
            setEmailIndicators(prev => ({
                ...prev,
                suspiciousLinks: {
                    status: urls.length === 0 ? 'safe' : urls.length <= 2 ? 'warning' : 'danger',
                    label: 'Liens Suspects',
                    message: urls.length === 0 ? 'Aucun lien détecté' : `${urls.length} lien(s) trouvé(s)`
                }
            }));
            
            // Check for credential requests
            const credentialWords = ['password', 'username', 'login', 'credential', 'ssn', 'social security', 'credit card', 'bank account'];
            const foundCredentials = credentialWords.filter(word => contentLower.includes(word));
            
            setEmailIndicators(prev => ({
                ...prev,
                credentialRequest: {
                    status: foundCredentials.length === 0 ? 'safe' : 'danger',
                    label: 'Demande de Données',
                    message: foundCredentials.length === 0 ? 'Aucune demande suspecte' : 'Demande d\'informations sensibles'
                }
            }));
            
        } catch (error) {
            console.error('Email analysis error:', error);
        } finally {
            setIsProgressiveAnalyzing(false);
        }
    };

    // Debounced URL analysis - DISABLED (only analyze on button click)
    // useEffect(() => {
    //     if (activeTab === 'url' && urlContent && !isAnalyzing) {
    //         const timer = setTimeout(() => {
    //             performProgressiveAnalysis(urlContent);
    //         }, 1000);
    //         return () => clearTimeout(timer);
    //     }
    // }, [urlContent, activeTab, isAnalyzing]);
    
    // Debounced Email analysis - DISABLED (only analyze on button click)
    // useEffect(() => {
    //     if (activeTab === 'email' && emailContent && !isAnalyzing) {
    //         const timer = setTimeout(() => {
    //             performEmailAnalysis(emailContent);
    //         }, 1000);
    //         return () => clearTimeout(timer);
    //     }
    // }, [emailContent, activeTab, isAnalyzing]);

    // Reset indicators when URL content changes (manual deletion)
    useEffect(() => {
        if (activeTab === 'url' && urlContent.trim().length < 10) {
            setUrlIndicators({
                https: { status: 'waiting', label: 'Vérification SSL', message: '' },
                domain: { status: 'waiting', label: 'Analyse du Domaine', message: '' },
                keywords: { status: 'waiting', label: 'Mots-clés Suspects', message: '' },
                structure: { status: 'waiting', label: 'Structure URL', message: '' }
            });
        }
    }, [urlContent, activeTab]);

    // Reset indicators when email content changes (manual deletion)
    useEffect(() => {
        if (activeTab === 'email' && emailContent.trim().length < 20) {
            setEmailIndicators({
                phishingKeywords: { status: 'waiting', label: 'Mots-clés de Phishing', message: '' },
                urgencyLanguage: { status: 'waiting', label: 'Langage Urgent', message: '' },
                suspiciousLinks: { status: 'waiting', label: 'Liens Suspects', message: '' },
                credentialRequest: { status: 'waiting', label: 'Demande de Données', message: '' }
            });
        }
    }, [emailContent, activeTab]);

    // Reset indicators when switching tabs
    useEffect(() => {
        setUrlIndicators({
            https: { status: 'waiting', label: 'Vérification SSL', message: '' },
            domain: { status: 'waiting', label: 'Analyse du Domaine', message: '' },
            keywords: { status: 'waiting', label: 'Mots-clés Suspects', message: '' },
            structure: { status: 'waiting', label: 'Structure URL', message: '' }
        });
        setEmailIndicators({
            phishingKeywords: { status: 'waiting', label: 'Mots-clés de Phishing', message: '' },
            urgencyLanguage: { status: 'waiting', label: 'Langage Urgent', message: '' },
            suspiciousLinks: { status: 'waiting', label: 'Liens Suspects', message: '' },
            credentialRequest: { status: 'waiting', label: 'Demande de Données', message: '' }
        });
    }, [activeTab]);

    const handleSubmit = (e) => {
        e.preventDefault();
        const content = activeTab === 'email' ? emailContent : urlContent;

        if (!content || !content.trim()) {
            alert(`Veuillez entrer ${activeTab === 'email' ? 'un texte' : 'une URL'}`);
            return;
        }

        // Trigger progressive analysis before full analysis
        if (activeTab === 'url') {
            performProgressiveAnalysis(content);
        } else {
            performEmailAnalysis(content);
        }

        // Then trigger full analysis
        onAnalyze(activeTab, content);
    };

    const handleClear = () => {
        if (activeTab === 'email') {
            setEmailContent('');
            setEmailIndicators({
                phishingKeywords: { status: 'waiting', label: 'Mots-clés de Phishing', message: '' },
                urgencyLanguage: { status: 'waiting', label: 'Langage Urgent', message: '' },
                suspiciousLinks: { status: 'waiting', label: 'Liens Suspects', message: '' },
                credentialRequest: { status: 'waiting', label: 'Demande de Données', message: '' }
            });
        } else {
            setUrlContent('');
            setUrlIndicators({
                https: { status: 'waiting', label: 'Vérification SSL', message: '' },
                domain: { status: 'waiting', label: 'Analyse du Domaine', message: '' },
                keywords: { status: 'waiting', label: 'Mots-clés Suspects', message: '' },
                structure: { status: 'waiting', label: 'Structure URL', message: '' }
            });
        }
    };

    const getIndicatorIcon = (status) => {
        if (status === 'waiting') {
            return (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" opacity="0.3">
                    <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                </svg>
            );
        } else if (status === 'analyzing') {
            return (
                <div className="spinner-small"></div>
            );
        } else if (status === 'safe') {
            return (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2">
                    <path d="M20 6L9 17L4 12" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
            );
        } else if (status === 'warning') {
            return (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2">
                    <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
            );
        } else if (status === 'danger') {
            return (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
                    <path d="M18 6L6 18M6 6L18 18" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
            );
        }
    };

    const getIndicatorClass = (status) => {
        if (status === 'safe') return 'indicator-safe';
        if (status === 'warning') return 'indicator-warning';
        if (status === 'danger') return 'indicator-danger';
        return '';
    };

    return (
        <div className="analysis-form-container fade-in-up">
            <div className="analysis-layout">
                {/* Main Analysis Card */}
                <div className="glass-card analysis-main-card">
                    <div className="analysis-header">
                        <h2 className="form-title">Analyseur de Menaces</h2>
                        <p className="form-subtitle">Détection de phishing en temps réel propulsée par l'intelligence artificielle.</p>
                    </div>

                    {/* Tabs */}
                    <div className="tabs-modern mb-lg">
                        <button
                            className={`tab-modern ${activeTab === 'url' ? 'active' : ''}`}
                            onClick={() => setActiveTab('url')}
                            disabled={isAnalyzing}
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M10 13C10.4295 13.5741 10.9774 14.0492 11.6066 14.3929C12.2357 14.7367 12.9315 14.9411 13.6467 14.9923C14.3618 15.0435 15.0796 14.9403 15.7513 14.6897C16.4231 14.4392 17.0331 14.047 17.54 13.54L20.54 10.54C21.4508 9.59698 21.9548 8.33398 21.9434 7.02299C21.932 5.71201 21.4061 4.45794 20.4791 3.53091C19.5521 2.60388 18.298 2.078 16.987 2.06658C15.676 2.05517 14.413 2.55918 13.47 3.47L11.75 5.18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M14 11C13.5705 10.4259 13.0226 9.95083 12.3934 9.60707C11.7642 9.26331 11.0685 9.05889 10.3533 9.00768C9.63819 8.95646 8.92037 9.05966 8.24861 9.31023C7.57685 9.5608 6.96684 9.95303 6.45996 10.46L3.45996 13.46C2.54917 14.403 2.04516 15.666 2.05657 16.977C2.06798 18.288 2.59387 19.542 3.52091 20.4691C4.44794 21.3961 5.70201 21.922 7.01299 21.9334C8.32398 21.9448 9.58698 21.4408 10.53 20.53L12.24 18.82" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            Analyser URL
                        </button>

                        <button
                            className={`tab-modern ${activeTab === 'email' ? 'active' : ''}`}
                            onClick={() => setActiveTab('email')}
                            disabled={isAnalyzing}
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M9 12H15M9 16H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17 21Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            Analyser Texte
                        </button>
                    </div>

                    {/* Cible de l'analyse */}
                    <div className="analysis-target">
                        <label className="target-label">Cible de l'analyse</label>
                        <form onSubmit={handleSubmit}>
                            {activeTab === 'url' && (
                                <div className="form-group">
                                    <input
                                        id="url-input"
                                        type="text"
                                        className="input-modern"
                                        placeholder="Collez l'URL suspecte (ex: http://banque-secure-login.com) ou le contenu de l'e-mail ici..."
                                        value={urlContent}
                                        onChange={(e) => setUrlContent(e.target.value)}
                                        disabled={isAnalyzing}
                                    />
                                </div>
                            )}

                            {activeTab === 'email' && (
                                <div className="form-group">
                                    <textarea
                                        id="email-input"
                                        className="textarea-modern"
                                        placeholder="Collez ici le contenu de l'email suspect...&#10;&#10;Exemple:&#10;From: support@paypa1.com&#10;Subject: Urgent: Verify your account"
                                        value={emailContent}
                                        onChange={(e) => setEmailContent(e.target.value)}
                                        disabled={isAnalyzing}
                                        rows="6"
                                    />
                                </div>
                            )}

                            {/* Action buttons */}
                            <div className="form-actions-modern">
                                {activeTab === 'email' && (
                                    <button
                                        type="button"
                                        className="btn-modern btn-secondary-modern"
                                        onClick={onSwitchToGmail}
                                        disabled={isAnalyzing}
                                    >
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                            <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round" />
                                        </svg>
                                        Sélectionner un Email
                                    </button>
                                )}

                                <button
                                    type="button"
                                    className="btn-modern btn-secondary-modern"
                                    onClick={handleClear}
                                    disabled={isAnalyzing}
                                >
                                    Effacer
                                </button>

                                <button
                                    type="submit"
                                    className="btn-modern btn-primary-modern"
                                    disabled={isAnalyzing}
                                >
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                                        <path d="M12 6V12L16 14" strokeWidth="2" strokeLinecap="round"/>
                                    </svg>
                                    Analyser
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                {/* Live Analysis Indicators */}
                <div className="glass-card analysis-live-card">
                    <div className="live-header">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M12 2L2 7L12 12L22 7L12 2Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            <path d="M2 17L12 22L22 17" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            <path d="M2 12L12 17L22 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        <h3>Analyse IA Live</h3>
                    </div>

                    <div className="live-indicators">
                        <p className="indicators-title">INDICATEURS DÉTECTÉS</p>
                        <p className="indicators-subtitle">TEMPS RÉEL</p>

                        <div className="indicator-list">
                            {Object.entries(liveIndicators).map(([key, indicator]) => (
                                <div key={key} className={`indicator-item ${indicator.status} ${getIndicatorClass(indicator.status)}`}>
                                    <div className="indicator-icon">
                                        {isProgressiveAnalyzing && indicator.status === 'waiting' 
                                            ? getIndicatorIcon('analyzing')
                                            : getIndicatorIcon(indicator.status)
                                        }
                                    </div>
                                    <div className="indicator-content">
                                        <span className="indicator-label">{indicator.label}</span>
                                        {indicator.message && (
                                            <span className="indicator-status">{indicator.message}</span>
                                        )}
                                        {!indicator.message && (
                                            <span className="indicator-status">
                                                {activeTab === 'url' ? 'En attente de l\'URL...' : 'En attente du contenu...'}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="live-message">
                            <p>
                                {activeTab === 'url' 
                                    ? "L'IA analyse l'URL en temps réel pendant que vous tapez..."
                                    : "L'IA analyse le contenu de l'email en temps réel..."
                                }
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalysisForm;
