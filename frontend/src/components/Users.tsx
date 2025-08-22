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

const Users: React.FC = () => {
  const [editUser, setEditUser] = useState<User | null>(null);
  const [editForm, setEditForm] = useState<Partial<User>>({});
  const [actionLoading, setActionLoading] = useState(false);

  // Delete user handler
  const handleDelete = async (id: number) => {
    if (!window.confirm('Confirmer la suppression de cet utilisateur ?')) return;
    setActionLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/auth/users/${id}/`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setUsers(users.filter(u => u.id !== id));
      } else {
        alert('Erreur lors de la suppression');
      }
    } catch {
      alert('Erreur réseau');
    }
    setActionLoading(false);
  };

  // Edit user handler
  const handleEditClick = (user: User) => {
    setEditUser(user);
    setEditForm({ ...user });
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  };

  const handleEditSave = async () => {
    if (!editUser) return;
    setActionLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/auth/users/${editUser.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(editForm),
      });
      if (res.ok) {
        const updated = await res.json();
        setUsers(users.map(u => u.id === editUser.id ? updated : u));
        setEditUser(null);
      } else {
        alert('Erreur lors de la modification');
      }
    } catch {
      alert('Erreur réseau');
    }
    setActionLoading(false);
  };

  const handleEditCancel = () => setEditUser(null);
  const { user, getAuthToken } = useAuth();
  const token = getAuthToken();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token && (user?.role === 'admin' || user?.role === 'recruteur')) {
      setLoading(true);
  fetch('http://localhost:8000/api/auth/users/', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => {
          let allUsers = data.results || [];
          if (user?.role === 'recruteur') {
            // Only show candidates for recruiter
            setUsers(allUsers.filter((u: any) => u.role === 'candidat'));
          } else {
            // Show all users for admin
            setUsers(allUsers);
          }
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
      <table className="table table-bordered table-hover mt-3">
        <thead className="table-light">
          <tr>
            <th>Nom</th>
            <th>Email</th>
            <th>Téléphone</th>
            {user?.role === 'admin' && <th>Rôle</th>}
            {user?.role === 'admin' && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.first_name} {u.last_name}</td>
              <td>{u.email}</td>
              <td>{u.phone || '-'}</td>
              {user?.role === 'admin' && <td>{u.role}</td>}
              {user?.role === 'admin' && (
                <td>
                  <button className="btn btn-sm btn-outline-primary me-2" onClick={() => handleEditClick(u)} disabled={actionLoading}>Modifier</button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(u.id)} disabled={actionLoading}>Supprimer</button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Edit Modal */}
      {editUser && (
        <div className="modal show" style={{ display: 'block', background: 'rgba(0,0,0,0.3)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Modifier Utilisateur</h5>
                <button type="button" className="btn-close" onClick={handleEditCancel}></button>
              </div>
              <div className="modal-body">
                <input className="form-control mb-2" name="first_name" value={editForm.first_name || ''} onChange={handleEditChange} placeholder="Prénom" />
                <input className="form-control mb-2" name="last_name" value={editForm.last_name || ''} onChange={handleEditChange} placeholder="Nom" />
                <input className="form-control mb-2" name="email" value={editForm.email || ''} onChange={handleEditChange} placeholder="Email" />
                <input className="form-control mb-2" name="phone" value={editForm.phone || ''} onChange={handleEditChange} placeholder="Téléphone" />
                {/* Add more fields as needed */}
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={handleEditCancel} disabled={actionLoading}>Annuler</button>
                <button className="btn btn-primary" onClick={handleEditSave} disabled={actionLoading}>Enregistrer</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


export default Users;
