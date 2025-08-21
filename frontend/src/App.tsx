import React, { useState } from 'react';
import './App.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthForm from './components/AuthForm';
import Layout, { TabName } from './components/Layout';
import JobManagement from './components/JobManagement';
import Dashboard from './components/Dashboard';
import Jobs from './components/Jobs';
import ApplicationManagement from './components/ApplicationManagement';
import Users from './components/Users';
import Profile from './components/Profile';

interface CVAnalysisResult {
  status: string;
  domain: string;
  confidence: number;
  quality_score: number;
  skills: string[];
  experience_years: number;
  filename: string;
}

interface BulkAnalysisResult {
  total_files: number;
  processed_files: number;
  results: CVAnalysisResult[];
  summary: {
    [domain: string]: {
      count: number;
      top_candidates: CVAnalysisResult[];
    };
  };
}

function AppContent() {
  const { isAuthenticated } = useAuth();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [analysisResult, setAnalysisResult] = useState<CVAnalysisResult | null>(null);
  const [bulkResults, setBulkResults] = useState<BulkAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<TabName>('jobs');

  // Route to correct main page after login
  const { user } = useAuth();
  React.useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'admin' || user.role === 'recruteur') {
        setActiveTab('dashboard');
      } else {
        setActiveTab('jobs');
      }
    }
  }, [isAuthenticated, user]);

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return <AuthForm onSuccess={() => window.location.reload()} />;
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError('');
      setAnalysisResult(null);
    }
  };

  const handleBulkFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setSelectedFiles(files);
      setError('');
      setBulkResults(null);
    }
  };

  const handleBulkAnalyze = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      setError('Veuillez sélectionner des fichiers CV');
      return;
    }

    setBulkLoading(true);
    setError('');

    const formData = new FormData();
    Array.from(selectedFiles).forEach((file, index) => {
      formData.append('cv_files', file);
    });

    try {
      const response = await fetch('http://127.0.0.1:8000/api/ai/bulk-analyze/', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || `Erreur HTTP: ${response.status}`);
      }

      setBulkResults(result);
    } catch (err) {
      console.error('Erreur détaillée:', err);
      setError('Erreur lors de l\'analyse en lot: ' + (err as Error).message);
    } finally {
      setBulkLoading(false);
    }
  };

  const handleAnalyzeCV = async () => {
    if (!selectedFile) {
      setError('Veuillez sélectionner un fichier CV');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('cv_file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/ai/analyze/', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || `Erreur HTTP: ${response.status}`);
      }

      setAnalysisResult(result);
    } catch (err) {
      console.error('Erreur détaillée:', err);
      setError('Erreur lors de l\'analyse du CV: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      {activeTab === 'dashboard' && <Dashboard />}
      {activeTab === 'jobs' && <Jobs />}
      {activeTab === 'applications' && <ApplicationManagement />}
      {activeTab === 'users' && <Users />}
      {activeTab === 'profile' && <Profile />}
      {/* Info section can be added to dashboard or as a separate tab if needed */}
    </Layout>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
