import React from 'react';

function ResultItem({ result, getThreatColor, getThreatIcon }) {
  const getThreatLabel = (level) => {
    switch (level) {
      case 'safe': return 'SÛR';
      case 'suspicious': return 'SUSPECT';
      case 'dangerous': return 'DANGEREUX';
      default: return level.toUpperCase();
    }
  };

  return (
    <div 
      className="result-item"
      style={{ borderLeftColor: getThreatColor(result.threat_level) }}
    >
      <div className="result-header">
        <div className="result-number">
          <span 
            className="threat-icon"
            style={{ 
              background: getThreatColor(result.threat_level),
              color: 'white'
            }}
          >
            {getThreatIcon(result.threat_level)}
          </span>
          <span>Email {result.index + 1}</span>
        </div>
        <span 
          className="threat-badge"
          style={{ 
            background: getThreatColor(result.threat_level)
          }}
        >
          {getThreatLabel(result.threat_level)}
        </span>
      </div>

      <div className="result-content">
        <p className="content-preview">{result.content_preview}</p>
        
        <div className="confidence-bar">
          <span className="confidence-label">Confiance: {result.confidence.toFixed(1)}%</span>
          <div className="confidence-progress">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${result.confidence}%`,
                background: getThreatColor(result.threat_level)
              }}
            ></div>
          </div>
        </div>

        {result.features.length > 0 && (
          <div className="features-section">
            <strong>Indicateurs:</strong>
            <ul className="features-list">
              {result.features.slice(0, 3).map((feature, i) => (
                <li key={i}>{feature}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultItem;
