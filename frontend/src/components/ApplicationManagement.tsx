import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Application {
  id: number;
  candidate_name: string;
  job_title: string;
  cv_file: string;
  cover_letter: string;
  status: string;
  created_at: string;
}

const ApplicationManagement: React.FC = () => {
  const { user, getAuthToken } = useAuth();
  const token = getAuthToken();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      setLoading(true);
      fetch('/api/candidates/applications/', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => {
          setApplications(data.results || []);
          setLoading(false);
        })
        .catch(() => {
          setError('Erreur lors du chargement des candidatures');
          setLoading(false);
        });
    }
  }, [token]);

  // TODO: Add form for candidates to submit new application
  // TODO: Add delete button for admin/recruteur

  return (
    <div>
      <h2>Gestion des Candidatures</h2>
      {loading && <p>Chargement...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Candidat</th>
            <th>Offre</th>
            <th>Statut</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app) => (
            <tr key={app.id}>
              <td>{app.candidate_name}</td>
              <td>{app.job_title}</td>
              <td>{app.status}</td>
              <td>{new Date(app.created_at).toLocaleDateString()}</td>
              <td>
                {/* TODO: Show delete button for admin/recruteur */}
                {/* TODO: Show download/view CV button */}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ApplicationManagement;
