import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './CVAnalysisModal.css';

interface Job {
  id: number;
  title: string;
  company_name: string;
  description: string;
  requirements: string;
  skills_required: string;
  experience_required: string;
  location: string;
  contract_type: string;
  category: number;
}

interface CVAnalysisModalProps {
  job: Job;
  onClose: () => void;
}

interface CVAnalysisResult {
  status: string;
  domain: string;
  confidence: number;
  quality_score: number;
  skills: string[];
  experience_years: number;
  filename: string;
  job_match_score?: number;
}

interface JobSpecificAnalysisResult {
  total_files: number;
  processed_files: number;
  job_info: {
    title: string;
    company: string;
    required_skills: string[];
  };
  results: CVAnalysisResult[];
  ranked_candidates: CVAnalysisResult[];
}

const CVAnalysisModal: React.FC<CVAnalysisModalProps> = ({ job, onClose }) => {
  const { getAuthToken } = useAuth();
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<JobSpecificAnalysisResult | null>(null);
  const [error, setError] = useState('');

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setSelectedFiles(files);
      setError('');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      setError('Veuillez sélectionner au moins un fichier CV');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      
      // Add all selected files
      Array.from(selectedFiles).forEach((file, index) => {
        formData.append('files', file);
      });

      // Add job information for better matching
      formData.append('job_id', job.id.toString());
      formData.append('job_title', job.title);
      formData.append('job_description', job.description);
      formData.append('job_requirements', job.requirements);
      formData.append('required_skills', job.skills_required);
      formData.append('experience_required', job.experience_required);

      const token = getAuthToken();
      const response = await fetch('http://localhost:8000/api/ai/analyze-job-cvs/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de l\'analyse des CV');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      console.error('Error analyzing CVs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getMatchingScoreColor = (score: number) => {
    if (score >= 80) return '#28a745'; // Green
    if (score >= 60) return '#ffc107'; // Yellow
    if (score >= 40) return '#fd7e14'; // Orange
    return '#dc3545'; // Red
  };

  const getMatchingScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent match';
    if (score >= 60) return 'Bon match';
    if (score >= 40) return 'Match moyen';
    return 'Match faible';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>🔍 Analyser les CV pour: {job.title}</h3>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="job-info">
            <h4>📋 Détails du poste</h4>
            <p><strong>Entreprise:</strong> {job.company_name}</p>
            <p><strong>Expérience requise:</strong> {job.experience_required}</p>
            <p><strong>Compétences requises:</strong> {job.skills_required}</p>
          </div>

          {!results && (
            <div className="upload-section">
              <h4>📄 Sélectionner les CV à analyser</h4>
              <div className="file-upload-container">
                <input
                  type="file"
                  id="cv-files"
                  multiple
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileSelect}
                  className="file-input-hidden"
                />
                <label htmlFor="cv-files" className="file-upload-btn">
                  📁 Choisir les fichiers CV
                </label>
                <div className="upload-help">
                  Formats acceptés: PDF, DOC, DOCX
                </div>
              </div>
              {selectedFiles && (
                <div className="selected-files">
                  <p>✅ {selectedFiles.length} fichier(s) sélectionné(s):</p>
                  <ul>
                    {Array.from(selectedFiles).slice(0, 5).map((file, index) => (
                      <li key={index}>{file.name}</li>
                    ))}
                    {selectedFiles.length > 5 && <li>... et {selectedFiles.length - 5} autres</li>}
                  </ul>
                </div>
              )}

              {error && <div className="error-message">❌ {error}</div>}

              <button
                onClick={handleAnalyze}
                disabled={loading || !selectedFiles}
                className="analyze-btn-modal"
              >
                {loading ? '🔄 Analyse en cours...' : '🚀 Lancer l\'analyse'}
              </button>
            </div>
          )}

          {results && (
            <div className="results-section">
              <div className="results-summary">
                <h4>📊 Résultats de l'analyse</h4>
                <div className="summary-stats">
                  <div className="stat">
                    <span className="stat-number">{results.processed_files}</span>
                    <span className="stat-label">CV analysés</span>
                  </div>
                  <div className="stat">
                    <span className="stat-number">{results.ranked_candidates?.length || 0}</span>
                    <span className="stat-label">Candidats classés</span>
                  </div>
                </div>
              </div>

              <div className="candidates-ranking">
                <h4>🏆 Classement des candidats</h4>
                {results.ranked_candidates && results.ranked_candidates.length > 0 ? (
                  <div className="candidates-list">
                    {results.ranked_candidates.map((candidate, index) => (
                      <div key={index} className="candidate-card">
                        <div className="candidate-rank">#{index + 1}</div>
                        <div className="candidate-info">
                          <h5>{candidate.filename}</h5>
                          <div className="candidate-details">
                            <span className="domain">🎯 {candidate.domain}</span>
                            <span className="experience">⏰ {candidate.experience_years} ans</span>
                            <span 
                              className="match-score"
                              style={{ 
                                backgroundColor: getMatchingScoreColor(candidate.job_match_score || candidate.quality_score),
                                color: 'white',
                                padding: '2px 8px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                fontWeight: 'bold'
                              }}
                            >
                              {Math.round(candidate.job_match_score || candidate.quality_score)}% {getMatchingScoreLabel(candidate.job_match_score || candidate.quality_score)}
                            </span>
                          </div>
                          <div className="candidate-skills">
                            <strong>Compétences:</strong> {candidate.skills.slice(0, 5).join(', ')}
                            {candidate.skills.length > 5 && '...'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>Aucun candidat trouvé correspondant aux critères.</p>
                )}
              </div>

              <div className="modal-actions">
                <button onClick={() => setResults(null)} className="secondary-btn">
                  🔄 Analyser d'autres CV
                </button>
                <button onClick={onClose} className="primary-btn">
                  ✅ Fermer
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CVAnalysisModal;
