# Documentation Complète du Backend PhishGuard

## 📋 Vue d'Ensemble

PhishGuard Backend est une API REST construite avec FastAPI qui fournit des services de détection de phishing alimentés par l'intelligence artificielle. Le backend gère l'authentification, l'analyse d'emails/URLs, l'intégration avec Gmail/Outlook, et la gestion des utilisateurs.

---

## 🏗️ Architecture Générale

### Technologies Principales
- **FastAPI** - Framework web moderne et rapide pour Python
- **SQLAlchemy 2.0** - ORM asynchrone pour la base de données
- **PostgreSQL** - Base de données relationnelle (via Supabase)
- **Uvicorn** - Serveur ASGI haute performance
- **Scikit-learn** - Machine Learning pour la détection
- **OAuth2** - Authentification avec Gmail/Outlook
- **JWT** - Tokens d'authentification
- **Bcrypt** - Hachage des mots de passe

### Architecture en Couches
```
┌─────────────────────────────────────┐
│         API Routes (FastAPI)        │  ← Endpoints HTTP
├─────────────────────────────────────┤
│      Services (Business Logic)      │  ← Logique métier
├─────────────────────────────────────┤
│      Models (SQLAlchemy ORM)        │  ← Modèles de données
├─────────────────────────────────────┤
│      Database (PostgreSQL)          │  ← Stockage persistant
└─────────────────────────────────────┘
```

---

## 📁 Structure des Dossiers

```
backend/
├── app/                    # Code source principal
│   ├── middleware/        # Middlewares (rate limiting, monitoring)
│   ├── models/           # Modèles SQLAlchemy et schémas Pydantic
│   ├── routes/           # Endpoints API (contrôleurs)
│   ├── services/         # Logique métier
│   │   ├── detection/   # Module de détection ML
│   │   └── email_templates/  # Templates HTML emails
│   ├── utils/           # Utilitaires
│   ├── __init__.py
│   ├── database.py      # Configuration base de données
│   └── main.py          # Application FastAPI principale
├── ml_models/           # Modèles ML entraînés (.pkl)
├── scripts/             # Scripts utilitaires
├── uploads/             # Fichiers uploadés (photos de profil)
├── .env                 # Variables d'environnement
├── requirements.txt     # Dépendances Python
└── run.py              # Point d'entrée du serveur
```

---

## 🚀 Fichiers de Démarrage

### **run.py**
**Rôle:** Point d'entrée principal pour démarrer le serveur.

**Fonctionnalité:**
```python
- Configure le chemin Python
- Lance Uvicorn avec hot-reload
- Affiche les informations de démarrage
- Port: 8000
- Host: 0.0.0.0 (accessible depuis le réseau)
```

**Commande:**
```bash
python run.py
```

**Sortie:**
```
Starting PhishGuard Backend Server
API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/api/health
```

---

### **app/main.py**
**Rôle:** Configuration de l'application FastAPI.

**Composants:**

1. **Lifespan Events**
   - Startup: Initialise la base de données
   - Shutdown: Nettoie les ressources

2. **CORS Configuration**
   - Autorise les requêtes depuis le frontend (localhost:5173)
   - Credentials: true
   - Méthodes: toutes
   - Headers: tous

3. **Middlewares**
   - DatabaseMonitorMiddleware: Surveille les connexions DB
   - Rate Limiting: Limite les requêtes par IP

4. **Routers Inclus**
   - `/api` - Analyse
   - `/api/auth` - Authentification
   - `/api/email` - Fournisseurs email
   - `/api/admin` - Administration
   - Et 10+ autres routes

**Endpoints Racine:**
- `GET /` - Informations API
- `GET /docs` - Documentation Swagger
- `GET /redoc` - Documentation ReDoc

---

## 🗄️ Base de Données

### **app/database.py**
**Rôle:** Configuration et gestion de la base de données.

**Composants:**

1. **Engine Asynchrone**
```python
- PostgreSQL avec asyncpg
- Pool de connexions: 10
- Max overflow: 5
- Pool recycle: 3600s (1h)
- SSL pour Supabase
```

2. **Session Factory**
```python
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

3. **Dependency Injection**
```python
async def get_db():
    # Fournit une session DB aux routes
    # Gère commit/rollback automatiquement
```

4. **Initialisation**
```python
async def init_db():
    # Crée toutes les tables au démarrage
```

**Variables d'Environnement:**
- `DATABASE_URL` - URL de connexion PostgreSQL

---

## 📦 Dépendances (requirements.txt)

### **Framework Web**
- `fastapi==0.115.5` - Framework API
- `uvicorn[standard]==0.32.1` - Serveur ASGI
- `pydantic==2.10.3` - Validation de données

### **Base de Données**
- `sqlalchemy==2.0.36` - ORM asynchrone
- `asyncpg==0.30.0` - Driver PostgreSQL async
- `greenlet==3.3.1` - Support async

### **Machine Learning**
- `scikit-learn==1.8.0` - Algorithmes ML
- `pandas==2.2.3` - Manipulation de données
- `numpy==2.1.3` - Calculs numériques
- `joblib==1.4.2` - Sérialisation modèles
- `xgboost==2.1.3` - Gradient boosting

### **Authentification & Sécurité**
- `passlib[bcrypt]==1.7.4` - Hachage mots de passe
- `python-jose[cryptography]==3.3.0` - JWT tokens
- `pyotp==2.9.0` - 2FA (TOTP)
- `qrcode==8.0` - Génération QR codes

### **Intégrations Email**
- `google-auth==2.27.0` - Auth Google
- `google-auth-oauthlib==1.2.0` - OAuth2 Google
- `google-api-python-client==2.116.0` - Gmail API
- `httpx==0.27.0` - Client HTTP async

### **Utilitaires**
- `python-dotenv==1.0.0` - Variables d'environnement
- `email-validator==2.3.0` - Validation emails
- `tldextract==5.1.2` - Extraction domaines
- `pillow==11.0.0` - Traitement images

---

## 🔧 Configuration (.env)

### **Variables Essentielles**

```env
# Base de données
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Sécurité
SECRET_KEY=votre_clé_secrète_très_longue
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Gmail OAuth
GOOGLE_CLIENT_ID=votre_client_id
GOOGLE_CLIENT_SECRET=votre_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/gmail/callback

# Outlook OAuth
OUTLOOK_CLIENT_ID=votre_client_id
OUTLOOK_CLIENT_SECRET=votre_client_secret
OUTLOOK_REDIRECT_URI=http://localhost:8000/api/outlook/callback

# Email Service (pour notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

---

## 📊 Modèles de Données

### **Structure des Modèles**

Le dossier `app/models/` contient deux types de fichiers:
1. **`*_models.py`** - Modèles SQLAlchemy (tables DB)
2. **`*_schemas.py`** - Schémas Pydantic (validation API)

> 📚 La description détaillée de chaque table et de chaque schéma se trouve dans **[BACKEND_PART2_MODELS.md](BACKEND_PART2_MODELS.md)**.

---

## 🛣️ Couches de l'Application

Le backend est découpé en 5 grandes couches qui correspondent chacune à un fichier de documentation dédié :

| Couche | Description | Documentation |
|---|---|---|
| **1. Démarrage / Config** | `run.py`, `app/main.py`, `app/database.py` (lifespan, CORS, middlewares) | Le présent document (Partie 1) |
| **2. Modèles** | SQLAlchemy ORM + schémas Pydantic | [BACKEND_PART2_MODELS.md](BACKEND_PART2_MODELS.md) |
| **3. Routes API** | Tous les endpoints REST organisés par domaine | [BACKEND_PART3_ROUTES.md](BACKEND_PART3_ROUTES.md) |
| **4. Services** | Logique métier (auth, détection ML, email, sessions, 2FA…) | [BACKEND_PART4_SERVICES.md](BACKEND_PART4_SERVICES.md) |
| **5. Middlewares / Utils / Déploiement** | Rate limiting, monitoring DB, géolocalisation, déploiement | [BACKEND_PART5_FINAL.md](BACKEND_PART5_FINAL.md) |

---

## 🤖 Stack ML (résumé)

| Modèle | Type | Dataset | Accuracy | Fichier |
|---|---|---|---|---|
| **Email / Texte** | LinearSVC + TF-IDF | ~19 741 emails | **97,5%** | `phishing_model.pkl` + `vectorizer.pkl` |
| **URL** | Random Forest (23 features) | ~822 000 URLs | **94,6%** | `url_classifier.pkl` |
| **Hybride** | Combinaison Email + URL | — | — | `hybrid_email_detector.py` |

> 📚 Détail complet (preprocessing, features, choix d'algorithmes, métriques) dans **[ML_DETECTION_DETAILLEE.md](ML_DETECTION_DETAILLEE.md)**.

---

## 🔄 Cycle de Vie d'une Requête d'Analyse

```
1. Client (React)  →  POST /api/analyze-email  (Bearer JWT)
2. Middleware rate_limit            (vérifie 100 req/min/IP)
3. Middleware database_monitor      (compte connexions actives)
4. Dépendance get_current_active_user (décode JWT, charge user)
5. Dépendance get_db                (ouvre AsyncSession)
6. Route analysis.analyze_email
       ↓
   PhishingDetector.analyze_email_hybrid()
       ├─ EmailPreprocessor.preprocess()        (RFC822 → texte propre)
       ├─ EmailDetector.analyze()               (LinearSVC + règles)
       │     ├─ TF-IDF vectorize
       │     ├─ model.decision_function()
       │     └─ sigmoid → confidence %
       ├─ Pour chaque URL extraite : URLDetector.analyze()
       └─ Combine résultats + decision_trace
7. StatsService.update_statistics()  (incrémente stats user + global)
8. AnalysisHistory.insert()          (sauvegarde l'analyse)
9. Réponse JSON  →  Client
```

---

## ⚙️ Démarrer le Backend en Local

```bash
cd backend
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # remplir les valeurs
python scripts/init_db.py           # crée les tables
python run.py                       # http://localhost:8000
```

Documentation interactive Swagger : **http://localhost:8000/docs**
Health check : **http://localhost:8000/api/health**

