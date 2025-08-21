# Backend Django - Système RH avec IA

## Configuration de l'environnement

1. **Créer l'environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration de la base de données**
- Créer une base PostgreSQL nommée `rh_management`
- Modifier les paramètres dans `config/settings.py`

4. **Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

6. **Lancer le serveur**
```bash
python manage.py runserver
```

## Structure des Apps Django

- **accounts**: Gestion des utilisateurs et authentification
- **candidates**: Gestion des candidats et candidatures
- **jobs**: Gestion des offres d'emploi
- **ai_analysis**: Analyse IA des CV
- **notifications**: Système de notifications
- **dashboard**: Tableaux de bord et statistiques

## API Endpoints

### Authentification
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/logout/` - Déconnexion

### Utilisateurs
- `GET /api/users/` - Liste des utilisateurs
- `GET /api/users/{id}/` - Détails utilisateur
- `PUT /api/users/{id}/` - Modifier utilisateur

### Candidatures
- `GET /api/candidatures/` - Liste des candidatures
- `POST /api/candidatures/` - Créer candidature
- `GET /api/candidatures/{id}/` - Détails candidature
- `POST /api/candidatures/analyze/` - Analyser CV avec IA

### Emplois
- `GET /api/jobs/` - Liste des emplois
- `POST /api/jobs/` - Créer emploi
- `GET /api/jobs/{id}/candidates/` - Candidats pour un emploi
