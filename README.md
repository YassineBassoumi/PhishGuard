# 🛡️ PhishGuard - Détection de Phishing par IA

Application web de détection de phishing utilisant l'intelligence artificielle pour analyser les emails et URLs suspects.

---

## 🚀 Fonctionnalités

### 🔍 Détection
- ✅ Analyse d'emails (ML + règles)
- ✅ Analyse d'URLs (ML + règles)
- ✅ Analyse depuis boîte email (Gmail, Outlook)
- ✅ Analyse manuelle (copier-coller)
- ✅ Analyse progressive en temps réel

### 📧 Intégration Email
- ✅ Connexion Gmail (OAuth 2.0)
- ✅ Connexion Outlook (OAuth 2.0)
- ✅ Récupération des emails
- ✅ Recherche avancée
- ✅ Analyse directe depuis la boîte

### 👤 Gestion Utilisateurs
- ✅ Inscription / Connexion
- ✅ Vérification email
- ✅ Authentification 2FA
- ✅ Gestion de profil
- ✅ Historique d'analyses
- ✅ Notifications

### 📊 Statistiques
- ✅ Tableau de bord
- ✅ Historique des analyses
- ✅ Distribution des menaces
- ✅ Statistiques personnelles

### 🔐 Sécurité
- ✅ JWT Authentication
- ✅ Rate limiting
- ✅ CORS configuré
- ✅ Validation des données
- ✅ Gestion des sessions

---

## 🏗️ Architecture

### Backend (Python/FastAPI)
```
backend/
├── app/
│   ├── models/          # Modèles de données
│   ├── routes/          # Endpoints API
│   ├── services/        # Logique métier
│   │   └── detection/   # Système de détection ML
│   ├── middleware/      # Middlewares
│   └── utils/           # Utilitaires
├── ml_models/           # Modèles ML entraînés
└── scripts/             # Scripts utilitaires
```

### Frontend (React/Vite)
```
frontend/
├── src/
│   ├── components/      # Composants React
│   ├── assets/          # Images, styles
│   └── App.jsx          # Application principale
└── public/              # Fichiers statiques
```

---

## 🛠️ Installation

### Prérequis
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+

### Backend

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
cd backend
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env avec vos credentials

# Initialiser la base de données
python scripts/init_db.py

# Lancer le serveur
python run.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/phishguard_db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
```

---

## 📚 Documentation

### Guides principaux
- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Résumé des corrections récentes
- **[GMAIL_TOKEN_FIX.md](GMAIL_TOKEN_FIX.md)** - Résolution problème tokens Gmail
- **[FIX_EMAIL_ANALYSIS_INCONSISTENCY.md](FIX_EMAIL_ANALYSIS_INCONSISTENCY.md)** - Fix incohérence analyse

### Documentation technique
- **[BACKEND_PART2_MODELS.md](BACKEND_PART2_MODELS.md)** - Modèles de données
- **[BACKEND_PART3_ROUTES.md](BACKEND_PART3_ROUTES.md)** - Routes API
- **[BACKEND_PART4_SERVICES.md](BACKEND_PART4_SERVICES.md)** - Services
- **[ML_URL_FEATURES_DOCUMENTATION.md](ML_URL_FEATURES_DOCUMENTATION.md)** - Features ML

### Scripts
- **[backend/scripts/README.md](backend/scripts/README.md)** - Documentation des scripts

---

## 🧪 Tests

### Test de cohérence email
```bash
python backend/scripts/debug_email_analysis_inconsistency.py
```

### Test des endpoints
```bash
# Analyse de message/texte (SMS, email, etc.)
curl -X POST http://localhost:8000/api/analyze-email \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"content": "URGENT! Your account has been suspended. Click here to verify now!"}'

# Note: L'endpoint accepte uniquement du texte brut, pas besoin d'en-têtes email structurés
```

---

## 🐛 Problèmes connus et solutions

### 1. Gmail "invalid_grant"
**Problème :** Token expiré après 7 jours  
**Solution :** Voir [GMAIL_TOKEN_FIX.md](GMAIL_TOKEN_FIX.md)

### 2. Analyses incohérentes
**Problème :** Résultats différents Gmail vs manuel  
**Solution :** Voir [FIX_EMAIL_ANALYSIS_INCONSISTENCY.md](FIX_EMAIL_ANALYSIS_INCONSISTENCY.md)

---

## 📊 Modèles ML

### Email Detection
- **Modèle :** SVM avec TF-IDF
- **Fichiers :** `phishing_model.pkl`, `vectorizer.pkl`
- **Précision :** ~95%

### URL Detection
- **Modèle :** Random Forest (12 features)
- **Fichier :** `phishing_url_best_model.pkl`
- **Précision :** 100% (sur dataset test)

---

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📝 Changelog

### Version 1.0 (2026-04-21)
- ✅ Fix incohérence analyse email (HTML → Texte)
- ✅ Gestion automatique tokens Gmail expirés
- ✅ Amélioration extraction contenu email
- ✅ Logging de débogage

---

## 📄 Licence

Ce projet est sous licence MIT.

---

## 👥 Auteurs

- **Équipe PhishGuard**

---

## 🙏 Remerciements

- Datasets de phishing utilisés pour l'entraînement
- Bibliothèques open-source (FastAPI, React, scikit-learn)
- Communauté de sécurité informatique

---

**Dernière mise à jour :** 2026-04-21
