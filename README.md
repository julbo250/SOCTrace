# SOCTrace 🛡️

> **Gestion des Changements SOC** - Une application web moderne pour suivre et documenter les changements dans votre infrastructure de sécurité.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)

## 📋 Table des Matières

- [À Propos](#à-propos)
- [Caractéristiques](#caractéristiques)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Sécurité](#sécurité)
- [Configuration](#configuration)
- [Dépannage](#dépannage)
- [Contribution](#contribution)
- [Licence](#licence)

## 🎯 À Propos

SOCTrace est une application web conçue pour les équipes SOC (Security Operations Center) qui ont besoin de suivre et de documenter les changements apportés à leur infrastructure de sécurité. Elle offre une solution intuitive, sécurisée et centralisée pour gérer les changements avec authentification, audit trail complet et export/import de données.

**Version:** 1.2  
**Dernière mise à jour:** Février 2024

<img width="1447" height="684" alt="Capture d’écran 2026-02-17 à 15 39 30" src="https://github.com/user-attachments/assets/28d8f499-6c61-4387-96f9-5fb875f9df7c" />

## ✨ Caractéristiques

### 🔐 Authentification & Sécurité
- Authentification par login/mot de passe
- Hachage sécurisé des mots de passe (SCRYPT)
- Gestion des sessions
- Modification du mot de passe intégrée
- Protection de toutes les routes

### 📊 Gestion des Changements
- Ajout de changements avec date, produit, type et description
- Suppression de changements
- Filtrage avancé par produit, type, analyste, date
- Tableau affichant tous les changements
- Tri et recherche en temps réel

### 📁 Import/Export
- Exportation en CSV de tous les changements
- Importation en CSV pour ajouter des données en masse
- Format CSV flexible et documenté
- Validation des données lors de l'import

### ⚙️ Gestion Dynamique des Types
- Ajout de nouveaux types de produits
- Ajout de nouveaux types de changements
- Suppression des types existants
- Types par défaut: Harfanglab, Elastic, Docker, Autre
- Types de changement: IOC, Whitelist, Règle, Autre

### 🖥️ Interface Utilisateur
- Design moderne et responsive
- Thème sombre professionnel
- Header spacieux avec 8 boutons d'action
- Modales pour toutes les actions
- Messages de confirmation et d'erreur clairs

### 💾 Persistance des Données
- Base de données SQLite
- Volume Docker nommé pour garantir la persistance
- Sauvegarde automatique de tous les changements

## 📋 Prérequis

- Docker
- Docker Compose
- Port 5000 disponible
- 100MB d'espace disque

## 🚀 Installation

### 1. Cloner le répertoire

```bash
git clone https://github.com/yourusername/soctrace.git
cd soctrace
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env et mettre à jour les identifiants si nécessaire
```

### 3. Rendre le script exécutable

```bash
chmod +x START.sh
```

### 4. Démarrer l'application

```bash
./START.sh
```

L'application démarre après 10 secondes et est accessible à:
```
http://localhost:5000
```

## 📖 Utilisation

### Démarrage

```bash
# Démarrer
./START.sh

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f web

# Redémarrer
docker-compose restart
```

### Première Connexion

1. Ouvrez http://localhost:5000
2. Les identifiants par défaut sont configurés dans le fichier `.env`
3. Connectez-vous avec vos identifiants
4. Commencez à ajouter des changements!

### Fonctionnalités Principales

#### Ajouter un Changement
```
1. Cliquez "Ajouter un changement" (bouton jaune)
2. Remplissez: Date, Produit, Type, Description, Analyste, Lien
3. Cliquez "Ajouter"
```

#### Gérer les Types
```
Ajouter:
1. Cliquez "Ajouter un nouveau type" (bouton vert)
2. Choisissez: Produit ou Changement
3. Entrez le nom et cliquez "Ajouter"

Supprimer:
1. Cliquez "Gérer les types" (bouton rouge)
2. Trouvez le type et cliquez "Supprimer"
3. Confirmez
```

#### Importer/Exporter
```
Exporter:
1. Cliquez "Exporter CSV"
2. Le fichier se télécharge automatiquement

Importer:
1. Cliquez "Importer CSV"
2. Sélectionnez votre fichier CSV
3. Cliquez "Importer"
```

## 🏗️ Architecture

```
SOCTrace/
├── app.py                 # Application Flask
├── manage_users.py        # Gestion des utilisateurs
├── requirements.txt       # Dépendances Python
├── Dockerfile            # Image Docker
├── docker-compose.yml    # Orchestration Docker
├── .env                  # Variables d'environnement
├── START.sh             # Script de démarrage
└── templates/
    ├── index.html       # Page principale
    ├── login.html       # Page de connexion
    └── about.html       # Page À propos
```

### Stack Technique

- **Backend:** Flask 3.0.0 (Python)
- **Base de données:** SQLite 3
- **Frontend:** HTML5, CSS3, JavaScript
- **Déploiement:** Docker & Docker Compose
- **Sécurité:** Werkzeug Security (SCRYPT)

## 🔌 API Endpoints

### Authentification
```
POST   /login              # Connexion
POST   /logout             # Déconnexion
```

### Changements
```
GET    /api/changes        # Récupérer tous les changements
POST   /api/changes        # Ajouter un changement
DELETE /api/changes/<id>   # Supprimer un changement
```

### Types
```
GET    /api/types          # Récupérer tous les types
POST   /api/add-type       # Ajouter un type
POST   /api/delete-type    # Supprimer un type
```

### Utilisateur
```
POST   /api/change-password # Changer le mot de passe
```

### Export/Import
```
GET    /api/export-csv     # Exporter en CSV
POST   /api/import-csv     # Importer depuis CSV
```

## 🔐 Sécurité

### Mots de Passe
- Hachage SCRYPT avec 32768 itérations
- Chaque mot de passe a un salt unique
- Mots de passe jamais stockés en clair
- Vérification lors de la connexion

### Sessions
- Cookies sécurisés (Secure, HttpOnly)
- Durée de vie: 24 heures
- Protection CSRF intégrée
- Routes protégées par login_required

### Base de Données
- Requêtes paramétrées (prévention SQL injection)
- Validation des entrées
- Messages d'erreur génériques

## ⚙️ Configuration

### Fichier .env

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=production

# Base de données
DATABASE=/app/data/inventory.db

# Session
SECRET_KEY=votre-clé-secrète-très-sûre-change-en-production

# Utilisateurs par défaut
DEFAULT_USERNAME=soc
DEFAULT_PASSWORD=Spluk2024!
```

### Variables d'Environnement Docker

Modifiez le `docker-compose.yml` pour personnaliser:

```yaml
environment:
  - FLASK_APP=app.py
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
```

## 🐛 Dépannage

### L'application ne démarre pas

```bash
# Vérifier que Docker est installé
docker --version
docker-compose --version

# Vérifier que le port 5000 est libre
lsof -i :5000

# Voir les logs d'erreur
docker-compose logs web

# Relancer avec rebuild
docker-compose down
docker-compose build --no-cache
./START.sh
```

### Problèmes de persistance des données

```bash
# Vérifier que le volume existe
docker volume ls

# Recréer le volume
docker volume rm soc-data
docker-compose down
./START.sh
```

### Impossible de se connecter

```bash
# Réinitialiser la base de données
docker-compose down
docker volume rm soc-data
docker-compose build --no-cache
./START.sh
# Utilisez les identifiants du .env
```

### Erreur lors de l'import CSV

- Vérifiez le format du fichier (colonnes obligatoires)
- Vérifiez que la date est au format YYYY-MM-DD
- Vérifiez l'encodage du fichier (UTF-8)

## 📚 Format du CSV

### Import/Export

```csv
Date,Type de produit,Type de changement,Désignation,Analyste,Lien application
2024-02-17,Elastic,IOC,Ajout de nouvel IOC,John Doe,https://exemple.com
2024-02-16,Docker,Configuration,Mise à jour image,Jane Smith,https://exemple.com
```

**Colonnes obligatoires:**
- Date (format: YYYY-MM-DD)
- Type de produit
- Type de changement
- Désignation
- Analyste

**Colonnes optionnelles:**
- Lien application

## 👥 Gestion des Utilisateurs

### Ajouter un utilisateur

```bash
docker-compose exec web python manage_users.py add <username> <password>
```

### Changer un mot de passe

```bash
docker-compose exec web python manage_users.py change <username> <new_password>
```

### Lister les utilisateurs

```bash
docker-compose exec web python manage_users.py list
```

### Supprimer un utilisateur

```bash
docker-compose exec web python manage_users.py delete <username>
```

## 📖 Documentation

- [Manuel Utilisateur](MANUEL_UTILISATEUR.docx) - Guide complet pour les utilisateurs
- [Documentation Technique](docs/) - Documentation technique détaillée (si disponible)

## 🤝 Contribution

Les contributions sont les bienvenues! Pour contribuer:

1. Forkez le projet
2. Créez une branche de feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**SOCTrace** a été créé pour les équipes SOC qui ont besoin d'une solution simple et efficace pour gérer les changements.

## 🙏 Remerciements

- Flask pour le framework web
- Docker pour la containerisation
- Werkzeug pour la sécurité
- Font Awesome pour les icônes

## 📧 Support

Pour toute question ou problème:
1. Vérifiez la section [Dépannage](#dépannage)
2. Consultez le [Manuel Utilisateur](MANUEL_UTILISATEUR.docx)
3. Ouvrez une issue sur GitHub

---

**Version:** 2.4  
**Dernière mise à jour:** Février 2024  
**Status:** ✅ Production Ready

