import React from 'react';
import ResultItem from './ResultItem';

function ResultsList({ results, getThreatColor, getThreatIcon }) {
  return (
    <div className="glass-card results-list-card">
      <h3 className="results-title">Résultats Détaillés</h3>
      <div className="results-list">
        {results.results.map((result) => (
          <ResultItem
            key={result.index}
            result={result}
            getThreatColor={getThreatColor}
            getThreatIcon={getThreatIcon}
          />
        ))}
      </div>
    </div>
  );
}

export default ResultsList;
