import React from 'react';
import NotificationBell from './NotificationBell';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';

export type TabName = 'dashboard' | 'jobs' | 'applications' | 'users' | 'profile';

interface LayoutProps {
  activeTab: TabName;
  onTabChange: (tab: TabName) => void;
  children: React.ReactNode;
}

const navItems = [
  { key: 'dashboard', label: 'Tableau de bord', icon: 'bi bi-bar-chart' },
  { key: 'jobs', label: 'Offres', icon: 'bi bi-briefcase' },
  { key: 'applications', label: 'Candidatures', icon: 'bi bi-file-earmark-text' },
  { key: 'users', label: 'Utilisateurs', icon: 'bi bi-people' },
  { key: 'profile', label: 'Profil', icon: 'bi bi-person' },
];

const Layout: React.FC<LayoutProps> = ({ activeTab, onTabChange, children }) => {
  const { user, logout } = useAuth();
  const isAdmin = user?.role === 'admin';
  const isRecruteur = user?.role === 'recruteur';

  return (
    <div className="layout-container d-flex">
      {/* Sidebar */}
      <aside className="sidebar bg-white border-end">
        <div className="sidebar-header text-center py-3 border-bottom">
          <span className="fw-bold fs-5 text-primary">RH Management</span>
        </div>
        <ul className="nav flex-column mt-4">
          {navItems.map(item => {
            if ((item.key === 'dashboard' || item.key === 'users') && !(isAdmin || isRecruteur)) return null;
            return (
              <li key={item.key} className="nav-item">
                <button
                  className={`nav-link d-flex align-items-center px-3 py-2${activeTab === item.key ? ' active bg-primary text-white fw-bold' : ' text-dark'}`}
                  onClick={() => onTabChange(item.key as TabName)}
                  style={{ border: 'none', background: 'none', width: '100%', textAlign: 'left' }}
                >
                  <i className={`${item.icon} me-2`}></i>
                  {item.label}
                </button>
              </li>
            );
          })}
        </ul>
      </aside>

      {/* Main area */}
      <div className="main-area flex-grow-1">
        {/* Header */}
        <header className="header bg-primary text-white d-flex align-items-center justify-content-between px-4 py-2">
          <h4 className="mb-0">{navItems.find(i => i.key === activeTab)?.label}</h4>
          <div className="d-flex align-items-center">
            {/* Notification Bell (always visible) */}
            <NotificationBell />
            <span className="me-3">
              <strong>{user?.first_name} {user?.last_name}</strong> <span className="badge bg-light text-primary ms-2">{user?.role}</span>
            </span>
            <button className="btn btn-outline-light btn-sm" onClick={logout}>Déconnexion</button>
          </div>
        </header>
        {/* Content */}
        <main className="content-area p-4" style={{ background: '#f7f7f9', minHeight: '80vh' }}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
