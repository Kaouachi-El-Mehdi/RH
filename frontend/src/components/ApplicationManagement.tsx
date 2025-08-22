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
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [showModal, setShowModal] = useState(false);
  // CV Analyzer logic
  const handleAnalyzeCV = async (cvUrl: string, appId?: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(cvUrl);
      if (!response.ok) throw new Error('Erreur lors du téléchargement du CV');
      const blob = await response.blob();
      const formData = new FormData();
      formData.append('cv_file', blob, 'cv.pdf');
      const aiResponse = await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api'}/ai/analyze/`, {
        method: 'POST',
        body: formData,
      });
      const result = await aiResponse.json();
      if (!aiResponse.ok) {
        setError('Erreur analyse IA: ' + (result.error || aiResponse.status));
      } else {
        setAnalysisResult(result);
        setShowModal(true);
        // Update backend with score
        if (appId && result.quality_score !== undefined) {
          const token = getAuthToken();
          await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api'}/candidates/applications/${appId}/update-ai-score/`, {
            method: 'POST',
            headers: {
              'Authorization': token ? `Bearer ${token}` : '',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ai_score: result.quality_score }),
          });
        }
      }
    } catch (e: any) {
      setError('Erreur analyse IA: ' + e.message);
    } finally {
      setLoading(false);
    }
  };
  // Modal for CV analysis result
  const AnalysisModal = () => (
    <div className={"modal fade " + (showModal ? "show d-block" : "") } tabIndex={-1} style={{ background: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header bg-info text-white">
            <h5 className="modal-title"><i className="bi bi-bar-chart"></i> Résultat Analyse CV</h5>
            <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
          </div>
          <div className="modal-body">
            {analysisResult ? (
              <>
                <div className="text-center mb-3">
                  <span style={{ fontSize: '2.5rem', fontWeight: 'bold', color: analysisResult.quality_score > 80 ? '#28a745' : analysisResult.quality_score > 50 ? '#ffc107' : '#dc3545' }}>
                    {analysisResult.quality_score ? analysisResult.quality_score.toFixed(2) : '--'}
                  </span>
                  <div className="fw-bold">Score IA</div>
                </div>
                <div className="mb-2">
                  <strong>Statut:</strong> <span className="badge bg-primary">{analysisResult.status}</span>
                </div>
                <div className="mb-2">
                  <strong>Domaine:</strong> <span className="badge bg-info text-dark">{analysisResult.domain}</span>
                </div>
                <div className="mb-2">
                  <strong>Compétences détectées:</strong>
                  <div className="d-flex flex-wrap mt-1">
                    {Array.isArray(analysisResult.skills) && analysisResult.skills.length > 0 ? (
                      analysisResult.skills.map((skill: string, idx: number) => (
                        <span key={idx} className="badge bg-secondary me-1 mb-1">{skill}</span>
                      ))
                    ) : <span className="text-muted">Aucune</span>}
                  </div>
                </div>
                <div className="mb-2">
                  <strong>Années d'expérience:</strong> <span className="badge bg-success">{analysisResult.experience_years ?? '--'}</span>
                </div>
                <div className="mb-2">
                  <strong>Fichier analysé:</strong> <span className="badge bg-light text-dark">{analysisResult.filename}</span>
                </div>
              </>
            ) : <span className="text-muted">Aucun résultat</span>}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Fermer</button>
          </div>
        </div>
      </div>
    </div>
  );
  const handleStatusUpdate = async (id: number, newStatus: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api'}/candidates/applications/${id}/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!response.ok) {
        let errText = '';
        try {
          const err = await response.json();
          errText = JSON.stringify(err);
        } catch (e) {
          errText = await response.text();
        }
        setError('Erreur lors de la mise à jour du statut: ' + errText);
        setLoading(false);
        return;
      }
      setApplications(applications.map(app => app.id === id ? { ...app, status: newStatus } : app));
      setLoading(false);
    } catch (e: any) {
      setError('Erreur lors de la mise à jour du statut: ' + e.message);
      setLoading(false);
    }
  };
  const handleDelete = async (id: number) => {
    if (!window.confirm('Confirmer la suppression de cette candidature ?')) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api'}/candidates/applications/${id}/`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        let errText = '';
        try {
          const err = await response.json();
          errText = JSON.stringify(err);
        } catch (e) {
          errText = await response.text();
        }
        setError('Erreur lors de la suppression: ' + errText);
        setLoading(false);
        return;
      }
      setApplications(applications.filter(app => app.id !== id));
      setLoading(false);
    } catch (e: any) {
      setError('Erreur lors de la suppression: ' + e.message);
      setLoading(false);
    }
  };
  const { user, getAuthToken } = useAuth();
  const token = getAuthToken();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      setLoading(true);
      console.log('Auth token:', token);
  fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api'}/candidates/applications/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(async (res) => {
          if (!res.ok) {
            let errText = '';
            try {
              const err = await res.json();
              errText = JSON.stringify(err);
            } catch (e) {
              errText = await res.text();
            }
            setError('Erreur lors du chargement des candidatures: ' + errText);
            setLoading(false);
            return;
          }
          const data = await res.json();
          setApplications(data.results || []);
          setLoading(false);
        })
        .catch((e) => {
          setError('Erreur lors du chargement des candidatures: ' + e.message);
          setLoading(false);
        });
    }
  }, [token]);

  // TODO: Add form for candidates to submit new application
  // TODO: Add delete button for admin/recruteur

  return (
    <div className="container py-4">
      <h2 className="mb-4">Gestion des Candidatures</h2>
      {loading && <p>Chargement...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <AnalysisModal />
      <div className="row justify-content-center">
        {applications.length === 0 && !loading ? (
          <div className="col-12"><p>Aucune candidature trouvée.</p></div>
        ) : (
          applications.map((app) => (
            <div key={app.id} className="col-lg-6 col-xl-5 mb-4 d-flex">
              <div className="card h-100 shadow-lg w-100 border-0" style={{ borderRadius: '1.25rem', background: 'linear-gradient(135deg, #f8fafc 80%, #e3eafc 100%)' }}>
                <div className="card-body p-4">
                  <div className="d-flex align-items-center mb-2">
                    <span className="me-2" style={{ fontSize: '2rem', color: '#3b82f6' }}><i className="bi bi-person-badge"></i></span>
                    <div>
                      <h5 className="card-title mb-0 fw-bold" style={{ fontSize: '1.3rem', color: '#222' }}>{app.candidate_name}</h5>
                      <h6 className="card-subtitle mb-0 text-muted" style={{ fontSize: '1rem' }}>
                        <span className="me-2"><i className="bi bi-briefcase"></i></span>{app.job_title}
                      </h6>
                    </div>
                  </div>
                  <div className="mb-3 d-flex align-items-center">
                    <span className={`badge px-3 py-2 me-2 text-uppercase fw-bold ${app.status === 'accepted' ? 'bg-success' : app.status === 'pending' ? 'bg-secondary' : app.status === 'rejected' ? 'bg-danger' : 'bg-info'}`}>{app.status}</span>
                    <span className="text-muted ms-2"><i className="bi bi-calendar"></i> {new Date(app.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="mb-2">
                    <strong style={{ color: '#3b82f6' }}>Lettre de motivation:</strong>
                    <div className="border rounded p-2 bg-light" style={{ maxHeight: '80px', overflow: 'auto', fontSize: '0.98em', background: '#f4f7fa' }}>
                      {app.cover_letter ? app.cover_letter.slice(0, 200) + (app.cover_letter.length > 200 ? '...' : '') : <span className="text-muted">Non fournie</span>}
                    </div>
                  </div>
                </div>
                <div className="card-footer d-flex flex-wrap align-items-center justify-content-between p-3" style={{ background: '#f0f4fa', borderBottomLeftRadius: '1.25rem', borderBottomRightRadius: '1.25rem' }}>
                  <div className="d-flex align-items-center">
                    <a href={app.cv_file} target="_blank" rel="noopener noreferrer" className="btn btn-outline-primary btn-sm me-2">
                      <i className="bi bi-file-earmark-arrow-down"></i> CV
                    </a>
                    <button className="btn btn-outline-danger btn-sm me-2" onClick={() => handleDelete(app.id)}>
                      <i className="bi bi-trash"></i> Supprimer
                    </button>
                    <button className="btn btn-primary btn-sm me-2" style={{ background: 'linear-gradient(90deg,#3b82f6,#6366f1)', border: 'none' }} onClick={() => handleAnalyzeCV(app.cv_file, app.id)}>
                      <i className="bi bi-search"></i> Analyser CV
                    </button>
                  </div>
                  <div className="d-flex align-items-center">
                    {(user?.role === 'admin' || user?.role === 'recruteur') && (
                      <>
                        <button className="btn btn-success btn-sm me-2" disabled={app.status === 'accepted'} onClick={() => handleStatusUpdate(app.id, 'accepted')}>
                          <i className="bi bi-check-circle"></i> Accepter
                        </button>
                        <button className="btn btn-outline-dark btn-sm" disabled={app.status === 'rejected'} onClick={() => handleStatusUpdate(app.id, 'rejected')}>
                          <i className="bi bi-x-circle"></i> Rejeter
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ApplicationManagement;
