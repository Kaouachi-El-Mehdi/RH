
import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface ApplicationStats {
  total: number;
  by_status: Array<{ status: string; count: number }>;
  avg_score: number;
  recent: Array<{
    id: number;
    job__title: string;
    status: string;
    ai_score: number;
    created_at: string;
    candidate_name?: string;
    job_title?: string;
  }>;
  // ...existing code...
}

const statusColors: { [key: string]: string } = {
  pending: '#ffc107',
  accepted: '#28a745',
  rejected: '#dc3545',
  interview: '#17a2b8',
};

const Dashboard: React.FC = () => {
  const { getAuthToken } = useAuth();
  const [stats, setStats] = useState<ApplicationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError('');
      try {
        const token = getAuthToken();
        const response = await fetch('http://localhost:8000/api/candidates/stats/', {
          headers: {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json',
          },
        });
        if (!response.ok) {
          throw new Error('Erreur lors de la récupération des statistiques');
        }
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [getAuthToken]);

  return (
    <div className="container py-4">
      <h2 className="mb-4">Tableau de Bord</h2>
      <p className="text-muted">Vue d'ensemble des statistiques des candidatures</p>
      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status" />
          <div>Chargement des statistiques...</div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : stats ? (
        <>
          <div className="row mb-4">
            <div className="col-md-4">
              <div className="card shadow-sm border-primary mb-3">
                <div className="card-body">
                  <h5 className="card-title">Total des candidatures</h5>
                  <p className="display-4 text-primary">{stats.total ?? '-'}</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card shadow-sm border-success mb-3">
                <div className="card-body">
                  <h5 className="card-title">Score IA moyen</h5>
                  <p className="display-4 text-success">{stats.avg_score !== undefined && stats.avg_score !== null ? stats.avg_score.toFixed(2) : '-'}</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card shadow-sm border-info mb-3">
                <div className="card-body">
                  <h5 className="card-title">Statut des candidatures</h5>
                  <div className="d-flex flex-wrap">
                    {Array.isArray(stats.by_status) && stats.by_status.length > 0 ? (
                      stats.by_status.map(({ status, count }) => (
                        <span
                          key={status}
                          className="badge mx-1"
                          style={{ backgroundColor: statusColors[status] || '#6c757d', color: '#fff', fontSize: '1rem' }}
                        >
                          {status}: {count}
                        </span>
                      ))
                    ) : (
                      <span className="text-muted">Aucun statut</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
          {/* Removed jobs AI scores table, restored previous dashboard layout */}
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h5 className="card-title">Candidatures récentes</h5>
              <div className="table-responsive">
                <table className="table table-striped">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Poste</th>
                      <th>Statut</th>
                      <th>Score IA</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Array.isArray(stats.recent) && stats.recent.length > 0 ? (
                      stats.recent.map((app, idx) => (
                        <tr key={app.id}>
                          <td>{idx + 1}</td>
                          <td>{app.job__title || '-'}</td>
                          <td>
                            <span
                              className="badge"
                              style={{ backgroundColor: statusColors[app.status] || '#6c757d', color: '#fff' }}
                            >
                              {app.status}
                            </span>
                          </td>
                          <td>{app.ai_score !== undefined && app.ai_score !== null ? app.ai_score.toFixed(2) : '-'}</td>
                          <td>{app.created_at ? new Date(app.created_at).toLocaleString() : '-'}</td>
                        </tr>
                      ))
                    ) : (
                      <tr><td colSpan={5} className="text-center text-muted">Aucune candidature récente</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default Dashboard;
