# 🎯 Système de Gestion RH avec IA

Une application web moderne pour la gestion des ressources humaines avec filtrage intelligent des CV par IA.

## 📋 Description du Projet

Cette application permet aux recruteurs de :
- Gérer efficacement de gros volumes de candidatures (1000+ CV)
- Filtrer automatiquement les CV par domaine (informatique, enseignement, avocat, etc.)
- Obtenir les meilleurs candidats (top 5-10) par poste grâce à l'IA
- Suivre et analyser les statistiques de recrutement

## 🛠 Stack Technique

- **Backend**: Django (Python) + Django REST Framework
- **Frontend**: React.js
- **Base de données**: PostgreSQL
- **IA/ML**: Modèles NLP (BERT/GPT) pour l'analyse des CV
- **Conteneurisation**: Docker
- **Déploiement**: AWS/Azure/Vercel

## 🏗 Structure du Projet

```
RH-Management/
├── backend/          # API Django
│   ├── apps/         # Applications Django
│   ├── config/       # Configuration Django
│   └── requirements.txt
├── frontend/         # Application React
│   ├── src/
│   ├── public/
│   └── package.json
├── database/         # Scripts et migrations PostgreSQL
├── ai-model/         # Modèles d'IA et scripts ML
├── data/            # Datasets pour l'entraînement
└── docs/            # Documentation
```

## 🎯 Fonctionnalités Principales

### 1. Gestion des Utilisateurs
- **Rôles**: Admin, Recruteur, Candidat
- Authentification sécurisée
- Gestion des profils et permissions

### 2. Gestion des Candidatures
- Upload et analyse de CV (PDF/Word)
- Gestion des lettres de motivation
- Historique des candidatures

### 3. Analyse IA des CV
- Extraction automatique des compétences
- Scoring de pertinence par poste
- Classification par domaine d'expertise
- Recommandations personnalisées

### 4. Notifications
- Notifications email automatiques
- Alertes en temps réel
- Suivi des candidatures

### 5. Tableau de Bord
- Statistiques de recrutement
- Analyses de performance
- Rapports détaillés

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker (optionnel)

### Installation

1. **Cloner le projet**
```bash
git clone [repository-url]
cd RH-Management
```

2. **Backend (Django)**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

3. **Frontend (React)**
```bash
cd frontend
npm install
npm start
```

4. **Base de données**
```bash
# Configuration PostgreSQL dans backend/config/settings.py
createdb rh_management
```

## 🔒 Sécurité

- Gestion sécurisée des mots de passe (hash + salt)
- Protection CSRF et XSS
- Authentification JWT
- HTTPS obligatoire en production
- Validation et sanitisation des données

## 📊 Performance

- Cache Redis pour les requêtes fréquentes
- Optimisation des requêtes PostgreSQL
- CDN pour les fichiers statiques
- Compression des images
- Pagination intelligente

## 🧪 Tests

- Tests unitaires (Django + Jest)
- Tests d'intégration
- Tests E2E (Cypress)
- Couverture de code > 80%

## 🚀 Déploiement

- Conteneurisation Docker
- CI/CD avec GitHub Actions
- Auto-scaling sur cloud
- Monitoring et logs

## 📝 Documentation

- API REST documentée (Swagger)
- Guide utilisateur
- Documentation technique
- Diagrammes d'architecture

## 👥 Contributeurs

- Équipe de développement RH Management

## 📄 Licence

Propriétaire - Tous droits réservés

---

**Prêt à révolutionner votre recrutement avec l'IA !** 🚀
