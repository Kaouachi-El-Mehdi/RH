import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Job {
  id: number;
  title: string;
  company_name: string;
  location: string;
  contract_type: string;
  experience_required: string;
  salary_min: number;
  salary_max: number;
  description: string;
}

const Jobs: React.FC = () => {
  const [categories, setCategories] = useState<{ id: number; name: string }[]>([]);
  const { user, getAuthToken } = useAuth();
  const token = getAuthToken();

  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    category: 1,
    company_name: '',
    description: '',
    requirements: '',
    responsibilities: '',
    benefits: '',
    location: '',
    is_remote: false,
    contract_type: 'cdi',
    experience_required: '0-1',
    salary_min: 0,
    salary_max: 0,
    skills_required: '',
    status: 'published',
    application_deadline: '',
    max_applications: '',
  });

  // Ajout des états pour l'édition
  const [editJob, setEditJob] = useState<Job | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editFormData, setEditFormData] = useState<any>({});

  // Charger les catégories
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/jobs/categories/')
      .then(res => res.json())
      .then(data => setCategories(data.results || []))
      .catch(() => setCategories([]));
  }, []);

  // Charger les offres
  useEffect(() => {
    setLoading(true);
    fetch('http://127.0.0.1:8000/api/jobs/', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then(async res => {
        if (!res.ok) {
          const err = await res.json();
          setError(err?.detail || 'Erreur lors du chargement des offres');
          setLoading(false);
          return;
        }
        const data = await res.json();
        setJobs(data.results || []);
        setLoading(false);
      })
      .catch(e => {
        setError('Erreur lors du chargement des offres: ' + e.message);
        setLoading(false);
      });
  }, [token, showForm]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...formData,
        category: Number(formData.category),
        salary_min: Number(formData.salary_min),
        salary_max: Number(formData.salary_max),
        max_applications: formData.max_applications
          ? Number(formData.max_applications)
          : null,
        status: 'published',
      };

      const response = await fetch('http://127.0.0.1:8000/api/jobs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const err = await response.json();
        setError(err?.message || err?.detail || JSON.stringify(err) || 'Erreur lors de la création');
      } else {
        setShowForm(false);
        setFormData({
          title: '',
          category: 1,
          company_name: '',
          description: '',
          requirements: '',
          responsibilities: '',
          benefits: '',
          location: '',
          is_remote: false,
          contract_type: 'cdi',
          experience_required: '0-1',
          salary_min: 0,
          salary_max: 0,
          skills_required: '',
          status: 'published',
          application_deadline: '',
          max_applications: '',
        });
      }
    } catch {
      setError('Erreur serveur');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteJob = async (jobId: number) => {
    if (!window.confirm('Confirmer la suppression de cette offre ?')) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/jobs/${jobId}/`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) {
        const err = await response.json();
        setError(
          err?.message || err?.detail || JSON.stringify(err) || 'Erreur lors de la suppression'
        );
      } else {
        setJobs(jobs.filter(job => job.id !== jobId));
      }
    } catch {
      setError('Erreur serveur');
    } finally {
      setLoading(false);
    }
  };

  // Ouvre le modal d'édition
  const handleEditClick = (job: Job) => {
    setEditJob(job);
    setEditFormData({ ...job });
    setShowEditModal(true);
  };

  // Gère la modification des champs du formulaire d'édition
  const handleEditInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditFormData((prev: any) => ({ ...prev, [name]: value }));
  };

  // Soumet la modification
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editJob) return;
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...editFormData,
        category: Number(editFormData.category),
        salary_min: Number(editFormData.salary_min),
        salary_max: Number(editFormData.salary_max),
        max_applications: editFormData.max_applications ? Number(editFormData.max_applications) : null,
      };
      const response = await fetch(`http://127.0.0.1:8000/api/jobs/${editJob.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const err = await response.json();
        setError(err?.message || err?.detail || JSON.stringify(err) || 'Erreur lors de la modification');
      } else {
        setShowEditModal(false);
        setEditJob(null);
        setEditFormData({});
        // Recharge la liste
        fetch('http://127.0.0.1:8000/api/jobs/', {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
          .then(async res => {
            const data = await res.json();
            setJobs(data.results || []);
          });
      }
    } catch {
      setError('Erreur serveur');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>Offres d'emploi</h2>
        {(user?.role === 'admin' || user?.role === 'recruteur') && (
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Annuler' : 'Créer une offre'}
          </button>
        )}
      </div>

      {showForm && (
        <form className="card p-3 mb-4" onSubmit={handleCreateJob}>
          <div className="row g-2">
            <div className="col-md-6">
              <select
                className="form-select"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                required
              >
                <option value="">Sélectionner une catégorie</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-6">
              <input
                className="form-control"
                name="title"
                placeholder="Titre"
                value={formData.title}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="col-md-6">
              <input
                className="form-control"
                name="company_name"
                placeholder="Entreprise"
                value={formData.company_name}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="col-md-6">
              <input
                className="form-control"
                name="location"
                placeholder="Lieu"
                value={formData.location}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="col-md-6">
              <select
                className="form-select"
                name="contract_type"
                value={formData.contract_type}
                onChange={handleInputChange}
                required
              >
                <option value="cdi">CDI</option>
                <option value="cdd">CDD</option>
                <option value="interim">Intérim</option>
                <option value="stage">Stage</option>
                <option value="freelance">Freelance</option>
              </select>
            </div>
            <div className="col-md-6">
              <select
                className="form-select"
                name="experience_required"
                value={formData.experience_required}
                onChange={handleInputChange}
                required
              >
                <option value="0-1">0-1 an</option>
                <option value="1-3">1-3 ans</option>
                <option value="3-5">3-5 ans</option>
                <option value="5-10">5-10 ans</option>
                <option value="10+">10+ ans</option>
              </select>
            </div>
            <div className="col-md-6">
              <input
                className="form-control"
                type="number"
                name="salary_min"
                placeholder="Salaire min"
                value={formData.salary_min}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="col-md-6">
              <input
                className="form-control"
                type="number"
                name="salary_max"
                placeholder="Salaire max"
                value={formData.salary_max}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="col-12">
              <textarea
                className="form-control"
                name="description"
                placeholder="Description"
                value={formData.description}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="col-md-6">
              <label className="form-label">Date limite de candidature</label>
              <input
                className="form-control"
                type="datetime-local"
                name="application_deadline"
                value={formData.application_deadline}
                onChange={handleInputChange}
              />
            </div>
            <div className="col-md-6">
              <label className="form-label">Nombre max de candidatures</label>
              <input
                className="form-control"
                type="number"
                name="max_applications"
                value={formData.max_applications}
                onChange={handleInputChange}
                min={1}
              />
            </div>
            <div className="col-12">
              <input
                className="form-control"
                name="requirements"
                placeholder="Exigences"
                value={formData.requirements}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="col-12">
              <textarea
                className="form-control"
                name="responsibilities"
                placeholder="Responsabilités"
                value={formData.responsibilities}
                onChange={handleInputChange}
              />
            </div>
            <div className="col-12">
              <textarea
                className="form-control"
                name="benefits"
                placeholder="Avantages"
                value={formData.benefits}
                onChange={handleInputChange}
              />
            </div>
            <div className="col-12">
              <input
                className="form-check-input"
                type="checkbox"
                name="is_remote"
                checked={formData.is_remote}
                onChange={e =>
                  setFormData(prev => ({ ...prev, is_remote: e.target.checked }))
                }
              />{' '}
              Télétravail possible
            </div>
            <div className="col-12">
              <input
                className="form-control"
                name="skills_required"
                placeholder="Compétences requises (séparées par des virgules)"
                value={formData.skills_required}
                onChange={handleInputChange}
              />
            </div>
          </div>
          {error && <div className="text-danger mt-2">{error}</div>}
          <button className="btn btn-success mt-3" type="submit" disabled={loading}>
            {loading ? 'Création...' : 'Créer'}
          </button>
        </form>
      )}

      {loading && <p>Chargement...</p>}
      {error && <p className="text-danger">{error}</p>}

      <div className="row">
        {jobs.length === 0 && !loading ? (
          <div className="col-12">
            <p>Aucune offre disponible.</p>
          </div>
        ) : (
          jobs.map(job => (
            <div key={job.id} className="col-md-6 col-lg-4 mb-4">
              <div className="card h-100">
                <div className="card-body">
                  <h5 className="card-title">{job.title}</h5>
                  <h6 className="card-subtitle mb-2 text-muted">{job.company_name}</h6>
                  <p className="card-text">
                    {job.location} | {job.contract_type}
                  </p>
                  <p className="card-text">
                    Expérience requise: {job.experience_required}
                  </p>
                  <p className="card-text">
                    Salaire: {job.salary_min} - {job.salary_max} €
                  </p>
                  <p className="card-text">{job.description}</p>

                  {user?.role === 'candidat' && (
                    <button className="btn btn-outline-primary btn-sm">Postuler</button>
                  )}

                  {(user?.role === 'admin' || user?.role === 'recruteur') && (
                    <>
                      <button className="btn btn-warning btn-sm" onClick={() => handleEditClick(job)}>
                        Edit
                      </button>
                      <button
                        className="btn btn-outline-danger btn-sm ms-2"
                        onClick={() => handleDeleteJob(job.id)}
                      >
                        Supprimer
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {showEditModal && editJob && (
        <div className="modal show d-block" tabIndex={-1}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Modifier l'offre</h5>
                <button type="button" className="btn-close" onClick={() => setShowEditModal(false)}></button>
              </div>
              <form onSubmit={handleEditSubmit}>
                <div className="modal-body">
                  <div className="mb-2">
                    <select className="form-select" name="category" value={editFormData.category} onChange={handleEditInputChange} required>
                      <option value="">Sélectionner une catégorie</option>
                      {categories.map(cat => (
                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="mb-2">
                    <input className="form-control" name="title" value={editFormData.title} onChange={handleEditInputChange} required />
                  </div>
                  <div className="mb-2">
                    <input className="form-control" name="company_name" value={editFormData.company_name} onChange={handleEditInputChange} required />
                  </div>
                  <div className="mb-2">
                    <input className="form-control" name="location" value={editFormData.location} onChange={handleEditInputChange} required />
                  </div>
                  <div className="mb-2">
                    <select className="form-select" name="contract_type" value={editFormData.contract_type} onChange={handleEditInputChange} required>
                      <option value="cdi">CDI</option>
                      <option value="cdd">CDD</option>
                      <option value="interim">Intérim</option>
                      <option value="stage">Stage</option>
                      <option value="freelance">Freelance</option>
                    </select>
                  </div>
                  <div className="mb-2">
                    <select className="form-select" name="experience_required" value={editFormData.experience_required} onChange={handleEditInputChange} required>
                      <option value="0-1">0-1 an</option>
                      <option value="1-3">1-3 ans</option>
                      <option value="3-5">3-5 ans</option>
                      <option value="5-10">5-10 ans</option>
                      <option value="10+">10+ ans</option>
                    </select>
                  </div>
                  <div className="mb-2">
                    <input className="form-control" type="number" name="salary_min" value={editFormData.salary_min} onChange={handleEditInputChange} required />
                  </div>
                  <div className="mb-2">
                    <input className="form-control" type="number" name="salary_max" value={editFormData.salary_max} onChange={handleEditInputChange} required />
                  </div>
                  <div className="mb-2">
                    <textarea className="form-control" name="description" value={editFormData.description} onChange={handleEditInputChange} required />
                  </div>
                  <div className="mb-2">
                    <input className="form-control" name="requirements" value={editFormData.requirements} onChange={handleEditInputChange} required />
                  </div>
                  <div className="mb-2">
                    <textarea className="form-control" name="responsibilities" value={editFormData.responsibilities} onChange={handleEditInputChange} />
                  </div>
                  <div className="mb-2">
                    <textarea className="form-control" name="benefits" value={editFormData.benefits} onChange={handleEditInputChange} />
                  </div>
                  <div className="mb-2">
                    <input className="form-check-input" type="checkbox" name="is_remote" checked={editFormData.is_remote} onChange={e => setEditFormData((prev: any) => ({ ...prev, is_remote: e.target.checked }))} /> Télétravail possible
                  </div>
                  <div className="mb-2">
                    <input className="form-control" name="skills_required" value={editFormData.skills_required} onChange={handleEditInputChange} />
                  </div>
                  <div className="mb-2">
                    <input className="form-control" type="datetime-local" name="application_deadline" value={editFormData.application_deadline} onChange={handleEditInputChange} />
                  </div>
                  <div className="mb-2">
                    <input className="form-control" type="number" name="max_applications" value={editFormData.max_applications} onChange={handleEditInputChange} min={1} />
                  </div>
                  {error && <div className="text-danger mt-2">{error}</div>}
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowEditModal(false)}>
                    Annuler
                  </button>
                  <button type="submit" className="btn btn-success" disabled={loading}>
                    {loading ? 'Modification...' : 'Enregistrer'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Jobs;
