# 🚛 CargoLink &bull; Guide de Démarrage & Onboarding Développeur

Bienvenue sur le projet **CargoLink**, la plateforme SaaS de coordination logistique intelligente (régulation des quais de chargement, gestion des entrepôts et synchronisation du fret en temps réel).

Ce document contient l'ensemble des instructions, prérequis et commandes nécessaires pour installer, configurer et commencer à développer sur le projet.

---

## 📋 Table des Matières

1. [Stack Technologique & Architecture](#1-stack-technologique--architecture)
2. [Prérequis](#2-prérequis)
3. [Installation & Lancement Rapide](#3-installation--lancement-rapide)
4. [Gestion de la Base de Données & Données de Démonstration](#4-gestion-de-la-base-de-données--données-de-démonstration)
5. [Système de Rôles & Sécurité (RBAC)](#5-système-de-rôles--sécurité-rbac)
6. [Lancer la Suite de Tests Automatisés](#6-lancer-la-suite-de-tests-automatisés)
7. [Structure du Projet](#7-structure-du-projet)
8. [Règles de Contribution & Conventions](#8-règles-de-contribution--conventions)

---

## 1. Stack Technologique & Architecture

- **Backend** : Python 3.13+ & Django 5.2
- **Base de Données** : PostgreSQL hébergé sur Supabase (`psycopg` v3)
- **Gestionnaire d'Environnement** : [`uv`](https://docs.astral.sh/uv/) (extrêmement rapide et fiable)
- **Frontend & Design** : HTML5 sémantique, Vanilla CSS3 (Design System Dark Mode SaaS, effets glassmorphism, composants d'état lumineux, icônes SVG Lucide)
- **Authentification & Sécurité** : RBAC custom (`UserProfile`), middleware de protection d'accès administration (`AdminAccessControlMiddleware`)

---

## 2. Prérequis

Avant de commencer, vérifiez que vous avez installé :
1. **Python 3.13+** : `python --version`
2. **Git** : `git --version`
3. **uv** (recommandé) :
   - *Sur Windows (PowerShell)* :
     ```powershell
     powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - *Sur macOS / Linux* :
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```

*(Alternative standard sans `uv` : Python `venv` et `pip` fonctionnent également).*

---

## 3. Installation & Lancement Rapide

### Étape 1 : Cloner le dépôt Git
```bash
git clone https://github.com/Mutedly007/CargoLink.git
cd CargoLink
```

### Étape 2 : Installer les dépendances
Avec `uv` (recommandé) :
```bash
uv sync
```
*(Alternative avec pip classique : `python -m venv .venv` puis `pip install -e .`)*

### Étape 3 : Appliquer les migrations de base de données
La base de données PostgreSQL Supabase est pré-configurée dans `cargolink/settings.py`. Pour appliquer le schéma :
```bash
uv run python manage.py migrate
```

### Étape 4 : Lancer le serveur de développement
```bash
uv run python manage.py runserver
```
L'application est immédiatement accessible dans votre navigateur à l'adresse :
👉 **http://127.0.0.1:8000/**

---

## 4. Gestion de la Base de Données & Données de Démonstration

### A. Remplir la base avec des entrepôts et quais de test
Une commande Django personnalisée est disponible pour peupler automatiquement la base de données avec 3 entrepôts réalistes et 6 quais équipés :
```bash
uv run python manage.py populate_entrepots
```

### B. Créer un compte super-administrateur
Pour créer votre compte administrateur Django et plateforme :
```bash
uv run python manage.py createsuperuser
```
*Suivez les invites (identifiant, email, mot de passe).*

---

## 5. Système de Rôles & Sécurité (RBAC)

La plateforme intègre 4 rôles métier définis dans le modèle `UserProfile` :

| Rôle | Code en Base | Périmètre fonctionnel |
| :--- | :--- | :--- |
| **Gestionnaire d'Entrepôt** | `ENTREPOT` | Création et gestion complète des sites de stockage, régulation et ajout des quais de déchargement. |
| **Transporteur / Chauffeur** | `TRANSPORTEUR` | Visualisation de la flotte, consultation des quais disponibles et des créneaux. |
| **Planificateur de Créneaux**| `PLANIFICATEUR` | Optimisation et réservation des créneaux d'amarrage sur les quais. |
| **Administrateur** | `ADMIN` | Accès superviseur global et panneau d'administration Django (`/admin/`). |

### 🔒 Sécurité de l'interface `/admin/`
L'accès à l'URL `/admin/` est protégé par le middleware `AdminAccessControlMiddleware` :
- Les utilisateurs non connectés ou ne disposant pas du rôle `ADMIN` se voient refuser l'accès via un écran sécurisé **`403 - Page non accessible`**.
- Le formulaire d'administration natif Django n'est jamais exposé publiquement.

---

## 6. Lancer la Suite de Tests Automatisés

La suite de tests couvre l'authentification, le contrôle d'accès, la landing page et le CRUD complet des entrepôts et quais.

### Exécuter l'ensemble des tests (recommandé avec `--keepdb`) :
```bash
uv run python manage.py test --keepdb
```

### Exécuter les tests d'un module spécifique :
```bash
# Tests du module Entrepôts & Quais
uv run python manage.py test entrepots.tests --keepdb

# Tests d'authentification et de contrôle d'accès
uv run python manage.py test accounts.tests --keepdb

# Tests de la landing page
uv run python manage.py test landing.tests --keepdb
```

---

## 7. Structure du Projet

```text
CargoLink/
├── accounts/                  # Module Utilisateurs, Profils & Authentification
│   ├── models.py              # UserProfile étendu avec rôles (ENTREPOT, etc.)
│   ├── middleware.py          # AdminAccessControlMiddleware (sécurité /admin)
│   ├── views.py               # Signup, Login avec redirection 'next', Logout
│   ├── static/accounts/css/   # auth.css (Formulaires de connexion, cartes 403)
│   └── templates/accounts/    # login.html, signup.html, admin_access_denied.html
│
├── entrepots/                 # Module Gestion des Entrepôts & Quais
│   ├── models.py              # Entrepot et Quai (métriques calculées, statuts)
│   ├── forms.py               # EntrepotForm, QuaiForm (validations client/serveur)
│   ├── views.py               # CRUD complet Entrepôts et Quais
│   ├── management/commands/   # populate_entrepots.py (Génération données de test)
│   ├── static/entrepots/css/  # entrepots.css (Design system dédié, KPI, dots)
│   └── templates/entrepots/   # Listes, détails, formulaires et suppressions
│
├── landing/                   # Vitrine publique & Layout commun
│   ├── templates/landing/     # base.html (Header/Navbar, Footer), landing.html
│   └── static/landing/css/    # base.css (Variables de thème, boutons, typographie)
│
├── cargolink/                 # Configuration centrale du projet
│   ├── settings.py            # Paramètres Django, PostgreSQL Supabase, LOGIN_URL
│   └── urls.py                # Routage global des applications
│
├── pyproject.toml             # Spécification des dépendances Python
└── README.md                  # Ce guide de démarrage
```

---

## 8. Règles de Contribution & Conventions

1. **Design & Interface Utilisateur** :
   - N'utilisez **pas d'emojis** bruts dans l'interface. Utilisez des icônes vectorielles SVG (style Lucide, `viewBox="0 0 24 24"`) et les puces d'état lumineuses `.status-dot`.
   - Utilisez le fichier CSS propre à chaque module (`static/<module>/css/<module>.css`). Évitez les balises `<style>` inline dans les templates HTML.
2. **Validation des modifications** :
   - Avant de commiter, assurez-vous que tous les tests passent avec `uv run python manage.py test --keepdb`.
3. **Workflow Git** :
   - Créez une branche de travail dédiée pour chaque fonctionnalité (`git checkout -b feature/ma-fonctionnalite`).
   - Ne poussez jamais directement sur `main` sans validation préalable.