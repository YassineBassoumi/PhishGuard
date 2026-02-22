import { useState, useEffect } from 'react';
import { Shield, Search, UserCheck, RefreshCw, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react';
import { adminApi } from '../../services/adminApi';
import { Toast } from './Toast';

export function BannedUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUnbanModal, setShowUnbanModal] = useState(false);
  const [toast, setToast] = useState(null);
  const usersPerPage = 10;

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  const closeToast = () => {
    setToast(null);
  };

  useEffect(() => {
    loadBannedUsers();
  }, [currentPage]);

  const loadBannedUsers = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * usersPerPage;
      const response = await adminApi.getBannedUsers(skip, usersPerPage);
      setUsers(response.data.users || []);
      setTotalUsers(response.data.total || 0);
    } catch (error) {
      console.error('Failed to load banned users:', error);
      if (error.response?.status === 401) {
        showToast('Session expirée. Veuillez vous reconnecter.', 'error');
      } else {
        showToast('Erreur lors du chargement des utilisateurs bannis', 'error');
      }
      setUsers([]);
      setTotalUsers(0);
    } finally {
      setLoading(false);
    }
  };

  const handleUnbanUser = (user) => {
    setSelectedUser(user);
    setShowUnbanModal(true);
  };

  const confirmUnban = async () => {
    try {
      await adminApi.unbanUser(selectedUser.id);
      setShowUnbanModal(false);
      setSelectedUser(null);
      showToast('Utilisateur débanni avec succès', 'success');
      loadBannedUsers();
    } catch (error) {
      console.error('Failed to unban user:', error);
      showToast('Erreur lors du débannissement de l\'utilisateur', 'error');
    }
  };

  const filteredUsers = (users || []).filter(user => {
    return user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
           user.email.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const totalPages = Math.ceil(totalUsers / usersPerPage);

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
          <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>Chargement des utilisateurs bannis...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '0' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed', margin: '0 0 8px 0' }}>
          Utilisateurs Bannis
        </h2>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
          Gérer les utilisateurs bannis et les débannir si nécessaire
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
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
          {/* Search */}
          <div style={{ position: 'relative' }}>
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
              placeholder="Rechercher par nom ou email..."
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

          {/* Refresh Button */}
          <button
            onClick={loadBannedUsers}
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
        </div>
      </div>

      {/* Banned Users Table */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        overflow: 'hidden',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#fef2f2', borderBottom: '2px solid #fecaca' }}>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Utilisateur
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Email
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Raison
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Banni Le
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Banni Par
                </th>
                <th style={{ padding: '16px', textAlign: 'center', fontSize: '12px', fontWeight: '600', color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ padding: '48px', textAlign: 'center' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                      <Shield style={{ width: '48px', height: '48px', color: '#d1d5db' }} />
                      <p style={{ fontSize: '16px', fontWeight: '600', color: '#6b7280', margin: 0 }}>
                        Aucun utilisateur banni
                      </p>
                      <p style={{ fontSize: '14px', color: '#9ca3af', margin: 0 }}>
                        {searchTerm ? 'Essayez de modifier votre recherche' : 'Tous les utilisateurs sont actifs'}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user, index) => (
                  <tr 
                    key={user.id}
                    style={{ 
                      borderBottom: '1px solid #f3f4f6',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fef2f2'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                  >
                    <td style={{ padding: '16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ 
                          width: '40px', 
                          height: '40px', 
                          borderRadius: '50%', 
                          background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontWeight: 'bold',
                          fontSize: '16px'
                        }}>
                          {user.username.charAt(0).toUpperCase()}
                        </div>
                        <span style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                          {user.username}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '16px', fontSize: '14px', color: '#6b7280' }}>
                      {user.email}
                    </td>
                    <td style={{ padding: '16px' }}>
                      <div style={{ 
                        maxWidth: '300px',
                        padding: '8px 12px',
                        backgroundColor: '#fef2f2',
                        borderRadius: '8px',
                        border: '1px solid #fecaca'
                      }}>
                        <p style={{ fontSize: '13px', color: '#991b1b', margin: 0, lineHeight: '1.5' }}>
                          {user.ban_reason || 'Aucune raison fournie'}
                        </p>
                      </div>
                    </td>
                    <td style={{ padding: '16px', fontSize: '14px', color: '#6b7280' }}>
                      {user.banned_at ? new Date(user.banned_at).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      }) : '-'}
                    </td>
                    <td style={{ padding: '16px', fontSize: '14px', color: '#6b7280' }}>
                      {user.banned_by_username || 'Système'}
                    </td>
                    <td style={{ padding: '16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
                        <button
                          onClick={() => handleUnbanUser(user)}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '8px 16px',
                            backgroundColor: '#d1fae5',
                            color: '#065f46',
                            border: 'none',
                            borderRadius: '8px',
                            fontSize: '13px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'background-color 0.2s'
                          }}
                          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#a7f3d0'}
                          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#d1fae5'}
                          title="Débannir l'utilisateur"
                        >
                          <UserCheck style={{ width: '16px', height: '16px' }} />
                          Débannir
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          padding: '16px 24px',
          borderTop: '1px solid #f3f4f6'
        }}>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
            Affichage de {((currentPage - 1) * usersPerPage) + 1} à {Math.min(currentPage * usersPerPage, totalUsers)} sur {totalUsers} utilisateurs bannis
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
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              style={{
                padding: '8px 12px',
                backgroundColor: currentPage === totalPages ? '#f3f4f6' : 'white',
                color: currentPage === totalPages ? '#9ca3af' : '#374151',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
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
      </div>

      {/* Unban User Modal */}
      {showUnbanModal && selectedUser && (
        <UnbanUserModal
          user={selectedUser}
          onConfirm={confirmUnban}
          onCancel={() => {
            setShowUnbanModal(false);
            setSelectedUser(null);
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

// Unban User Modal Component
function UnbanUserModal({ user, onConfirm, onCancel }) {
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
            backgroundColor: '#d1fae5',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <UserCheck style={{ width: '24px', height: '24px', color: '#059669' }} />
          </div>
          <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
            Débannir l'Utilisateur
          </h3>
        </div>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: '0 0 24px 0' }}>
          Êtes-vous sûr de vouloir débannir {user.username} ? L'utilisateur pourra à nouveau se connecter et utiliser la plateforme.
        </p>

        {user.ban_reason && (
          <div style={{ 
            padding: '16px', 
            backgroundColor: '#fef2f2', 
            borderRadius: '12px', 
            marginBottom: '24px',
            border: '1px solid #fecaca'
          }}>
            <p style={{ fontSize: '12px', fontWeight: '600', color: '#991b1b', margin: '0 0 8px 0', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Raison du bannissement :
            </p>
            <p style={{ fontSize: '14px', color: '#7f1d1d', margin: 0 }}>
              {user.ban_reason}
            </p>
          </div>
        )}

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
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Débannir
          </button>
        </div>
      </div>
    </div>
  );
}
