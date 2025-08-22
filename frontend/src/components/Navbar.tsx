import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNotifications } from '../contexts/NotificationContext';
import './Navbar.css';

type TabName = 'dashboard' | 'jobs' | 'applications' | 'users' | 'profile';
interface NavbarProps {
  activeTab: TabName;
  onTabChange: (tab: TabName) => void;
}

const Navbar: React.FC<NavbarProps> = ({ activeTab, onTabChange }) => {
  const { user, logout } = useAuth();
  const isAdmin = user?.role === 'admin';
  const isRecruteur = user?.role === 'recruteur';
  const handleLogout = () => {
    logout();
    window.location.reload();
  };
  let notifications: any[] = [];
  let unreadCount = 0;
  let markAsRead = (id: any) => {};
  const [showDropdown, setShowDropdown] = useState(false);
  try {
    // Try to use notification context if available
    ({ notifications, unreadCount, markAsRead } = useNotifications());
  } catch (e) {
    // Fallback: static bell and dropdown
    notifications = [];
    unreadCount = 0;
    markAsRead = (id: any) => {};
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light mb-4">
      <div className="container-fluid">
        <a className="navbar-brand fw-bold" href="#">RH Management</a>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            {(isAdmin || isRecruteur) && (
              <li className="nav-item">
                <button className={`nav-link btn btn-link${activeTab === 'dashboard' ? ' active fw-bold' : ''}`} onClick={() => onTabChange('dashboard')}>Tableau de Bord</button>
              </li>
            )}
            <li className="nav-item">
              <button className={`nav-link btn btn-link${activeTab === 'jobs' ? ' active fw-bold' : ''}`} onClick={() => onTabChange('jobs')}>Offres d'emploi</button>
            </li>
            <li className="nav-item">
              <button className={`nav-link btn btn-link${activeTab === 'applications' ? ' active fw-bold' : ''}`} onClick={() => onTabChange('applications')}>Candidatures</button>
            </li>
            {(isAdmin || isRecruteur) && (
              <li className="nav-item">
                <button className={`nav-link btn btn-link${activeTab === 'users' ? ' active fw-bold' : ''}`} onClick={() => onTabChange('users')}>Utilisateurs</button>
              </li>
            )}
            <li className="nav-item">
              <button className={`nav-link btn btn-link${activeTab === 'profile' ? ' active fw-bold' : ''}`} onClick={() => onTabChange('profile')}>Profil</button>
            </li>
          </ul>
          <div className="d-flex align-items-center">
            {/* Notification Bell (always visible) */}
            <div className="position-relative me-3">
              <button className="btn btn-link position-relative" onClick={() => setShowDropdown(!showDropdown)}>
                <span className="bi bi-bell" style={{ fontSize: '1.5rem' }}></span>
                {unreadCount > 0 && (
                  <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                    {unreadCount}
                  </span>
                )}
              </button>
              {showDropdown && (
                <div className="dropdown-menu show p-2" style={{ minWidth: 300, right: 0, left: 'auto' }}>
                  <h6 className="dropdown-header">Notifications</h6>
                  {notifications.length === 0 ? (
                    <span className="dropdown-item-text">Aucune notification</span>
                  ) : (
                    notifications.slice(0, 8).map((n) => (
                      <div key={n.id} className={`dropdown-item d-flex align-items-start${n.is_read ? '' : ' fw-bold'}`} style={{ cursor: 'pointer' }} onClick={() => markAsRead(n.id)}>
                        <span className={`me-2 bi ${n.is_read ? 'bi-bell' : 'bi-bell-fill'}`}></span>
                        <div>
                          <div>{n.title}</div>
                          <small className="text-muted">{n.message}</small>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
            <span className="me-3">
              <strong>{user?.first_name} {user?.last_name}</strong> <span className="badge bg-secondary">{user?.role}</span>
            </span>
            <button className="btn btn-outline-danger btn-sm" onClick={handleLogout}>Déconnexion</button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
