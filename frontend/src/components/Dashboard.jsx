import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import HistoryFilters from './HistoryFilters';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
    const { token } = useAuth();
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [distribution, setDistribution] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        type: '',
        threatLevel: '',
        startDate: '',
        endDate: '',
        limit: 10
    });
    const [searchQuery, setSearchQuery] = useState('');
    const [filteredHistory, setFilteredHistory] = useState([]);

    useEffect(() => {
        fetchDashboardData();
        // Refresh every 30 seconds
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, [filters]);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            
            // Build query params for history
            const historyParams = new URLSearchParams();
            historyParams.append('limit', filters.limit.toString());
            if (filters.type) historyParams.append('analysis_type', filters.type);
            if (filters.threatLevel) historyParams.append('threat_level', filters.threatLevel);
            if (filters.startDate) historyParams.append('start_date', filters.startDate);
            if (filters.endDate) historyParams.append('end_date', filters.endDate);
            
            // Fetch all data in parallel with auth token
            const headers = {
                'Authorization': `Bearer ${token}`
            };
            
            const [statsRes, historyRes, distributionRes] = await Promise.all([
                fetch('http://localhost:8000/api/stats', { headers }),
                fetch(`http://localhost:8000/api/history?${historyParams.toString()}`, { headers }),
                fetch('http://localhost:8000/api/threat-distribution', { headers })
            ]);

            if (!statsRes.ok || !historyRes.ok || !distributionRes.ok) {
                throw new Error('Failed to fetch dashboard data');
            }

            const statsData = await statsRes.json();
            const historyData = await historyRes.json();
            const distributionData = await distributionRes.json();

            setStats(statsData);
            setHistory(historyData.history || []);
            setFilteredHistory(historyData.history || []);
            setDistribution(distributionData);
            setError(null);
        } catch (err) {
            console.error('Dashboard fetch error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (newFilters) => {
        setFilters(newFilters);
    };

    const handleClearFilters = () => {
        setFilters({
            type: '',
            threatLevel: '',
            startDate: '',
            endDate: '',
            limit: 10
        });
    };

    const handleSearch = (query) => {
        setSearchQuery(query);
        if (!query.trim()) {
            setFilteredHistory(history);
            return;
        }

        const lowercaseQuery = query.toLowerCase();
        const filtered = history.filter(item => 
            item.content.toLowerCase().includes(lowercaseQuery) ||
            item.type.toLowerCase().includes(lowercaseQuery) ||
            item.threatLevel.toLowerCase().includes(lowercaseQuery)
        );
        setFilteredHistory(filtered);
    };

    // Update filtered history when history changes
    useEffect(() => {
        handleSearch(searchQuery);
    }, [history]);

    const getThreatIcon = (threatLevel) => {
        switch (threatLevel) {
            case 'safe':
                return '✓';
            case 'suspicious':
                return '⚠';
            case 'dangerous':
                return '✕';
            default:
                return '?';
        }
    };

    const getThreatColor = (threatLevel) => {
        switch (threatLevel) {
            case 'safe':
                return '#10b981';
            case 'suspicious':
                return '#f59e0b';
            case 'dangerous':
                return '#ef4444';
            default:
                return '#6b7280';
        }
    };

    const formatDate = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    };

    if (loading && !stats) {
        return (
            <div className="dashboard-container">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading dashboard...</p>
                </div>
            </div>
        );
    }

    if (error && !stats) {
        return (
            <div className="dashboard-container">
                <div className="error-state">
                    <p>Error loading dashboard: {error}</p>
                    <button className="btn btn-primary" onClick={fetchDashboardData}>
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    const totalThreats = distribution ? (distribution.safe + distribution.suspicious + distribution.dangerous) : 0;
    const safePercent = totalThreats > 0 ? (distribution.safe / totalThreats * 100) : 0;
    const suspiciousPercent = totalThreats > 0 ? (distribution.suspicious / totalThreats * 100) : 0;
    const dangerousPercent = totalThreats > 0 ? (distribution.dangerous / totalThreats * 100) : 0;

    return (
        <div className="dashboard-container fade-in-up">
            <div className="dashboard-header">
                <h2 className="dashboard-title">Tableau de Bord</h2>
                <button 
                    className="btn btn-secondary btn-sm"
                    onClick={fetchDashboardData}
                    disabled={loading}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M21.5 2V6M21.5 6H17.5M21.5 6L18.5 3C17.2 1.8 15.5 1 13.5 1C9.4 1 6 4.4 6 8.5C6 12.6 9.4 16 13.5 16C16.8 16 19.6 13.8 20.5 10.8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Actualiser
                </button>
            </div>

            {/* Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M9 11L12 14L22 4M21 12V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H16" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">Total Analyses</div>
                        <div className="stat-value">{stats?.totalAnalyses || 0}</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">Menaces Détectées</div>
                        <div className="stat-value">{stats?.threatsDetected || 0}</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M13 10V3L4 14H11L11 21L20 10L13 10Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">Précision</div>
                        <div className="stat-value">{stats?.accuracy || 0}%</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M12 8V12L15 15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    </div>
                    <div className="stat-content">
                        <div className="stat-label">Temps Moyen</div>
                        <div className="stat-value">{stats?.averageResponseTime || 'N/A'}</div>
                    </div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="charts-section">
                {/* Threat Distribution Chart */}
                <div className="glass-card chart-card">
                    <h3 className="chart-title">Distribution des Menaces</h3>
                    {distribution && totalThreats > 0 ? (
                        <>
                            <div className="chart-container">
                                <div className="bar-chart">
                                    <div className="bar-item">
                                        <div className="bar-label">
                                            <span className="bar-icon" style={{ color: '#10b981' }}>✓</span>
                                            Sûr
                                        </div>
                                        <div className="bar-wrapper">
                                            <div 
                                                className="bar-fill" 
                                                style={{ 
                                                    width: `${safePercent}%`,
                                                    background: '#10b981'
                                                }}
                                            ></div>
                                        </div>
                                        <div className="bar-value">{distribution.safe}</div>
                                    </div>

                                    <div className="bar-item">
                                        <div className="bar-label">
                                            <span className="bar-icon" style={{ color: '#f59e0b' }}>⚠</span>
                                            Suspect
                                        </div>
                                        <div className="bar-wrapper">
                                            <div 
                                                className="bar-fill" 
                                                style={{ 
                                                    width: `${suspiciousPercent}%`,
                                                    background: '#f59e0b'
                                                }}
                                            ></div>
                                        </div>
                                        <div className="bar-value">{distribution.suspicious}</div>
                                    </div>

                                    <div className="bar-item">
                                        <div className="bar-label">
                                            <span className="bar-icon" style={{ color: '#ef4444' }}>✕</span>
                                            Dangereux
                                        </div>
                                        <div className="bar-wrapper">
                                            <div 
                                                className="bar-fill" 
                                                style={{ 
                                                    width: `${dangerousPercent}%`,
                                                    background: '#ef4444'
                                                }}
                                            ></div>
                                        </div>
                                        <div className="bar-value">{distribution.dangerous}</div>
                                    </div>
                                </div>
                            </div>

                            {/* Donut Chart */}
                            <div className="donut-chart">
                                <svg viewBox="0 0 100 100" className="donut-svg">
                                    <circle cx="50" cy="50" r="40" fill="none" stroke="#1e293b" strokeWidth="20"/>
                                    <circle 
                                        cx="50" 
                                        cy="50" 
                                        r="40" 
                                        fill="none" 
                                        stroke="#10b981" 
                                        strokeWidth="20"
                                        strokeDasharray={`${safePercent * 2.51} 251`}
                                        strokeDashoffset="0"
                                        transform="rotate(-90 50 50)"
                                    />
                                    <circle 
                                        cx="50" 
                                        cy="50" 
                                        r="40" 
                                        fill="none" 
                                        stroke="#f59e0b" 
                                        strokeWidth="20"
                                        strokeDasharray={`${suspiciousPercent * 2.51} 251`}
                                        strokeDashoffset={`-${safePercent * 2.51}`}
                                        transform="rotate(-90 50 50)"
                                    />
                                    <circle 
                                        cx="50" 
                                        cy="50" 
                                        r="40" 
                                        fill="none" 
                                        stroke="#ef4444" 
                                        strokeWidth="20"
                                        strokeDasharray={`${dangerousPercent * 2.51} 251`}
                                        strokeDashoffset={`-${(safePercent + suspiciousPercent) * 2.51}`}
                                        transform="rotate(-90 50 50)"
                                    />
                                </svg>
                                <div className="donut-center">
                                    <div className="donut-total">{totalThreats}</div>
                                    <div className="donut-label">Total</div>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="empty-chart">
                            <p>Aucune donnée disponible</p>
                            <p className="text-muted">Effectuez des analyses pour voir les statistiques</p>
                        </div>
                    )}
                </div>

                {/* Recent Activity */}
                <div className="glass-card history-card">
                    <h3 className="chart-title">Activité Récente</h3>
                    
                    {/* Filters */}
                    <HistoryFilters 
                        onFilterChange={handleFilterChange}
                        onClearFilters={handleClearFilters}
                    />

                    {/* Search Bar */}
                    <div className="search-bar">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeWidth="2" strokeLinecap="round" />
                        </svg>
                        <input 
                            type="text"
                            className="search-input"
                            placeholder="Rechercher dans l'historique..."
                            value={searchQuery}
                            onChange={(e) => handleSearch(e.target.value)}
                        />
                        {searchQuery && (
                            <button 
                                className="search-clear"
                                onClick={() => handleSearch('')}
                            >
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M18 6L6 18M6 6L18 18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                            </button>
                        )}
                    </div>

                    {/* Results Count */}
                    {(searchQuery || filters.type || filters.threatLevel || filters.startDate) && (
                        <div className="results-count">
                            <strong>{filteredHistory.length}</strong> résultat{filteredHistory.length !== 1 ? 's' : ''} trouvé{filteredHistory.length !== 1 ? 's' : ''}
                        </div>
                    )}
                    
                    {filteredHistory.length > 0 ? (
                        <div className="history-list">
                            {filteredHistory.map((item) => (
                                <div key={item.id} className="history-item">
                                    <div 
                                        className="history-icon"
                                        style={{ background: getThreatColor(item.threatLevel) }}
                                    >
                                        {getThreatIcon(item.threatLevel)}
                                    </div>
                                    <div className="history-content">
                                        <div className="history-header">
                                            <span className="history-type">
                                                {item.type === 'email' ? '📧 Email' : '🔗 URL'}
                                            </span>
                                            <span className="history-time">{formatDate(item.timestamp)}</span>
                                        </div>
                                        <div className="history-text">{item.content}</div>
                                        <div className="history-footer">
                                            <span 
                                                className="history-badge"
                                                style={{ 
                                                    background: `${getThreatColor(item.threatLevel)}20`,
                                                    color: getThreatColor(item.threatLevel)
                                                }}
                                            >
                                                {item.threatLevel}
                                            </span>
                                            <span className="history-confidence">
                                                {item.confidence.toFixed(1)}% confiance
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-history">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" opacity="0.3">
                                <path d="M12 8V12L15 15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            <p>{searchQuery ? 'Aucun résultat trouvé' : 'Aucune activité récente'}</p>
                            <p className="text-muted">
                                {searchQuery ? 'Essayez une autre recherche' : 'Vos analyses apparaîtront ici'}
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
