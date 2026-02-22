import { useState, useEffect } from 'react';
import { FileText, Search, Filter, RefreshCw, ChevronLeft, ChevronRight, Calendar, User, Target, Activity } from 'lucide-react';
import { adminApi } from '../../services/adminApi';
import { Toast } from './Toast';

export function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalLogs, setTotalLogs] = useState(0);
  const [selectedAction, setSelectedAction] = useState('');
  const [availableActions, setAvailableActions] = useState([]);
  const [toast, setToast] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const logsPerPage = 20;

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  const closeToast = () => {
    setToast(null);
  };

  useEffect(() => {
    loadAuditActions();
  }, []);

  useEffect(() => {
    loadAuditLogs();
  }, [currentPage, selectedAction]);

  const loadAuditActions = async () => {
    try {
      const response = await adminApi.getAuditActions();
      setAvailableActions(response.data.actions || []);
    } catch (error) {
      console.error('Failed to load audit actions:', error);
    }
  };

  const loadAuditLogs = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * logsPerPage;
      const params = {
        skip,
        limit: logsPerPage
      };
      
      if (selectedAction) {
        params.action = selectedAction;
      }

      const response = await adminApi.getAuditLogs(params);
      setLogs(response.data || []);
      // Estimate total based on returned data
      setTotalLogs(response.data.length === logsPerPage ? (currentPage * logsPerPage) + 1 : skip + response.data.length);
    } catch (error) {
      console.error('Failed to load audit logs:', error);
      if (error.response?.status === 401) {
        showToast('Session expirée. Veuillez vous reconnecter.', 'error');
      } else {
        showToast('Erreur lors du chargement des journaux d\'audit', 'error');
      }
      setLogs([]);
      setTotalLogs(0);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setCurrentPage(1);
    loadAuditLogs();
  };

  const handleClearFilters = () => {
    setSelectedAction('');
    setSearchTerm('');
    setCurrentPage(1);
  };

  const filteredLogs = (logs || []).filter(log => {
    const searchLower = searchTerm.toLowerCase();
    return (
      log.action.toLowerCase().includes(searchLower) ||
      (log.actor_username && log.actor_username.toLowerCase().includes(searchLower)) ||
      (log.target_username && log.target_username.toLowerCase().includes(searchLower)) ||
      (log.ip_address && log.ip_address.toLowerCase().includes(searchLower))
    );
  });

  const getActionColor = (action) => {
    if (action.includes('DELETED') || action.includes('BANNED')) {
      return { bg: '#fef2f2', text: '#991b1b', border: '#fecaca' };
    } else if (action.includes('CREATED') || action.includes('UNBANNED')) {
      return { bg: '#f0fdf4', text: '#166534', border: '#bbf7d0' };
    } else if (action.includes('UPDATED') || action.includes('CHANGED')) {
      return { bg: '#fef3c7', text: '#92400e', border: '#fde68a' };
    } else if (action.includes('VIEWED')) {
      return { bg: '#eff6ff', text: '#1e40af', border: '#bfdbfe' };
    }
    return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' };
  };

  const formatActionName = (action) => {
    return action.replace(/_/g, ' ').toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalPages = Math.ceil(totalLogs / logsPerPage);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ position: 'relative', width: '64px', height: '64px', margin: '0 auto 16px' }}>
            <div style={{ 
              position: 'absolute', width: '64px', height: '64px', 
              border: '4px solid #e9d5ff', borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
            <div style={{ 
              position: 'absolute', width: '64px', height: '64px', 
              border: '4px solid transparent', borderTopColor: '#9333ea',
              borderRadius: '50%', animation: 'spin 1s linear infinite'
            }}></div>
          </div>
          <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>Chargement des journaux d'audit...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '0' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed', margin: '0 0 8px 0' }}>
          Journaux d'Audit
        </h2>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
          Suivre toutes les actions administratives et les modifications du système
        </p>
      </div>

      {/* Filters and Search */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        padding: '24px', 
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Search */}
          <div style={{ position: 'relative', flex: '1', minWidth: '250px' }}>
            <Search style={{ 
              position: 'absolute', 
              left: '12px', 
              top: '50%', 
              transform: 'translateY(-50%)',
              width: '20px', 
              height: '20px', 
              color: '#9ca3af' 
            }} />
            <input
              type="text"
              placeholder="Rechercher par action, utilisateur, IP..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 12px 12px 44px',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#7c3aed'}
              onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
            />
          </div>

          {/* Action Filter */}
          <div style={{ position: 'relative', minWidth: '200px' }}>
            <Filter style={{ 
              position: 'absolute', 
              left: '12px', 
              top: '50%', 
              transform: 'translateY(-50%)',
              width: '20px', 
              height: '20px', 
              color: '#9ca3af',
              pointerEvents: 'none'
            }} />
            <select
              value={selectedAction}
              onChange={(e) => {
                setSelectedAction(e.target.value);
                setCurrentPage(1);
              }}
              style={{
                width: '100%',
                padding: '12px 12px 12px 44px',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '14px',
                outline: 'none',
                cursor: 'pointer',
                backgroundColor: 'white',
                appearance: 'none'
              }}
            >
              <option value="">Toutes les actions</option>
              {availableActions.map(action => (
                <option key={action} value={action}>
                  {formatActionName(action)}
                </option>
              ))}
            </select>
          </div>

          {/* Action Buttons */}
          <button
            onClick={handleRefresh}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              padding: '12px 24px',
              backgroundColor: '#7c3aed',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#6d28d9'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#7c3aed'}
          >
            <RefreshCw style={{ width: '16px', height: '16px' }} />
            Actualiser
          </button>

          {(selectedAction || searchTerm) && (
            <button
              onClick={handleClearFilters}
              style={{
                padding: '12px 24px',
                backgroundColor: 'white',
                color: '#6b7280',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
            >
              Réinitialiser
            </button>
          )}
        </div>
      </div>

      {/* Audit Logs Table */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        overflow: 'hidden',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Date & Heure
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Action
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Acteur
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Cible
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Adresse IP
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Détails
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ padding: '48px', textAlign: 'center' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                      <FileText style={{ width: '48px', height: '48px', color: '#d1d5db' }} />
                      <p style={{ fontSize: '16px', fontWeight: '600', color: '#6b7280', margin: 0 }}>
                        Aucun journal d'audit trouvé
                      </p>
                      <p style={{ fontSize: '14px', color: '#9ca3af', margin: 0 }}>
                        {searchTerm || selectedAction ? 'Essayez de modifier vos filtres' : 'Les actions administratives apparaîtront ici'}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => {
                  const actionColors = getActionColor(log.action);
                  return (
                    <tr 
                      key={log.id}
                      style={{ 
                        borderBottom: '1px solid #f3f4f6',
                        transition: 'background-color 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                    >
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <Calendar style={{ width: '16px', height: '16px', color: '#9ca3af' }} />
                          <span style={{ fontSize: '13px', color: '#374151' }}>
                            {formatDate(log.created_at)}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span style={{
                          display: 'inline-block',
                          padding: '6px 12px',
                          backgroundColor: actionColors.bg,
                          color: actionColors.text,
                          border: `1px solid ${actionColors.border}`,
                          borderRadius: '8px',
                          fontSize: '12px',
                          fontWeight: '600'
                        }}>
                          {formatActionName(log.action)}
                        </span>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <User style={{ width: '16px', height: '16px', color: '#9ca3af' }} />
                          <span style={{ fontSize: '14px', color: '#374151', fontWeight: '500' }}>
                            {log.actor_username || 'Système'}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        {log.target_username ? (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Target style={{ width: '16px', height: '16px', color: '#9ca3af' }} />
                            <span style={{ fontSize: '14px', color: '#6b7280' }}>
                              {log.target_username}
                            </span>
                          </div>
                        ) : (
                          <span style={{ fontSize: '14px', color: '#d1d5db' }}>-</span>
                        )}
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span style={{ 
                          fontSize: '13px', 
                          color: '#6b7280',
                          fontFamily: 'monospace'
                        }}>
                          {log.ip_address || '-'}
                        </span>
                      </td>
                      <td style={{ padding: '16px' }}>
                        {log.details && Object.keys(log.details).length > 0 ? (
                          <details style={{ cursor: 'pointer' }}>
                            <summary style={{ 
                              fontSize: '13px', 
                              color: '#7c3aed',
                              fontWeight: '500',
                              listStyle: 'none',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}>
                              <Activity style={{ width: '14px', height: '14px' }} />
                              Voir détails
                            </summary>
                            <div style={{ 
                              marginTop: '8px',
                              padding: '12px',
                              backgroundColor: '#f9fafb',
                              borderRadius: '8px',
                              fontSize: '12px',
                              color: '#374151'
                            }}>
                              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                                {JSON.stringify(log.details, null, 2)}
                              </pre>
                            </div>
                          </details>
                        ) : (
                          <span style={{ fontSize: '14px', color: '#d1d5db' }}>-</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {filteredLogs.length > 0 && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: '16px 24px',
            borderTop: '1px solid #f3f4f6'
          }}>
            <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
              Page {currentPage} sur {totalPages || 1}
            </p>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                style={{
                  padding: '8px 12px',
                  backgroundColor: currentPage === 1 ? '#f3f4f6' : 'white',
                  color: currentPage === 1 ? '#9ca3af' : '#374151',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                <ChevronLeft style={{ width: '16px', height: '16px' }} />
                Précédent
              </button>
              <button
                onClick={() => setCurrentPage(prev => prev + 1)}
                disabled={filteredLogs.length < logsPerPage}
                style={{
                  padding: '8px 12px',
                  backgroundColor: filteredLogs.length < logsPerPage ? '#f3f4f6' : 'white',
                  color: filteredLogs.length < logsPerPage ? '#9ca3af' : '#374151',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  cursor: filteredLogs.length < logsPerPage ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                Suivant
                <ChevronRight style={{ width: '16px', height: '16px' }} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={closeToast}
        />
      )}

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        
        details summary::-webkit-details-marker {
          display: none;
        }
      `}</style>
    </div>
  );
}
