import React from 'react';
import SummaryCard from './SummaryCard';
import ResultsList from './ResultsList';

function BulkAnalysisResults({ results, onNewAnalysis, getThreatColor, getThreatIcon }) {
  return (
    <div className="results-container">
      <SummaryCard results={results} onNewAnalysis={onNewAnalysis} />
      <ResultsList 
        results={results} 
        getThreatColor={getThreatColor} 
        getThreatIcon={getThreatIcon} 
      />
    </div>
  );
}

export default BulkAnalysisResults;
