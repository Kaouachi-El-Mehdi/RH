import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import CVAnalysisModal from './CVAnalysisModal';
import './JobManagement.css';

interface Job {
  id: number;
  title: string;
  company_name: string;
  description: string;
  requirements: string;
  location: string;
  contract_type: string;
  experience_required: string;
  salary_min?: number;
  salary_max?: number;
  skills_required: string;
  status: string;
  is_remote: boolean;
  created_at: string;
  category: number;
}

interface JobCategory {
  id: number;
  name: string;
  description: string;
}

const JobManagement: React.FC = () => {
  const { getAuthToken } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [categories, setCategories] = useState<JobCategory[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [selectedJobForAnalysis, setSelectedJobForAnalysis] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [newJob, setNewJob] = useState({
    title: '',
    company_name: '',
    description: '',
    requirements: '',
    responsibilities: '',
    benefits: '',
    location: '',
    contract_type: 'cdi',
    experience_required: '1-3',
    salary_min: '',
    salary_max: '',
    skills_required: '',
    is_remote: false,
    category: 1,
    application_deadline: '',
    max_applications: '100'
  });

  useEffect(() => {
    fetchJobs();
    fetchCategories();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/jobs/');
      const data = await response.json();
      setJobs(data.results || data);
    } catch (err) {
      console.error('Erreur lors du chargement des offres:', err);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/jobs/categories/');
      const data = await response.json();
      setCategories(data.results || data);
    } catch (err) {
      console.error('Erreur lors du chargement des catégories:', err);
    }
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = getAuthToken();
      const jobData = {
        ...newJob,
        salary_min: newJob.salary_min ? parseFloat(newJob.salary_min) : null,
        salary_max: newJob.salary_max ? parseFloat(newJob.salary_max) : null,
        max_applications: newJob.max_applications ? parseInt(newJob.max_applications) : null,
        application_deadline: newJob.application_deadline || null,
        status: 'published',
      };
      
      console.log('Sending job data:', jobData);
      
      const response = await fetch('http://127.0.0.1:8000/api/jobs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(jobData),
      });

      if (response.ok) {
        await fetchJobs();
        setShowCreateForm(false);
        setNewJob({
          title: '',
          company_name: '',
          description: '',
          requirements: '',
          responsibilities: '',
          benefits: '',
          location: '',
          contract_type: 'cdi',
          experience_required: '1-3',
          salary_min: '',
          salary_max: '',
          skills_required: '',
          is_remote: false,
          category: 1,
          application_deadline: '',
          max_applications: '100'
        });
      } else {
        const errorData = await response.json();
        console.log('Job creation error:', errorData);
        setError(errorData.detail || JSON.stringify(errorData) || 'Erreur lors de la création de l\'offre');
      }
    } catch (err) {
      setError('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setNewJob(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleAnalyzeCV = (job: Job) => {
    setSelectedJobForAnalysis(job);
    setShowAnalysisModal(true);
  };

  return (
    <div className="job-management">
      <div className="job-header">
        <h2>🏢 Gestion des Offres d'Emploi</h2>
        <button 
          className="create-job-btn"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? '❌ Annuler' : '➕ Créer une Offre'}
        </button>
      </div>

      {showCreateForm && (
        <div className="create-job-form">
          <h3>✏️ Nouvelle Offre d'Emploi</h3>
          <form onSubmit={handleCreateJob}>
            <div className="form-grid">
              <div className="form-group">
                <label>Titre du poste *</label>
                <input
                  type="text"
                  name="title"
                  value={newJob.title}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Entreprise *</label>
                <input
                  type="text"
                  name="company_name"
                  value={newJob.company_name}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Catégorie *</label>
                <select
                  name="category"
                  value={newJob.category}
                  onChange={handleInputChange}
                  required
                >
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Lieu *</label>
                <input
                  type="text"
                  name="location"
                  value={newJob.location}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Type de contrat</label>
                <select
                  name="contract_type"
                  value={newJob.contract_type}
                  onChange={handleInputChange}
                >
                  <option value="cdi">CDI</option>
                  <option value="cdd">CDD</option>
                  <option value="stage">Stage</option>
                  <option value="freelance">Freelance</option>
                  <option value="interim">Intérim</option>
                </select>
              </div>

              <div className="form-group">
                <label>Expérience requise</label>
                <select
                  name="experience_required"
                  value={newJob.experience_required}
                  onChange={handleInputChange}
                >
                  <option value="0-1">0-1 an</option>
                  <option value="1-3">1-3 ans</option>
                  <option value="3-5">3-5 ans</option>
                  <option value="5-10">5-10 ans</option>
                  <option value="10+">10+ ans</option>
                </select>
              </div>

              <div className="form-group">
                <label>Salaire min (€)</label>
                <input
                  type="number"
                  name="salary_min"
                  value={newJob.salary_min}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Salaire max (€)</label>
                <input
                  type="number"
                  name="salary_max"
                  value={newJob.salary_max}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="form-group full-width">
              <label>Description du poste *</label>
              <textarea
                name="description"
                value={newJob.description}
                onChange={handleInputChange}
                rows={4}
                required
              />
            </div>

            <div className="form-group full-width">
              <label>Exigences du poste *</label>
              <textarea
                name="requirements"
                value={newJob.requirements}
                onChange={handleInputChange}
                rows={4}
                required
              />
            </div>

            <div className="form-group full-width">
              <label>Compétences requises (séparées par des virgules) *</label>
              <textarea
                name="skills_required"
                value={newJob.skills_required}
                onChange={handleInputChange}
                rows={2}
                placeholder="JavaScript, React, Node.js, PostgreSQL..."
                required
              />
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="is_remote"
                  checked={newJob.is_remote}
                  onChange={handleInputChange}
                />
                🏠 Télétravail possible
              </label>
            </div>

            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}

            <div className="form-actions">
              <button 
                type="submit" 
                className="submit-btn"
                disabled={loading}
              >
                {loading ? '⏳ Création...' : '🚀 Créer l\'Offre'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="jobs-list">
        <h3>📋 Offres d'Emploi ({jobs.length})</h3>
        {jobs.length === 0 ? (
          <div className="empty-state">
            <p>Aucune offre d'emploi créée pour le moment.</p>
            <p>Commencez par créer votre première offre!</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {jobs.map(job => (
              <div key={job.id} className="job-card">
                <div className="job-header-card">
                  <h4>{job.title}</h4>
                  <span className={`status ${job.status}`}>{job.status}</span>
                </div>
                <div className="job-company">{job.company_name}</div>
                <div className="job-location">📍 {job.location}</div>
                <div className="job-contract">📝 {job.contract_type.toUpperCase()}</div>
                <div className="job-experience">⏰ {job.experience_required}</div>
                {job.is_remote && <div className="remote-badge">🏠 Remote</div>}
                <div className="job-skills">
                  🛠️ {job.skills_required.split(',').slice(0, 3).map(skill => skill.trim()).join(', ')}
                  {job.skills_required.split(',').length > 3 && '...'}
                </div>
                <div className="job-actions">
                  <button 
                    className="analyze-btn"
                    onClick={() => handleAnalyzeCV(job)}
                  >
                    🔍 Analyser les CV
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* CV Analysis Modal */}
      {showAnalysisModal && selectedJobForAnalysis && (
        <CVAnalysisModal 
          job={selectedJobForAnalysis}
          onClose={() => {
            setShowAnalysisModal(false);
            setSelectedJobForAnalysis(null);
          }}
        />
      )}
    </div>
  );
};

export default JobManagement;
