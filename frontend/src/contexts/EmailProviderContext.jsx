import React, { createContext, useState, useContext, useEffect } from 'react';
import { useAuth } from './AuthContext';

const EmailProviderContext = createContext(null);

export const useEmailProvider = () => {
    const context = useContext(EmailProviderContext);
    if (!context) {
        throw new Error('useEmailProvider must be used within an EmailProviderProvider');
    }
    return context;
};

export const EmailProviderProvider = ({ children }) => {
    const { user, token } = useAuth();
    const [selectedProvider, setSelectedProvider] = useState(null);
    const [connectedProviders, setConnectedProviders] = useState([]);
    const [loading, setLoading] = useState(false);

    // Load connected providers when user changes
    useEffect(() => {
        if (user && token) {
            fetchConnectedProviders();
            loadProviderCredentials();
        } else {
            setConnectedProviders([]);
            setSelectedProvider(null);
        }
    }, [user, token]);

    // Check for OAuth callback
    useEffect(() => {
        // Only process callback if user and token are available
        if (!user || !token) return;
        
        const urlParams = new URLSearchParams(window.location.search);
        const authSuccess = urlParams.get('auth');
        const provider = urlParams.get('provider');
        const credsEncoded = urlParams.get('creds');

        if (authSuccess === 'success' && provider && credsEncoded) {
            handleOAuthCallback(provider, credsEncoded);
        } else if (authSuccess === 'error') {
            const errorMsg = urlParams.get('message') || 'Unknown error';
            const errorProvider = urlParams.get('provider') || 'email provider';
            console.error(`${errorProvider} authentication failed:`, decodeURIComponent(errorMsg));
            alert(`Erreur d'authentification ${errorProvider}: ${decodeURIComponent(errorMsg)}`);
            // Clean up URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }, [user, token]); // Add dependencies

    const fetchConnectedProviders = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/email/providers/connected', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setConnectedProviders(data.connected_providers || []);
                
                // Set first connected provider as selected if none selected
                if (!selectedProvider && data.connected_providers.length > 0) {
                    setSelectedProvider(data.connected_providers[0]);
                }
            }
        } catch (err) {
            console.error('Failed to fetch connected providers:', err);
        }
    };

    const handleOAuthCallback = async (provider, credsEncoded) => {
        setLoading(true);
        
        try {
            // Decode URL-safe base64 credentials
            // Convert URL-safe base64 to standard base64
            const standardBase64 = credsEncoded.replace(/-/g, '+').replace(/_/g, '/');
            // Add padding if needed
            const padding = '='.repeat((4 - (standardBase64.length % 4)) % 4);
            const credsJson = atob(standardBase64 + padding);
            const credentials = JSON.parse(credsJson);

            console.log(`Processing OAuth callback for provider: ${provider}, user: ${user.username}`);

            // Store credentials in backend
            const response = await fetch(`http://localhost:8000/api/email/providers/store-credentials?provider=${provider}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(credentials)
            });

            if (response.ok) {
                console.log(`Successfully stored ${provider} credentials for user ${user.username}`);
                
                // Also store in localStorage for quick access (user-specific)
                const userId = user.id || user.username;
                localStorage.setItem(`${provider}_credentials_${userId}`, JSON.stringify(credentials));

                // Update connected providers
                await fetchConnectedProviders();
                setSelectedProvider(provider);

                // Clean up URL
                window.history.replaceState({}, document.title, window.location.pathname);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to store credentials');
            }
        } catch (err) {
            console.error('Failed to process OAuth callback:', err);
            alert(`Erreur lors de la connexion ${provider}: ${err.message}`);
            // Clean up URL even on error
            window.history.replaceState({}, document.title, window.location.pathname);
        } finally {
            setLoading(false);
        }
    };

    const loadProviderCredentials = () => {
        if (!user) return;

        const userId = user.id || user.username;
        const providers = ['gmail', 'outlook', 'yahoo'];
        
        providers.forEach(provider => {
            const stored = localStorage.getItem(`${provider}_credentials_${userId}`);
            if (stored && !connectedProviders.includes(provider)) {
                setConnectedProviders(prev => [...prev, provider]);
            }
        });
    };

    const getProviderCredentials = (provider) => {
        if (!user) return null;
        
        const userId = user.id || user.username;
        const stored = localStorage.getItem(`${provider}_credentials_${userId}`);
        
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (err) {
                console.error('Failed to parse credentials:', err);
                return null;
            }
        }
        
        return null;
    };

    const fetchEmails = async (provider, maxResults = 20) => {
        try {
            const response = await fetch('http://localhost:8000/api/email/emails', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    provider: provider || selectedProvider,
                    max_results: maxResults
                })
            });

            if (!response.ok) {
                throw new Error('Failed to fetch emails');
            }

            return await response.json();
        } catch (err) {
            console.error('Failed to fetch emails:', err);
            throw err;
        }
    };

    const getEmailContent = async (provider, messageId) => {
        try {
            const response = await fetch('http://localhost:8000/api/email/email/content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    provider: provider || selectedProvider,
                    message_id: messageId
                })
            });

            if (!response.ok) {
                throw new Error('Failed to fetch email content');
            }

            return await response.json();
        } catch (err) {
            console.error('Failed to fetch email content:', err);
            throw err;
        }
    };

    const disconnectProvider = async (provider) => {
        try {
            const response = await fetch('http://localhost:8000/api/email/providers/disconnect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ provider })
            });

            if (response.ok) {
                // Remove from localStorage
                const userId = user.id || user.username;
                localStorage.removeItem(`${provider}_credentials_${userId}`);

                // Update state
                setConnectedProviders(prev => prev.filter(p => p !== provider));
                
                if (selectedProvider === provider) {
                    setSelectedProvider(connectedProviders[0] || null);
                }
            }
        } catch (err) {
            console.error('Failed to disconnect provider:', err);
            throw err;
        }
    };

    const value = {
        selectedProvider,
        setSelectedProvider,
        connectedProviders,
        loading,
        fetchEmails,
        getEmailContent,
        disconnectProvider,
        getProviderCredentials
    };

    return (
        <EmailProviderContext.Provider value={value}>
            {children}
        </EmailProviderContext.Provider>
    );
};
