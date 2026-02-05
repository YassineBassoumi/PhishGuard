import React, { useState, useEffect } from 'react';
import './EmailList.css';
import { useAuth } from '../contexts/AuthContext';
import { useEmailProvider } from '../contexts/EmailProviderContext';

const MultiProviderEmailList = ({ onSelectEmail, onSelectMultiple }) => {
    const { token } = useAuth();
    const { selectedProvider, connectedProviders, setSelectedProvider } = useEmailProvider();
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedEmailId, setSelectedEmailId] = useState(null);
    const [selectedEmails, setSelectedEmails] = useState([]);
    const [multiSelectMode, setMultiSelectMode] = useState(false);

    useEffect(() => {
        if (selectedProvider && connectedProviders.includes(selectedProvider)) {
            fetchEmails();
        }
    }, [selectedProvider]);

    const fetchEmails = async () => {
        if (!selectedProvider) return;
        
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/api/email/emails', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    provider: selectedProvider,
                    max_results: 20
                })
            });

            if (!response.ok) {
                throw new Error('Failed to fetch emails');
            }

            const data = await response.json();
            setEmails(data.emails || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleEmailClick = async (email) => {
        if (multiSelectMode) {
            toggleEmailSelection(email);
        } else {
            setSelectedEmailId(email.id);
            
            try {
                const response = await fetch('http://localhost:8000/api/email/email/content', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        provider: selectedProvider,
                        message_id: email.id
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch email content');
                }

                const data = await response.json();
                onSelectEmail(data.content, email);
            } catch (err) {
                setError(err.message);
            }
        }
    };

    const toggleEmailSelection = (email) => {
        setSelectedEmails(prev => {
            const isSelected = prev.some(e => e.id === email.id);
            if (isSelected) {
                return prev.filter(e => e.id !== email.id);
            } else {
                return [...prev, email];
            }
        });
    };

    const toggleMultiSelectMode = () => {
        setMultiSelectMode(!multiSelectMode);
        setSelectedEmails([]);
    };

    const handleAnalyzeSelected = async () => {
        if (selectedEmails.length === 0) {
            alert('Veuillez sélectionner au moins un email');
            return;
        }

        setLoading(true);
        try {
            const emailContents = await Promise.all(
                selectedEmails.map(async (email) => {
                    const response = await fetch('http://localhost:8000/api/email/email/content', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            provider: selectedProvider,
                            message_id: email.id
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to fetch email ${email.id}`);
                    }

                    const data = await response.json();
                    return data.content;
                })
            );

            if (onSelectMultiple) {
                onSelectMultiple(emailContents);
            }
        } catch (err) {
            setError(err.message);
            alert('Erreur lors de la récupération des emails: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const selectAll = () => {
        setSelectedEmails([...emails]);
    };

    const deselectAll = () => {
        setSelectedEmails([]);
    };

    const getProviderIcon = (provider) => {
        switch(provider) {
            case 'gmail':
                return '📧';
            case 'outlook':
                return '📨';
            case 'yahoo':
                return '📬';
            default:
                return '✉️';
        }
    };

    if (loading && emails.length === 0) {
        return (
            <div className="email-list-container">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Chargement de vos emails...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="email-list-container">
                <div className="error-state">
                    <p>Erreur: {error}</p>
                    <button className="btn btn-primary" onClick={fetchEmails}>
                        Réessayer
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="email-list-container fade-in-up">
            <div className="glass-card">
                {/* Provider Tabs */}
                {connectedProviders.length > 1 && (
                    <div className="provider-tabs" style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem' }}>
                        {connectedProviders.map(provider => (
                            <button
                                key={provider}
                                className={`btn ${selectedProvider === provider ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                                onClick={() => setSelectedProvider(provider)}
                                style={{ textTransform: 'capitalize' }}
                            >
                                {getProviderIcon(provider)} {provider}
                            </button>
                        ))}
                    </div>
                )}

                <div className="email-list-header">
                    <h2 className="form-title">
                        {getProviderIcon(selectedProvider)} Vos Emails {selectedProvider && `(${selectedProvider.charAt(0).toUpperCase() + selectedProvider.slice(1)})`}
                    </h2>
                    <div className="header-actions">
                        <button 
                            className="btn btn-secondary btn-sm"
                            onClick={() => window.location.href = '/?view=providers'}
                            title="Gérer les fournisseurs d'email"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M12 5V19M5 12H19" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            Ajouter un compte
                        </button>
                        <button 
                            className={`btn btn-sm ${multiSelectMode ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={toggleMultiSelectMode}
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M9 11L12 14L22 4M21 12V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H16" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            {multiSelectMode ? 'Mode Sélection' : 'Sélection Multiple'}
                        </button>
                        <button className="btn btn-secondary btn-sm" onClick={fetchEmails}>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M21.5 2V6M21.5 6H17.5M21.5 6L18.5 3C17.2 1.8 15.5 1 13.5 1C9.4 1 6 4.4 6 8.5C6 12.6 9.4 16 13.5 16C16.8 16 19.6 13.8 20.5 10.8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            Actualiser
                        </button>
                    </div>
                </div>

                {multiSelectMode && (
                    <div className="multi-select-toolbar">
                        <div className="selection-info">
                            <span className="selection-count">
                                {selectedEmails.length} email{selectedEmails.length !== 1 ? 's' : ''} sélectionné{selectedEmails.length !== 1 ? 's' : ''}
                            </span>
                        </div>
                        <div className="selection-actions">
                            <button className="btn-link" onClick={selectAll}>
                                Tout sélectionner
                            </button>
                            <button className="btn-link" onClick={deselectAll}>
                                Tout désélectionner
                            </button>
                            <button 
                                className="btn btn-primary btn-sm"
                                onClick={handleAnalyzeSelected}
                                disabled={selectedEmails.length === 0 || loading}
                            >
                                {loading ? (
                                    <>
                                        <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                                        <span>Chargement...</span>
                                    </>
                                ) : (
                                    <>
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                            <path d="M9 12H15M9 16H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17 21Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                        </svg>
                                        <span>Analyser en Masse</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {emails.length === 0 ? (
                    <div className="empty-state">
                        <p>Aucun email trouvé</p>
                    </div>
                ) : (
                    <div className="email-list">
                        {emails.map((email) => {
                            const isSelected = selectedEmails.some(e => e.id === email.id);
                            return (
                                <div
                                    key={email.id}
                                    className={`email-item ${selectedEmailId === email.id ? 'selected' : ''} ${isSelected ? 'multi-selected' : ''}`}
                                    onClick={() => handleEmailClick(email)}
                                >
                                    {multiSelectMode && (
                                        <div className="email-checkbox">
                                            <input 
                                                type="checkbox" 
                                                checked={isSelected}
                                                onChange={() => {}}
                                                onClick={(e) => e.stopPropagation()}
                                            />
                                        </div>
                                    )}
                                    <div className="email-item-content">
                                        <div className="email-item-header">
                                            <span className="email-from">{email.from}</span>
                                            <span className="email-date">{new Date(email.date).toLocaleDateString()}</span>
                                        </div>
                                        <div className="email-subject">{email.subject}</div>
                                        <div className="email-snippet">{email.snippet}</div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default MultiProviderEmailList;
