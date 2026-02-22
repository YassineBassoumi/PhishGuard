import { useState, useEffect } from 'react';
import { Users, Search, Edit, Trash2, Shield, Ban, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { adminApi } from '../../services/adminApi';
import { Toast } from './Toast';

export function UsersManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showBanModal, setShowBanModal] = useState(false);
  const [toast, setToast] = useState(null);
  const usersPerPage = 10;

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  const closeToast = () => {
    setToast(null);
  };

  useEffect(() => {
    loadUsers();
  }, [currentPage, roleFilter]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * usersPerPage;
      const response = await adminApi.getUsers(skip, usersPerPage);
      setUsers(response.data.users || []);
      setTotalUsers(response.data.total || 0);
    } catch (error) {
      console.error('Failed to load users:', error);
      if (error.response?.status === 401) {
        showToast('Session expirée. Veuillez vous reconnecter.', 'error');
      } else {
        showToast('Erreur lors du chargement des utilisateurs', 'error');
      }
      setUsers([]);
      setTotalUsers(0);
    } finally {
      setLoading(false);
    }
  };

  const handleEditRole = (user) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const handleDeleteUser = (user) => {
    setSelectedUser(user);
    setShowDeleteModal(true);
  };

  const handleBanUser = (user) => {
    setSelectedUser(user);
    setShowBanModal(true);
  };

  const confirmEditRole = async (newRole) => {
    try {
      await adminApi.updateUserRole(selectedUser.id, newRole);
      setShowEditModal(false);
      setSelectedUser(null);
      showToast('Rôle mis à jour avec succès', 'success');
      loadUsers();
    } catch (error) {
      console.error('Failed to update role:', error);
      showToast('Erreur lors de la mise à jour du rôle', 'error');
    }
  };

  const confirmDelete = async () => {
    try {
      await adminApi.deleteUser(selectedUser.id);
      setShowDeleteModal(false);
      setSelectedUser(null);
      showToast('Utilisateur supprimé avec succès', 'success');
      loadUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
      showToast('Erreur lors de la suppression de l\'utilisateur', 'error');
    }
  };

  const confirmBan = async (reason) => {
    try {
      await adminApi.banUser(selectedUser.id, reason);
      setShowBanModal(false);
      setSelectedUser(null);
      showToast('Utilisateur banni avec succès', 'success');
      loadUsers();
    } catch (error) {
      console.error('Failed to ban user:', error);
      showToast('Erreur lors du bannissement de l\'utilisateur', 'error');
    }
  };

  const filteredUsers = (users || []).filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'ALL' || user.role === roleFilter;
    return matchesSearch && matchesRole;
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
          <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>Chargement des utilisateurs...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '0' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed', margin: '0 0 8px 0' }}>
          Gestion des Utilisateurs
        </h2>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
          Gérer les utilisateurs, leurs rôles et leurs permissions
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

          {/* Role Filter */}
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            style={{
              padding: '12px',
              border: '1px solid #e5e7eb',
              borderRadius: '12px',
              fontSize: '14px',
              outline: 'none',
              cursor: 'pointer',
              backgroundColor: 'white'
            }}
          >
            <option value="ALL">Tous les rôles</option>
            <option value="USER">Utilisateurs</option>
            <option value="ADMIN">Administrateurs</option>
            <option value="SUPERADMIN">Super Administrateurs</option>
          </select>

          {/* Refresh Button */}
          <button
            onClick={loadUsers}
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

      {/* Users Table */}
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
                  Email
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Rôle
                </th>
                <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Dernière Connexion
                </th>
                <th style={{ padding: '16px', textAlign: 'center', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ padding: '48px', textAlign: 'center' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                      <Users style={{ width: '48px', height: '48px', color: '#d1d5db' }} />
                      <p style={{ fontSize: '16px', fontWeight: '600', color: '#6b7280', margin: 0 }}>
                        Aucun utilisateur trouvé
                      </p>
                      <p style={{ fontSize: '14px', color: '#9ca3af', margin: 0 }}>
                        {searchTerm || roleFilter !== 'ALL' ? 'Essayez de modifier vos filtres' : 'Aucun utilisateur dans le système'}
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
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                >
                  <td style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ 
                        width: '40px', 
                        height: '40px', 
                        borderRadius: '50%', 
                        background: 'linear-gradient(135deg, #7c3aed, #5b21b6)',
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
                    <span style={{
                      padding: '4px 12px',
                      borderRadius: '8px',
                      fontSize: '12px',
                      fontWeight: '600',
                      backgroundColor: user.role === 'SUPERADMIN' ? '#ede9fe' : user.role === 'ADMIN' ? '#dbeafe' : '#f3f4f6',
                      color: user.role === 'SUPERADMIN' ? '#7c3aed' : user.role === 'ADMIN' ? '#3b82f6' : '#6b7280'
                    }}>
                      {user.role === 'SUPERADMIN' ? 'Super Admin' : user.role === 'ADMIN' ? 'Admin' : 'Utilisateur'}
                    </span>
                  </td>
                  <td style={{ padding: '16px', fontSize: '14px', color: '#6b7280' }}>
                    {user.last_login ? new Date(user.last_login).toLocaleDateString('fr-FR') : 'Jamais'}
                  </td>
                  <td style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
                      <button
                        onClick={() => handleEditRole(user)}
                        style={{
                          padding: '8px',
                          backgroundColor: '#dbeafe',
                          color: '#3b82f6',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#bfdbfe'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#dbeafe'}
                        title="Modifier le rôle"
                      >
                        <Edit style={{ width: '16px', height: '16px' }} />
                      </button>
                      <button
                        onClick={() => handleBanUser(user)}
                        style={{
                          padding: '8px',
                          backgroundColor: '#fed7aa',
                          color: '#ea580c',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fdba74'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#fed7aa'}
                        title="Bannir l'utilisateur"
                      >
                        <Ban style={{ width: '16px', height: '16px' }} />
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user)}
                        style={{
                          padding: '8px',
                          backgroundColor: '#fee2e2',
                          color: '#ef4444',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fecaca'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#fee2e2'}
                        title="Supprimer l'utilisateur"
                      >
                        <Trash2 style={{ width: '16px', height: '16px' }} />
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
            Affichage de {((currentPage - 1) * usersPerPage) + 1} à {Math.min(currentPage * usersPerPage, totalUsers)} sur {totalUsers} utilisateurs
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

      {/* Edit Role Modal */}
      {showEditModal && selectedUser && (
        <EditRoleModal
          user={selectedUser}
          onConfirm={confirmEditRole}
          onCancel={() => {
            setShowEditModal(false);
            setSelectedUser(null);
          }}
        />
      )}

      {/* Ban User Modal */}
      {showBanModal && selectedUser && (
        <BanUserModal
          user={selectedUser}
          onConfirm={confirmBan}
          onCancel={() => {
            setShowBanModal(false);
            setSelectedUser(null);
          }}
        />
      )}

      {/* Delete User Modal */}
      {showDeleteModal && selectedUser && (
        <DeleteUserModal
          user={selectedUser}
          onConfirm={confirmDelete}
          onCancel={() => {
            setShowDeleteModal(false);
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

// Edit Role Modal Component
function EditRoleModal({ user, onConfirm, onCancel }) {
  const [selectedRole, setSelectedRole] = useState(user.role);

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
        <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: '0 0 8px 0' }}>
          Modifier le Rôle
        </h3>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: '0 0 24px 0' }}>
          Modifier le rôle de {user.username}
        </p>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
            Nouveau Rôle
          </label>
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #e5e7eb',
              borderRadius: '12px',
              fontSize: '14px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="USER">Utilisateur</option>
            <option value="ADMIN">Administrateur</option>
            <option value="SUPERADMIN">Super Administrateur</option>
          </select>
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
            onClick={() => onConfirm(selectedRole)}
            style={{
              padding: '12px 24px',
              backgroundColor: '#7c3aed',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Confirmer
          </button>
        </div>
      </div>
    </div>
  );
}

// Ban User Modal Component
function BanUserModal({ user, onConfirm, onCancel }) {
  const [reason, setReason] = useState('');

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
            backgroundColor: '#fed7aa',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Ban style={{ width: '24px', height: '24px', color: '#ea580c' }} />
          </div>
          <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
            Bannir l'Utilisateur
          </h3>
        </div>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: '0 0 24px 0' }}>
          Êtes-vous sûr de vouloir bannir {user.username} ? L'utilisateur ne pourra plus se connecter.
        </p>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
            Raison du Bannissement
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Entrez la raison du bannissement..."
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #e5e7eb',
              borderRadius: '12px',
              fontSize: '14px',
              outline: 'none',
              minHeight: '100px',
              resize: 'vertical',
              fontFamily: 'inherit'
            }}
          />
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
            onClick={() => onConfirm(reason)}
            disabled={!reason.trim()}
            style={{
              padding: '12px 24px',
              backgroundColor: !reason.trim() ? '#f3f4f6' : '#ea580c',
              color: !reason.trim() ? '#9ca3af' : 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: !reason.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            Bannir
          </button>
        </div>
      </div>
    </div>
  );
}

// Delete User Modal Component
function DeleteUserModal({ user, onConfirm, onCancel }) {
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
            <Trash2 style={{ width: '24px', height: '24px', color: '#ef4444' }} />
          </div>
          <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
            Supprimer l'Utilisateur
          </h3>
        </div>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: '0 0 24px 0' }}>
          Êtes-vous sûr de vouloir supprimer {user.username} ? Cette action est irréversible et toutes les données de l'utilisateur seront perdues.
        </p>

        <div style={{ 
          padding: '16px', 
          backgroundColor: '#fef2f2', 
          borderRadius: '12px', 
          marginBottom: '24px',
          border: '1px solid #fecaca'
        }}>
          <p style={{ fontSize: '13px', color: '#991b1b', margin: 0, fontWeight: '500' }}>
            ⚠️ Attention : Cette action est définitive et ne peut pas être annulée.
          </p>
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
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  );
}
