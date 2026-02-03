import React, { useState } from 'react';
import './App.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Hero from './components/Hero';
import AnalysisForm from './components/AnalysisForm';
import ResultsDisplay from './components/ResultsDisplay';
import Features from './components/Features';
import GmailAuth from './components/GmailAuth';
import EmailList from './components/EmailList';
import Dashboard from './components/Dashboard';
import BulkAnalysis from './components/BulkAnalysis';
import Login from './components/Login';
import Register from './components/Register';
import UserProfile from './components/UserProfile';

function AppContent() {
  const { isAuthenticated, loading: authLoading, token } = useAuth();
  const [results, setResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [viewMode, setViewMode] = useState('manual'); // 'manual', 'gmail', 'dashboard', 'bulk', or 'profile'
  const [authView, setAuthView] = useState('login'); // 'login' or 'register'
  const [gmailCredentials, setGmailCredentials] = useState(null);
  const [bulkEmails, setBulkEmails] = useState(null);

  // Check for stored credentials on mount
  React.useEffect(() => {
    // First check URL for auth success
    const urlParams = new URLSearchParams(window.location.search);
    const authSuccess = urlParams.get('auth');
    
    if (authSuccess === 'success') {
      setViewMode('gmail');
    }
    
    // Then check for stored credentials
    const storedCredentials = localStorage.getItem('gmail_credentials');
    if (storedCredentials) {
      try {
        const credentials = JSON.parse(storedCredentials);
        setGmailCredentials(credentials);
      } catch (err) {
        localStorage.removeItem('gmail_credentials');
      }
    }
  }, []);

  const handleAnalysis = async (type, content) => {
    setIsAnalyzing(true);
    setResults(null);

    try {
      // Determine API endpoint based on type
      const apiUrl = type === 'email'
        ? 'http://localhost:8000/api/analyze-email'
        : 'http://localhost:8000/api/analyze-url';

      // Prepare request body
      const requestBody = type === 'email'
        ? { content: content }
        : { url: content };

      // Call backend API with authentication
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      // Check if response is ok
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      // Parse response
      const data = await response.json();

      // Set results
      setResults(data);
    } catch (error) {
      console.error('Analysis failed:', error);

      // Show error to user
      setResults({
        type: type,
        content: content.substring(0, 100) + '...',
        threatLevel: 'safe',
        confidence: 0,
        features: ['Analysis failed: ' + error.message],
        recommendations: ['Please try again or contact support']
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGmailAuth = (credentials) => {
    setGmailCredentials(credentials);
    setViewMode('gmail');
  };

  const handleEmailSelect = (content, emailData) => {
    // Analyze the selected email
    handleAnalysis('email', content);
  };

  const handleMultipleEmailsSelect = (emailContents) => {
    // Switch to bulk analysis view with pre-filled emails
    setViewMode('bulk');
    setBulkEmails(emailContents);
  };

  const handleSwitchToGmail = () => {
    setViewMode('gmail');
  };

  const handleSwitchToManual = () => {
    setViewMode('manual');
    setResults(null);
  };

  const handleSwitchToDashboard = () => {
    setViewMode('dashboard');
    setResults(null);
  };

  const handleSwitchToBulk = () => {
    setViewMode('bulk');
    setResults(null);
  };

  const handleSwitchToProfile = () => {
    setViewMode('profile');
    setResults(null);
  };

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="app">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div className="spinner" style={{ width: '48px', height: '48px', borderWidth: '4px' }}></div>
          <p style={{ color: 'var(--text-muted)' }}>Chargement...</p>
        </div>
      </div>
    );
  }

  // Show login/register if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="app">
        <Hero />
        <main className="container">
          {authView === 'login' ? (
            <Login onSwitchToRegister={() => setAuthView('register')} />
          ) : (
            <Register onSwitchToLogin={() => setAuthView('login')} />
          )}
        </main>
        <footer style={{
          textAlign: 'center',
          padding: '3rem 1rem',
          marginTop: '4rem',
          borderTop: '1px solid rgba(148, 163, 184, 0.1)'
        }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            © 2026 PhishGuard AI - Advanced Phishing Detection System
          </p>
        </footer>
      </div>
    );
  }

  return (
    <div className="app">
      <Hero />

      <main className="container">
        {/* Navigation Tabs */}
        <div className="view-tabs">
          <button 
            className={`view-tab ${viewMode === 'manual' ? 'active' : ''}`}
            onClick={handleSwitchToManual}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeWidth="2" strokeLinecap="round" />
            </svg>
            Analyser
          </button>
          <button 
            className={`view-tab ${viewMode === 'bulk' ? 'active' : ''}`}
            onClick={handleSwitchToBulk}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 12H15M9 16H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17 21Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Analyse en Masse
          </button>
          <button 
            className={`view-tab ${viewMode === 'dashboard' ? 'active' : ''}`}
            onClick={handleSwitchToDashboard}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 13H11V3H3V13ZM3 21H11V15H3V21ZM13 21H21V11H13V21ZM13 3V9H21V3H13Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Tableau de Bord
          </button>
          {gmailCredentials && (
            <button 
              className={`view-tab ${viewMode === 'gmail' ? 'active' : ''}`}
              onClick={() => setViewMode('gmail')}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 8L10.89 13.26C11.25 13.48 11.75 13.48 12.11 13.26L20 8M5 19H19C20.1 19 21 18.1 21 17V7C21 5.9 20.1 5 19 5H5C3.9 5 3 5.9 3 7V17C3 18.1 3.9 19 5 19Z" strokeWidth="2" strokeLinecap="round" />
              </svg>
              Gmail
            </button>
          )}
          <button 
            className={`view-tab ${viewMode === 'profile' ? 'active' : ''}`}
            onClick={handleSwitchToProfile}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Profil
          </button>
        </div>

        <section className="mb-xl">
          {viewMode === 'profile' ? (
            <UserProfile />
          ) : viewMode === 'dashboard' ? (
            <Dashboard />
          ) : viewMode === 'bulk' ? (
            <BulkAnalysis initialEmails={bulkEmails} />
          ) : viewMode === 'manual' ? (
            <AnalysisForm 
              onAnalyze={handleAnalysis} 
              isAnalyzing={isAnalyzing}
              onSwitchToGmail={handleSwitchToGmail}
            />
          ) : (
            <>
              {!gmailCredentials ? (
                <GmailAuth onAuthenticated={handleGmailAuth} />
              ) : (
                <EmailList 
                  credentials={gmailCredentials}
                  onSelectEmail={handleEmailSelect}
                  onSelectMultiple={handleMultipleEmailsSelect}
                />
              )}
            </>
          )}
        </section>

        {(results || isAnalyzing) && viewMode !== 'dashboard' && viewMode !== 'bulk' && viewMode !== 'profile' && (
          <section className="mb-xl">
            <ResultsDisplay results={results} isAnalyzing={isAnalyzing} />
          </section>
        )}

        {viewMode === 'manual' && <Features />}
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '3rem 1rem',
        marginTop: '4rem',
        borderTop: '1px solid rgba(148, 163, 184, 0.1)'
      }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          © 2026 PhishGuard AI - Advanced Phishing Detection System
        </p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
