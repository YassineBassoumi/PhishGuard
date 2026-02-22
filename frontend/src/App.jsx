import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { EmailProviderProvider, useEmailProvider } from './contexts/EmailProviderContext';
import Sidebar from './components/Sidebar';
import LoadingScreen from './components/LoadingScreen';
import AuthView from './components/AuthView';
import ResetPassword from './components/ResetPassword';
import VerifyEmail from './components/VerifyEmail';
import AccountSecured from './pages/AccountSecured';
import NotificationsPage from './pages/NotificationsPage';
import NotificationCenter from './components/NotificationCenter';
import MainContent from './components/MainContent';
import Footer from './components/Footer';
import { AdminPanel } from './components/admin/AdminPanel';
import WelcomeRedirect from './components/WelcomeRedirect';

function AppContent() {
  const { isAuthenticated, loading: authLoading, token, user, logout } = useAuth();
  const { connectedProviders } = useEmailProvider();
  const [results, setResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [viewMode, setViewMode] = useState('manual');
  const [bulkEmails, setBulkEmails] = useState(null);
  const [showWelcomeRedirect, setShowWelcomeRedirect] = useState(false);
  const [redirectProvider, setRedirectProvider] = useState(null);

  // Check for OAuth callback and switch to email view
  React.useEffect(() => {
    if (!user) return;

    const urlParams = new URLSearchParams(window.location.search);
    const authSuccess = urlParams.get('auth');
    const viewParam = urlParams.get('view');
    
    // Check for first login
    const isFirstLogin = localStorage.getItem('is_first_login');
    const suggestedProvider = localStorage.getItem('first_login_provider');
    
    if (isFirstLogin === 'true' && suggestedProvider) {
      // Clear the first login flag
      localStorage.removeItem('is_first_login');
      
      // Redirect to email provider setup
      setViewMode('providers');
      setRedirectProvider(suggestedProvider);
      setShowWelcomeRedirect(true);
      
      // Auto-trigger OAuth flow after countdown
      setTimeout(async () => {
        try {
          // Get auth URL from backend
          const response = await fetch(`http://localhost:8000/api/email/${suggestedProvider}/auth`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const data = await response.json();
            // Redirect to OAuth
            window.location.href = data.auth_url;
          }
        } catch (error) {
          console.error('Auto-connect failed:', error);
          setShowWelcomeRedirect(false);
        }
      }, 3000); // 3 second countdown
    } else if (authSuccess === 'success') {
      setViewMode('email');
    } else if (viewParam === 'providers') {
      setViewMode('providers');
    }
  }, [user, token]);

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

  const handleEmailSelect = (content) => {
    // Analyze the selected email
    handleAnalysis('email', content);
  };

  const handleMultipleEmailsSelect = (emailContents) => {
    // Switch to bulk analysis view with pre-filled emails
    setViewMode('bulk');
    setBulkEmails(emailContents);
  };

  const handleSwitchToEmail = () => {
    setViewMode('email');
  };

  const handleViewChange = (view) => {
    setViewMode(view);
    setResults(null);
  };

  const handleBackToApp = () => {
    setViewMode('manual');
  };

  if (authLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <AuthView />;
  }

  // Show admin panel if user selected admin view
  if (viewMode === 'admin') {
    return (
      <div className="admin-panel-root">
        <AdminPanel 
          user={user}
          token={token}
          onLogout={logout}
          onBackToApp={handleBackToApp}
        />
      </div>
    );
  }

  return (
    <div className="app app-with-sidebar">
      {showWelcomeRedirect && redirectProvider && (
        <WelcomeRedirect 
          provider={redirectProvider}
          onClose={() => setShowWelcomeRedirect(false)}
        />
      )}
      
      <Sidebar 
        viewMode={viewMode}
        onViewChange={handleViewChange}
        user={user}
      />
      <main className="main-content-wrapper">
        <div className="main-header">
          <h1 className="main-greeting">
            Bonjour, {user?.email?.split('@')[0] || 'User'} 👋
          </h1>
          <NotificationCenter />
        </div>
        <MainContent 
          viewMode={viewMode}
          connectedProviders={connectedProviders}
          onAnalyze={handleAnalysis}
          isAnalyzing={isAnalyzing}
          results={results}
          onSwitchToEmail={handleSwitchToEmail}
          onSelectEmail={handleEmailSelect}
          onSelectMultiple={handleMultipleEmailsSelect}
          bulkEmails={bulkEmails}
          token={token}
        />
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <EmailProviderProvider>
        <Routes>
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/account-secured" element={<AccountSecured />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/*" element={<AppContent />} />
        </Routes>
      </EmailProviderProvider>
    </AuthProvider>
  );
}

export default App;
