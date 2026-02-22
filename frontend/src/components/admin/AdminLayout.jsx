import { useState } from 'react';
import { 
  Users, 
  Activity, 
  Shield, 
  FileText, 
  Mail, 
  BarChart3,
  Menu,
  X,
  LogOut,
  Home
} from 'lucide-react';

const navigation = [
  { name: 'Tableau de Bord', icon: BarChart3, id: 'dashboard' },
  { name: 'Utilisateurs', icon: Users, id: 'users' },
  { name: 'Utilisateurs Bannis', icon: Shield, id: 'banned' },
  { name: 'Journaux d\'Audit', icon: FileText, id: 'audit' },
  { name: 'Fournisseurs Email', icon: Mail, id: 'email-providers' },
  { name: 'Activité Utilisateur', icon: Activity, id: 'activity' },
];

export function AdminLayout({ children, currentView, onViewChange, user, onLogout, onBackToApp }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'linear-gradient(to bottom right, #f9fafb, #f9fafb, #faf5ff)' }}>
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(17, 24, 39, 0.5)',
            backdropFilter: 'blur(4px)',
            zIndex: 40
          }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <div 
        style={{
          position: 'fixed',
          top: 0,
          bottom: 0,
          left: 0,
          width: '288px',
          backgroundColor: 'white',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
          transition: 'transform 0.3s ease-in-out',
          zIndex: 50,
          display: window.innerWidth >= 1024 ? 'none' : 'flex',
          flexDirection: 'column'
        }}
      >
        <div style={{ display: 'flex', height: '64px', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', borderBottom: '1px solid #e5e7eb', background: 'linear-gradient(to right, #9333ea, #4f46e5)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Shield style={{ height: '28px', width: '28px', color: 'white' }} />
            <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: 'white', margin: 0 }}>Panneau Admin</h2>
          </div>
          <button 
            onClick={() => setSidebarOpen(false)}
            style={{ color: 'white', background: 'transparent', border: 'none', borderRadius: '8px', padding: '6px', cursor: 'pointer' }}
          >
            <X style={{ height: '20px', width: '20px' }} />
          </button>
        </div>
        <nav style={{ flex: 1, padding: '16px 12px', overflowY: 'auto' }}>
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                onViewChange(item.id);
                setSidebarOpen(false);
              }}
              style={{
                display: 'flex',
                width: '100%',
                alignItems: 'center',
                gap: '12px',
                borderRadius: '12px',
                padding: '12px 16px',
                fontSize: '14px',
                fontWeight: '500',
                border: 'none',
                cursor: 'pointer',
                marginBottom: '4px',
                background: currentView === item.id ? 'linear-gradient(to right, #9333ea, #4f46e5)' : 'transparent',
                color: currentView === item.id ? 'white' : '#374151',
                boxShadow: currentView === item.id ? '0 10px 15px -3px rgba(147, 51, 234, 0.3)' : 'none',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                if (currentView !== item.id) {
                  e.currentTarget.style.backgroundColor = '#f3f4f6';
                  e.currentTarget.style.transform = 'translateX(4px)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== item.id) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.transform = 'translateX(0)';
                }
              }}
            >
              <item.icon style={{ height: '20px', width: '20px', flexShrink: 0 }} />
              <span>{item.name}</span>
            </button>
          ))}
        </nav>
        <div style={{ borderTop: '1px solid #e5e7eb', padding: '16px', backgroundColor: '#f9fafb' }}>
          <button
            onClick={onBackToApp}
            style={{
              display: 'flex',
              width: '100%',
              alignItems: 'center',
              gap: '12px',
              borderRadius: '12px',
              padding: '12px 16px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              marginBottom: '8px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <Home style={{ height: '20px', width: '20px' }} />
            <span>Retour à l'App</span>
          </button>
          <button
            onClick={onLogout}
            style={{
              display: 'flex',
              width: '100%',
              alignItems: 'center',
              gap: '12px',
              borderRadius: '12px',
              padding: '12px 16px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#dc2626',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#fef2f2';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <LogOut style={{ height: '20px', width: '20px' }} />
            <span>Déconnexion</span>
          </button>
        </div>
      </div>

      {/* Desktop sidebar */}
      <aside style={{
        position: 'fixed',
        top: 0,
        bottom: 0,
        left: 0,
        width: '288px',
        backgroundColor: 'white',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        borderRight: '1px solid #e5e7eb',
        zIndex: 50,
        display: window.innerWidth >= 1024 ? 'flex' : 'none',
        flexDirection: 'column',
        overflowY: 'auto'
      }}>
        <div style={{ display: 'flex', height: '64px', alignItems: 'center', padding: '0 24px', borderBottom: '1px solid #e5e7eb', background: 'linear-gradient(to right, #9333ea, #4f46e5)', flexShrink: 0 }}>
          <Shield style={{ height: '32px', width: '32px', color: 'white' }} />
          <h2 style={{ marginLeft: '12px', fontSize: '20px', fontWeight: 'bold', color: 'white', margin: '0 0 0 12px' }}>Panneau Admin</h2>
        </div>
        <nav style={{ flex: 1, padding: '16px 12px', overflowY: 'auto' }}>
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              style={{
                display: 'flex',
                width: '100%',
                alignItems: 'center',
                gap: '12px',
                borderRadius: '12px',
                padding: '12px 16px',
                fontSize: '14px',
                fontWeight: '500',
                border: 'none',
                cursor: 'pointer',
                marginBottom: '4px',
                background: currentView === item.id ? 'linear-gradient(to right, #9333ea, #4f46e5)' : 'transparent',
                color: currentView === item.id ? 'white' : '#374151',
                boxShadow: currentView === item.id ? '0 10px 15px -3px rgba(147, 51, 234, 0.3)' : 'none',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                if (currentView !== item.id) {
                  e.currentTarget.style.backgroundColor = '#f3f4f6';
                  e.currentTarget.style.transform = 'translateX(4px)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== item.id) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.transform = 'translateX(0)';
                }
              }}
            >
              <item.icon style={{ height: '20px', width: '20px', flexShrink: 0 }} />
              <span>{item.name}</span>
            </button>
          ))}
        </nav>
        <div style={{ borderTop: '1px solid #e5e7eb', padding: '16px', backgroundColor: '#f9fafb', flexShrink: 0 }}>
          <button
            onClick={onBackToApp}
            style={{
              display: 'flex',
              width: '100%',
              alignItems: 'center',
              gap: '12px',
              borderRadius: '12px',
              padding: '12px 16px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              marginBottom: '8px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <Home style={{ height: '20px', width: '20px' }} />
            <span>Retour à l'App</span>
          </button>
          <button
            onClick={onLogout}
            style={{
              display: 'flex',
              width: '100%',
              alignItems: 'center',
              gap: '12px',
              borderRadius: '12px',
              padding: '12px 16px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#dc2626',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#fef2f2';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <LogOut style={{ height: '20px', width: '20px' }} />
            <span>Déconnexion</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div style={{ marginLeft: window.innerWidth >= 1024 ? '288px' : '0', flex: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* Top bar */}
        <div style={{ position: 'sticky', top: 0, zIndex: 30, display: 'flex', height: '64px', alignItems: 'center', gap: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: 'rgba(255, 255, 255, 0.8)', backdropFilter: 'blur(12px)', padding: '0 16px', boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)' }}>
          <button
            type="button"
            style={{ padding: '10px', color: '#374151', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', display: window.innerWidth >= 1024 ? 'none' : 'block' }}
            onClick={() => setSidebarOpen(true)}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            <Menu style={{ height: '24px', width: '24px' }} />
          </button>

          <div style={{ display: 'flex', flex: 1, gap: '16px', alignItems: 'center' }}>
            <div style={{ flex: 1 }}>
              <h1 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: 0 }}>
                {navigation.find(item => item.id === currentView)?.name || 'Tableau de Bord'}
              </h1>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', backgroundColor: '#f9fafb', borderRadius: '12px', padding: '8px 16px', border: '1px solid #e5e7eb' }}>
              <div style={{ textAlign: 'right' }}>
                <p style={{ fontSize: '14px', fontWeight: '600', color: '#111827', margin: 0 }}>{user?.username}</p>
                <p style={{ fontSize: '12px', color: '#9333ea', fontWeight: '500', margin: 0 }}>{user?.role}</p>
              </div>
              <div style={{ height: '40px', width: '40px', borderRadius: '50%', background: user?.profile_picture ? 'transparent' : 'linear-gradient(to bottom right, #9333ea, #4f46e5)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', overflow: 'hidden' }}>
                {user?.profile_picture ? (
                  <img 
                    src={`http://localhost:8000/api/profile/picture/${user.profile_picture}`} 
                    alt="Profile"
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  user?.username?.charAt(0).toUpperCase()
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main style={{ padding: '32px 16px', flex: 1 }}>
          <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
