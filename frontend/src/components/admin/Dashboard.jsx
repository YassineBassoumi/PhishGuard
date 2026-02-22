import { useState, useEffect } from 'react';
import { Users, Shield, Activity, Mail, TrendingUp, AlertCircle, Clock, UserCheck, RefreshCw } from 'lucide-react';
import { adminApi } from '../../services/adminApi';

export function Dashboard() {
  const [stats, setStats] = useState(null);
  const [emailStats, setEmailStats] = useState(null);
  const [auditStats, setAuditStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setRefreshing(true);
      const [statsRes, emailRes, auditRes] = await Promise.all([
        adminApi.getStats(),
        adminApi.getEmailProviderStats(),
        adminApi.getAuditStats()
      ]);
      
      setStats(statsRes.data);
      setEmailStats(emailRes.data);
      setAuditStats(auditRes.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ position: 'relative', width: '64px', height: '64px', margin: '0 auto 16px' }}>
            <div style={{ 
              position: 'absolute',
              width: '64px', 
              height: '64px', 
              border: '4px solid #e9d5ff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
            <div style={{ 
              position: 'absolute',
              width: '64px', 
              height: '64px', 
              border: '4px solid transparent',
              borderTopColor: '#9333ea',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
          </div>
          <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>Chargement des statistiques...</p>
        </div>
      </div>
    );
  }

  const mainStats = [
    {
      title: 'UTILISATEURS TOTAUX',
      value: stats?.total_users || 0,
      icon: Users,
      color: '#3b82f6',
      bgColor: '#dbeafe',
      borderColor: '#3b82f6',
      change: '+12%'
    },
    {
      title: 'ANALYSES TOTALES',
      value: stats?.total_analyses || 0,
      icon: Activity,
      color: '#10b981',
      bgColor: '#d1fae5',
      borderColor: '#10b981',
      change: '+8%'
    },
    {
      title: 'UTILISATEURS BANNIS',
      value: stats?.banned_users || 0,
      icon: Shield,
      color: '#ef4444',
      bgColor: '#fee2e2',
      borderColor: '#ef4444',
      change: '0%'
    },
    {
      title: 'CONNEXIONS EMAIL',
      value: emailStats?.total_connections || 0,
      icon: Mail,
      color: '#8b5cf6',
      bgColor: '#ede9fe',
      borderColor: '#8b5cf6',
      change: '+2%'
    },
  ];

  return (
    <div style={{ padding: '0' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed', margin: '0 0 8px 0' }}>
            Vue d'ensemble
          </h2>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
            Statistiques en temps réel de la plateforme PhishGuard
          </p>
        </div>
        <button
          onClick={loadStats}
          disabled={refreshing}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            backgroundColor: refreshing ? '#f3f4f6' : '#7c3aed',
            color: refreshing ? '#9ca3af' : 'white',
            border: 'none',
            borderRadius: '12px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: refreshing ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => {
            if (!refreshing) e.currentTarget.style.backgroundColor = '#6d28d9';
          }}
          onMouseLeave={(e) => {
            if (!refreshing) e.currentTarget.style.backgroundColor = '#7c3aed';
          }}
        >
          <RefreshCw style={{ width: '16px', height: '16px', animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
          Actualiser
        </button>
      </div>

      {/* Main Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {mainStats.map((stat, index) => (
          <div
            key={index}
            style={{
              backgroundColor: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
              borderTop: `4px solid ${stat.borderColor}`,
              transition: 'transform 0.2s, box-shadow 0.2s',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <p style={{ fontSize: '11px', fontWeight: '600', color: '#6b7280', letterSpacing: '0.5px', margin: '0 0 8px 0' }}>
                  {stat.title}
                </p>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                  <h3 style={{ fontSize: '36px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
                    {stat.value}
                  </h3>
                  <span style={{ fontSize: '14px', fontWeight: '600', color: stat.change.startsWith('+') ? '#10b981' : '#6b7280' }}>
                    {stat.change}
                  </span>
                </div>
              </div>
              <div style={{ 
                width: '48px', 
                height: '48px', 
                borderRadius: '12px', 
                backgroundColor: stat.bgColor,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <stat.icon style={{ width: '24px', height: '24px', color: stat.color }} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Detailed Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {/* Users by Role */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '24px', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div style={{ 
              width: '40px', 
              height: '40px', 
              borderRadius: '10px', 
              backgroundColor: '#dbeafe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Users style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>
              Utilisateurs par Rôle
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {stats?.users_by_role && Object.entries(stats.users_by_role).map(([role, count]) => {
              const roleConfig = {
                'USER': { label: 'Utilisateurs', color: '#6b7280', bgColor: '#f3f4f6' },
                'ADMIN': { label: 'Administrateurs', color: '#3b82f6', bgColor: '#dbeafe' },
                'SUPERADMIN': { label: 'Super Admins', color: '#8b5cf6', bgColor: '#ede9fe' }
              };
              const config = roleConfig[role];
              return (
                <div key={role} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ 
                      width: '8px', 
                      height: '8px', 
                      borderRadius: '50%', 
                      backgroundColor: config.color 
                    }}></div>
                    <span style={{ fontSize: '14px', color: '#374151' }}>{config.label}</span>
                  </div>
                  <span style={{ fontSize: '18px', fontWeight: '700', color: '#111827' }}>{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Activity */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '24px', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div style={{ 
              width: '40px', 
              height: '40px', 
              borderRadius: '10px', 
              backgroundColor: '#d1fae5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Activity style={{ width: '20px', height: '20px', color: '#10b981' }} />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>
              Activité
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <UserCheck style={{ width: '16px', height: '16px', color: '#10b981' }} />
                <span style={{ fontSize: '14px', color: '#374151' }}>Utilisateurs Actifs</span>
              </div>
              <span style={{ fontSize: '18px', fontWeight: '700', color: '#111827' }}>{stats?.active_users || 0}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Clock style={{ width: '16px', height: '16px', color: '#3b82f6' }} />
                <span style={{ fontSize: '14px', color: '#374151' }}>Connexions (24h)</span>
              </div>
              <span style={{ fontSize: '18px', fontWeight: '700', color: '#111827' }}>{stats?.recent_logins_24h || 0}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle style={{ width: '16px', height: '16px', color: '#6b7280' }} />
                <span style={{ fontSize: '14px', color: '#374151' }}>Jamais Connectés</span>
              </div>
              <span style={{ fontSize: '18px', fontWeight: '700', color: '#111827' }}>{stats?.never_logged_in || 0}</span>
            </div>
          </div>
        </div>

        {/* Email Providers */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '24px', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div style={{ 
              width: '40px', 
              height: '40px', 
              borderRadius: '10px', 
              backgroundColor: '#ede9fe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Mail style={{ width: '20px', height: '20px', color: '#8b5cf6' }} />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>
              Fournisseurs Email
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {emailStats?.connections_by_provider && Object.entries(emailStats.connections_by_provider).map(([provider, count]) => (
              <div key={provider}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ 
                    fontSize: '12px', 
                    fontWeight: '600', 
                    color: 'white',
                    backgroundColor: provider === 'gmail' ? '#ef4444' : '#0ea5e9',
                    padding: '4px 12px',
                    borderRadius: '6px',
                    textTransform: 'uppercase'
                  }}>
                    {provider}
                  </span>
                  <span style={{ fontSize: '18px', fontWeight: '700', color: '#111827' }}>{count}</span>
                </div>
                <div style={{ 
                  width: '100%', 
                  height: '8px', 
                  backgroundColor: '#f3f4f6', 
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{ 
                    width: `${(count / (emailStats?.total_connections || 1)) * 100}%`,
                    height: '100%',
                    backgroundColor: provider === 'gmail' ? '#ef4444' : '#0ea5e9',
                    transition: 'width 0.3s ease'
                  }}></div>
                </div>
              </div>
            ))}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              paddingTop: '12px',
              borderTop: '1px solid #e5e7eb'
            }}>
              <span style={{ fontSize: '14px', color: '#6b7280' }}>Actives</span>
              <span style={{ fontSize: '16px', fontWeight: '700', color: '#10b981' }}>{emailStats?.active_connections || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '14px', color: '#6b7280' }}>Expirées</span>
              <span style={{ fontSize: '16px', fontWeight: '700', color: '#ef4444' }}>{emailStats?.expired_connections || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Admin Activity */}
      {auditStats && (
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '24px', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <div style={{ 
              width: '40px', 
              height: '40px', 
              borderRadius: '10px', 
              backgroundColor: '#ddd6fe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <TrendingUp style={{ width: '20px', height: '20px', color: '#7c3aed' }} />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>
              Activité Administrative Récente
            </h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px' }}>
            <div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ 
                  padding: '16px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '12px',
                  border: '1px solid #e5e7eb'
                }}>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 4px 0' }}>Total des Logs d'Audit</p>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#7c3aed', margin: 0 }}>{auditStats.total_logs}</p>
                  <p style={{ fontSize: '11px', color: '#9ca3af', margin: '4px 0 0 0' }}>Données cumulées</p>
                </div>
                <div style={{ 
                  padding: '16px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '12px',
                  border: '1px solid #e5e7eb'
                }}>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 4px 0' }}>Actions (24h)</p>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>{auditStats.recent_activity_24h}</p>
                  <p style={{ fontSize: '11px', color: '#9ca3af', margin: '4px 0 0 0' }}>Période courante</p>
                </div>
              </div>
            </div>
            {auditStats.most_active_admins && auditStats.most_active_admins.length > 0 && (
              <div>
                <p style={{ fontSize: '12px', fontWeight: '600', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.5px', margin: '0 0 16px 0' }}>
                  Administrateurs les Plus Actifs
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {auditStats.most_active_admins.slice(0, 3).map((admin, index) => (
                    <div 
                      key={index}
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between',
                        padding: '12px',
                        backgroundColor: '#f9fafb',
                        borderRadius: '12px',
                        border: '1px solid #e5e7eb',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#f3f4f6';
                        e.currentTarget.style.borderColor = '#7c3aed';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = '#f9fafb';
                        e.currentTarget.style.borderColor = '#e5e7eb';
                      }}
                    >
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
                          fontSize: '16px',
                          boxShadow: '0 4px 6px rgba(124, 58, 237, 0.3)'
                        }}>
                          {admin.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p style={{ fontSize: '14px', fontWeight: '600', color: '#111827', margin: 0 }}>
                            {admin.username}
                          </p>
                          <p style={{ fontSize: '11px', color: '#6b7280', margin: 0 }}>
                            {admin.action_count === 1 ? 'Admin' : 'Super Admin'}
                          </p>
                        </div>
                      </div>
                      <span style={{ 
                        fontSize: '14px', 
                        fontWeight: '700', 
                        color: '#7c3aed',
                        backgroundColor: '#ede9fe',
                        padding: '4px 12px',
                        borderRadius: '8px'
                      }}>
                        {admin.action_count} actions
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
