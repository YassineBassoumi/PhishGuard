import React from 'react';
import AnalysisForm from './AnalysisForm';
import ResultsDisplay from './ResultsDisplay';
import EmailProviderSelector from './EmailProviderSelector';
import MultiProviderEmailList from './MultiProviderEmailList';
import Dashboard from './Dashboard';
import BulkAnalysis from './BulkAnalysis';
import UserProfile from './UserProfile';

function MainContent({ 
  viewMode, 
  connectedProviders,
  onAnalyze,
  isAnalyzing,
  results,
  onSwitchToEmail,
  onSelectEmail,
  onSelectMultiple,
  bulkEmails,
  token
}) {
  return (
    <>
      <section className="mb-xl">
        {viewMode === 'profile' ? (
          <UserProfile />
        ) : viewMode === 'dashboard' ? (
          <Dashboard />
        ) : viewMode === 'bulk' ? (
          <BulkAnalysis initialEmails={bulkEmails} />
        ) : viewMode === 'providers' ? (
          <EmailProviderSelector />
        ) : viewMode === 'manual' ? (
          <AnalysisForm 
            onAnalyze={onAnalyze} 
            isAnalyzing={isAnalyzing}
            onSwitchToGmail={onSwitchToEmail}
            token={token}
          />
        ) : (
          <>
            {connectedProviders.length === 0 ? (
              <EmailProviderSelector />
            ) : (
              <MultiProviderEmailList 
                onSelectEmail={onSelectEmail}
                onSelectMultiple={onSelectMultiple}
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
    </>
  );
}

export default MainContent;
