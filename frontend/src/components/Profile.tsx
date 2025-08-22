import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';

const Profile: React.FC = () => {
  const [editMode, setEditMode] = useState(false);
  const { user, getAuthToken } = useAuth();
  const token = getAuthToken();
  const [profile, setProfile] = useState<any>(null);
  const [form, setForm] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      setLoading(true);
      fetch(`${API_URL}/auth/profile/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(async res => {
          const data = await res.json();
          if (data.success) {
            setProfile(data.user);
            setForm({
              first_name: data.user.first_name || '',
              last_name: data.user.last_name || '',
              username: data.user.username || '',
              email: data.user.email || '',
              phone: data.user.phone || '',
              birth_date: data.user.birth_date || '',
              address: data.user.address || '',
            });
          } else {
            setError('Erreur lors du chargement du profil');
          }
          setLoading(false);
        })
        .catch(() => {
          setError('Erreur lors du chargement du profil');
          setLoading(false);
        });
    }
  }, [token]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm((prev: any) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await fetch(`${API_URL}/auth/profile/update/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Profil mis à jour avec succès !');
        setProfile(data.user);
      } else {
        setError('Erreur: ' + JSON.stringify(data.errors));
      }
    } catch (err: any) {
      setError('Erreur lors de la mise à jour: ' + err.message);
    }
    setLoading(false);
  };

  return (
    <div className="container py-4">
      <h2 className="mb-4">Mon Profil</h2>
      {loading && <p>Chargement...</p>}
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      {profile && !editMode && (
        <div className="card p-4 shadow-sm" style={{ maxWidth: 600 }}>
          <div className="mb-3"><strong>Prénom:</strong> {profile.first_name}</div>
          <div className="mb-3"><strong>Nom:</strong> {profile.last_name}</div>
          <div className="mb-3"><strong>Nom d'utilisateur:</strong> {profile.username}</div>
          <div className="mb-3"><strong>Email:</strong> {profile.email}</div>
          <div className="mb-3"><strong>Téléphone:</strong> {profile.phone || <span className="text-muted">Non renseigné</span>}</div>
          <div className="mb-3"><strong>Date de naissance:</strong> {profile.birth_date || <span className="text-muted">Non renseignée</span>}</div>
          <div className="mb-3"><strong>Adresse:</strong> {profile.address || <span className="text-muted">Non renseignée</span>}</div>
          <button className="btn btn-outline-primary mt-2" onClick={() => setEditMode(true)}>Modifier</button>
        </div>
      )}
      {profile && editMode && (
        <form className="card p-4 shadow-sm" onSubmit={handleSubmit} style={{ maxWidth: 600 }}>
          <div className="mb-3">
            <label className="form-label">Prénom</label>
            <input type="text" name="first_name" className="form-control" value={form.first_name} onChange={handleInputChange} />
          </div>
          <div className="mb-3">
            <label className="form-label">Nom</label>
            <input type="text" name="last_name" className="form-control" value={form.last_name} onChange={handleInputChange} />
          </div>
          <div className="mb-3">
            <label className="form-label">Nom d'utilisateur</label>
            <input type="text" name="username" className="form-control" value={form.username} onChange={handleInputChange} disabled />
          </div>
          <div className="mb-3">
            <label className="form-label">Email</label>
            <input type="email" name="email" className="form-control" value={form.email} onChange={handleInputChange} disabled />
          </div>
          <div className="mb-3">
            <label className="form-label">Téléphone</label>
            <input type="text" name="phone" className="form-control" value={form.phone} onChange={handleInputChange} />
          </div>
          <div className="mb-3">
            <label className="form-label">Date de naissance</label>
            <input type="date" name="birth_date" className="form-control" value={form.birth_date} onChange={handleInputChange} />
          </div>
          <div className="mb-3">
            <label className="form-label">Adresse</label>
            <textarea name="address" className="form-control" value={form.address} onChange={handleInputChange} rows={2} />
          </div>
          <div className="d-flex gap-2">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Enregistrement...' : 'Enregistrer'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => setEditMode(false)}>
              Annuler
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default Profile;
