import { useState, useEffect } from 'react';
import { Users, Search, Activity, TrendingUp, Mail, Link, Shield, AlertTriangle, CheckCircle, Clock, Calendar, BarChart3, PieChart } from 'lucide-react';
import { adminApi } from '../../services/adminApi';
import { Toast } from './Toast';

export function UserActivity() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [userActivity, setUserActivity] = useState(null);
  const [loadingActivity, setLoadingActivity] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  const closeToast = () => {
    setToast(null);
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await adminApi.getUsers(0, 1000);
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Failed to load users:', error);
      if (error.response?.status === 401) {
        showToast('Session expirée. Veuillez vous reconnecter.', 'error');
      } else {
        showToast('Erreur lors du chargement des utilisateurs', 'error');
      }
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const loadUserActivity = async (userId) => {
    try {
      setLoadingActivity(true);
      const response = await adminApi.getUserActivity(userId);
      setUserActivity(response.data);
    } catch (error) {
      console.error('Failed to load user activity:', error);
      showToast('Erreur lors du chargement de l\'activité utilisateur', 'error');
      setUserActivity(null);
    } finally {
      setLoadingActivity(false);
    }
  };

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    loadUserActivity(user.id);
  };

  const handleBackToList = () => {
    setSelectedUser(null);
    setUserActivity(null);
  };

  const filteredUsers = (users || []).filter(user => {
    const searchLower = searchTerm.toLowerCase();
    return (
      user.username.toLowerCase().includes(searchLower) ||
      user.email.toLowerCase().includes(searchLower)
    );
  });

  const formatDate = (dateString) => {
    if (!dateString) return 'Jamais';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getThreatColor = (threatLevel) => {
    switch (threatLevel) {
      case 'safe':
        return { bg: '#f0fdf4', text: '#166534', border: '#bbf7d0', icon: CheckCircle };
      case 'suspicious':
        return { bg: '#fef3c7', text: '#92400e', border: '#fde68a', icon: AlertTriangle };
      case 'dangerous':
        return { bg: '#fef2f2', text: '#991b1b', border: '#fecaca', icon: Shield };
      default:
        return { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb', icon: Activity };
    }
  };

  const getThreatLabel = (threatLevel) => {
    switch (threatLevel) {
      case 'safe':
        return 'Sûr';
      case 'suspicious':
        return 'Suspect';
      case 'dangerous':
        return 'Dangereux';
      default:
        return threatLevel;
    }
  };

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
          <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>Chargement...</p>
        </div>
      </div>
    );
  }

  // Show user activity details
  if (selectedUser && userActivity) {
    return (
      <div style={{ padding: '0' }}>
        {/* Header with Back Button */}
        <div style={{ marginBottom: '32px' }}>
          <button
            onClick={handleBackToList}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              backgroundColor: 'white',
              color: '#6b7280',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              marginBottom: '16px'
            }}
          >
            ← Retour à la liste
          </button>
          <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed', margin: '0 0 8px 0' }}>
            Activité de {userActivity.username}
          </h2>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
            {userActivity.email}
          </p>
        </div>

        {/* User Info Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '16px',
            padding: '24px',
            color: 'white'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <Activity style={{ width: '24px', height: '24px' }} />
              <div style={{ fontSize: '14px', opacity: 0.9 }}>Total Analyses</div>
            </div>
            <div style={{ fontSize: '36px', fontWeight: 'bold' }}>{userActivity.total_analyses || 0}</div>
          </div>

          <div style={{ 
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            borderRadius: '16px',
            padding: '24px',
            color: 'white'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <Mail style={{ width: '24px', height: '24px' }} />
              <div style={{ fontSize: '14px', opacity: 0.9 }}>Analyses Email</div>
            </div>
            <div style={{ fontSize: '36px', fontWeight: 'bold' }}>{userActivity.analyses_by_type?.email || 0}</div>
          </div>

          <div style={{ 
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            borderRadius: '16px',
            padding: '24px',
            color: 'white'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <Link style={{ width: '24px', height: '24px' }} />
              <div style={{ fontSize: '14px', opacity: 0.9 }}>Analyses URL</div>
            </div>
            <div style={{ fontSize: '36px', fontWeight: 'bold' }}>{userActivity.analyses_by_type?.url || 0}</div>
          </div>

          <div style={{ 
            background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            borderRadius: '16px',
            padding: '24px',
            color: 'white'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <Clock style={{ width: '24px', height: '24px' }} />
              <div style={{ fontSize: '14px', opacity: 0.9 }}>Dernière Connexion</div>
            </div>
            <div style={{ fontSize: '16px', fontWeight: '600' }}>
              {userActivity.last_login ? new Date(userActivity.last_login).toLocaleDateString('fr-FR', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              }) : 'Jamais'}
            </div>
          </div>
        </div>

        {/* Threat Breakdown */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '16px', 
          padding: '24px', 
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <PieChart style={{ width: '24px', height: '24px', color: '#7c3aed' }} />
            <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
              Répartition des Menaces
            </h3>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            {Object.entries(userActivity.threat_breakdown || {}).map(([level, count]) => {
              const colors = getThreatColor(level);
              const Icon = colors.icon;
              const percentage = userActivity.total_analyses > 0 
                ? ((count / userActivity.total_analyses) * 100).toFixed(1) 
                : 0;
              
              return (
                <div 
                  key={level}
                  style={{
                    padding: '20px',
                    backgroundColor: colors.bg,
                    border: `2px solid ${colors.border}`,
                    borderRadius: '12px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <Icon style={{ width: '20px', height: '20px', color: colors.text }} />
                    <span style={{ fontSize: '14px', fontWeight: '600', color: colors.text }}>
                      {getThreatLabel(level)}
                    </span>
                  </div>
                  <div style={{ fontSize: '28px', fontWeight: 'bold', color: colors.text, marginBottom: '4px' }}>
                    {count}
                  </div>
                  <div style={{ fontSize: '13px', color: colors.text, opacity: 0.8 }}>
                    {percentage}% du total
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Activity */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '16px', 
          padding: '24px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <BarChart3 style={{ width: '24px', height: '24px', color: '#7c3aed' }} />
            <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
              Activité Récente
            </h3>
          </div>

          {userActivity.recent_activity && userActivity.recent_activity.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {userActivity.recent_activity.map((activity, index) => {
                const colors = getThreatColor(activity.threat_level);
                const Icon = colors.icon;
                
                return (
                  <div 
                    key={activity.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px',
                      backgroundColor: '#f9fafb',
                      borderRadius: '12px',
                      border: '1px solid #e5e7eb'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
                      <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '10px',
                        backgroundColor: colors.bg,
                        border: `2px solid ${colors.border}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Icon style={{ width: '20px', height: '20px', color: colors.text }} />
                      </div>
                      
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
                          <span style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '4px 10px',
                            backgroundColor: activity.type === 'email' ? '#dbeafe' : '#fef3c7',
                            color: activity.type === 'email' ? '#1e40af' : '#92400e',
                            borderRadius: '6px',
                            fontSize: '12px',
                            fontWeight: '600'
                          }}>
                            {activity.type === 'email' ? <Mail style={{ width: '12px', height: '12px' }} /> : <Link style={{ width: '12px', height: '12px' }} />}
                            {activity.type === 'email' ? 'Email' : 'URL'}
                          </span>
                          
                          <span style={{
                            padding: '4px 10px',
                            backgroundColor: colors.bg,
                            color: colors.text,
                            border: `1px solid ${colors.border}`,
                            borderRadius: '6px',
                            fontSize: '12px',
                            fontWeight: '600'
                          }}>
                            {getThreatLabel(activity.threat_level)}
                          </span>
                          
                          <span style={{ fontSize: '13px', color: '#6b7280' }}>
                            Confiance: {(activity.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        
                        <div style={{ fontSize: '12px', color: '#9ca3af' }}>
                          {formatDate(activity.created_at)}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '48px' }}>
              <Activity style={{ width: '48px', height: '48px', color: '#d1d5db', margin: '0 auto 12px' }} />
              <p style={{ fontSize: '16px', fontWeight: '600', color: '#6b7280', margin: 0 }}>
                Aucune activité récente
              </p>
            </div>
          )}
        </div>

        {/* Account Info */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '16px', 
          padding: '24px',
          marginTop: '24px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', marginBottom: '16px' }}>
            Informations du Compte
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Nom d'utilisateur</div>
              <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>{userActivity.username}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Email</div>
              <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>{userActivity.email}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Membre depuis</div>
              <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>{formatDate(userActivity.created_at)}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Dernière connexion</div>
              <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>{formatDate(userActivity.last_login)}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show user list
  return (
    <div style={{ padding: '0' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed', margin: '0 0 8px 0' }}>
          Activité des Utilisateurs
        </h2>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
          Sélectionnez un utilisateur pour voir son activité détaillée
        </p>
      </div>

      {/* Search */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        padding: '24px', 
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
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
            placeholder="Rechercher un utilisateur..."
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
      </div>

      {/* Users Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
        {filteredUsers.length === 0 ? (
          <div style={{ 
            gridColumn: '1 / -1',
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '48px',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <Users style={{ width: '48px', height: '48px', color: '#d1d5db', margin: '0 auto 12px' }} />
            <p style={{ fontSize: '16px', fontWeight: '600', color: '#6b7280', margin: 0 }}>
              Aucun utilisateur trouvé
            </p>
          </div>
        ) : (
          filteredUsers.map((user) => (
            <div
              key={user.id}
              onClick={() => handleUserSelect(user)}
              style={{
                backgroundColor: 'white',
                borderRadius: '16px',
                padding: '24px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                border: '2px solid transparent'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#7c3aed';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'transparent';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                <div style={{ 
                  width: '56px', 
                  height: '56px', 
                  borderRadius: '50%', 
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '24px'
                }}>
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '16px', fontWeight: '700', color: '#111827', marginBottom: '4px' }}>
                    {user.username}
                  </div>
                  <div style={{ fontSize: '13px', color: '#6b7280' }}>
                    {user.email}
                  </div>
                </div>
              </div>
              
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                paddingTop: '16px',
                borderTop: '1px solid #f3f4f6'
              }}>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>
                  <Calendar style={{ width: '14px', height: '14px', display: 'inline', marginRight: '4px' }} />
                  {user.last_login ? new Date(user.last_login).toLocaleDateString('fr-FR', {
                    month: 'short',
                    day: 'numeric'
                  }) : 'Jamais'}
                </div>
                <div style={{
                  padding: '4px 12px',
                  backgroundColor: '#f3f4f6',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#374151'
                }}>
                  {user.role}
                </div>
              </div>
            </div>
          ))
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
      `}</style>
    </div>
  );
}
