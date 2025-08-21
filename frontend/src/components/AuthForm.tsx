import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './AuthForm.css';

interface AuthFormProps {
  onSuccess: () => void;
}

const AuthForm: React.FC<AuthFormProps> = ({ onSuccess }) => {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    first_name: '',
    last_name: '',
    role: 'recruteur' as 'admin' | 'recruteur' | 'candidat',
    confirmPassword: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        // Login
        const result = await login(formData.email, formData.password);
        if (result.success) {
          onSuccess();
        } else {
          setError(result.message || 'Email ou mot de passe incorrect');
        }
      } else {
        // Register
        if (formData.password !== formData.confirmPassword) {
          setError('Les mots de passe ne correspondent pas');
          setLoading(false);
          return;
        }

        const result = await register({
          email: formData.email,
          password: formData.password,
          password_confirm: formData.confirmPassword,
          username: formData.username,
          first_name: formData.first_name,
          last_name: formData.last_name,
          role: formData.role
        });

        if (result.success) {
          onSuccess();
        } else {
          setError(result.message || 'Erreur lors de la création du compte');
        }
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-overlay">
      <div className="auth-form">
        <div className="auth-header">
          <h2>{isLogin ? '🔐 Connexion' : '📝 Inscription'}</h2>
          <p>
            {isLogin 
              ? 'Connectez-vous à votre compte RH' 
              : 'Créez votre compte pour accéder au système RH'
            }
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <>
              <div className="form-row">
                <div className="form-group">
                  <label>Prénom *</label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    required={!isLogin}
                  />
                </div>
                <div className="form-group">
                  <label>Nom *</label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    required={!isLogin}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Nom d'utilisateur *</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required={!isLogin}
                />
              </div>

              <div className="form-group">
                <label>Rôle *</label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  required={!isLogin}
                >
                  <option value="recruteur">🏢 Recruteur</option>
                  <option value="candidat">👤 Candidat</option>
                  <option value="admin">👑 Administrateur</option>
                </select>
              </div>
            </>
          )}

          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Mot de passe *</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>Confirmer le mot de passe *</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required={!isLogin}
              />
            </div>
          )}

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <button 
            type="submit" 
            className="auth-submit-btn"
            disabled={loading}
          >
            {loading 
              ? (isLogin ? '🔄 Connexion...' : '🔄 Création...') 
              : (isLogin ? '🚀 Se connecter' : '✨ Créer le compte')
            }
          </button>
        </form>

        <div className="auth-switch">
          <p>
            {isLogin ? "Pas encore de compte ?" : "Déjà un compte ?"}
            <button
              type="button"
              className="switch-btn"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setFormData({
                  email: '',
                  password: '',
                  username: '',
                  first_name: '',
                  last_name: '',
                  role: 'recruteur',
                  confirmPassword: ''
                });
              }}
            >
              {isLogin ? 'Créer un compte' : 'Se connecter'}
            </button>
          </p>
        </div>

        <div className="demo-accounts">
          <h4>🧪 Comptes de démonstration</h4>
          <div className="demo-grid">
            <div className="demo-card">
              <strong>👑 Admin</strong>
              <p>admin@rh.com / admin123</p>
            </div>
            <div className="demo-card">
              <strong>🏢 Recruteur</strong>
              <p>recruteur@rh.com / recruteur123</p>
            </div>
            <div className="demo-card">
              <strong>👤 Candidat</strong>
              <p>candidat@rh.com / candidat123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthForm;
