import React, { useState } from 'react';
import './HistoryFilters.css';

const HistoryFilters = ({ onFilterChange, onClearFilters }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [filters, setFilters] = useState({
        type: '',
        threatLevel: '',
        startDate: '',
        endDate: '',
        limit: 10
    });

    const handleFilterChange = (field, value) => {
        const newFilters = { ...filters, [field]: value };
        setFilters(newFilters);
        onFilterChange(newFilters);
    };

    const handleClear = () => {
        const clearedFilters = {
            type: '',
            threatLevel: '',
            startDate: '',
            endDate: '',
            limit: 10
        };
        setFilters(clearedFilters);
        onClearFilters();
    };

    const hasActiveFilters = filters.type || filters.threatLevel || filters.startDate || filters.endDate;

    return (
        <div className="history-filters">
            <div className="filters-header">
                <button 
                    className="filters-toggle"
                    onClick={() => setIsExpanded(!isExpanded)}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M3 4H21M3 12H15M3 20H9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <span>Filtres</span>
                    {hasActiveFilters && <span className="filter-badge">{
                        [filters.type, filters.threatLevel, filters.startDate, filters.endDate]
                            .filter(Boolean).length
                    }</span>}
                    <svg 
                        width="16" 
                        height="16" 
                        viewBox="0 0 24 24" 
                        fill="none" 
                        stroke="currentColor"
                        className={`chevron ${isExpanded ? 'expanded' : ''}`}
                    >
                        <path d="M6 9L12 15L18 9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                </button>

                {hasActiveFilters && (
                    <button className="clear-filters-btn" onClick={handleClear}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M18 6L6 18M6 6L18 18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        Effacer
                    </button>
                )}
            </div>

            {isExpanded && (
                <div className="filters-content">
                    <div className="filters-grid">
                        {/* Type Filter */}
                        <div className="filter-group">
                            <label className="filter-label">Type</label>
                            <select 
                                className="filter-select"
                                value={filters.type}
                                onChange={(e) => handleFilterChange('type', e.target.value)}
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
                                onChange={(e) => handleFilterChange('threatLevel', e.target.value)}
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
                                onChange={(e) => handleFilterChange('startDate', e.target.value)}
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
                                onChange={(e) => handleFilterChange('endDate', e.target.value)}
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
                                onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
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
                                handleFilterChange('startDate', today);
                                handleFilterChange('endDate', today);
                            }}
                        >
                            Aujourd'hui
                        </button>
                        <button 
                            className="quick-filter-btn"
                            onClick={() => {
                                const today = new Date();
                                const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
                                handleFilterChange('startDate', weekAgo.toISOString().split('T')[0]);
                                handleFilterChange('endDate', today.toISOString().split('T')[0]);
                            }}
                        >
                            7 Derniers Jours
                        </button>
                        <button 
                            className="quick-filter-btn"
                            onClick={() => {
                                const today = new Date();
                                const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
                                handleFilterChange('startDate', monthAgo.toISOString().split('T')[0]);
                                handleFilterChange('endDate', today.toISOString().split('T')[0]);
                            }}
                        >
                            30 Derniers Jours
                        </button>
                        <button 
                            className="quick-filter-btn danger"
                            onClick={() => handleFilterChange('threatLevel', 'dangerous')}
                        >
                            Menaces Uniquement
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default HistoryFilters;
