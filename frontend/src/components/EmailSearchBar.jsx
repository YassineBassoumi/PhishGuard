import React, { useState, useEffect } from 'react';
import './EmailSearchBar.css';

const EmailSearchBar = ({ onSearch, onClear, loading }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [advancedFilters, setAdvancedFilters] = useState({
        from_email: '',
        subject: '',
        date_from: '',
        date_to: '',
        has_attachments: null
    });

    // Debounce search — wait until user stops typing
    // - 800ms delay (was 500ms — too aggressive)
    // - Requires at least 3 characters to avoid firing on every keystroke
    useEffect(() => {
        const trimmed = searchQuery.trim();

        // Don't search for very short queries (1-2 chars produce too much noise)
        if (trimmed.length > 0 && trimmed.length < 3) {
            return;
        }

        const timer = setTimeout(() => {
            if (trimmed || hasActiveFilters()) {
                handleSearch();
            }
        }, 800);

        return () => clearTimeout(timer);
    }, [searchQuery]);

    const hasActiveFilters = () => {
        return advancedFilters.from_email || 
               advancedFilters.subject || 
               advancedFilters.date_from || 
               advancedFilters.date_to || 
               advancedFilters.has_attachments !== null;
    };

    const handleSearch = () => {
        const filters = {
            q: searchQuery.trim() || undefined,
            ...advancedFilters
        };
        
        // Remove empty filters
        Object.keys(filters).forEach(key => {
            if (filters[key] === '' || filters[key] === null || filters[key] === undefined) {
                delete filters[key];
            }
        });

        onSearch(filters);
    };

    const handleClear = () => {
        setSearchQuery('');
        setAdvancedFilters({
            from_email: '',
            subject: '',
            date_from: '',
            date_to: '',
            has_attachments: null
        });
        onClear();
    };

    const handleAdvancedFilterChange = (field, value) => {
        setAdvancedFilters(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const applyAdvancedFilters = () => {
        handleSearch();
        setShowAdvanced(false);
    };

    return (
        <div className="email-search-container">
            <div className="search-bar">
                <div className="search-input-wrapper">
                    <svg className="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="11" cy="11" r="8" strokeWidth="2"/>
                        <path d="M21 21L16.65 16.65" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Rechercher dans les emails..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        disabled={loading}
                    />
                    {(searchQuery || hasActiveFilters()) && (
                        <button 
                            className="clear-search-btn"
                            onClick={handleClear}
                            title="Effacer la recherche"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M18 6L6 18M6 6L18 18" strokeWidth="2" strokeLinecap="round"/>
                            </svg>
                        </button>
                    )}
                </div>
                <button 
                    className={`advanced-filter-btn ${showAdvanced ? 'active' : ''}`}
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    title="Filtres avancés"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M3 4H21M3 12H15M3 20H9" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Filtres
                    {hasActiveFilters() && <span className="filter-badge">{Object.values(advancedFilters).filter(v => v !== '' && v !== null).length}</span>}
                </button>
            </div>

            {showAdvanced && (
                <div className="advanced-filters-panel">
                    <div className="filters-grid">
                        <div className="filter-group">
                            <label>De (expéditeur)</label>
                            <input
                                type="text"
                                placeholder="nom ou email..."
                                value={advancedFilters.from_email}
                                onChange={(e) => handleAdvancedFilterChange('from_email', e.target.value)}
                            />
                        </div>

                        <div className="filter-group">
                            <label>Sujet</label>
                            <input
                                type="text"
                                placeholder="mots-clés..."
                                value={advancedFilters.subject}
                                onChange={(e) => handleAdvancedFilterChange('subject', e.target.value)}
                            />
                        </div>

                        <div className="filter-group">
                            <label>Date de début</label>
                            <input
                                type="date"
                                value={advancedFilters.date_from}
                                onChange={(e) => handleAdvancedFilterChange('date_from', e.target.value)}
                            />
                        </div>

                        <div className="filter-group">
                            <label>Date de fin</label>
                            <input
                                type="date"
                                value={advancedFilters.date_to}
                                onChange={(e) => handleAdvancedFilterChange('date_to', e.target.value)}
                            />
                        </div>

                        <div className="filter-group">
                            <label>Pièces jointes</label>
                            <select
                                value={advancedFilters.has_attachments === null ? '' : advancedFilters.has_attachments}
                                onChange={(e) => handleAdvancedFilterChange('has_attachments', e.target.value === '' ? null : e.target.value === 'true')}
                            >
                                <option value="">Tous</option>
                                <option value="true">Avec pièces jointes</option>
                                <option value="false">Sans pièces jointes</option>
                            </select>
                        </div>
                    </div>

                    <div className="filter-actions">
                        <button 
                            className="btn btn-secondary btn-sm"
                            onClick={() => {
                                setAdvancedFilters({
                                    from_email: '',
                                    subject: '',
                                    date_from: '',
                                    date_to: '',
                                    has_attachments: null
                                });
                            }}
                        >
                            Réinitialiser
                        </button>
                        <button 
                            className="btn btn-primary btn-sm"
                            onClick={applyAdvancedFilters}
                        >
                            Appliquer
                        </button>
                    </div>
                </div>
            )}

            {loading && (
                <div className="search-loading">
                    <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                    <span>Recherche en cours...</span>
                </div>
            )}
        </div>
    );
};

export default EmailSearchBar;
