import React, { useState } from 'react';
import './AnalysisForm.css';

const AnalysisForm = ({ onAnalyze, isAnalyzing, onSwitchToGmail }) => {
    const [activeTab, setActiveTab] = useState('email');
    const [emailContent, setEmailContent] = useState('');
    const [urlContent, setUrlContent] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        const content = activeTab === 'email' ? emailContent : urlContent;

        if (!content.trim()) {
            alert(`Veuillez entrer ${activeTab === 'email' ? 'un email' : 'une URL'}`);
            return;
        }

        onAnalyze(activeTab, content);
    };

    const handleClear = () => {
        if (activeTab === 'email') {
            setEmailContent('');
        } else {
            setUrlContent('');
        }
    };

    return (
        <div className="analysis-form-container fade-in-up">
            <div className="glass-card">
                <h2 className="form-title mb-lg">Analyser un contenu</h2>

                {/* Tabs */}
                <div className="tabs mb-lg">
                    <button
                        className={`tab ${activeTab === 'email' ? 'active' : ''}`}
                        onClick={() => setActiveTab('email')}
                        disabled={isAnalyzing}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round" />
                        </svg>
                        Analyser un Email
                    </button>

                    <button
                        className={`tab ${activeTab === 'url' ? 'active' : ''}`}
                        onClick={() => setActiveTab('url')}
                        disabled={isAnalyzing}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M10 13C10.4295 13.5741 10.9774 14.0492 11.6066 14.3929C12.2357 14.7367 12.9315 14.9411 13.6467 14.9923C14.3618 15.0435 15.0796 14.9403 15.7513 14.6897C16.4231 14.4392 17.0331 14.047 17.54 13.54L20.54 10.54C21.4508 9.59698 21.9548 8.33398 21.9434 7.02299C21.932 5.71201 21.4061 4.45794 20.4791 3.53091C19.5521 2.60388 18.298 2.078 16.987 2.06658C15.676 2.05517 14.413 2.55918 13.47 3.47L11.75 5.18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M14 11C13.5705 10.4259 13.0226 9.95083 12.3934 9.60707C11.7642 9.26331 11.0685 9.05889 10.3533 9.00768C9.63819 8.95646 8.92037 9.05966 8.24861 9.31023C7.57685 9.5608 6.96684 9.95303 6.45996 10.46L3.45996 13.46C2.54917 14.403 2.04516 15.666 2.05657 16.977C2.06798 18.288 2.59387 19.542 3.52091 20.4691C4.44794 21.3961 5.70201 21.922 7.01299 21.9334C8.32398 21.9448 9.58698 21.4408 10.53 20.53L12.24 18.82" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        Analyser une URL
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit}>
                    {activeTab === 'email' ? (
                        <div className="form-group mb-lg">
                            <label htmlFor="email-input" className="form-label">
                                Contenu de l'email
                            </label>
                            <textarea
                                id="email-input"
                                className="textarea"
                                placeholder="Collez ici le contenu de l'email suspect...&#10;&#10;Exemple:&#10;From: support@paypa1.com&#10;Subject: Urgent: Verify your account&#10;&#10;Dear user,&#10;Your account has been locked. Click here to verify..."
                                value={emailContent}
                                onChange={(e) => setEmailContent(e.target.value)}
                                disabled={isAnalyzing}
                            />
                            <div style={{ marginTop: '1rem', textAlign: 'center' }}>
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={onSwitchToGmail}
                                    style={{ fontSize: '0.9rem' }}
                                >
                                    Ou sélectionner depuis Gmail
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="form-group mb-lg">
                            <label htmlFor="url-input" className="form-label">
                                URL à analyser
                            </label>
                            <input
                                id="url-input"
                                type="text"
                                className="input"
                                placeholder="https://exemple-suspect.com/verify-account"
                                value={urlContent}
                                onChange={(e) => setUrlContent(e.target.value)}
                                disabled={isAnalyzing}
                            />
                            <p className="input-hint">
                                Entrez l'URL complète incluant http:// ou https://
                            </p>
                        </div>
                    )}

                    {/* Action buttons */}
                    <div className="form-actions">
                        <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={handleClear}
                            disabled={isAnalyzing}
                        >
                            Effacer
                        </button>

                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={isAnalyzing}
                        >
                            {isAnalyzing ? (
                                <>
                                    <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '3px' }}></div>
                                    <span>Analyse en cours...</span>
                                </>
                            ) : (
                                <>
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeWidth="2" strokeLinecap="round" />
                                    </svg>
                                    <span>Analyser</span>
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AnalysisForm;
