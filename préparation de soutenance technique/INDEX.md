# 📚 Préparation Soutenance Technique — PhishGuard

> Dossier centralisé pour la préparation de la soutenance technique du projet **PhishGuard** (détection de phishing par IA).

---

## 🗺️ Carte de lecture (par ordre conseillé)

### 1️⃣ Comprendre le projet (vision globale)
| # | Document | Ce qu'on y apprend |
|---|---|---|
| 1 | [PRESENTATION_PROJET.md](PRESENTATION_PROJET.md) | Contexte, problématique, objectifs, solution proposée, public cible |
| 2 | [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) | Diagrammes (architecture, séquence, modèle de données) en Mermaid |

### 2️⃣ Maîtriser la stack technique
| # | Document | Ce qu'on y apprend |
|---|---|---|
| 3 | [DOCUMENTATION_BACKEND_COMPLETE.md](DOCUMENTATION_BACKEND_COMPLETE.md) | **Partie 1** — Démarrage, `main.py`, base de données, dépendances |
| 4 | [BACKEND_PART2_MODELS.md](BACKEND_PART2_MODELS.md) | **Partie 2** — Modèles SQLAlchemy + schémas Pydantic |
| 5 | [BACKEND_PART3_ROUTES.md](BACKEND_PART3_ROUTES.md) | **Partie 3** — Tous les endpoints REST |
| 6 | [BACKEND_PART4_SERVICES.md](BACKEND_PART4_SERVICES.md) | **Partie 4** — Services / logique métier |
| 7 | [BACKEND_PART5_FINAL.md](BACKEND_PART5_FINAL.md) | **Partie 5** — Middlewares, utils, déploiement |
| 8 | [DOCUMENTATION_FRONTEND_COMPLETE.md](DOCUMENTATION_FRONTEND_COMPLETE.md) | Frontend React (composants, contextes, routing) |
| 9 | [ML_DETECTION_DETAILLEE.md](ML_DETECTION_DETAILLEE.md) | Deep dive Machine Learning (datasets, features, métriques) |

### 3️⃣ Préparer le passage devant le jury
| # | Document | Ce qu'on y apprend |
|---|---|---|
| 10 | [PLAN_SOUTENANCE.md](PLAN_SOUTENANCE.md) | Déroulé minute par minute de la présentation orale |
| 11 | [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | Scénario de démo live (étape par étape, plan B en cas de bug) |
| 12 | [QUESTIONS_REPONSES.md](QUESTIONS_REPONSES.md) | Questions probables du jury avec réponses préparées |
| 13 | [CHECKLIST_J-21.md](CHECKLIST_J-21.md) | Planning de préparation sur 3 semaines |

---

## 🎯 Pitch en 30 secondes

> *« PhishGuard est une plateforme web qui protège les utilisateurs contre les attaques de phishing.*
> *Elle analyse en temps réel les emails et les URLs suspects grâce à deux modèles de machine learning (LinearSVC à 97,5 % d'accuracy pour le texte, Random Forest à 94,6 % pour les URLs) et se connecte directement à Gmail et Outlook via OAuth 2.0 pour scanner la boîte de réception.*
> *L'application est construite avec FastAPI côté backend, React + Vite côté frontend, PostgreSQL pour la persistance, et inclut authentification JWT, 2FA, gestion des sessions, panneau d'administration et système de notifications. »*

---

## 🏷️ Chiffres-clés à retenir

| Indicateur | Valeur |
|---|---|
| Lignes de code backend (Python) | ~7 000 |
| Lignes de code frontend (React) | ~6 000 |
| Endpoints REST | **70+** (organisés en 12 routers) |
| Tables en base de données | **10+** (users, analysis_history, statistics, sessions, audit_logs, notifications, …) |
| Modèles ML | **2 + 1 hybride** |
| Accuracy modèle email | **97,5 %** (LinearSVC + TF-IDF, 19 741 emails) |
| Accuracy modèle URL | **94,6 %** (Random Forest, 23 features, 822 K URLs) |
| Providers email intégrés | **2** (Gmail + Outlook via OAuth 2.0) |
| Méthodes de protection | JWT, bcrypt, 2FA TOTP + backup codes, rate limiting, CORS, audit logs, désactivation réversible |
| Composants React | 50+ |
| Pages distinctes (UI) | 10+ |

---

## 🛠️ Stack technique en un coup d'œil

**Backend** : Python 3.11 · FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL (Supabase) · scikit-learn · joblib · Uvicorn · python-jose (JWT) · passlib/bcrypt · pyotp (2FA) · google-api-python-client · httpx

**Frontend** : React 19 · Vite 7 · React Router 7 · Axios · Tailwind CSS 4 · Recharts · date-fns · lucide-react

**ML / Data** : scikit-learn (LinearSVC, RandomForestClassifier, TfidfVectorizer) · pandas · numpy · xgboost · joblib

**Sécurité** : OAuth 2.0 (Google + Microsoft) · JWT HS256 · bcrypt · TOTP (2FA) · rate limiting in-memory · audit logs · géolocalisation IP

---

## ✅ Ce que le jury va probablement chercher à valider

1. **Tu maîtrises ton code** — tu peux ouvrir n'importe quel fichier et expliquer ce qu'il fait.
2. **Tu justifies tes choix techniques** — pourquoi FastAPI ? Pourquoi LinearSVC ? Pourquoi Random Forest ? Pourquoi PostgreSQL ?
3. **Tu connais les limites** — qu'est-ce qui ne marche pas encore ? Quels sont les faux positifs / négatifs ?
4. **Tu as une vision** — quelles évolutions futures ? Comment passer en production ?
5. **La démo fonctionne** — tu as répété, tu as un plan B, tu connais 2-3 exemples par cœur.

> ➡️ Pour chacun de ces points, voir [QUESTIONS_REPONSES.md](QUESTIONS_REPONSES.md).

---

## 📞 Contacts / Liens utiles

- Repo GitHub : https://github.com/YassineBassoumi/PhishGuard
- Documentation API (en local) : http://localhost:8000/docs
- README projet : [../README.md](../README.md)
