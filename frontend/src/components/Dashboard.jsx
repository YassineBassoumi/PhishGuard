import React, { useState, useEffect } from 'react';
import './Dashboard.css';
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
    const [filteredHistory, setFilteredHistory] = useState([]);
    const [isExpanded, setIsExpanded] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');

    // Check if any filters are active
    const hasActiveFilters = filters.type || filters.threatLevel || filters.startDate || filters.endDate;

    useEffect(() => {
        if (token) {
            fetchDashboardData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filters, token]);

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
        const clearedFilters = {
            type: '',
            threatLevel: '',
            startDate: '',
            endDate: '',
            limit: 10
        };
        setFilters(clearedFilters);
        setIsExpanded(false); // Close the filter panel
    };

    const handleSearch = (query) => {
        setSearchQuery(query);
        if (!query.trim()) {
            setFilteredHistory(history);
            return;
        }

        const lowercaseQuery = query.toLowerCase();
        const filtered = history.filter(item => 
            (item.content && item.content.toLowerCase().includes(lowercaseQuery)) ||
            (item.type && item.type.toLowerCase().includes(lowercaseQuery)) ||
            (item.threatLevel && item.threatLevel.toLowerCase().includes(lowercaseQuery))
        );
        setFilteredHistory(filtered);
    };

    // Update filtered history when history changes
    useEffect(() => {
        if (searchQuery) {
            handleSearch(searchQuery);
        } else {
            setFilteredHistory(history);
        }
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
                <div>
                    <h2 className="dashboard-title">Résumé de l'Analyse</h2>
                    <p className="dashboard-subtitle">Vue d'ensemble de vos analyses de sécurité</p>
                </div>
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

            {/* Stats Cards - New Design */}
            <div className="stats-grid-new">
                <div className="stat-card-new stat-card-primary">
                    <div className="stat-card-header">
                        <div className="stat-icon-new">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                <path d="M9 11L12 14L22 4M21 12V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H16" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        </div>
                        <div className="stat-trend stat-trend-up">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M7 17L17 7M17 7H7M17 7V17" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        </div>
                    </div>
                    <div className="stat-value-new">{stats?.totalAnalyses || 0}</div>
                    <div className="stat-label-new">Emails Et Url Analysés</div>
                    <div className="stat-footer">Total des analyses effectuées</div>
                </div>

                <div className="stat-card-new stat-card-success">
                    <div className="stat-card-header">
                        <div className="stat-icon-new">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        </div>
                    </div>
                    <div className="stat-value-new">{distribution ? distribution.safe : 0}</div>
                    <div className="stat-label-new">Sûrs</div>
                    <div className="stat-footer">Aucune menace détectée</div>
                </div>

                <div className="stat-card-new stat-card-warning">
                    <div className="stat-card-header">
                        <div className="stat-icon-new">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        </div>
                    </div>
                    <div className="stat-value-new">{distribution ? distribution.suspicious : 0}</div>
                    <div className="stat-label-new">Suspects</div>
                    <div className="stat-footer">Nécessitent une attention</div>
                </div>

                <div className="stat-card-new stat-card-danger">
                    <div className="stat-card-header">
                        <div className="stat-icon-new">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                <path d="M12 9V11M12 15H12.01M5.07183 19H18.9282C20.4678 19 21.4301 17.3333 20.6603 16L13.7321 4C12.9623 2.66667 11.0377 2.66667 10.2679 4L3.33975 16C2.56995 17.3333 3.53223 19 5.07183 19Z" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        </div>
                    </div>
                    <div className="stat-value-new">{distribution ? distribution.dangerous : 0}</div>
                    <div className="stat-label-new">Dangereux</div>
                    <div className="stat-footer">Menaces confirmées</div>
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
                    <div className="history-card-header">
                        <h3 className="chart-title">Activité Récente</h3>
                        
                        {/* Filters Button */}
                        <div className="filters-header">
                            <button 
                                className="filters-toggle"
                                onClick={() => setIsExpanded(!isExpanded)}
                            >
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M3 4H21M3 12H15M3 20H9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                                <span>Filtres</span>
                                {hasActiveFilters && <span className="filter-badge">{
                                    [filters.type, filters.threatLevel, filters.startDate, filters.endDate]
                                        .filter(Boolean).length
                                }</span>}
                                <svg 
                                    width="14" 
                                    height="14" 
                                    viewBox="0 0 24 24" 
                                    fill="none" 
                                    stroke="currentColor"
                                    className={`chevron ${isExpanded ? 'expanded' : ''}`}
                                >
                                    <path d="M6 9L12 15L18 9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                            </button>

                            {hasActiveFilters && (
                                <button className="clear-filters-btn" onClick={handleClearFilters}>
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M18 6L6 18M6 6L18 18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                    </svg>
                                    Effacer
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Filter Panel Overlay */}
                    {isExpanded && (
                        <div className="filter-overlay">
                            <div className="filter-panel">
                                <div className="filter-panel-header">
                                    <h4>Filtrer les résultats</h4>
                                    <button className="close-filter-panel" onClick={() => setIsExpanded(false)}>
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M18 6L6 18M6 6L18 18" strokeLinecap="round" strokeLinejoin="round"/>
                                        </svg>
                                    </button>
                                </div>

                                <div className="filter-panel-content">
                                    <div className="filters-grid">
                                        {/* Type Filter */}
                                        <div className="filter-group">
                                            <label className="filter-label">Type</label>
                                            <select 
                                                className="filter-select"
                                                value={filters.type}
                                                onChange={(e) => handleFilterChange({ ...filters, type: e.target.value })}
                                            >
                                                <option value="">Tous</option>
                                                <option value="email">📧 Email</option>
                                                <option value="url">🔗 URL</option>
                                            </select>
                                        </div>

                                        {/* Threat Level Filter */}
                                        <div className="filter-group">
                                            <label className="filter-label">Niveau de Menace</label>
                                            <select 
                                                className="filter-select"
                                                value={filters.threatLevel}
                                                onChange={(e) => handleFilterChange({ ...filters, threatLevel: e.target.value })}
                                            >
                                                <option value="">Tous</option>
                                                <option value="safe">✓ Sûr</option>
                                                <option value="suspicious">⚠ Suspect</option>
                                                <option value="dangerous">✕ Dangereux</option>
                                            </select>
                                        </div>

                                        {/* Start Date Filter */}
                                        <div className="filter-group">
                                            <label className="filter-label">Date de Début</label>
                                            <input 
                                                type="date"
                                                className="filter-input"
                                                value={filters.startDate}
                                                onChange={(e) => handleFilterChange({ ...filters, startDate: e.target.value })}
                                                max={filters.endDate || new Date().toISOString().split('T')[0]}
                                            />
                                        </div>

                                        {/* End Date Filter */}
                                        <div className="filter-group">
                                            <label className="filter-label">Date de Fin</label>
                                            <input 
                                                type="date"
                                                className="filter-input"
                                                value={filters.endDate}
                                                onChange={(e) => handleFilterChange({ ...filters, endDate: e.target.value })}
                                                min={filters.startDate}
                                                max={new Date().toISOString().split('T')[0]}
                                            />
                                        </div>

                                        {/* Limit Filter */}
                                        <div className="filter-group">
                                            <label className="filter-label">Nombre de Résultats</label>
                                            <select 
                                                className="filter-select"
                                                value={filters.limit}
                                                onChange={(e) => handleFilterChange({ ...filters, limit: parseInt(e.target.value) })}
                                            >
                                                <option value="10">10</option>
                                                <option value="25">25</option>
                                                <option value="50">50</option>
                                                <option value="100">100</option>
                                            </select>
                                        </div>
                                    </div>

                                    {/* Quick Filters */}
                                    <div className="quick-filters">
                                        <span className="quick-filters-label">Filtres Rapides:</span>
                                        <button 
                                            className="quick-filter-btn"
                                            onClick={() => {
                                                const today = new Date().toISOString().split('T')[0];
                                                handleFilterChange({ ...filters, startDate: today, endDate: today });
                                            }}
                                        >
                                            Aujourd'hui
                                        </button>
                                        <button 
                                            className="quick-filter-btn"
                                            onClick={() => {
                                                const today = new Date();
                                                const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
                                                handleFilterChange({ ...filters, startDate: weekAgo.toISOString().split('T')[0], endDate: today.toISOString().split('T')[0] });
                                            }}
                                        >
                                            7 Derniers Jours
                                        </button>
                                        <button 
                                            className="quick-filter-btn"
                                            onClick={() => {
                                                const today = new Date();
                                                const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
                                                handleFilterChange({ ...filters, startDate: monthAgo.toISOString().split('T')[0], endDate: today.toISOString().split('T')[0] });
                                            }}
                                        >
                                            30 Derniers Jours
                                        </button>
                                        <button 
                                            className="quick-filter-btn danger"
                                            onClick={() => handleFilterChange({ ...filters, threatLevel: 'dangerous' })}
                                        >
                                            Menaces Uniquement
                                        </button>
                                    </div>

                                    <div className="filter-panel-actions">
                                        <button className="btn-apply-filters" onClick={() => setIsExpanded(false)}>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <path d="M5 13L9 17L19 7" strokeLinecap="round" strokeLinejoin="round"/>
                                            </svg>
                                            Appliquer les filtres
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Search Bar */}
                    <div className="search-bar">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeLinecap="round" />
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
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M18 6L6 18M6 6L18 18" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                            </button>
                        )}
                    </div>

                    {/* Results Count and Active Filters */}
                    {(searchQuery || filters.type || filters.threatLevel || filters.startDate || filters.endDate) && (
                        <div className="filter-results-info">
                            <div className="results-count">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 3M12 12H15M12 16H15M9 12H9.01M9 16H9.01" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                                <span>
                                    <strong>{filteredHistory.length}</strong> résultat{filteredHistory.length !== 1 ? 's' : ''} trouvé{filteredHistory.length !== 1 ? 's' : ''}
                                </span>
                            </div>
                            <div className="active-filters">
                                {searchQuery && (
                                    <span className="filter-tag filter-tag-search">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeLinecap="round"/>
                                        </svg>
                                        Recherche: "{searchQuery}"
                                    </span>
                                )}
                                {filters.type && (
                                    <span className="filter-tag">
                                        {filters.type === 'email' ? '📧' : '🔗'} {filters.type === 'email' ? 'Email' : 'URL'}
                                    </span>
                                )}
                                {filters.threatLevel && (
                                    <span className="filter-tag filter-tag-threat">
                                        {filters.threatLevel === 'safe' && '✓ Sûr'}
                                        {filters.threatLevel === 'suspicious' && '⚠ Suspect'}
                                        {filters.threatLevel === 'dangerous' && '✕ Dangereux'}
                                    </span>
                                )}
                                {filters.startDate && (
                                    <span className="filter-tag">
                                        📅 Du {new Date(filters.startDate).toLocaleDateString('fr-FR')}
                                    </span>
                                )}
                                {filters.endDate && (
                                    <span className="filter-tag">
                                        📅 Au {new Date(filters.endDate).toLocaleDateString('fr-FR')}
                                    </span>
                                )}
                            </div>
                        </div>
                    )}
                    
                    {/* History List */}
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
                            {(searchQuery || filters.type || filters.threatLevel || filters.startDate || filters.endDate) ? (
                                <>
                                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" opacity="0.3" strokeWidth="2">
                                        <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" strokeLinecap="round" strokeLinejoin="round"/>
                                    </svg>
                                    <p>Aucun résultat trouvé</p>
                                    <p className="text-muted">
                                        {searchQuery ? 'Essayez une autre recherche' : 'Essayez de modifier vos critères de filtrage'}
                                    </p>
                                    {searchQuery ? (
                                        <button 
                                            className="btn-clear-all-filters"
                                            onClick={() => handleSearch('')}
                                        >
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <path d="M18 6L6 18M6 6L18 18" strokeLinecap="round" strokeLinejoin="round"/>
                                            </svg>
                                            Effacer la recherche
                                        </button>
                                    ) : (
                                        <button 
                                            className="btn-clear-all-filters"
                                            onClick={handleClearFilters}
                                        >
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <path d="M18 6L6 18M6 6L18 18" strokeLinecap="round" strokeLinejoin="round"/>
                                            </svg>
                                            Effacer tous les filtres
                                        </button>
                                    )}
                                </>
                            ) : (
                                <>
                                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" opacity="0.3" strokeWidth="2">
                                        <path d="M12 8V12L15 15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" strokeLinecap="round" strokeLinejoin="round"/>
                                    </svg>
                                    <p>Aucune activité récente</p>
                                    <p className="text-muted">
                                        Vos analyses apparaîtront ici
                                    </p>
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
