import React, { useEffect, useState, useContext } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  phone?: string;
  birth_date?: string;
  address?: string;
  profile_picture?: string;
  is_verified: boolean;
  created_at: string;
}

const UserManagement: React.FC = () => {
  const { user, getAuthToken } = useAuth();
  const token = getAuthToken();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token && (user?.role === 'admin' || user?.role === 'recruteur')) {
      setLoading(true);
      fetch('/api/accounts/users/', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => {
          setUsers(data.results || []);
          setLoading(false);
        })
        .catch(() => {
          setError('Erreur lors du chargement des utilisateurs');
          setLoading(false);
        });
    }
  }, [token, user]);

  if (!token || (user?.role !== 'admin' && user?.role !== 'recruteur')) {
    return <div>Accès refusé.</div>;
  }

  return (
    <div>
      <h2>Gestion des Utilisateurs</h2>
      {loading && <p>Chargement...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Nom</th>
            <th>Rôle</th>
            <th>Téléphone</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.email}</td>
              <td>{u.first_name} {u.last_name}</td>
              <td>{u.role}</td>
              <td>{u.phone || '-'}</td>
              <td>
                {/* TODO: Add edit/delete buttons for admin */}
                {user?.role === 'admin' && (
                  <>
                    <button>Modifier</button>
                    <button>Supprimer</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserManagement;
