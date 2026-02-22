# Documentation Backend - Partie 5: Middlewares, Utils & Déploiement

## 🛡️ Middlewares (app/middleware/)

### **rate_limiter.py**
**Rôle:** Limitation du taux de requêtes (protection DDoS).

**Fonctionnalité:**
```python
- Limite: 100 requêtes par minute par IP
- Stockage en mémoire (dict)
- Cleanup automatique des anciennes entrées
- Retourne 429 Too Many Requests si dépassé
```

**Implémentation:**
```python
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    ip = request.client.host
    current_time = time.time()
    
    # Vérifie limite
    if ip in rate_limit_storage:
        requests = rate_limit_storage[ip]
        # Filtre requêtes dernière minute
        recent = [t for t in requests if current_time - t < 60]
        
        if len(recent) >= 100:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
    
    # Enregistre requête
    rate_limit_storage[ip].append(current_time)
    
    return await call_next(request)
```

**Exceptions:**
- Routes publiques: /docs, /redoc, /openapi.json
- Health check: /api/health

---

### **database_monitor.py**
**Rôle:** Surveillance des connexions base de données.

**Classe:** `DatabaseMonitorMiddleware`

**Fonctionnalité:**
```python
- Compte connexions actives
- Détecte fuites de connexions
- Log warnings si > seuil
- Mesure temps de requête DB
```

**Métriques:**
- Connexions actives
- Connexions max atteintes
- Temps moyen de requête
- Requêtes lentes (> 1s)

**Alertes:**
- Warning si > 8 connexions actives
- Critical si > 10 connexions
- Email admin si problème persistant

---

## 🔧 Utilitaires (app/utils/)

### **geolocation.py**
**Rôle:** Géolocalisation par adresse IP.

**Fonction:** `get_location_from_ip(ip: str)`

**Fonctionnalité:**
```python
- Utilise API ipapi.co
- Retourne: ville, pays, région
- Cache les résultats (1h)
- Fallback si API indisponible
```

**Exemple:**
```python
location = get_location_from_ip("8.8.8.8")
# Retourne: "Mountain View, United States"
```

**Cas Spéciaux:**
- localhost (127.0.0.1) → "Local"
- IP privées → "Private Network"
- Erreur API → "Unknown"

---

### **permissions.py**
**Rôle:** Vérification des permissions utilisateur.

**Fonctions:**

1. **`require_role(required_role: str)`**
   - Décorateur pour routes
   - Vérifie rôle utilisateur
   - Raise 403 si insuffisant

2. **`can_access_resource(user, resource)`**
   - Vérifie accès à une ressource
   - Logique de propriété
   - Retourne: bool

3. **`is_admin(user)`**
   - Vérifie si admin ou superadmin
   - Retourne: bool

4. **`is_superadmin(user)`**
   - Vérifie si superadmin
   - Retourne: bool

**Hiérarchie des Rôles:**
```
superadmin > admin > user
```

**Utilisation:**
```python
@router.get("/admin/users")
@require_role("admin")
async def get_users(user = Depends(get_current_user)):
    # Route protégée admin
    pass
```

---

### **rate_limit_utils.py**
**Rôle:** Utilitaires pour rate limiting avancé.

**Fonctions:**

1. **`check_rate_limit(key: str, limit: int, window: int)`**
   - Vérifie limite pour une clé
   - Window en secondes
   - Retourne: (allowed: bool, remaining: int)

2. **`increment_counter(key: str)`**
   - Incrémente compteur
   - Utilisé après requête réussie

3. **`reset_counter(key: str)`**
   - Réinitialise compteur
   - Utilisé après window expirée

**Exemples d'Utilisation:**
```python
# Login: 5 tentatives / 15 minutes
allowed, remaining = check_rate_limit(
    f"login:{email}",
    limit=5,
    window=900
)

# Email verification: 3 envois / heure
allowed, remaining = check_rate_limit(
    f"email_verify:{user_id}",
    limit=3,
    window=3600
)
```

---

## 📁 Modèles ML (ml_models/)

### **phishing_model.pkl**
**Type:** SVM (Support Vector Machine)
**Usage:** Détection de phishing dans emails
**Features:** TF-IDF vectorization (5000 features)
**Accuracy:** ~95%

**Entraînement:**
- Dataset: 10,000+ emails (phishing + légitimes)
- Preprocessing: lowercase, remove stopwords
- Vectorization: TF-IDF
- Algorithm: LinearSVC

---

### **phishing_url_model_final_v3.pkl**
**Type:** SVM
**Usage:** Détection de phishing dans URLs
**Features:** 12 caractéristiques extraites
**Accuracy:** ~93%

**Features Utilisées:**
1. IP address usage
2. URL length
3. URL shortener
4. @ symbol
5. Double slash
6. Dash in domain
7. Subdomain dots
8. HTTPS
9. Non-standard port
10. Suspicious keywords
11. Subdomain parts
12. Suspicious TLD

---

### **vectorizer.pkl**
**Type:** TfidfVectorizer
**Usage:** Vectorisation du texte des emails
**Config:**
- max_features: 5000
- ngram_range: (1, 2)
- min_df: 2
- max_df: 0.95

---

## 📜 Scripts Utilitaires (scripts/)

### **init_db.py**
**Rôle:** Initialisation de la base de données.

**Fonctionnalité:**
```python
- Crée toutes les tables
- Initialise données de base
- Vérifie connexion DB
```

**Usage:**
```bash
python scripts/init_db.py
```

**Sortie:**
```
Initializing PhishGuard Database
Creating tables...
✅ Database tables created successfully!
Tables created:
  - users
  - analysis_history
  - statistics
  - email_providers
  - user_email_credentials
  - ...
```

---

### **promote_to_superadmin.py**
**Rôle:** Promouvoir un utilisateur en superadmin.

**Usage:**
```bash
python scripts/promote_to_superadmin.py username
```

**Fonctionnalité:**
```python
- Trouve user par username
- Change role à "superadmin"
- Crée audit log
- Affiche confirmation
```

**Sortie:**
```
✅ User 'john' promoted to superadmin
```

---

### **verify_user.py**
**Rôle:** Vérifier manuellement un email utilisateur.

**Usage:**
```bash
python scripts/verify_user.py username
```

**Fonctionnalité:**
```python
- Trouve user par username
- Marque email_verified = True
- Affiche confirmation
```

---

### **setup.py**
**Rôle:** Vérification de l'environnement.

**Usage:**
```bash
python scripts/setup.py
```

**Vérifications:**
```python
✅ .env file found
✅ DATABASE_URL configured
✅ SECRET_KEY configured
✅ ML models found:
   - phishing_model.pkl
   - phishing_url_model_final_v3.pkl
   - vectorizer.pkl
✅ SMTP configured
⚠️  GOOGLE_CLIENT_ID not set (Gmail disabled)
✅ Database connection successful
```

---

### **cleanup_orphaned_pictures.py**
**Rôle:** Nettoyer les photos de profil orphelines.

**Usage:**
```bash
python scripts/cleanup_orphaned_pictures.py
```

**Fonctionnalité:**
```python
- Liste fichiers dans uploads/profile_pictures/
- Compare avec DB (user.profile_picture)
- Identifie fichiers orphelins
- Demande confirmation
- Supprime fichiers
- Affiche espace libéré
```

**Sortie:**
```
📊 Found 5 profile pictures in database
📁 Found 8 files in upload directory

⚠️  Found 3 orphaned files:
  - old-pic-1.jpg (245 KB)
  - old-pic-2.jpg (189 KB)
  - old-pic-3.jpg (312 KB)

❓ Delete these files? (yes/no): yes

✅ Cleanup complete!
   Deleted: 3 files
   Freed: 0.73 MB
```

---

## 📤 Uploads (uploads/)

### **Structure:**
```
uploads/
└── profile_pictures/
    ├── uuid1.jpg
    ├── uuid2.png
    └── uuid3.webp
```

### **Gestion:**
- Noms de fichiers: UUID v4
- Formats acceptés: JPG, PNG, GIF, WebP
- Taille max: 5 MB
- Validation: Pillow (vérification image valide)
- Stockage: Système de fichiers local

### **Sécurité:**
- Validation du type MIME
- Vérification de l'extension
- Scan antivirus (recommandé en production)
- Permissions restrictives (read-only pour web)

---

## 🚀 Déploiement

### **Environnement de Développement**

**Prérequis:**
```bash
- Python 3.11+
- PostgreSQL 14+
- pip
```

**Installation:**
```bash
# 1. Cloner le repo
git clone https://github.com/user/phishguard.git
cd phishguard/backend

# 2. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Configurer .env
cp .env.example .env
# Éditer .env avec vos valeurs

# 5. Initialiser DB
python scripts/init_db.py

# 6. Créer superadmin
python scripts/promote_to_superadmin.py admin

# 7. Lancer serveur
python run.py
```

**Serveur de Développement:**
- URL: http://localhost:8000
- Hot reload: activé
- Logs: console + phishguard.log

---

### **Environnement de Production**

**Serveur ASGI:**
```bash
# Gunicorn avec Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name api.phishguard.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**SSL/TLS:**
```bash
# Certbot (Let's Encrypt)
certbot --nginx -d api.phishguard.com
```

**Systemd Service:**
```ini
[Unit]
Description=PhishGuard API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/phishguard/backend
Environment="PATH=/var/www/phishguard/backend/venv/bin"
ExecStart=/var/www/phishguard/backend/venv/bin/gunicorn \
  app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

---

### **Variables d'Environnement Production**

```env
# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://user:pass@db.supabase.co:5432/postgres

# Security
SECRET_KEY=super_long_random_string_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URL=https://phishguard.com

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxx

# OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=https://api.phishguard.com/api/gmail/callback

OUTLOOK_CLIENT_ID=xxx
OUTLOOK_CLIENT_SECRET=xxx
OUTLOOK_REDIRECT_URI=https://api.phishguard.com/api/outlook/callback

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

### **Monitoring et Logs**

**Logging:**
```python
# Configuration dans main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phishguard.log'),
        logging.StreamHandler()
    ]
)
```

**Sentry (Error Tracking):**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0
)
```

**Prometheus Metrics:**
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

### **Backup et Maintenance**

**Backup Base de Données:**
```bash
# Backup quotidien
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restauration
psql $DATABASE_URL < backup_20240101.sql
```

**Nettoyage:**
```bash
# Sessions expirées
python scripts/cleanup_expired_sessions.py

# Photos orphelines
python scripts/cleanup_orphaned_pictures.py

# Logs anciens
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 📊 Performance

### **Optimisations Appliquées**

1. **Base de Données:**
   - Index sur colonnes fréquemment requêtées
   - Pool de connexions (10 connexions)
   - Requêtes asynchrones
   - Prepared statements désactivés (pgbouncer)

2. **API:**
   - Pagination sur toutes les listes
   - Cache des résultats ML (5 min)
   - Compression gzip
   - Rate limiting

3. **ML:**
   - Lazy loading des modèles
   - Vectorization en batch
   - Cache des prédictions

### **Métriques Cibles**

- Temps de réponse API: < 200ms (p95)
- Analyse ML: < 500ms
- Connexions DB: < 8 actives
- Uptime: > 99.9%

---

## 🔐 Sécurité

### **Mesures Implémentées**

1. **Authentification:**
   - JWT avec expiration
   - Bcrypt pour mots de passe
   - 2FA optionnel (TOTP)
   - Rate limiting login

2. **Autorisation:**
   - RBAC (Role-Based Access Control)
   - Vérification permissions
   - Audit logs

3. **Protection:**
   - CORS configuré
   - HTTPS obligatoire (production)
   - SQL injection: ORM
   - XSS: validation Pydantic
   - CSRF: tokens

4. **Données:**
   - Tokens OAuth chiffrés
   - Mots de passe hachés
   - Sessions sécurisées
   - Logs d'audit

---

## 📚 Documentation API

### **Swagger UI**
- URL: http://localhost:8000/docs
- Interactive
- Test des endpoints
- Schémas de données

### **ReDoc**
- URL: http://localhost:8000/redoc
- Documentation lisible
- Export PDF possible

---

Cette documentation complète couvre l'ensemble du backend PhishGuard!
