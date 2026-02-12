import React from 'react';

function SummaryCard({ results, onNewAnalysis }) {
  return (
    <div className="glass-card summary-card">
      <div className="summary-header">
        <h2 className="bulk-analysis-title">Résumé de l'Analyse</h2>
        <button className="btn btn-secondary btn-sm" onClick={onNewAnalysis}>
          Nouvelle Analyse
        </button>
      </div>

      <div className="summary-stats">
        <div className="summary-stat">
          <div className="stat-value">{results.total}</div>
          <div className="stat-label">Emails Analysés</div>
        </div>
        <div className="summary-stat safe">
          <div className="stat-value">{results.summary.safe}</div>
          <div className="stat-label">Sûrs</div>
        </div>
        <div className="summary-stat suspicious">
          <div className="stat-value">{results.summary.suspicious}</div>
          <div className="stat-label">Suspects</div>
        </div>
        <div className="summary-stat dangerous">
          <div className="stat-value">{results.summary.dangerous}</div>
          <div className="stat-label">Dangereux</div>
        </div>
      </div>

      <div className="summary-details">
        <div className="detail-item">
          <span className="detail-label">Menaces Détectées:</span>
          <span className="detail-value">{results.summary.threats_detected}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Confiance Moyenne:</span>
          <span className="detail-value">{results.summary.average_confidence}%</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Temps de Traitement:</span>
          <span className="detail-value">{results.processing_time}s</span>
        </div>
      </div>
    </div>
  );
}

export default SummaryCard;
