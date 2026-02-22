import { useState, useEffect } from 'react';
import { Mail, Search, Filter, RefreshCw, ChevronLeft, ChevronRight, Trash2, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { adminApi } from '../../services/adminApi';
import { Toast } from './Toast';

export function EmailProviders() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalConnections, setTotalConnections] = useState(0);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [toast, setToast] = useState(null);
  const [showRevokeModal, setShowRevokeModal] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [stats, setStats] = useState(null);
  const connectionsPerPage = 15;

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  const closeToast = () => {
    setToast(null);
  };

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    loadConnections();
  }, [currentPage, selectedProvider]);

  const loadStats = async () => {
    try {
      const response = await adminApi.getEmailProviderStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadConnections = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * connectionsPerPage;
      const params = {
        skip,
        limit: connectionsPerPage
      };
      
      if (selectedProvider) {
        params.provider = selectedProvider;
      }

      const response = await adminApi.getEmailConnections(params);
      setConnections(response.data || []);
      setTotalConnections(response.data.length === connectionsPerPage ? (currentPage * connectionsPerPage) + 1 : skip + response.data.length);
    } catch (error) {
      console.error('Failed to load connections:', error);
      if (error.response?.status === 401) {
        showToast('Session expirée. Veuillez vous reconnecter.', 'error');
      } else {
        showToast('Erreur lors du chargement des connexions email', 'error');
      }
      setConnections([]);
      setTotalConnections(0);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeConnection = (connection) => {
    setSelectedConnection(connection);
    setShowRevokeModal(true);
  };

  const confirmRevoke = async () => {
    try {
      await adminApi.revokeEmailConnection(selectedConnection.id);
      setShowRevokeModal(false);
      setSelectedConnection(null);
      showToast('Connexion email révoquée avec succès', 'success');
      loadConnections();
      loadStats();
    } catch (error) {
      console.error('Failed to revoke connection:', error);
      showToast('Erreur lors de la révocation de la connexion', 'error');
    }
  };

  const handleRefresh = () => {
    setCurrentPage(1);
    loadConnections();
    loadStats();
  };

  const handleClearFilters = () => {
    setSelectedProvider('');
    setSearchTerm('');
    setCurrentPage(1);
  };

  const filteredConnections = (connections || []).filter(conn => {
    const searchLower = searchTerm.toLowerCase();
    return (
      conn.username.toLowerCase().includes(searchLower) ||
      conn.email.toLowerCase().includes(searchLower) ||
      (conn.email_address && conn.email_address.toLowerCase().includes(searchLower))
    );
  });

  const getProviderIcon = (provider) => {
    if (provider === 'gmail') {
      return '📧';
    } else if (provider === 'outlook') {
      return '📨';
    }
    return '✉️';
  };

  const getProviderColor = (provider) => {
    if (provider === 'gmail') {
      return { bg: '#fef3c7', text: '#92400e', border: '#fde68a' };
    } else if (provider === 'outlook') {
      return { bg: '#dbeafe', text: '#1e40af', border: '#bfdbfe' };
    }
    return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' };
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalPages = Math.ceil(totalConnections / connectionsPerPage);

  if (loading && !stats) {
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
          <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>Chargement des connexions email...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '0' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed', margin: '0 0 8px 0' }}>
          Fournisseurs Email
        </h2>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
          Gérer les connexions email des utilisateurs (Gmail, Outlook)
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '16px',
            padding: '24px',
            color: 'white'
          }}>
            <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>Total Connexions</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{stats.total_connections || 0}</div>
          </div>
          
          <div style={{ 
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            borderRadius: '16px',
            padding: '24px',
            color: 'white'
          }}>
            <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>Connexions Actives</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{stats.active_connections || 0}</div>
          </div>
          
          <div style={{ 
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            borderRadius: '16px',
            padding: '24px',
            color: 'white'
          }}>
            <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>Connexions Expirées</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{stats.expired_connections || 0}</div>
          </div>
          
          <div style={{ 
            background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            borderRadius: '16px',
            padding: '24px',
            color: 'white'
          }}>
            <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>Utilisateurs Connectés</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{stats.users_with_connections || 0}</div>
          </div>
        </div>
      )}

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
              placeholder="Rechercher par utilisateur ou email..."
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

          {/* Provider Filter */}
          <div style={{ position: 'relative', minWidth: '180px' }}>
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
              value={selectedProvider}
              onChange={(e) => {
                setSelectedProvider(e.target.value);
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
              <option value="">Tous les fournisseurs</option>
              <option value="gmail">Gmail</option>
              <option value="outlook">Outlook</option>
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

          {(selectedProvider || searchTerm) && (
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

      {/* Connections Table */}
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
                  Utilisateur
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Fournisseur
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Email Connecté
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Statut
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Expiration
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Connecté Le
                </th>
                <th style={{ padding: '16px', textAlign: 'center', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" style={{ padding: '48px', textAlign: 'center' }}>
                    <div style={{ display: 'flex', justifyContent: 'center' }}>
                      <div style={{ position: 'relative', width: '48px', height: '48px' }}>
                        <div style={{ 
                          position: 'absolute', width: '48px', height: '48px', 
                          border: '4px solid #e9d5ff', borderRadius: '50%',
                          animation: 'spin 1s linear infinite'
                        }}></div>
                        <div style={{ 
                          position: 'absolute', width: '48px', height: '48px', 
                          border: '4px solid transparent', borderTopColor: '#9333ea',
                          borderRadius: '50%', animation: 'spin 1s linear infinite'
                        }}></div>
                      </div>
                    </div>
                  </td>
                </tr>
              ) : filteredConnections.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ padding: '48px', textAlign: 'center' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                      <Mail style={{ width: '48px', height: '48px', color: '#d1d5db' }} />
                      <p style={{ fontSize: '16px', fontWeight: '600', color: '#6b7280', margin: 0 }}>
                        Aucune connexion email trouvée
                      </p>
                      <p style={{ fontSize: '14px', color: '#9ca3af', margin: 0 }}>
                        {searchTerm || selectedProvider ? 'Essayez de modifier vos filtres' : 'Les utilisateurs n\'ont pas encore connecté leurs comptes email'}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredConnections.map((conn) => {
                  const providerColors = getProviderColor(conn.provider);
                  return (
                    <tr 
                      key={conn.id}
                      style={{ 
                        borderBottom: '1px solid #f3f4f6',
                        transition: 'background-color 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                    >
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <div style={{ 
                            width: '40px', 
                            height: '40px', 
                            borderRadius: '50%', 
                            background: 'linear-gradient(135deg, #667eea, #764ba2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '16px'
                          }}>
                            {conn.username.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                              {conn.username}
                            </div>
                            <div style={{ fontSize: '12px', color: '#6b7280' }}>
                              {conn.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          padding: '6px 12px',
                          backgroundColor: providerColors.bg,
                          color: providerColors.text,
                          border: `1px solid ${providerColors.border}`,
                          borderRadius: '8px',
                          fontSize: '13px',
                          fontWeight: '600'
                        }}>
                          <span style={{ fontSize: '16px' }}>{getProviderIcon(conn.provider)}</span>
                          {conn.provider.charAt(0).toUpperCase() + conn.provider.slice(1)}
                        </span>
                      </td>
                      <td style={{ padding: '16px', fontSize: '14px', color: '#374151' }}>
                        {conn.email_address || '-'}
                      </td>
                      <td style={{ padding: '16px' }}>
                        {conn.is_expired ? (
                          <span style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '6px 12px',
                            backgroundColor: '#fef2f2',
                            color: '#991b1b',
                            border: '1px solid #fecaca',
                            borderRadius: '8px',
                            fontSize: '12px',
                            fontWeight: '600'
                          }}>
                            <XCircle style={{ width: '14px', height: '14px' }} />
                            Expiré
                          </span>
                        ) : (
                          <span style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '6px 12px',
                            backgroundColor: '#f0fdf4',
                            color: '#166534',
                            border: '1px solid #bbf7d0',
                            borderRadius: '8px',
                            fontSize: '12px',
                            fontWeight: '600'
                          }}>
                            <CheckCircle style={{ width: '14px', height: '14px' }} />
                            Actif
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '16px', fontSize: '13px', color: '#6b7280' }}>
                        {formatDate(conn.token_expiry)}
                      </td>
                      <td style={{ padding: '16px', fontSize: '13px', color: '#6b7280' }}>
                        {formatDate(conn.created_at)}
                      </td>
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
                          <button
                            onClick={() => handleRevokeConnection(conn)}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              padding: '8px 16px',
                              backgroundColor: '#fee2e2',
                              color: '#991b1b',
                              border: 'none',
                              borderRadius: '8px',
                              fontSize: '13px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              transition: 'background-color 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fecaca'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#fee2e2'}
                            title="Révoquer la connexion"
                          >
                            <Trash2 style={{ width: '16px', height: '16px' }} />
                            Révoquer
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {filteredConnections.length > 0 && (
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
                disabled={filteredConnections.length < connectionsPerPage}
                style={{
                  padding: '8px 12px',
                  backgroundColor: filteredConnections.length < connectionsPerPage ? '#f3f4f6' : 'white',
                  color: filteredConnections.length < connectionsPerPage ? '#9ca3af' : '#374151',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  cursor: filteredConnections.length < connectionsPerPage ? 'not-allowed' : 'pointer',
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

      {/* Revoke Connection Modal */}
      {showRevokeModal && selectedConnection && (
        <RevokeConnectionModal
          connection={selectedConnection}
          onConfirm={confirmRevoke}
          onCancel={() => {
            setShowRevokeModal(false);
            setSelectedConnection(null);
          }}
        />
      )}

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
      `}</style>
    </div>
  );
}

// Revoke Connection Modal Component
function RevokeConnectionModal({ connection, onConfirm, onCancel }) {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '32px',
        maxWidth: '500px',
        width: '90%',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            backgroundColor: '#fee2e2',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <AlertCircle style={{ width: '24px', height: '24px', color: '#dc2626' }} />
          </div>
          <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
            Révoquer la Connexion Email
          </h3>
        </div>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: '0 0 24px 0' }}>
          Êtes-vous sûr de vouloir révoquer la connexion {connection.provider} de {connection.username} ? 
          L'utilisateur devra se reconnecter pour accéder à ses emails.
        </p>

        <div style={{ 
          padding: '16px', 
          backgroundColor: '#f9fafb', 
          borderRadius: '12px', 
          marginBottom: '24px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', color: '#6b7280' }}>Utilisateur:</span>
            <span style={{ fontSize: '13px', fontWeight: '600', color: '#111827' }}>{connection.username}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', color: '#6b7280' }}>Fournisseur:</span>
            <span style={{ fontSize: '13px', fontWeight: '600', color: '#111827' }}>
              {connection.provider.charAt(0).toUpperCase() + connection.provider.slice(1)}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', color: '#6b7280' }}>Email:</span>
            <span style={{ fontSize: '13px', fontWeight: '600', color: '#111827' }}>{connection.email_address || '-'}</span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            onClick={onCancel}
            style={{
              padding: '12px 24px',
              backgroundColor: 'white',
              color: '#374151',
              border: '1px solid #e5e7eb',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Annuler
          </button>
          <button
            onClick={onConfirm}
            style={{
              padding: '12px 24px',
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Révoquer
          </button>
        </div>
      </div>
    </div>
  );
}
