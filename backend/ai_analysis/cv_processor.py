"""
CV Processor - Extraction et traitement de texte des CV
Système d'IA pour l'analyse et le filtrage automatique des CV
"""
import os
import re
import PyPDF2
import docx
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import nltk
import pickle
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVProcessor:
    """
    Processeur de CV pour extraction de texte et analyse
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extrait le texte d'un fichier DOCX"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extrait le texte d'un fichier TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction TXT {file_path}: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extrait le texte selon le format du fichier"""
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            logger.warning(f"Format non supporté: {ext}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Nettoie et normalise le texte"""
        # Supprimer les caractères spéciaux et normaliser
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()
    
    def extract_skills(self, text: str) -> List[str]:
        """Extrait les compétences techniques du CV"""
        # Liste des compétences techniques communes
        technical_skills = [
            # Programmation
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'html', 'css', 'sql', 'r', 'matlab', 'scala', 'kotlin', 'swift',
            
            # Frameworks et librairies
            'django', 'flask', 'react', 'angular', 'vue', 'node.js', 'express',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            
            # Bases de données
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            
            # Outils et technologies
            'docker', 'kubernetes', 'aws', 'azure', 'git', 'jenkins', 'linux',
            'apache', 'nginx', 'hadoop', 'spark',
            
            # Méthodologies
            'agile', 'scrum', 'devops', 'ci/cd', 'machine learning', 'deep learning',
            'data science', 'big data', 'intelligence artificielle'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in technical_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_experience_years(self, text: str) -> int:
        """Extrait le nombre d'années d'expérience"""
        # Recherche de patterns d'expérience
        patterns = [
            r'(\d+)\s*an[s]?\s*d[\']?experience',
            r'(\d+)\s*annee[s]?\s*d[\']?experience',
            r'experience\s*:\s*(\d+)\s*an[s]?',
            r'(\d+)\s*years?\s*of\s*experience',
            r'(\d+)\s*years?\s*experience'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    def categorize_domain(self, text: str, skills: List[str]) -> str:
        """Catégorise le domaine professionnel"""
        text_lower = text.lower()
        
        # Informatique / Tech
        tech_keywords = ['développeur', 'programmeur', 'informatique', 'software', 'web', 'mobile', 'data', 'ia', 'intelligence artificielle', 'python', 'java', 'javascript']
        tech_skills = ['python', 'java', 'javascript', 'react', 'django', 'sql', 'html', 'css']
        
        tech_score = sum(1 for keyword in tech_keywords if keyword in text_lower)
        tech_score += sum(1 for skill in tech_skills if skill in skills)
        
        # Enseignement
        edu_keywords = ['enseignant', 'professeur', 'éducation', 'pédagogie', 'formation', 'école', 'université', 'mathématiques', 'cours', 'élève']
        edu_score = sum(1 for keyword in edu_keywords if keyword in text_lower)
        
        # Droit / Avocat
        law_keywords = ['avocat', 'juriste', 'droit', 'juridique', 'tribunal', 'contentieux', 'legal', 'barreau', 'cabinet']
        law_score = sum(1 for keyword in law_keywords if keyword in text_lower)
        
        # Marketing / Communication
        marketing_keywords = ['marketing', 'communication', 'publicité', 'digital', 'social media', 'seo', 'campagne', 'ads']
        marketing_score = sum(1 for keyword in marketing_keywords if keyword in text_lower)
        
        # Finance / Comptabilité
        finance_keywords = ['comptable', 'finance', 'banque', 'audit', 'fiscalité', 'contrôle de gestion']
        finance_score = sum(1 for keyword in finance_keywords if keyword in text_lower)
        
        # Santé
        health_keywords = ['médecin', 'infirmier', 'santé', 'médical', 'pharmacie', 'hôpital']
        health_score = sum(1 for keyword in health_keywords if keyword in text_lower)
        
        # Déterminer le domaine avec le score le plus élevé
        scores = {
            'informatique': tech_score,
            'enseignement': edu_score,
            'avocat': law_score,
            'marketing': marketing_score,
            'finance': finance_score,
            'sante': health_score
        }
        
        max_domain = max(scores, key=scores.get)
        max_score = scores[max_domain]
        
        # Si aucun score significatif, retourner 'autre'
        if max_score == 0:
            return 'autre'
        
        return max_domain


class CVAnalyzer:
    """
    Analyseur IA pour le filtrage et la classification des CV
    """
    
    def __init__(self):
        self.processor = CVProcessor()
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.domain_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.quality_classifier = SVC(kernel='rbf', random_state=42)
        self.is_trained = False
        
    def process_cv_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Traite un dataset de CV et extrait les features"""
        cv_data = []
        
        # Parcourir tous les dossiers de domaines
        for domain_folder in os.listdir(dataset_path):
            domain_path = os.path.join(dataset_path, domain_folder)
            
            if not os.path.isdir(domain_path):
                continue
                
            logger.info(f"📁 Traitement du domaine: {domain_folder}")
            
            # Parcourir tous les fichiers CV dans ce domaine
            cv_files = [f for f in os.listdir(domain_path) if f.endswith('.pdf')]
            
            for i, file in enumerate(cv_files):
                if i >= 50:  # Limiter à 50 CV par domaine pour l'entraînement initial
                    break
                    
                file_path = os.path.join(domain_path, file)
                logger.info(f"📄 Traitement du CV: {file} ({i+1}/{min(50, len(cv_files))})")
                
                # Extraction du texte
                text = self.processor.extract_text(file_path)
                if not text:
                    continue
                
                # Nettoyage du texte
                cleaned_text = self.processor.clean_text(text)
                
                # Extraction des features
                skills = self.processor.extract_skills(text)
                experience_years = self.processor.extract_experience_years(text)
                
                # Utiliser le nom du dossier comme domaine
                domain = domain_folder.lower().replace('-', '_')
                
                cv_data.append({
                    'filename': file,
                    'text': cleaned_text,
                    'raw_text': text,
                    'skills': skills,
                    'skills_count': len(skills),
                    'experience_years': experience_years,
                    'domain': domain,
                    'word_count': len(cleaned_text.split()),
                    'file_path': file_path
                })
        
        return pd.DataFrame(cv_data)
    
    def train_models(self, cv_dataframe: pd.DataFrame):
        """Entraîne les modèles IA sur le dataset"""
        logger.info("Début de l'entraînement des modèles IA...")
        
        # Préparation des données
        texts = cv_dataframe['text'].tolist()
        domains = cv_dataframe['domain'].tolist()
        
        # Vectorisation TF-IDF
        X = self.vectorizer.fit_transform(texts)
        
        # Entraînement du classificateur de domaines seulement si plusieurs domaines
        unique_domains = set(domains)
        if len(unique_domains) > 1:
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, domains, test_size=0.2, random_state=42, stratify=domains
                )
                
                self.domain_classifier.fit(X_train, y_train)
                
                # Évaluation
                y_pred = self.domain_classifier.predict(X_test)
                logger.info("Classification des domaines:")
                logger.info(classification_report(y_test, y_pred))
            except ValueError as e:
                logger.warning(f"Impossible de diviser le dataset pour l'entraînement des domaines: {e}")
                # Entraîner sur tout le dataset
                self.domain_classifier.fit(X, domains)
        else:
            logger.info("Un seul domaine détecté, entraînement simple...")
            self.domain_classifier.fit(X, domains)
        
        # Créer un score de qualité basé sur les features
        cv_dataframe['quality_score'] = (
            cv_dataframe['skills_count'] * 0.4 +
            cv_dataframe['experience_years'] * 0.3 +
            (cv_dataframe['word_count'] / 100) * 0.3
        )
        
        # Normaliser le score de qualité (0-100)
        max_score = cv_dataframe['quality_score'].max()
        if max_score > 0:
            cv_dataframe['quality_score'] = (cv_dataframe['quality_score'] / max_score * 100)
        
        # Classification binaire pour la qualité (bon/moyen CV)
        quality_labels = ['bon' if score >= 60 else 'moyen' for score in cv_dataframe['quality_score']]
        
        # Entraînement du classificateur de qualité seulement si plusieurs classes
        unique_quality = set(quality_labels)
        if len(unique_quality) > 1:
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, quality_labels, test_size=0.2, random_state=42
                )
                
                self.quality_classifier.fit(X_train, y_train)
                
                # Évaluation
                y_pred = self.quality_classifier.predict(X_test)
                logger.info("Classification de la qualité:")
                logger.info(classification_report(y_test, y_pred))
            except ValueError as e:
                logger.warning(f"Impossible de diviser le dataset pour l'entraînement de la qualité: {e}")
                # Entraîner sur tout le dataset
                self.quality_classifier.fit(X, quality_labels)
        else:
            logger.info("Une seule classe de qualité détectée, entraînement simple...")
            self.quality_classifier.fit(X, quality_labels)
        
        self.is_trained = True
        logger.info("Entraînement terminé avec succès!")
        
        return cv_dataframe
    
    def analyze_cv(self, cv_text: str) -> Dict:
        """Analyse un CV individuel"""
        if not self.is_trained:
            raise ValueError("Les modèles doivent être entraînés avant l'analyse")
        
        # Traitement du texte
        cleaned_text = self.processor.clean_text(cv_text)
        skills = self.processor.extract_skills(cv_text)
        experience_years = self.processor.extract_experience_years(cv_text)
        
        # Vectorisation
        X = self.vectorizer.transform([cleaned_text])
        
        # Prédictions
        predicted_domain = self.domain_classifier.predict(X)[0]
        domain_proba = max(self.domain_classifier.predict_proba(X)[0])
        
        predicted_quality = self.quality_classifier.predict(X)[0]
        
        # Calcul du score de qualité
        quality_score = (
            len(skills) * 0.4 +
            experience_years * 0.3 +
            (len(cleaned_text.split()) / 100) * 0.3
        )
        
        return {
            'domain': predicted_domain,
            'domain_confidence': float(domain_proba),
            'quality': predicted_quality,
            'quality_score': float(quality_score),
            'skills': skills,
            'skills_count': len(skills),
            'experience_years': experience_years,
            'word_count': len(cleaned_text.split())
        }
    
    def filter_top_candidates(self, cv_analyses: List[Dict], domain: str, top_n: int = 10) -> List[Dict]:
        """Filtre les top N candidats pour un domaine donné"""
        # Filtrer par domaine
        domain_candidates = [cv for cv in cv_analyses if cv['domain'] == domain]
        
        # Trier par score de qualité
        domain_candidates.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Retourner les top N
        return domain_candidates[:top_n]
    
    def save_models(self, models_path: str):
        """Sauvegarde les modèles entraînés"""
        os.makedirs(models_path, exist_ok=True)
        
        with open(os.path.join(models_path, 'vectorizer.pkl'), 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        with open(os.path.join(models_path, 'domain_classifier.pkl'), 'wb') as f:
            pickle.dump(self.domain_classifier, f)
        
        with open(os.path.join(models_path, 'quality_classifier.pkl'), 'wb') as f:
            pickle.dump(self.quality_classifier, f)
        
        logger.info(f"Modèles sauvegardés dans {models_path}")
    
    def load_models(self, models_path: str):
        """Charge les modèles pré-entraînés"""
        with open(os.path.join(models_path, 'vectorizer.pkl'), 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        with open(os.path.join(models_path, 'domain_classifier.pkl'), 'rb') as f:
            self.domain_classifier = pickle.load(f)
        
        with open(os.path.join(models_path, 'quality_classifier.pkl'), 'rb') as f:
            self.quality_classifier = pickle.load(f)
        
        self.is_trained = True
        logger.info(f"Modèles chargés depuis {models_path}")
