import React, { useState, useEffect, useCallback } from 'react';
import './EmailProviderSelector.css';
import { useAuth } from '../contexts/AuthContext';

const EmailProviderSelector = ({ onProviderConnected }) => {
    const { token } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [connectedProviders, setConnectedProviders] = useState([]);
    const [suggestedProvider, setSuggestedProvider] = useState(null);

    const fetchConnectedProviders = useCallback(async () => {
        try {
            const response = await fetch('http://localhost:8000/api/email/providers/connected', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setConnectedProviders(data.connected_providers || []);
            }
        } catch (err) {
            console.error('Failed to fetch connected providers:', err);
        }
    }, [token]);

    useEffect(() => {
        fetchConnectedProviders();
        
        // Check for suggested provider from first login
        const suggested = localStorage.getItem('first_login_provider');
        if (suggested) {
            setSuggestedProvider(suggested);
            // Clear it after reading
            localStorage.removeItem('first_login_provider');
        }
    }, [fetchConnectedProviders]);

    const handleProviderConnect = async (provider) => {
        setLoading(true);
        setError(null);

        try {
            // Use the unified API endpoint
            const response = await fetch(`http://localhost:8000/api/email/${provider}/auth`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to initiate authentication');
            }

            const data = await response.json();
            
            // Call the callback if provided
            if (onProviderConnected) {
                onProviderConnected(provider);
            }
            
            // Redirect to OAuth (will come back with provider parameter)
            window.location.href = data.auth_url;
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    const providers = [
        {
            id: 'gmail',
            name: 'Gmail',
            description: 'Google Gmail',
            icon: (
                <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
            ),
            gradient: 'gmail-gradient',
            available: true
        },
        {
            id: 'outlook',
            name: 'Outlook',
            description: 'Microsoft Outlook/Hotmail',
            icon: (
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                    <rect width="64" height="64" rx="8" fill="#0078D4"/>
                    <circle cx="32" cy="32" r="18" fill="white"/>
                    <circle cx="32" cy="32" r="12" fill="#0078D4"/>
                    <circle cx="32" cy="32" r="6" fill="white"/>
                </svg>
            ),
            gradient: 'outlook-gradient',
            available: true
        }
    ];

    return (
        <div className="email-provider-selector fade-in-up">
            <div className="glass-card">
                <h2 className="form-title">Connectez votre Email</h2>
                <p className="provider-description">
                    Sélectionnez votre fournisseur d'email pour analyser vos messages
                </p>

                {error && (
                    <div className="error-message">
                        <p>{error}</p>
                    </div>
                )}

                <div className="provider-grid">
                    {providers.map((provider) => {
                        const isConnected = connectedProviders.includes(provider.id);
                        const isSuggested = suggestedProvider === provider.id;
                        
                        return (
                            <button
                                key={provider.id}
                                className={`provider-btn ${isConnected ? 'connected' : ''} ${!provider.available ? 'disabled' : ''} ${isSuggested ? 'suggested' : ''}`}
                                onClick={() => provider.available && handleProviderConnect(provider.id)}
                                disabled={loading || !provider.available}
                            >
                                <div className={`provider-icon ${provider.gradient}`}>
                                    {provider.icon}
                                </div>
                                <span className="provider-name">{provider.name}</span>
                                <span className="provider-desc">{provider.description}</span>
                                
                                {isSuggested && !isConnected && (
                                    <div className="suggested-badge">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                            <path d="M13 2L3 14h8l-1 8 10-12h-8l1-8z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                        </svg>
                                        Recommandé
                                    </div>
                                )}
                                
                                {isConnected && (
                                    <div className="connected-badge">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                            <path d="M20 6L9 17L4 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                        </svg>
                                        Connecté
                                    </div>
                                )}
                                
                                {!provider.available && (
                                    <div className="coming-soon-badge">
                                        Bientôt disponible
                                    </div>
                                )}
                            </button>
                        );
                    })}
                </div>

                <p className="provider-note">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12 15V17M12 11V13M12 7V9M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21Z" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Nous n'accédons qu'à vos emails en lecture seule. Vos données restent privées et sécurisées.
                </p>
            </div>
        </div>
    );
};

export default EmailProviderSelector;
