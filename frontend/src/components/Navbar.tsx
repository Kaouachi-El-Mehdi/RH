import React from 'react';
import { useAuth } from '../contexts/AuthContext';
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
